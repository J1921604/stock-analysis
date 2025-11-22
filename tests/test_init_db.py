"""
Database initialization script tests
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from init_db import init_database, verify_database


class TestInitDatabase:
    """Test database initialization"""
    
    def test_init_database_creates_tables(self, tmp_path):
        """Test that init_database creates all required tables"""
        db_path = tmp_path / "test.db"
        schema_path = Path(__file__).parent.parent / "schema.sql"
        
        # Initialize database
        init_database(str(db_path), str(schema_path))
        
        # Verify database exists
        assert db_path.exists()
        
        # Connect and verify tables
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'companies',
            'financials',
            'stock_prices',
            'analysis_cache',
            'topix_data',
            'notification_history'
        }
        
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
        conn.close()
    
    def test_init_database_creates_indexes(self, tmp_path):
        """Test that init_database creates all required indexes"""
        db_path = tmp_path / "test.db"
        schema_path = Path(__file__).parent.parent / "schema.sql"
        
        init_database(str(db_path), str(schema_path))
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        # Should have at least 10 indexes
        assert len(indexes) >= 10, f"Expected at least 10 indexes, got {len(indexes)}"
        conn.close()
    
    def test_init_database_creates_sample_data(self, tmp_path):
        """Test that init_database creates sample companies"""
        db_path = tmp_path / "test.db"
        schema_path = Path(__file__).parent.parent / "schema.sql"
        
        init_database(str(db_path), str(schema_path))
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        
        assert count >= 2, f"Expected at least 2 sample companies, got {count}"
        conn.close()
    
    def test_verify_database_returns_true(self, tmp_path):
        """Test that verify_database returns True for valid database"""
        db_path = tmp_path / "test.db"
        schema_path = Path(__file__).parent.parent / "schema.sql"
        
        init_database(str(db_path), str(schema_path))
        result = verify_database(str(db_path))
        
        assert result is True


class TestDatabaseSchema:
    """Test database schema integrity"""
    
    @pytest.fixture
    def db_conn(self, tmp_path):
        """Create a test database"""
        db_path = tmp_path / "test.db"
        schema_path = Path(__file__).parent.parent / "schema.sql"
        
        from init_db import init_database
        init_database(str(db_path), str(schema_path))
        
        conn = sqlite3.connect(str(db_path))
        # PRAGMA設定を有効化（接続ごとに必要）
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.close()
    
    def test_companies_table_structure(self, db_conn):
        """Test companies table has correct columns"""
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA table_info(companies)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {'id', 'name', 'market', 'sector', 'shares_outstanding', 'market_cap'}
        assert expected_columns.issubset(columns)
    
    def test_financials_table_structure(self, db_conn):
        """Test financials table has correct columns"""
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA table_info(financials)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {'company_id', 'filing_date', 'cash', 'securities', 'receivables', 'inventory', 'liabilities', 'revenue', 'net_income'}
        assert expected_columns.issubset(columns)
    
    def test_stock_prices_table_structure(self, db_conn):
        """Test stock_prices table has correct columns"""
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA table_info(stock_prices)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {'company_id', 'date', 'open', 'high', 'low', 'close', 'volume'}
        assert expected_columns.issubset(columns)
    
    def test_foreign_key_constraints(self, db_conn):
        """Test that foreign key constraints are enabled"""
        cursor = db_conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()[0]
        
        assert result == 1, "Foreign key constraints should be enabled"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
