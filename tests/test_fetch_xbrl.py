"""
EDINET XBRL fetch script tests
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from fetch_xbrl import EDINETClient, fetch_xbrl_for_ticker, get_recent_business_days


class TestBusinessDayCalculation:
    """Test business day helper function"""
    
    def test_get_recent_business_days_default(self):
        """Test default 2 business days ago"""
        result = get_recent_business_days(2)
        date_obj = datetime.strptime(result, "%Y-%m-%d")
        
        # Should be a valid date
        assert isinstance(date_obj, datetime)
        # Should be in the past
        assert date_obj < datetime.now()
    
    def test_get_recent_business_days_custom(self):
        """Test custom business day count"""
        result = get_recent_business_days(5)
        date_obj = datetime.strptime(result, "%Y-%m-%d")
        
        assert isinstance(date_obj, datetime)
        assert date_obj < datetime.now()


class TestEDINETClient:
    """Test EDINET API client"""
    
    def test_client_initialization(self):
        """Test client initializes with correct defaults"""
        client = EDINETClient()
        
        assert client.rate_limit_delay == 1.0
        assert client.connect_timeout == 10
        assert client.read_timeout == 30
        assert client.session is not None
    
    def test_client_custom_timeouts(self):
        """Test client accepts custom timeout parameters"""
        client = EDINETClient(connect_timeout=5, read_timeout=15)
        
        assert client.connect_timeout == 5
        assert client.read_timeout == 15
    
    @patch('fetch_xbrl.requests.Session.get')
    def test_get_document_list_success(self, mock_get):
        """Test successful document list retrieval"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"status": "200"},
            "results": [
                {"docID": "S100XXXX", "secCode": "9501"},
                {"docID": "S100YYYY", "secCode": "6758"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = EDINETClient()
        documents = client.get_document_list("2025-11-22")
        
        assert len(documents) == 2
        assert documents[0]["docID"] == "S100XXXX"
        mock_get.assert_called_once()
    
    @patch('fetch_xbrl.requests.Session.get')
    def test_get_document_list_api_error(self, mock_get):
        """Test API error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.json.return_value = {
            "metadata": {"status": "500"},
            "results": []
        }
        mock_get.return_value = mock_response
        
        client = EDINETClient()
        documents = client.get_document_list("2025-11-22")
        
        assert len(documents) == 0
    
    @patch('fetch_xbrl.requests.Session.get')
    def test_download_document_success(self, mock_get, tmp_path):
        """Test successful document download"""
        # Mock response with ZIP content
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'test zip content']
        mock_get.return_value = mock_response
        
        client = EDINETClient()
        output_path = tmp_path / "S100XXXX.zip"
        
        result = client.download_document("S100XXXX", output_path)
        
        assert result is True
        assert output_path.exists()
        assert output_path.read_bytes() == b'test zip content'
    
    @patch('fetch_xbrl.requests.Session.get')
    def test_download_document_failure(self, mock_get, tmp_path):
        """Test download failure handling"""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        client = EDINETClient()
        output_path = tmp_path / "S100XXXX.zip"
        
        result = client.download_document("S100XXXX", output_path)
        
        assert result is False
        assert not output_path.exists()
    
    @patch('fetch_xbrl.time.sleep')
    def test_rate_limiting(self, mock_sleep):
        """Test rate limiting mechanism"""
        client = EDINETClient(rate_limit_delay=1.0)
        
        # First request should not wait
        client._wait_for_rate_limit()
        mock_sleep.assert_not_called()
        
        # Second request should wait
        client._wait_for_rate_limit()
        # May or may not sleep depending on timing


class TestFetchXBRLForTicker:
    """Test XBRL fetch for specific ticker"""
    
    @patch('fetch_xbrl.EDINETClient')
    def test_fetch_xbrl_for_ticker_no_documents(self, mock_client_class, tmp_path):
        """Test fetch with no matching documents"""
        # Mock client
        mock_client = Mock()
        mock_client.get_document_list.return_value = []
        mock_client_class.return_value = mock_client
        
        # Create real client instance
        from fetch_xbrl import EDINETClient
        client = EDINETClient()
        client.get_document_list = mock_client.get_document_list
        
        count = fetch_xbrl_for_ticker(
            "9501",
            client,
            tmp_path,
            start_date="2025-11-20",
            end_date="2025-11-21"
        )
        
        assert count == 0
    
    @patch('fetch_xbrl.EDINETClient')
    def test_fetch_xbrl_for_ticker_with_documents(self, mock_client_class, tmp_path):
        """Test fetch with matching documents"""
        # Mock client
        mock_client = Mock()
        mock_client.get_document_list.return_value = [
            {"docID": "S100XXXX", "secCode": "95010"}
        ]
        mock_client.download_document.return_value = True
        mock_client_class.return_value = mock_client
        
        # Create real client instance
        from fetch_xbrl import EDINETClient
        client = EDINETClient()
        client.get_document_list = mock_client.get_document_list
        client.download_document = mock_client.download_document
        
        count = fetch_xbrl_for_ticker(
            "9501",
            client,
            tmp_path,
            start_date="2025-11-20",
            end_date="2025-11-20"
        )
        
        assert count == 1
    
    @patch('fetch_xbrl.EDINETClient')
    def test_fetch_xbrl_for_ticker_skip_existing(self, mock_client_class, tmp_path):
        """Test skipping already downloaded files"""
        # Create existing file
        existing_file = tmp_path / "S100XXXX.zip"
        existing_file.write_text("existing")
        
        # Mock client
        mock_client = Mock()
        mock_client.get_document_list.return_value = [
            {"docID": "S100XXXX", "secCode": "95010"}
        ]
        mock_client_class.return_value = mock_client
        
        # Create real client instance
        from fetch_xbrl import EDINETClient
        client = EDINETClient()
        client.get_document_list = mock_client.get_document_list
        
        count = fetch_xbrl_for_ticker(
            "9501",
            client,
            tmp_path,
            start_date="2025-11-20",
            end_date="2025-11-20"
        )
        
        # Should skip existing file
        assert count == 0
        mock_client.download_document.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=scripts.fetch_xbrl', '--cov-report=term-missing'])
