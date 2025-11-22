#!/usr/bin/env python3
"""
統合データパイプライン実行スクリプト

このスクリプトは以下を順次実行します:
1. データベース初期化（オプション）
2. TOPIX構成銘柄の企業マスタ更新
3. 株価データ取得（全企業 + TOPIX）
4. XBRLファイル取得（差分更新）
5. XBRLパース・財務データ登録
6. 3つの解析エンジン実行（NetNet、O'Neil、MarketTop）

Usage:
    python scripts/pipeline.py                     # 全パイプライン実行
    python scripts/pipeline.py --init-db           # DB初期化から実行
    python scripts/pipeline.py --skip-xbrl         # XBRL取得をスキップ
    python scripts/pipeline.py --analysis-only     # 解析のみ実行
"""

import argparse
import logging
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class Pipeline:
    """データパイプライン実行管理"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.scripts_dir = Path('scripts')
    
    def run_command(self, cmd: list, description: str) -> bool:
        """
        外部コマンド実行
        
        Args:
            cmd: コマンドリスト
            description: 実行内容説明
        
        Returns:
            成功時True
        """
        logger.info(f">>> {description}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.stdout:
                logger.info(result.stdout)
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed: {description}")
            if e.stdout:
                logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            return False
    
    def step_init_db(self) -> bool:
        """Step 1: データベース初期化"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'init_db.py'), 
             '--db', str(self.db_path), '--force'],
            "Step 1: Initialize database"
        )
    
    def step_insert_topix_companies(self) -> bool:
        """Step 2: TOPIX構成銘柄をcompaniesテーブルに登録"""
        logger.info(">>> Step 2: Insert TOPIX companies")
        
        # TOPIX Core30の主要銘柄（サンプル）
        topix_companies = [
            ('7203', 'トヨタ自動車', '東証プライム', '輸送用機器', 3262997492, 45000000000000),
            ('6758', 'ソニーグループ', '東証プライム', '電気機器', 1240388753, 15000000000000),
            ('9984', 'ソフトバンクグループ', '東証プライム', '情報・通信業', 4800000000, 10000000000000),
            ('9432', '日本電信電話', '東証プライム', '情報・通信業', 4000000000, 15000000000000),
            ('6861', 'キーエンス', '東証プライム', '電気機器', 231835900, 14000000000000),
            ('8306', '三菱UFJフィナンシャル・グループ', '東証プライム', '銀行業', 12992632502, 12000000000000),
            ('6902', 'デンソー', '東証プライム', '輸送用機器', 913447500, 6000000000000),
            ('6954', 'ファナック', '東証プライム', '電気機器', 1889885350, 6500000000000),
            ('4063', '信越化学工業', '東証プライム', '化学', 1240000000, 9000000000000),
            ('9433', 'KDDI', '東証プライム', '情報・通信業', 2187124430, 8000000000000),
        ]
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for company in topix_companies:
                cursor.execute("""
                    INSERT OR REPLACE INTO companies 
                    (id, name, market, sector, shares_outstanding, market_cap)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, company)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Inserted {len(topix_companies)} TOPIX companies")
            return True
        
        except Exception as e:
            logger.error(f"Failed to insert TOPIX companies: {e}")
            return False
    
    def step_fetch_prices(self) -> bool:
        """Step 3: 株価データ取得（全企業 + TOPIX）"""
        # 全企業の株価取得
        success1 = self.run_command(
            [sys.executable, str(self.scripts_dir / 'fetch_prices.py'),
             '--db', str(self.db_path), '--all'],
            "Step 3a: Fetch stock prices for all companies"
        )
        
        # TOPIX指数取得
        success2 = self.run_command(
            [sys.executable, str(self.scripts_dir / 'fetch_prices.py'),
             '--db', str(self.db_path), '--topix'],
            "Step 3b: Fetch TOPIX index data"
        )
        
        return success1 and success2
    
    def step_fetch_xbrl(self) -> bool:
        """Step 4: XBRL取得（差分更新）"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'fetch_xbrl.py'),
             '--db', str(self.db_path), '--since-db'],
            "Step 4: Fetch XBRL files (differential update)"
        )
    
    def step_parse_xbrl(self) -> bool:
        """Step 5: XBRLパース・財務データ登録"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'parse_xbrl.py'),
             '--db', str(self.db_path), '--batch', 'data/raw/xbrl'],
            "Step 5: Parse XBRL and extract financial data"
        )
    
    def step_analyze_netnet(self) -> bool:
        """Step 6a: NetNet株解析"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'analyzers' / 'netnet.py'),
             '--db', str(self.db_path)],
            "Step 6a: Run NetNet analysis"
        )
    
    def step_analyze_oneil(self) -> bool:
        """Step 6b: O'Neil成長株解析"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'analyzers' / 'oneil.py'),
             '--db', str(self.db_path)],
            "Step 6b: Run O'Neil analysis"
        )
    
    def step_analyze_market_top(self) -> bool:
        """Step 6c: マーケット天井検出"""
        return self.run_command(
            [sys.executable, str(self.scripts_dir / 'analyzers' / 'market_top.py'),
             '--db', str(self.db_path)],
            "Step 6c: Run Market Top detection"
        )
    
    def run_full_pipeline(self, init_db: bool = False, skip_xbrl: bool = False) -> bool:
        """
        完全パイプライン実行
        
        Args:
            init_db: DB初期化を実行するか
            skip_xbrl: XBRL取得をスキップするか
        
        Returns:
            全ステップ成功時True
        """
        logger.info("=" * 60)
        logger.info("Starting Data Pipeline")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        steps = []
        
        if init_db:
            steps.append(('Initialize DB', self.step_init_db))
        
        steps.extend([
            ('Insert TOPIX companies', self.step_insert_topix_companies),
            ('Fetch stock prices', self.step_fetch_prices),
        ])
        
        if not skip_xbrl:
            steps.extend([
                ('Fetch XBRL files', self.step_fetch_xbrl),
                ('Parse XBRL files', self.step_parse_xbrl),
            ])
        
        steps.extend([
            ('Analyze NetNet', self.step_analyze_netnet),
            ('Analyze O\'Neil', self.step_analyze_oneil),
            ('Analyze Market Top', self.step_analyze_market_top),
        ])
        
        # 全ステップ実行
        results = []
        for step_name, step_func in steps:
            logger.info(f"\n{'='*60}")
            result = step_func()
            results.append((step_name, result))
            
            if not result:
                logger.warning(f"Step failed: {step_name}")
        
        # 結果サマリー
        elapsed = datetime.now() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("Pipeline Summary")
        logger.info("=" * 60)
        
        for step_name, result in results:
            status = "✓ SUCCESS" if result else "✗ FAILED"
            logger.info(f"{status}: {step_name}")
        
        success_count = sum(1 for _, result in results if result)
        total_count = len(results)
        
        logger.info(f"\nTotal: {success_count}/{total_count} steps succeeded")
        logger.info(f"Elapsed time: {elapsed}")
        
        return success_count == total_count
    
    def run_analysis_only(self) -> bool:
        """解析のみ実行"""
        logger.info("Running analysis engines only...")
        
        steps = [
            ('NetNet analysis', self.step_analyze_netnet),
            ('O\'Neil analysis', self.step_analyze_oneil),
            ('Market Top detection', self.step_analyze_market_top),
        ]
        
        results = []
        for step_name, step_func in steps:
            result = step_func()
            results.append((step_name, result))
        
        success_count = sum(1 for _, result in results if result)
        return success_count == len(results)


def main():
    parser = argparse.ArgumentParser(description='Run complete data pipeline')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--init-db', action='store_true',
                        help='Initialize database before running pipeline')
    parser.add_argument('--skip-xbrl', action='store_true',
                        help='Skip XBRL fetch and parse steps')
    parser.add_argument('--analysis-only', action='store_true',
                        help='Run analysis engines only (skip data fetch)')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    pipeline = Pipeline(db_path)
    
    if args.analysis_only:
        success = pipeline.run_analysis_only()
    else:
        success = pipeline.run_full_pipeline(
            init_db=args.init_db,
            skip_xbrl=args.skip_xbrl
        )
    
    if success:
        logger.info("\n✓ Pipeline completed successfully")
        sys.exit(0)
    else:
        logger.error("\n✗ Pipeline failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
