#!/usr/bin/env python3
"""
O'Neilスクリーナー - 成長株解析エンジン

解析指標:
1. EPS成長率（3年CAGR）: > 25%
2. EPS成長率（5年CAGR）: > 20%
3. リラティブストレングス（RS）: > 80
4. 売上高成長率: > 15%

RS計算式:
    RS = (株価52週変化率 / TOPIX52週変化率) × 100

Usage:
    python scripts/analyzers/oneil.py --db data/db/stock-analysis.db
"""

import argparse
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ONeilAnalyzer:
    """O'Neil成長株解析エンジン"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def calculate_eps_growth(self, company_id: str) -> Optional[tuple]:
        """
        EPS成長率計算（3年・5年CAGR）
        
        Args:
            company_id: 企業ID
        
        Returns:
            (eps_3y, eps_5y) または None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 過去6年分の財務データ取得（年次決算のみ）
            cursor.execute("""
                SELECT 
                    filing_date,
                    net_income,
                    revenue
                FROM financials
                WHERE company_id = ?
                ORDER BY filing_date DESC
                LIMIT 6
            """, (company_id,))
            
            rows = cursor.fetchall()
            
            if len(rows) < 3:
                return None
            
            # 発行済株式数取得
            cursor.execute("""
                SELECT shares_outstanding
                FROM companies
                WHERE id = ?
            """, (company_id,))
            
            company_row = cursor.fetchone()
            if not company_row or not company_row[0]:
                return None
            
            shares = company_row[0]
            
            # EPS計算
            eps_data = []
            for filing_date, net_income, revenue in rows:
                if net_income is not None and shares > 0:
                    eps = net_income / shares
                    eps_data.append((filing_date, eps))
            
            if len(eps_data) < 3:
                return None
            
            # 3年CAGR計算
            if len(eps_data) >= 3:
                eps_latest = eps_data[0][1]
                eps_3y_ago = eps_data[2][1]
                
                if eps_3y_ago > 0:
                    eps_3y_cagr = ((eps_latest / eps_3y_ago) ** (1/3) - 1) * 100
                else:
                    eps_3y_cagr = None
            else:
                eps_3y_cagr = None
            
            # 5年CAGR計算
            if len(eps_data) >= 5:
                eps_latest = eps_data[0][1]
                eps_5y_ago = eps_data[4][1]
                
                if eps_5y_ago > 0:
                    eps_5y_cagr = ((eps_latest / eps_5y_ago) ** (1/5) - 1) * 100
                else:
                    eps_5y_cagr = None
            else:
                eps_5y_cagr = None
            
            return (eps_3y_cagr, eps_5y_cagr)
        
        except Exception as e:
            logger.error(f"Failed to calculate EPS growth for {company_id}: {e}")
            return None
        finally:
            conn.close()
    
    def calculate_relative_strength(self, company_id: str) -> Optional[float]:
        """
        リラティブストレングス（RS）計算
        
        RS = (株価52週変化率 / TOPIX52週変化率) × 100
        
        Args:
            company_id: 企業ID
        
        Returns:
            RS値 または None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 52週前の日付計算
            date_52w_ago = (datetime.now() - timedelta(weeks=52)).strftime('%Y-%m-%d')
            
            # 株価データ取得（最新 & 52週前）
            cursor.execute("""
                SELECT date, close
                FROM stock_prices
                WHERE company_id = ?
                ORDER BY date DESC
                LIMIT 1
            """, (company_id,))
            
            latest_row = cursor.fetchone()
            if not latest_row:
                return None
            
            latest_date, latest_price = latest_row
            
            cursor.execute("""
                SELECT close
                FROM stock_prices
                WHERE company_id = ? AND date <= ?
                ORDER BY date DESC
                LIMIT 1
            """, (company_id, date_52w_ago))
            
            past_row = cursor.fetchone()
            if not past_row:
                return None
            
            past_price = past_row[0]
            
            if past_price <= 0:
                return None
            
            stock_change = ((latest_price - past_price) / past_price) * 100
            
            # TOPIX変化率取得
            cursor.execute("""
                SELECT close
                FROM topix_data
                ORDER BY date DESC
                LIMIT 1
            """)
            
            topix_latest_row = cursor.fetchone()
            if not topix_latest_row:
                logger.warning("No TOPIX data found")
                return None
            
            topix_latest = topix_latest_row[0]
            
            cursor.execute("""
                SELECT close
                FROM topix_data
                WHERE date <= ?
                ORDER BY date DESC
                LIMIT 1
            """, (date_52w_ago,))
            
            topix_past_row = cursor.fetchone()
            if not topix_past_row:
                return None
            
            topix_past = topix_past_row[0]
            
            if topix_past <= 0:
                return None
            
            topix_change = ((topix_latest - topix_past) / topix_past) * 100
            
            # RS計算
            if topix_change == 0:
                return None
            
            rs = (stock_change / topix_change) * 100
            
            return rs
        
        except Exception as e:
            logger.error(f"Failed to calculate RS for {company_id}: {e}")
            return None
        finally:
            conn.close()
    
    def analyze_company(self, company_id: str) -> Optional[Dict]:
        """
        企業のO'Neil解析実行
        
        Args:
            company_id: 企業ID
        
        Returns:
            解析結果辞書 または None
        """
        # EPS成長率計算
        eps_growth = self.calculate_eps_growth(company_id)
        if not eps_growth:
            logger.debug(f"Failed to calculate EPS growth for {company_id}")
            return None
        
        eps_3y, eps_5y = eps_growth
        
        # RS計算
        rs = self.calculate_relative_strength(company_id)
        
        result = {
            'company_id': company_id,
            'eps_3y': eps_3y,
            'eps_5y': eps_5y,
            'rs': rs,
            'calculated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # スクリーニング判定
        criteria_met = []
        if eps_3y and eps_3y > 25:
            criteria_met.append('EPS_3Y>25%')
        if eps_5y and eps_5y > 20:
            criteria_met.append('EPS_5Y>20%')
        if rs and rs > 80:
            criteria_met.append('RS>80')
        
        if criteria_met:
            logger.info(f"O'Neil criteria met for {company_id}: {', '.join(criteria_met)}")
        
        return result
    
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
                WHERE company_id = ? AND analysis_type = 'oneil'
            """, (result['company_id'],))
            
            # 新規データ挿入
            cursor.execute("""
                INSERT INTO analysis_cache
                (company_id, analysis_type, calculated_at, oneil_eps_3y, oneil_eps_5y, oneil_rs)
                VALUES (?, 'oneil', ?, ?, ?, ?)
            """, (
                result['company_id'],
                result['calculated_at'],
                result['eps_3y'],
                result['eps_5y'],
                result['rs']
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
        全企業に対してO'Neil解析実行
        
        Returns:
            解析成功数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 企業一覧取得
        cursor.execute("SELECT id FROM companies")
        company_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"Starting O'Neil analysis for {len(company_ids)} companies")
        
        success_count = 0
        high_growth_count = 0
        
        for company_id in company_ids:
            result = self.analyze_company(company_id)
            
            if result:
                if self.save_to_cache(result):
                    success_count += 1
                    
                    # 高成長株判定（EPS 3Y > 25% かつ RS > 80）
                    if (result['eps_3y'] and result['eps_3y'] > 25 and
                        result['rs'] and result['rs'] > 80):
                        high_growth_count += 1
                        logger.info(f"  ✓ High Growth: {company_id} "
                                  f"(EPS 3Y={result['eps_3y']:.1f}%, RS={result['rs']:.1f})")
        
        logger.info(f"O'Neil analysis completed: {success_count}/{len(company_ids)} analyzed")
        logger.info(f"High growth stocks (EPS>25% & RS>80): {high_growth_count}")
        
        return success_count


def main():
    parser = argparse.ArgumentParser(description="O'Neil growth stock analyzer")
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--ticker', type=str, help='Analyze specific ticker only')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    analyzer = ONeilAnalyzer(db_path)
    
    if args.ticker:
        # 個別銘柄解析
        result = analyzer.analyze_company(args.ticker)
        if result:
            analyzer.save_to_cache(result)
            print(f"\nEPS Growth (3Y): {result['eps_3y']:.2f}%" if result['eps_3y'] else "N/A")
            print(f"EPS Growth (5Y): {result['eps_5y']:.2f}%" if result['eps_5y'] else "N/A")
            print(f"Relative Strength: {result['rs']:.2f}" if result['rs'] else "N/A")
    else:
        # 全企業解析
        analyzer.analyze_all_companies()


if __name__ == '__main__':
    main()
