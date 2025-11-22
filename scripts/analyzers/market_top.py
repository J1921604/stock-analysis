#!/usr/bin/env python3
"""
マーケット天井検出エンジン

分配日（Distribution Day）判定:
    1. TOPIX終値が前日比-0.2%以上下落
    2. 出来高が前日比+10%以上増加

天井警告:
    過去25営業日間に分配日が5回以上 → 天井警告

Usage:
    python scripts/analyzers/market_top.py --db data/db/stock-analysis.db
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


class MarketTopDetector:
    """マーケット天井検出エンジン"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.window_days = 25  # 分析ウィンドウ（営業日）
        self.threshold_count = 5  # 天井警告閾値
    
    def detect_distribution_days(self) -> List[Dict]:
        """
        分配日検出
        
        Returns:
            分配日リスト（日付、終値、前日比%、出来高、出来高増減%）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 過去50営業日分のTOPIXデータ取得（25営業日 + バッファ）
            cursor.execute("""
                SELECT date, close, volume
                FROM topix_data
                ORDER BY date DESC
                LIMIT 50
            """)
            
            rows = cursor.fetchall()
            
            if len(rows) < 2:
                logger.warning("Insufficient TOPIX data (< 2 days)")
                return []
            
            # 逆順（古い順）に変換
            rows = list(reversed(rows))
            
            distribution_days = []
            
            for i in range(1, len(rows)):
                prev_date, prev_close, prev_volume = rows[i-1]
                curr_date, curr_close, curr_volume = rows[i]
                
                # 前日比計算
                price_change_pct = ((curr_close - prev_close) / prev_close) * 100
                volume_change_pct = ((curr_volume - prev_volume) / prev_volume) * 100 if prev_volume > 0 else 0
                
                # 分配日判定
                is_distribution = (
                    price_change_pct <= -0.2 and
                    volume_change_pct >= 10.0
                )
                
                distribution_days.append({
                    'date': curr_date,
                    'close': curr_close,
                    'price_change_pct': price_change_pct,
                    'volume': curr_volume,
                    'volume_change_pct': volume_change_pct,
                    'is_distribution': is_distribution
                })
            
            return distribution_days
        
        except Exception as e:
            logger.error(f"Failed to detect distribution days: {e}")
            return []
        finally:
            conn.close()
    
    def analyze_market_top(self) -> Optional[Dict]:
        """
        マーケット天井分析
        
        Returns:
            分析結果辞書 または None
        """
        distribution_days = self.detect_distribution_days()
        
        if not distribution_days:
            logger.warning("No distribution days data")
            return None
        
        # 最近25営業日のデータのみ抽出
        recent_days = distribution_days[-self.window_days:] if len(distribution_days) >= self.window_days else distribution_days
        
        # 分配日カウント
        dist_count = sum(1 for day in recent_days if day['is_distribution'])
        
        # 天井判定
        is_top_warning = dist_count >= self.threshold_count
        
        # 最新日付
        latest_date = recent_days[-1]['date'] if recent_days else None
        
        result = {
            'date': latest_date,
            'distribution_count': dist_count,
            'is_top_warning': is_top_warning,
            'window_days': len(recent_days),
            'threshold': self.threshold_count,
            'calculated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if is_top_warning:
            logger.warning(f"⚠️  MARKET TOP WARNING: {dist_count} distribution days in {len(recent_days)} days")
        else:
            logger.info(f"✓ Market normal: {dist_count} distribution days in {len(recent_days)} days")
        
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
            # 既存データ削除（entity_id='market-top'）
            cursor.execute("""
                DELETE FROM analysis_cache
                WHERE company_id = 'market-top' AND analysis_type = 'market_top'
            """)
            
            # 新規データ挿入
            cursor.execute("""
                INSERT INTO analysis_cache
                (company_id, analysis_type, calculated_at, market_top_count)
                VALUES ('market-top', 'market_top', ?, ?)
            """, (
                result['calculated_at'],
                result['distribution_count']
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_distribution_day_details(self) -> List[Dict]:
        """
        分配日詳細取得（過去25営業日）
        
        Returns:
            分配日詳細リスト
        """
        distribution_days = self.detect_distribution_days()
        
        # 最近25営業日のみ返す
        recent_days = distribution_days[-self.window_days:] if len(distribution_days) >= self.window_days else distribution_days
        
        return recent_days


def main():
    parser = argparse.ArgumentParser(description='Market top detector')
    parser.add_argument('--db', type=str, default='data/db/stock-analysis.db',
                        help='Database file path (default: data/db/stock-analysis.db)')
    parser.add_argument('--details', action='store_true',
                        help='Show detailed distribution day list')
    
    args = parser.parse_args()
    
    db_path = Path(args.db)
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    detector = MarketTopDetector(db_path)
    
    # マーケット天井分析
    result = detector.analyze_market_top()
    
    if result:
        detector.save_to_cache(result)
        
        print(f"\n{'='*60}")
        print("Market Top Analysis Result")
        print(f"{'='*60}")
        print(f"Latest Date: {result['date']}")
        print(f"Distribution Days (25d window): {result['distribution_count']}")
        print(f"Threshold: {result['threshold']}")
        print(f"Status: {'⚠️  TOP WARNING' if result['is_top_warning'] else '✓ Normal'}")
        print(f"{'='*60}\n")
        
        # 詳細表示
        if args.details:
            details = detector.get_distribution_day_details()
            
            print("\nDistribution Day Details (Last 25 trading days):")
            print(f"{'Date':<12} {'Close':>8} {'Change%':>8} {'Volume':>12} {'Vol%':>8} {'Dist':>5}")
            print("-" * 60)
            
            for day in details:
                dist_mark = "✓" if day['is_distribution'] else ""
                print(f"{day['date']:<12} {day['close']:>8.2f} {day['price_change_pct']:>7.2f}% "
                      f"{day['volume']:>12,} {day['volume_change_pct']:>7.2f}% {dist_mark:>5}")


if __name__ == '__main__':
    main()
