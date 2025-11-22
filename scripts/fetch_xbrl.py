#!/usr/bin/env python3
"""
EDINET API連携 - XBRL取得スクリプト

EDINET API仕様:
- Base URL: https://disclosure.edinet-fsa.go.jp/api/v1
- レート制限: 1秒/1ファイル（Token Bucket Algorithm実装）
- リトライ: 3回まで（バックオフ: 1秒、2秒、4秒）

Usage:
    python scripts/fetch_xbrl.py --ticker 9501 --output data/raw/xbrl
    python scripts/fetch_xbrl.py --since-db --output data/raw/xbrl
"""

import argparse
import logging
import os
import time
import sqlite3
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Business day calculation helper
def get_recent_business_days(days: int = 2) -> str:
    """Get date N business days ago (approximation: skip weekends)"""
    current = datetime.now()
    count = 0
    while count < days:
        current -= timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Sunday=6
            count += 1
    return current.strftime("%Y-%m-%d")

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class EDINETClient:
    """EDINET API クライアント"""
    
    BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v1"
    
    def __init__(self, rate_limit_delay: float = 1.0, connect_timeout: int = 10, read_timeout: int = 30):
        """
        Args:
            rate_limit_delay: リクエスト間の遅延時間（秒）
            connect_timeout: 接続タイムアウト（秒）
            read_timeout: 読み取りタイムアウト（秒）
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        
        # リトライ設定付きセッション
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,  # 1秒、2秒、4秒
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _wait_for_rate_limit(self):
        """レート制限遵守のための待機"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_document_list(self, date: str, doc_type: str = "2") -> List[Dict]:
        """
        書類一覧取得
        
        Args:
            date: 日付（YYYY-MM-DD）
            doc_type: 書類種別（1:有価証券通知書、2:有価証券報告書等）
        
        Returns:
            書類情報のリスト
        """
        self._wait_for_rate_limit()
        
        url = f"{self.BASE_URL}/documents.json"
        params = {
            "date": date.replace("-", ""),
            "type": doc_type
        }
        
        try:
            response = self.session.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout))
            response.raise_for_status()
            data = response.json()
            
            if data.get("metadata", {}).get("status") != "200":
                logger.warning(f"API returned non-200 status: {data}")
                return []
            
            results = data.get("results", [])
            logger.info(f"Found {len(results)} documents for {date}")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get document list for {date}: {e}")
            return []
    
    def download_document(self, doc_id: str, output_path: Path) -> bool:
        """
        XBRL書類ダウンロード
        
        Args:
            doc_id: 書類管理番号
            output_path: 保存先パス（ZIPファイル）
        
        Returns:
            成功時True
        """
        self._wait_for_rate_limit()
        
        url = f"{self.BASE_URL}/documents/{doc_id}"
        params = {"type": "1"}  # type=1: ZIPファイル（XBRLを含む）
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            response = self.session.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout * 2), stream=True)
            response.raise_for_status()
            
            # ZIPファイル保存
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {doc_id} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {doc_id}: {e}")
            return False


def fetch_xbrl_for_ticker(
    ticker: str,
    client: EDINETClient,
    output_dir: Path,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> int:
    """
    指定銘柄のXBRL取得
    
    Args:
        ticker: 証券コード（例: 9501）
        client: EDINET APIクライアント
        output_dir: 保存先ディレクトリ
        start_date: 開始日（YYYY-MM-DD）
        end_date: 終了日（YYYY-MM-DD）
    
    Returns:
        ダウンロード成功数
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Fetching XBRL for ticker={ticker}, period={start_date} to {end_date}")
    
    downloaded_count = 0
    total_candidates = 0
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current_date <= end_dt:
        date_str = current_date.strftime("%Y-%m-%d")
        documents = client.get_document_list(date_str)
        
        # 対象銘柄の書類をフィルタ
        matching_docs = [d for d in documents if d.get("secCode", "").startswith(ticker)]
        total_candidates += len(matching_docs)
        
        for idx, doc in enumerate(matching_docs, 1):
            doc_id = doc.get("docID")
            if not doc_id:
                continue
            
            # 既にダウンロード済みかチェック
            output_file = output_dir / f"{doc_id}.zip"
            if output_file.exists():
                logger.debug(f"Already downloaded: {doc_id}")
                continue
            
            # ダウンロード（進捗表示）
            logger.info(f"Downloading {doc_id} ({downloaded_count + 1} successful, {idx}/{len(matching_docs)} on {date_str})")
            if client.download_document(doc_id, output_file):
                downloaded_count += 1
        
        current_date += timedelta(days=1)
    
    logger.info(f"Downloaded {downloaded_count} XBRL files for ticker={ticker}")
    return downloaded_count


def fetch_xbrl_since_db(
    db_path: Path,
    client: EDINETClient,
    output_dir: Path
) -> int:
    """
    DB最終更新日以降のXBRL取得（差分更新）
    
    Args:
        db_path: データベースパス
        client: EDINET APIクライアント
        output_dir: 保存先ディレクトリ
    
    Returns:
        ダウンロード成功数
    """
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 最終更新日取得
    cursor.execute("SELECT MAX(filing_date) FROM financials")
    result = cursor.fetchone()
    last_update = result[0] if result and result[0] else None
    
    # 企業一覧取得
    cursor.execute("SELECT id FROM companies")
    tickers = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    if not tickers:
        logger.warning("No companies found in database")
        return 0
    
    # デフォルトは1年前から（標準設定に戻す）
    start_date = last_update if last_update else (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Fetching XBRL for {len(tickers)} companies since {start_date}")
    
    total_downloaded = 0
    for idx, ticker in enumerate(tickers, 1):
        logger.info(f"Processing ticker {ticker} ({idx}/{len(tickers)})")
        downloaded = fetch_xbrl_for_ticker(ticker, client, output_dir, start_date, end_date)
        total_downloaded += downloaded
        logger.info(f"Ticker {ticker} complete: {downloaded} new files (total so far: {total_downloaded})")
    
    return total_downloaded


def main():
    parser = argparse.ArgumentParser(description='Fetch XBRL from EDINET API')
    parser.add_argument('--ticker', type=str, help='Target ticker code (e.g., 9501)')
    parser.add_argument('--since-db', action='store_true', 
                        help='Fetch XBRLs since last DB update (default: 2 business days if DB empty)')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--output', type=str, default='data/raw/xbrl',
                        help='Output directory (default: data/raw/xbrl)')
    parser.add_argument('--since', type=str, 
                        help='Start date (YYYY-MM-DD, default: 2 business days ago for --since-db, 1 year for --ticker)')
    parser.add_argument('--start-date', type=str, 
                        help='(deprecated, use --since) Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD, default: today)')
    parser.add_argument('--rate-limit', type=float, default=1.0,
                        help='Rate limit delay in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    client = EDINETClient(rate_limit_delay=args.rate_limit)
    
    if args.since_db:
        # 差分更新モード
        db_path = Path(args.db)
        downloaded = fetch_xbrl_since_db(db_path, client, output_dir)
    elif args.ticker:
        # 個別銘柄モード
        downloaded = fetch_xbrl_for_ticker(
            args.ticker, client, output_dir, args.start_date, args.end_date
        )
    else:
        logger.error("Either --ticker or --since-db must be specified")
        return
    
    logger.info(f"Total downloaded: {downloaded} files")


if __name__ == '__main__':
    main()
