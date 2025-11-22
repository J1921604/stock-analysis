#!/usr/bin/env python3
"""
ビルドスクリプト

以下を実行:
1. データベースをsrc/にコピー
2. 静的アセット検証

Usage:
    python scripts/build.py
"""

import shutil
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def build():
    """ビルド実行"""
    
    logger.info("Starting build process...")
    
    # データベースコピー
    db_src = Path('data/db/stock-analysis.db')
    db_dest = Path('src/stock-analysis.db')
    
    if db_src.exists():
        shutil.copy2(db_src, db_dest)
        logger.info(f"✓ Copied database: {db_src} -> {db_dest}")
    else:
        logger.error(f"Database not found: {db_src}")
        return False
    
    # 静的アセット検証
    required_files = [
        'src/index.html',
        'src/styles.css',
        'src/db-loader.js',
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✓ Found: {file_path}")
        else:
            logger.error(f"✗ Missing: {file_path}")
            all_exist = False
    
    if all_exist:
        logger.info("\n✓ Build completed successfully")
        logger.info("  - Database copied to src/")
        logger.info("  - Target companies: TEPCO (9501), 中部電力 (9502), JERA (E36542)")
        return True
    else:
        logger.error("\n✗ Build failed: missing files")
        return False


if __name__ == '__main__':
    success = build()
    exit(0 if success else 1)
