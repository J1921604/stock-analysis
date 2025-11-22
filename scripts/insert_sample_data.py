#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""サンプルデータ挿入スクリプト - 東京電力・中部電力の2社 + TOPIXデータ"""
import argparse
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def insert_sample_data(db_path):
    """分析対象の2社とTOPIXデータのみ挿入"""
    conn = sqlite3.connect(Path(db_path))
    cursor = conn.cursor()
    
    # 既存データをクリア
    cursor.execute("DELETE FROM stock_prices")
    cursor.execute("DELETE FROM financials")
    cursor.execute("DELETE FROM analysis_cache")
    cursor.execute("DELETE FROM topix_data")
    
    # 分析対象企業2社のみ挿入
    cursor.executemany(
        "INSERT OR REPLACE INTO companies (id, name, market, sector, shares_outstanding, market_cap) VALUES (?, ?, ?, ?, ?, ?)",
        [
            ('9501', '東京電力ホールディングス', '東証プライム', '電気・ガス業', 16070000000, None),
            ('9502', '中部電力', '東証プライム', '電気・ガス業', 1900000000, None)
        ]
    )
    logger.info("Inserted 2 target companies: 9501, 9502")
    
    # TOPIXデータ挿入 (過去90日分)
    topix_data = [
        (
            (datetime.now().date() - timedelta(days=i)).isoformat(),
            2500 + i * 2,
            5000000 + i * 10000
        )
        for i in range(90, -1, -1)
    ]
    cursor.executemany("INSERT INTO topix_data (date, close, volume) VALUES (?, ?, ?)", topix_data)
    logger.info(f"Inserted {len(topix_data)} TOPIX data records")
    
    conn.commit()
    
    # 検証
    companies_count = cursor.execute('SELECT COUNT(*) FROM companies WHERE id IN ("9501", "9502")').fetchone()[0]
    financials_count = cursor.execute('SELECT COUNT(*) FROM financials').fetchone()[0]
    prices_count = cursor.execute('SELECT COUNT(*) FROM stock_prices').fetchone()[0]
    topix_count = cursor.execute('SELECT COUNT(*) FROM topix_data').fetchone()[0]
    
    logger.info(f"Verification: companies={companies_count}, financials={financials_count}, stock_prices={prices_count}, topix_data={topix_count}")
    
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Insert sample data for Tokyo Electric Power & Chubu Electric Power')
    parser.add_argument('--db', default='data/db/stock-analysis.db', help='Database path')
    args = parser.parse_args()
    insert_sample_data(args.db)
