#!/usr/bin/env python3
"""
XBRLパーサー - 財務データ抽出スクリプト

対象要素:
- 現金及び現金同等物
- 有価証券
- 売上債権
- 棚卸資産
- 総資産
- 負債合計
- 売上高
- 純利益

Usage:
    python scripts/parse_xbrl.py --input data/raw/xbrl/S1234567.zip --output data/cache/parsed
    python scripts/parse_xbrl.py --batch data/raw/xbrl --db data/db/stock-analysis.db
"""

import argparse
import logging
import os
import re
import sqlite3
import zipfile
from pathlib import Path
from typing import Dict, Optional, List
from xml.etree import ElementTree as ET

from lxml import etree

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class XBRLParser:
    """XBRLパーサー"""
    
    # XBRL名前空間（EDINET標準）
    NAMESPACES = {
        'xbrli': 'http://www.xbrl.org/2003/instance',
        'jpcrp': 'http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2023-11-01',
        'jppfs': 'http://disclosure.edinet-fsa.go.jp/taxonomy/jppfs/2023-11-01',
        'dei': 'http://xbrl.sec.gov/dei/2023'
    }
    
    # 財務項目マッピング（XBRL要素名 -> DB カラム名）
    FINANCIAL_ITEMS = {
        'CashAndCashEquivalents': 'cash',
        'ShortTermInvestmentSecurities': 'securities',
        'NotesAndAccountsReceivableTrade': 'receivables',
        'Inventories': 'inventory',
        'Assets': 'total_assets',
        'Liabilities': 'liabilities',
        'NetSales': 'revenue',
        'ProfitLoss': 'net_income',
    }
    
    def __init__(self):
        pass
    
    def extract_from_zip(self, zip_path: Path) -> Optional[Dict]:
        """
        ZIPファイルからXBRL抽出・パース
        
        Args:
            zip_path: ZIPファイルパス
        
        Returns:
            財務データ辞書 または None
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # XBRL Instance ファイル検索（*_jpcrp*_cor.xbrl）
                xbrl_files = [f for f in zf.namelist() if f.endswith('.xbrl') and 'jpcrp' in f]
                
                if not xbrl_files:
                    logger.warning(f"No XBRL file found in {zip_path.name}")
                    return None
                
                # 最初のXBRLファイルを使用
                xbrl_file = xbrl_files[0]
                logger.debug(f"Parsing XBRL: {xbrl_file}")
                
                with zf.open(xbrl_file) as f:
                    tree = etree.parse(f)
                    return self.parse_xbrl(tree)
        
        except Exception as e:
            logger.error(f"Failed to extract XBRL from {zip_path.name}: {e}")
            return None
    
    def parse_xbrl(self, tree: etree._ElementTree) -> Optional[Dict]:
        """
        XBRLツリーから財務データ抽出
        
        Args:
            tree: lxml ElementTree
        
        Returns:
            財務データ辞書 または None
        """
        root = tree.getroot()
        
        # 企業情報抽出
        company_id = self._extract_company_id(root)
        filing_date = self._extract_filing_date(root)
        
        if not company_id or not filing_date:
            logger.warning("Failed to extract company_id or filing_date")
            return None
        
        # 財務データ抽出
        financial_data = {
            'company_id': company_id,
            'filing_date': filing_date
        }
        
        for xbrl_name, db_column in self.FINANCIAL_ITEMS.items():
            value = self._extract_numeric_fact(root, xbrl_name)
            financial_data[db_column] = value
        
        logger.info(f"Parsed financials for {company_id} ({filing_date})")
        return financial_data
    
    def _extract_company_id(self, root) -> Optional[str]:
        """証券コード抽出"""
        # EDINETコード -> 証券コード変換が必要
        # 簡易実装: context内のidentifierから抽出
        for elem in root.xpath('.//xbrli:identifier', namespaces=self.NAMESPACES):
            text = elem.text
            if text and len(text) == 4:  # 4桁の証券コード
                return text
        
        # fallback: dei:EntityCentralIndexKey
        for elem in root.xpath('.//dei:EntityCentralIndexKey', namespaces=self.NAMESPACES):
            text = elem.text
            if text and text.isdigit() and len(text) == 4:
                return text
        
        return None
    
    def _extract_filing_date(self, root) -> Optional[str]:
        """決算日抽出"""
        # dei:DocumentPeriodEndDate
        for elem in root.xpath('.//dei:DocumentPeriodEndDate', namespaces=self.NAMESPACES):
            text = elem.text
            if text:
                # YYYYMMDD -> YYYY-MM-DD 変換
                if len(text) == 8 and text.isdigit():
                    return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
                return text
        
        return None
    
    def _extract_numeric_fact(self, root, fact_name: str) -> Optional[float]:
        """
        数値ファクト抽出
        
        Args:
            root: XML root
            fact_name: XBRL要素名（例: CashAndCashEquivalents）
        
        Returns:
            数値 または None
        """
        # jppfs名前空間で検索
        xpath = f'.//jppfs:{fact_name}'
        
        for elem in root.xpath(xpath, namespaces=self.NAMESPACES):
            text = elem.text
            if not text:
                continue
            
            try:
                # カンマ除去 + float変換
                value = float(text.replace(',', ''))
                
                # unit属性確認（円単位）
                unit = elem.get('unitRef')
                if unit and 'JPY' in unit.upper():
                    return value
                
                # decimals属性で桁数調整
                decimals = elem.get('decimals')
                if decimals and decimals.isdigit():
                    return value * (10 ** int(decimals))
                
                return value
            
            except ValueError:
                continue
        
        return None
    
    def save_to_db(self, data: Dict, db_path: Path) -> bool:
        """
        財務データをDB保存
        
        Args:
            data: 財務データ辞書
            db_path: データベースパス
        
        Returns:
            成功時True
        """
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # 既存データ削除（同一企業・同一決算日）
            cursor.execute(
                "DELETE FROM financials WHERE company_id = ? AND filing_date = ?",
                (data['company_id'], data['filing_date'])
            )
            
            # 新規データ挿入
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = tuple(data.values())
            
            cursor.execute(
                f"INSERT INTO financials ({columns}) VALUES ({placeholders})",
                values
            )
            
            conn.commit()
            logger.info(f"Saved financials for {data['company_id']} ({data['filing_date']})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()


def batch_parse_xbrl(input_dir: Path, db_path: Path) -> int:
    """
    ディレクトリ内の全ZIPファイルをバッチ処理
    
    Args:
        input_dir: 入力ディレクトリ
        db_path: データベースパス
    
    Returns:
        処理成功数
    """
    parser = XBRLParser()
    success_count = 0
    
    zip_files = list(input_dir.glob('*.zip'))
    logger.info(f"Found {len(zip_files)} ZIP files in {input_dir}")
    
    for zip_path in zip_files:
        logger.info(f"Processing: {zip_path.name}")
        
        data = parser.extract_from_zip(zip_path)
        if data:
            if parser.save_to_db(data, db_path):
                success_count += 1
    
    logger.info(f"Batch parse completed: {success_count}/{len(zip_files)} successful")
    return success_count


def main():
    parser = argparse.ArgumentParser(description='Parse XBRL files and extract financial data')
    parser.add_argument('--input', type=str, help='Input ZIP file path')
    parser.add_argument('--batch', type=str, help='Batch process directory')
    parser.add_argument('--output', type=str, default='data/cache/parsed',
                        help='Output directory (default: data/cache/parsed)')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    xbrl_parser = XBRLParser()
    
    if args.batch:
        # バッチ処理モード
        input_dir = Path(args.batch)
        batch_parse_xbrl(input_dir, db_path)
    
    elif args.input:
        # 単一ファイル処理モード
        zip_path = Path(args.input)
        data = xbrl_parser.extract_from_zip(zip_path)
        
        if data:
            xbrl_parser.save_to_db(data, db_path)
    
    else:
        logger.error("Either --input or --batch must be specified")


if __name__ == '__main__':
    main()
