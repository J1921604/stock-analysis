#!/usr/bin/env python3
"""
株価データ取得スクリプト（Yahoo Finance API）

Usage:
    python scripts/fetch_prices.py --ticker 9501 --output data/raw/prices
    python scripts/fetch_prices.py --db data/db/stock-analysis.db --all
"""

import argparse
import logging
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class StockPriceFetcher:
    """株価データ取得クライアント"""
    
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Args:
            rate_limit_delay: リクエスト間の遅延時間（秒）
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """レート制限遵守のための待機"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch_prices(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        株価データ取得
        
        Args:
            ticker: 証券コード（例: 9501）
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
        
        Returns:
            株価データ（DataFrame）または None
        """
        self._wait_for_rate_limit()
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Yahoo Finance用のティッカー変換（日本株は.Tサフィックス）
        yahoo_ticker = f"{ticker}.T"
        
        try:
            logger.info(f"Fetching prices for {ticker} ({start_date} to {end_date})")
            
            stock = yf.Ticker(yahoo_ticker)
            df = stock.history(start=start_date, end=end_date, auto_adjust=False)
            
            if df.empty:
                logger.warning(f"No price data found for {ticker}")
                return None
            
            # カラム名をDB形式に変換
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # 日付をYYYY-MM-DD形式に変換
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # company_id追加
            df['company_id'] = ticker
            
            # 必要なカラムのみ選択
            df = df[['company_id', 'date', 'open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"Fetched {len(df)} price records for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch prices for {ticker}: {e}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, output_path: Path):
        """
        株価データをCSV保存
        
        Args:
            df: 株価データ
            output_path: 保存先パス
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved to {output_path}")
    
    def save_to_db(self, df: pd.DataFrame, db_path: Path):
        """
        株価データをDB保存
        
        Args:
            df: 株価データ
            db_path: データベースパス
        """
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        
        try:
            # 既存データ削除（同一企業・同一日付）
            company_id = df['company_id'].iloc[0]
            dates = tuple(df['date'].tolist())
            
            placeholders = ','.join(['?'] * len(dates))
            conn.execute(
                f"DELETE FROM stock_prices WHERE company_id = ? AND date IN ({placeholders})",
                (company_id, *dates)
            )
            
            # 新規データ挿入
            df.to_sql('stock_prices', conn, if_exists='append', index=False)
            conn.commit()
            
            logger.info(f"Saved {len(df)} records to database")
            
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            conn.rollback()
        finally:
            conn.close()


def fetch_topix_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    TOPIX指数データ取得
    
    Args:
        start_date: 開始日（YYYY-MM-DD）
        end_date: 終了日（YYYY-MM-DD）
    
    Returns:
        TOPIXデータ（DataFrame）または None
    """
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        logger.info(f"Fetching TOPIX data ({start_date} to {end_date})")
        
        # TOPIXのYahoo Financeティッカー: ^TOPX
        topix = yf.Ticker("^TOPX")
        df = topix.history(start=start_date, end=end_date, auto_adjust=False)
        
        if df.empty:
            logger.warning("No TOPIX data found")
            return None
        
        # カラム名をDB形式に変換
        df = df.reset_index()
        df = df.rename(columns={
            'Date': 'date',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # 日付をYYYY-MM-DD形式に変換
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 必要なカラムのみ選択
        df = df[['date', 'close', 'volume']]
        
        logger.info(f"Fetched {len(df)} TOPIX records")
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch TOPIX data: {e}")
        return None


def save_topix_to_db(df: pd.DataFrame, db_path: Path):
    """
    TOPIXデータをDB保存
    
    Args:
        df: TOPIXデータ
        db_path: データベースパス
    """
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 既存データ削除（同一日付）
        dates = tuple(df['date'].tolist())
        placeholders = ','.join(['?'] * len(dates))
        conn.execute(
            f"DELETE FROM topix_data WHERE date IN ({placeholders})",
            dates
        )
        
        # 新規データ挿入
        df.to_sql('topix_data', conn, if_exists='append', index=False)
        conn.commit()
        
        logger.info(f"Saved {len(df)} TOPIX records to database")
        
    except Exception as e:
        logger.error(f"Failed to save TOPIX to database: {e}")
        conn.rollback()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='Fetch stock prices from Yahoo Finance')
    parser.add_argument('--ticker', type=str, help='Target ticker code (e.g., 9501)')
    parser.add_argument('--all', action='store_true', 
                        help='Fetch prices for all companies in database')
    parser.add_argument('--topix', action='store_true',
                        help='Fetch TOPIX index data')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--output', type=str, default='data/raw/prices',
                        help='Output directory for CSV (default: data/raw/prices)')
    parser.add_argument('--start-date', type=str,
                        help='Start date (YYYY-MM-DD, default: 1 year ago)')
    parser.add_argument('--end-date', type=str,
                        help='End date (YYYY-MM-DD, default: today)')
    parser.add_argument('--rate-limit', type=float, default=0.5,
                        help='Rate limit delay in seconds (default: 0.5)')
    
    args = parser.parse_args()
    
    fetcher = StockPriceFetcher(rate_limit_delay=args.rate_limit)
    db_path = Path(args.db)
    output_dir = Path(args.output)
    
    if args.topix:
        # TOPIX取得
        df = fetch_topix_data(args.start_date, args.end_date)
        if df is not None:
            save_topix_to_db(df, db_path)
            fetcher.save_to_csv(df, output_dir / "topix.csv")
    
    elif args.all:
        # 全企業の株価取得
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM companies")
        tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"Fetching prices for {len(tickers)} companies")
        
        for ticker in tickers:
            df = fetcher.fetch_prices(ticker, args.start_date, args.end_date)
            if df is not None:
                fetcher.save_to_db(df, db_path)
                fetcher.save_to_csv(df, output_dir / f"{ticker}.csv")
    
    elif args.ticker:
        # 個別銘柄の株価取得
        df = fetcher.fetch_prices(args.ticker, args.start_date, args.end_date)
        if df is not None:
            fetcher.save_to_db(df, db_path)
            fetcher.save_to_csv(df, output_dir / f"{args.ticker}.csv")
    
    else:
        logger.error("Either --ticker, --all, or --topix must be specified")


if __name__ == '__main__':
    main()
