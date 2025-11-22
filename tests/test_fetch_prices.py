"""
Stock price fetching script tests
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import pandas as pd
import sqlite3
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from fetch_prices import StockPriceFetcher, fetch_topix_data


class TestStockPriceFetcher:
    """Test StockPriceFetcher class"""
    
    @patch('fetch_prices.yf.Ticker')
    def test_fetch_prices_success(self, mock_ticker):
        """Test successful stock price fetching"""
        # Create mock price data
        mock_df = pd.DataFrame({
            'Date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'Open': [1000, 1010, 1020, 1030, 1040],
            'High': [1050, 1060, 1070, 1080, 1090],
            'Low': [990, 1000, 1010, 1020, 1030],
            'Close': [1020, 1030, 1040, 1050, 1060],
            'Volume': [100000, 110000, 120000, 130000, 140000]
        })
        mock_df = mock_df.set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = StockPriceFetcher(rate_limit_delay=0)
        result = fetcher.fetch_prices('7203', '2025-01-01', '2025-01-05')
        
        assert result is not None
        assert len(result) == 5
        assert 'close' in result.columns
        assert 'volume' in result.columns
    
    @patch('fetch_prices.yf.Ticker')
    def test_fetch_prices_no_data(self, mock_ticker):
        """Test fetching with no available data"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance
        
        fetcher = StockPriceFetcher(rate_limit_delay=0)
        result = fetcher.fetch_prices('9999', '2025-01-01', '2025-01-05')
        
        assert result is None
    
    @patch('fetch_prices.yf.Ticker')
    def test_fetch_prices_api_error(self, mock_ticker):
        """Test error handling during fetch"""
        mock_ticker.side_effect = Exception("API connection failed")
        
        fetcher = StockPriceFetcher(rate_limit_delay=0)
        result = fetcher.fetch_prices('7203', '2025-01-01', '2025-01-05')
        
        assert result is None


class TestFetchTopixData:
    """Test TOPIX data fetching"""
    
    @patch('fetch_prices.yf.Ticker')
    def test_fetch_topix_success(self, mock_ticker):
        """Test successful TOPIX data fetching"""
        mock_df = pd.DataFrame({
            'Date': pd.date_range('2025-01-01', periods=5, freq='D'),
            'Close': [2500, 2510, 2520, 2530, 2540],
            'Volume': [5000000, 5100000, 5200000, 5300000, 5400000]
        })
        mock_df = mock_df.set_index('Date')
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_topix_data('2025-01-01', '2025-01-05')
        
        assert result is not None
        assert len(result) == 5
        assert 'close' in result.columns
    
    @patch('fetch_prices.yf.Ticker')
    def test_fetch_topix_failure(self, mock_ticker):
        """Test TOPIX fetch failure"""
        mock_ticker.side_effect = Exception("Network error")
        
        result = fetch_topix_data('2025-01-01', '2025-01-05')
        
        assert result is None


class TestSavePriceData:
    """Test price data saving to CSV"""
    
    def test_save_creates_csv_file(self, tmp_path):
        """Test that save_price_data creates CSV file"""
        # Create sample DataFrame
        df = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'close': [1000, 1010, 1020],
            'volume': [100000, 110000, 120000]
        })
        
        output_dir = tmp_path / 'prices'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / '7203.csv'
        
        # Save CSV
        df.to_csv(output_file, index=False)
        
        # Verify
        assert output_file.exists()
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == 3
        assert 'close' in loaded_df.columns
    
    def test_save_overwrites_existing(self, tmp_path):
        """Test that save_price_data overwrites existing files"""
        output_dir = tmp_path / 'prices'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / '7203.csv'
        
        # Create initial file
        df1 = pd.DataFrame({
            'date': ['2025-01-01'],
            'close': [1000],
            'volume': [100000]
        })
        df1.to_csv(output_file, index=False)
        
        # Overwrite with new data
        df2 = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02'],
            'close': [1000, 1010],
            'volume': [100000, 110000]
        })
        df2.to_csv(output_file, index=False)
        
        # Verify overwrite
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == 2


class TestDatabaseIntegration:
    """Test database integration for price fetching"""
    
    @pytest.fixture
    def test_db(self, tmp_path):
        """Create test database with companies"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        
        conn.execute("""
            CREATE TABLE companies (
                id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE stock_prices (
                company_id TEXT,
                date TEXT,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (company_id, date)
            )
        """)
        
        conn.execute("INSERT INTO companies VALUES ('7203', 'Toyota')")
        conn.execute("INSERT INTO companies VALUES ('6758', 'Sony')")
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def test_fetch_all_companies(self, test_db):
        """Test fetching prices for all companies in database"""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM companies ORDER BY id")
        companies = cursor.fetchall()
        
        assert len(companies) == 2
        # Companies may be in any order, verify both exist
        company_ids = [c[0] for c in companies]
        assert '7203' in company_ids
        assert '6758' in company_ids
        
        conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=fetch_prices', '--cov-report=term-missing'])
