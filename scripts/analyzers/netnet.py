#!/usr/bin/env python3
"""
NetNet株解析エンジン

NetNetPBR計算式:
    NetNet = (現金×1.0 + 有価証券×0.75 + 売上債権×0.75) - 総負債
    NetNetPBR = NetNet / 時価総額

割安判定:
    NetNetPBR < 1.0 → 割安株

Usage:
    python scripts/analyzers/netnet.py --db data/db/stock-analysis.db
"""

import argparse
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class NetNetAnalyzer:
    """NetNet株解析エンジン"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def calculate_netnet_pbr(self, company_id: str) -> Optional[Dict]:
        """
        NetNetPBR計算
        
        Args:
            company_id: 企業ID（証券コード）
        
        Returns:
            解析結果辞書 または None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 最新財務データ取得
            cursor.execute("""
                SELECT 
                    filing_date,
                    cash,
                    securities,
                    receivables,
                    liabilities
                FROM financials
                WHERE company_id = ?
                ORDER BY filing_date DESC
                LIMIT 1
            """, (company_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.debug(f"No financial data found for {company_id}")
                return None
            
            filing_date, cash, securities, receivables, liabilities = row
            
            # NULL値チェック
            if any(v is None for v in [cash, securities, receivables, liabilities]):
                logger.debug(f"Incomplete financial data for {company_id}")
                return None
            
            # 最新株価データ取得
            cursor.execute("""
                SELECT close
                FROM stock_prices
                WHERE company_id = ?
                ORDER BY date DESC
                LIMIT 1
            """, (company_id,))
            
            price_row = cursor.fetchone()
            if not price_row:
                logger.debug(f"No stock price data found for {company_id}")
                return None
            
            close_price = price_row[0]
            
            # 発行済株式数取得
            cursor.execute("""
                SELECT shares_outstanding
                FROM companies
                WHERE id = ?
            """, (company_id,))
            
            company_row = cursor.fetchone()
            if not company_row or not company_row[0]:
                logger.debug(f"No shares_outstanding for {company_id}")
                return None
            
            shares_outstanding = company_row[0]
            
            # NetNet計算
            immediate_cash = (
                cash * 1.0 +
                securities * 0.75 +
                receivables * 0.75
            )
            
            netnet = immediate_cash - liabilities
            
            # 時価総額計算
            market_cap = close_price * shares_outstanding
            
            # NetNetPBR計算
            if market_cap <= 0:
                logger.debug(f"Invalid market_cap for {company_id}")
                return None
            
            netnet_pbr = netnet / market_cap
            
            result = {
                'company_id': company_id,
                'filing_date': filing_date,
                'netnet': netnet,
                'market_cap': market_cap,
                'netnet_pbr': netnet_pbr,
                'calculated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"NetNetPBR calculated for {company_id}: {netnet_pbr:.4f}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to calculate NetNetPBR for {company_id}: {e}")
            return None
        finally:
            conn.close()
    
    def save_to_cache(self, result: Dict) -> bool:
        """
        解析結果をanalysis_cacheテーブルに保存
        
        Args:
            result: 解析結果辞書
        
        Returns:
            成功時True
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 既存データ削除
            cursor.execute("""
                DELETE FROM analysis_cache
                WHERE company_id = ? AND analysis_type = 'netnet'
            """, (result['company_id'],))
            
            # 新規データ挿入
            cursor.execute("""
                INSERT INTO analysis_cache
                (company_id, analysis_type, calculated_at, netnet_pbr)
                VALUES (?, 'netnet', ?, ?)
            """, (
                result['company_id'],
                result['calculated_at'],
                result['netnet_pbr']
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def analyze_all_companies(self) -> int:
        """
        全企業に対してNetNet解析実行
        
        Returns:
            解析成功数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 企業一覧取得
        cursor.execute("SELECT id FROM companies")
        company_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"Starting NetNet analysis for {len(company_ids)} companies")
        
        success_count = 0
        undervalued_count = 0
        
        for company_id in company_ids:
            result = self.calculate_netnet_pbr(company_id)
            
            if result:
                if self.save_to_cache(result):
                    success_count += 1
                    
                    if result['netnet_pbr'] < 1.0:
                        undervalued_count += 1
                        logger.info(f"  ✓ Undervalued: {company_id} (NetNetPBR={result['netnet_pbr']:.4f})")
        
        logger.info(f"NetNet analysis completed: {success_count}/{len(company_ids)} analyzed")
        logger.info(f"Undervalued stocks (NetNetPBR < 1.0): {undervalued_count}")
        
        return success_count


def main():
    parser = argparse.ArgumentParser(description='NetNet stock analyzer')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--ticker', type=str, help='Analyze specific ticker only')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    analyzer = NetNetAnalyzer(db_path)
    
    if args.ticker:
        # 個別銘柄解析
        result = analyzer.calculate_netnet_pbr(args.ticker)
        if result:
            analyzer.save_to_cache(result)
            print(f"\nNetNetPBR: {result['netnet_pbr']:.4f}")
            print(f"NetNet: {result['netnet']:,.0f} 円")
            print(f"時価総額: {result['market_cap']:,.0f} 円")
    else:
        # 全企業解析
        analyzer.analyze_all_companies()


if __name__ == '__main__':
    main()
