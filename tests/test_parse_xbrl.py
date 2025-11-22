"""
XBRL parser tests
"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from lxml import etree
import sqlite3

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from parse_xbrl import XBRLParser


class TestXBRLParser:
    """Test XBRL parser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return XBRLParser()
    
    @pytest.fixture
    def sample_xbrl(self):
        """Create sample XBRL XML"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
                    xmlns:jppfs="http://disclosure.edinet-fsa.go.jp/taxonomy/jppfs/2023-11-01"
                    xmlns:jpcrp="http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2023-11-01"
                    xmlns:dei="http://xbrl.sec.gov/dei/2023">
          <xbrli:context id="CurrentYearInstant">
            <xbrli:entity>
              <xbrli:identifier scheme="http://disclosure.edinet-fsa.go.jp">7203</xbrli:identifier>
            </xbrli:entity>
            <xbrli:period>
              <xbrli:instant>2024-03-31</xbrli:instant>
            </xbrli:period>
          </xbrli:context>
          
          <xbrli:unit id="JPY">
            <xbrli:measure>iso4217:JPY</xbrli:measure>
          </xbrli:unit>
          
          <dei:DocumentPeriodEndDate contextRef="CurrentYearInstant">20240331</dei:DocumentPeriodEndDate>
          <jpcrp:SecurityCodeDEI contextRef="CurrentYearInstant">7203</jpcrp:SecurityCodeDEI>
          
          <jppfs:CashAndCashEquivalents contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            100000000000
          </jppfs:CashAndCashEquivalents>
          <jppfs:ShortTermInvestmentSecurities contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            50000000000
          </jppfs:ShortTermInvestmentSecurities>
          <jppfs:NotesAndAccountsReceivableTrade contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            75000000000
          </jppfs:NotesAndAccountsReceivableTrade>
          <jppfs:Inventories contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            30000000000
          </jppfs:Inventories>
          <jppfs:Assets contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            500000000000
          </jppfs:Assets>
          <jppfs:Liabilities contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            200000000000
          </jppfs:Liabilities>
          <jppfs:NetSales contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            800000000000
          </jppfs:NetSales>
          <jppfs:ProfitLoss contextRef="CurrentYearInstant" unitRef="JPY" decimals="-6">
            50000000000
          </jppfs:ProfitLoss>
        </xbrli:xbrl>"""
        
        return etree.fromstring(xml.encode('utf-8'))
    
    def test_parser_initialization(self, parser):
        """Test parser initializes correctly"""
        assert parser is not None
        assert hasattr(parser, 'NAMESPACES')
        assert hasattr(parser, 'FINANCIAL_ITEMS')
    
    def test_extract_filing_date_success(self, parser, sample_xbrl):
        """Test filing date extraction"""
        tree = etree.ElementTree(sample_xbrl)
        data = parser.parse_xbrl(tree)
        
        assert data is not None
        assert data['filing_date'] == '2024-03-31'
    
    def test_extract_numeric_fact_success(self, parser, sample_xbrl):
        """Test numeric fact extraction"""
        value = parser._extract_numeric_fact(sample_xbrl, 'CashAndCashEquivalents')
        
        assert value == 100000000000.0
    
    def test_extract_numeric_fact_not_found(self, parser, sample_xbrl):
        """Test handling of missing fact"""
        value = parser._extract_numeric_fact(sample_xbrl, 'NonExistentFact')
        
        assert value is None
    
    def test_parse_xbrl_complete(self, parser, sample_xbrl):
        """Test complete XBRL parsing"""
        tree = etree.ElementTree(sample_xbrl)
        data = parser.parse_xbrl(tree)
        
        assert data is not None
        assert data['filing_date'] == '2024-03-31'
        assert data['cash'] == 100000000000.0
        assert data['securities'] == 50000000000.0
        assert data['receivables'] == 75000000000.0
        assert data['inventory'] == 30000000000.0
        assert data['total_assets'] == 500000000000.0
        assert data['liabilities'] == 200000000000.0
        assert data['revenue'] == 800000000000.0
        assert data['net_income'] == 50000000000.0
    
    def test_save_to_db_success(self, parser, tmp_path):
        """Test saving parsed data to database"""
        # Create test database
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        
        # Create financials table
        conn.execute("""
            CREATE TABLE financials (
                company_id TEXT,
                filing_date TEXT,
                cash REAL,
                securities REAL,
                receivables REAL,
                inventory REAL,
                total_assets REAL,
                liabilities REAL,
                revenue REAL,
                net_income REAL,
                PRIMARY KEY (company_id, filing_date)
            )
        """)
        conn.commit()
        conn.close()
        
        # Test data
        data = {
            'company_id': '9501',
            'filing_date': '2024-03-31',
            'cash': 100000000000.0,
            'securities': 50000000000.0,
            'receivables': 75000000000.0,
            'inventory': 30000000000.0,
            'total_assets': 500000000000.0,
            'liabilities': 200000000000.0,
            'revenue': 800000000000.0,
            'net_income': 50000000000.0
        }
        
        # Save to DB
        result = parser.save_to_db(data, db_path)
        
        assert result is True
        
        # Verify saved data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financials WHERE company_id = '9501'")
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == '9501'
        assert row[1] == '2024-03-31'
        assert row[2] == 100000000000.0
        
        conn.close()
    
    def test_save_to_db_duplicate_handling(self, parser, tmp_path):
        """Test duplicate record handling"""
        # Create test database
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        
        conn.execute("""
            CREATE TABLE financials (
                company_id TEXT,
                filing_date TEXT,
                cash REAL,
                PRIMARY KEY (company_id, filing_date)
            )
        """)
        conn.commit()
        conn.close()
        
        # Save first time
        data = {
            'company_id': '9501',
            'filing_date': '2024-03-31',
            'cash': 100000000000.0
        }
        parser.save_to_db(data, db_path)
        
        # Save again with updated value
        data['cash'] = 110000000000.0
        result = parser.save_to_db(data, db_path)
        
        assert result is True
        
        # Verify only one record exists with updated value
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), cash FROM financials WHERE company_id = '9501'")
        count, cash = cursor.fetchone()
        
        assert count == 1
        assert cash == 110000000000.0
        
        conn.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=scripts.parse_xbrl', '--cov-report=term-missing'])
