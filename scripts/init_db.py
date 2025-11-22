#!/usr/bin/env python3
"""
データベース初期化スクリプト

Usage:
    python scripts/init_db.py --db data/db/stock-analysis.db
"""

import argparse
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def init_database(db_path: Path, schema_path: Path = Path('schema.sql')):
    """
    データベース初期化
    
    Args:
        db_path: SQLiteデータベースパス
        schema_path: SQLスキーマファイルパス
    """
    try:
        # ディレクトリ作成
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 既存DBチェック
        if db_path.exists():
            logger.warning(f"Database already exists: {db_path}")
            response = input("既存のデータベースを削除して再作成しますか? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("初期化を中止しました")
                return
            
            db_path.unlink()
            logger.info(f"Deleted existing database: {db_path}")
        
        # スキーマ読込
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # データベース作成
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # スキーマ実行
        cursor.executescript(schema_sql)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized successfully: {db_path}")
        
        # 検証
        verify_database(db_path)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def verify_database(db_path: Path):
    """
    データベース検証
    
    Args:
        db_path: SQLiteデータベースパス
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # テーブル一覧取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'companies',
        'financials',
        'stock_prices',
        'analysis_cache',
        'topix_data',
        'notification_history'
    ]
    
    logger.info(f"Tables created: {tables}")
    
    # テーブル確認
    for table in expected_tables:
        if table not in tables:
            logger.error(f"Table missing: {table}")
            raise Exception(f"Table missing: {table}")
    
    # サンプルデータ確認
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    logger.info(f"Sample companies: {company_count}")
    
    if company_count < 2:
        logger.warning("Expected at least 2 sample companies")
    
    # インデックス確認
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
    indexes = [row[0] for row in cursor.fetchall()]
    logger.info(f"Indexes created: {len(indexes)} indexes")
    
    conn.close()
    logger.info("Database verification completed")


def main():
    parser = argparse.ArgumentParser(description='Initialize stock analysis database')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--schema', type=str, default='schema.sql',
                        help='Schema file path (default: schema.sql)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    schema_path = Path(args.schema)
    
    init_database(db_path, schema_path)


if __name__ == '__main__':
    main()
