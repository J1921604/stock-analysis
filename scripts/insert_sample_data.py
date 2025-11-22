#!/usr/bin/env python3
"""
サンプルデータ挿入スクリプト

Usage:
    python scripts/insert_sample_data.py --db data/db/stock-analysis.db
"""

import argparse
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def insert_sample_data(db_path):
    """
    サンプルデータ挿入（企業、財務、株価、TOPIXデータ）
    
    Args:
        db_path: SQLiteデータベースパス（str or Path）
    """
    db_path = Path(db_path)
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        logger.info("Run: python scripts/init_db.py first")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既存データクリア（サンプルデータのみ）
        cursor.execute("DELETE FROM stock_prices WHERE company_id IN ('1', '2', '101', '102', '103')")
        cursor.execute("DELETE FROM financials WHERE company_id IN ('1', '2', '101', '102', '103')")
        cursor.execute("DELETE FROM companies WHERE id IN ('101', '102', '103')")
        cursor.execute("DELETE FROM topix_data")
        
        # サンプル企業追加（既存の2社 + 新規3社 = 計5社）
        sample_companies = [
            ('6758', 'ソニーグループ', '東証プライム', '電気機器', 1200000000, 12000000000000),
            ('9984', 'ソフトバンクグループ', '東証プライム', '情報・通信業', 5000000000, 10000000000000),
            ('9432', '日本電信電話', '東証プライム', '情報・通信業', 4000000000, 15000000000000),
        ]
        
        cursor.executemany("""
            INSERT INTO companies (id, name, market, sector, shares_outstanding, market_cap)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_companies)
        
        logger.info(f"Inserted {len(sample_companies)} sample companies")
        
        # サンプル財務データ（NetNet株検索用）
        base_date = (datetime.now().date() - timedelta(days=180)).isoformat()
        
        sample_financials = [
            # トヨタ（7203）: NetNet株条件満たす（流動資産 > 総負債）
            ('7203', base_date, 50000000000, 30000000000, 15000000000, 8000000000,
             120000000000, 45000000000, 800000000000, 400000000000),
            
            # キーエンス（6861）: NetNet株条件満たさない（総負債大）
            ('6861', base_date, 30000000000, 20000000000, 8000000000, 4000000000,
             600000000000, 550000000000, 600000000000, 300000000000),
            
            # ソニー（6758）: NetNet株候補
            ('6758', base_date, 40000000000, 25000000000, 12000000000, 6000000000,
             700000000000, 350000000000, 700000000000, 450000000000),
            
            # ソフトバンクG（9984）: 高負債（NetNet株不適格）
            ('9984', base_date, 60000000000, 40000000000, 20000000000, 10000000000,
             1000000000000, 850000000000, 1000000000000, 600000000000),
            
            # NTT（9432）: NetNet株候補
            ('9432', base_date, 35000000000, 22000000000, 10000000000, 5000000000,
             650000000000, 320000000000, 650000000000, 420000000000),
        ]
        
        cursor.executemany("""
            INSERT INTO financials (
                company_id, filing_date, cash, securities, receivables, inventory,
                total_assets, liabilities, revenue, net_income
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_financials)
        
        logger.info(f"Inserted {len(sample_financials)} sample financials")
        
        # サンプル株価データ（過去90日分）
        today = datetime.now().date()
        
        for company_id in ['7203', '6861', '6758', '9984', '9432']:
            prices = []
            base_price = 1000 if company_id in ['7203', '6861'] else 2000
            
            for day_offset in range(90):
                date = (today - timedelta(days=90 - day_offset)).isoformat()
                # 簡易的な価格変動シミュレーション
                variation = (day_offset % 10 - 5) * 10
                open_price = base_price + variation
                high = open_price + 20
                low = open_price - 15
                close = open_price + (day_offset % 3 - 1) * 5
                volume = 1000000 + (day_offset * 10000)
                
                prices.append((company_id, date, open_price, high, low, close, volume))
            
            cursor.executemany("""
                INSERT INTO stock_prices (company_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, prices)
        
        logger.info(f"Inserted {90 * 5} stock price records (90 days × 5 companies)")
        
        # TOPIX指数データ（過去90日分）
        topix_data = []
        base_topix = 2400
        
        for day_offset in range(90):
            date = (today - timedelta(days=90 - day_offset)).isoformat()
            variation = (day_offset % 10 - 5) * 5
            close = base_topix + variation + (day_offset % 3 - 1) * 3
            volume = 500000000
            
            topix_data.append((date, close, volume))
        
        cursor.executemany("""
            INSERT INTO topix_data (date, close, volume)
            VALUES (?, ?, ?)
        """, topix_data)
        
        logger.info(f"Inserted {len(topix_data)} TOPIX data records")
        
        conn.commit()
        
        # 検証
        cursor.execute("SELECT COUNT(*) FROM companies")
        companies_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM financials")
        financials_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM stock_prices")
        prices_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM topix_data")
        topix_count = cursor.fetchone()[0]
        
        logger.info(f"Verification: companies={companies_count}, financials={financials_count}, "
                   f"stock_prices={prices_count}, topix_data={topix_count}")
        
        conn.close()
        logger.info("Sample data inserted successfully")
        
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='Insert sample data into database')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    insert_sample_data(db_path)


if __name__ == '__main__':
    main()
