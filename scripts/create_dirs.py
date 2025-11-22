#!/usr/bin/env python3
"""
ディレクトリ構造作成スクリプト

Usage:
    python scripts/create_dirs.py
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_directory_structure():
    """プロジェクトディレクトリ構造作成"""
    
    directories = [
        # データディレクトリ
        'data/db',                  # SQLiteデータベース
        'data/raw/xbrl',            # XBRLファイル（ZIP）
        'data/raw/prices',          # 株価CSVファイル
        'data/raw/topix',           # TOPIXデータ
        'data/cache/parsed',        # パース済みJSON
        'data/analysis',            # 解析結果CSV
        
        # スクリプトディレクトリ
        'scripts/analyzers',        # 解析エンジン
        
        # テストディレクトリ
        'tests',                    # ユニットテスト
        'tests/e2e',                # E2Eテスト
        
        # フロントエンドディレクトリ
        'src',                      # HTML/CSS/JS
        'src/pages',                # ページHTMLファイル
        
        # ログディレクトリ
        'logs',                     # ログファイル
        
        # ドキュメントディレクトリ
        'docs',                     # 追加ドキュメント
        
        # GitHub Actionsディレクトリ
        '.github/workflows',        # ワークフローYAML
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    # .gitkeepファイル作成（空ディレクトリをGit管理下に置く）
    gitkeep_dirs = [
        'data/raw/xbrl',
        'data/raw/prices',
        'data/raw/topix',
        'data/cache/parsed',
        'data/analysis',
        'logs',
    ]
    
    for dir_path in gitkeep_dirs:
        gitkeep_file = Path(dir_path) / '.gitkeep'
        gitkeep_file.touch()
        logger.info(f"Created .gitkeep: {dir_path}")
    
    logger.info("Directory structure created successfully")


def main():
    create_directory_structure()


if __name__ == '__main__':
    main()
