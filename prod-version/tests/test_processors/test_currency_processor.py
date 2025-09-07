"""
Tests for the CurrencyProcessor class.

This module contains comprehensive tests for currency rate processing functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from processors.currency_processor import CurrencyProcessor
from models.currency import CurrencyRate
from config.settings import get_settings


class TestCurrencyProcessor:
    """Test cases for CurrencyProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a CurrencyProcessor instance for testing."""
        with patch('processors.currency_processor.get_currency_rate_repository'), \
             patch('processors.currency_processor.get_country_repository'):
            return CurrencyProcessor()
    
    @pytest.fixture
    def sample_currency_data(self):
        """Sample currency data for testing."""
        return {
            "amount": 1.0,
            "base": "ILS",
            "date": "2024-01-01",
            "rates": {
                "USD": 0.28,
                "EUR": 0.25,
                "GBP": 0.22
            }
        }
    
    @pytest.fixture
    def sample_countries_data(self):
        """Sample countries data for testing."""
        return [
            {
                "country_name": "Israel",
                "currencies": ["ILS", "USD"]
            },
            {
                "country_name": "United States",
                "currencies": ["USD"]
            }
        ]
    
    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.settings is not None
        assert processor.currency_repo is not None
        assert processor.country_repo is not None
        assert processor.supported_currencies is None
    
    def test_get_supported_currencies_success(self, processor):
        """Test successful fetching of supported currencies."""
        mock_currencies = {"USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound"}
        
        with patch.object(processor, 'make_request', return_value=mock_currencies):
            result = processor.get_supported_currencies()
            
            assert result is not None
            assert isinstance(result, set)
            assert "USD" in result
            assert "EUR" in result
            assert "GBP" in result
            assert processor.supported_currencies == result
    
    def test_get_supported_currencies_failure(self, processor):
        """Test fetching supported currencies with API failure."""
        with patch.object(processor, 'make_request', return_value=None):
            result = processor.get_supported_currencies()
            
            assert result is not None
            assert isinstance(result, set)
            assert len(result) > 0  # Should have fallback currencies
            assert "USD" in result  # Should include common currencies
    
    def test_get_currency_rate_success(self, processor, sample_currency_data):
        """Test successful currency rate fetching."""
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR", "GBP"}), \
             patch.object(processor, 'make_request', return_value=sample_currency_data):
            
            rate = processor.get_currency_rate("USD")
            
            assert rate is not None
            assert isinstance(rate, float)
            assert rate == 0.28
    
    def test_get_currency_rate_ils(self, processor):
        """Test ILS to ILS rate (should be 1.0)."""
        rate = processor.get_currency_rate("ILS")
        assert rate == 1.0
    
    def test_get_currency_rate_unsupported(self, processor):
        """Test currency rate for unsupported currency."""
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR"}):
            rate = processor.get_currency_rate("XYZ")
            assert rate is None
    
    def test_get_currency_rate_failure(self, processor):
        """Test currency rate fetching failure."""
        with patch.object(processor, 'get_supported_currencies', return_value={"USD"}), \
             patch.object(processor, 'make_request', return_value=None):
            
            rate = processor.get_currency_rate("USD")
            assert rate is None
    
    def test_get_all_currency_rates_success(self, processor, sample_currency_data):
        """Test successful fetching of all currency rates."""
        with patch.object(processor, 'make_request', return_value=sample_currency_data):
            rates = processor.get_all_currency_rates()
            
            assert rates is not None
            assert isinstance(rates, dict)
            assert "ILS" in rates
            assert "USD" in rates
            assert "EUR" in rates
            assert "GBP" in rates
            assert rates["ILS"] == 1.0
    
    def test_get_all_currency_rates_failure(self, processor):
        """Test fetching all currency rates with API failure."""
        with patch.object(processor, 'make_request', return_value=None):
            rates = processor.get_all_currency_rates()
            assert rates == {}
    
    def test_get_countries_with_currencies_success(self, processor, sample_countries_data):
        """Test successful fetching of countries with currencies."""
        with patch.object(processor.country_repo, 'get_countries_with_currencies', return_value=sample_countries_data):
            countries = processor.get_countries_with_currencies()
            
            assert countries is not None
            assert len(countries) == 2
            assert countries[0]["country_name"] == "Israel"
            assert countries[0]["currencies"] == ["ILS", "USD"]
    
    def test_get_countries_with_currencies_failure(self, processor):
        """Test fetching countries with currencies failure."""
        with patch.object(processor.country_repo, 'get_countries_with_currencies', side_effect=Exception("Database error")):
            countries = processor.get_countries_with_currencies()
            assert countries == []
    
    def test_validate_currency_rate_valid(self, processor):
        """Test validation of valid currency rate."""
        result = processor.validate_currency_rate("Israel", "USD", 0.28)
        assert result is True
    
    def test_validate_currency_rate_invalid_country(self, processor):
        """Test validation with invalid country name."""
        result = processor.validate_currency_rate("", "USD", 0.28)
        assert result is False
    
    def test_validate_currency_rate_invalid_currency(self, processor):
        """Test validation with invalid currency code."""
        result = processor.validate_currency_rate("Israel", "XY", 0.28)
        assert result is False
    
    def test_validate_currency_rate_invalid_rate(self, processor):
        """Test validation with invalid rate."""
        result = processor.validate_currency_rate("Israel", "USD", -0.28)
        assert result is False
    
    def test_save_currency_rate_success(self, processor):
        """Test successful currency rate saving."""
        with patch.object(processor.currency_repo, 'insert_currency_rate', return_value=1):
            result = processor.save_currency_rate("Israel", "USD", 0.28)
            assert result is True
    
    def test_save_currency_rate_failure(self, processor):
        """Test currency rate saving failure."""
        with patch.object(processor.currency_repo, 'insert_currency_rate', return_value=None):
            result = processor.save_currency_rate("Israel", "USD", 0.28)
            assert result is False
    
    def test_save_currency_rate_validation_failure(self, processor):
        """Test currency rate saving with validation failure."""
        result = processor.save_currency_rate("", "USD", 0.28)
        assert result is False
    
    def test_process_currency_rates_batch(self, processor, sample_countries_data):
        """Test processing a batch of currency rates."""
        all_rates = {"USD": 0.28, "EUR": 0.25, "ILS": 1.0}
        
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR", "ILS"}), \
             patch.object(processor, 'save_currency_rate', return_value=True):
            
            stats = processor.process_currency_rates_batch(sample_countries_data, all_rates)
            
            assert stats['total_countries'] == 2
            assert stats['total_currencies'] == 3  # ILS+USD + USD
            assert stats['processed'] == 3
            assert stats['successful'] == 3
            assert stats['failed'] == 0
            assert stats['unsupported'] == 0
    
    def test_process_currency_rates_batch_unsupported_currencies(self, processor, sample_countries_data):
        """Test processing with unsupported currencies."""
        all_rates = {"USD": 0.28, "ILS": 1.0}
        
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "ILS"}), \
             patch.object(processor, 'save_currency_rate', return_value=True):
            
            stats = processor.process_currency_rates_batch(sample_countries_data, all_rates)
            
            assert stats['total_countries'] == 2
            assert stats['total_currencies'] == 3
            assert stats['processed'] == 3
            assert stats['successful'] == 3
            assert stats['failed'] == 0
            assert stats['unsupported'] == 0
    
    def test_process_success(self, processor, sample_countries_data):
        """Test successful main processing."""
        all_rates = {"USD": 0.28, "EUR": 0.25, "ILS": 1.0}
        
        with patch.object(processor, 'get_countries_with_currencies', return_value=sample_countries_data), \
             patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR", "ILS"}), \
             patch.object(processor, 'get_all_currency_rates', return_value=all_rates), \
             patch.object(processor, 'process_currency_rates_batch') as mock_batch:
            
            mock_batch.return_value = {
                'total_countries': 2,
                'total_currencies': 3,
                'processed': 3,
                'successful': 3,
                'failed': 0,
                'unsupported': 0
            }
            
            result = processor.process()
            assert result is True
    
    def test_process_no_countries(self, processor):
        """Test processing with no countries."""
        with patch.object(processor, 'get_countries_with_currencies', return_value=[]):
            result = processor.process()
            assert result is False
    
    def test_process_no_rates(self, processor, sample_countries_data):
        """Test processing with no currency rates."""
        with patch.object(processor, 'get_countries_with_currencies', return_value=sample_countries_data), \
             patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR", "ILS"}), \
             patch.object(processor, 'get_all_currency_rates', return_value={}):
            
            result = processor.process()
            assert result is False
    
    def test_get_latest_rates(self, processor):
        """Test getting latest rates."""
        mock_rates = [{"currency_code": "USD", "shekel_rate": 0.28}]
        
        with patch.object(processor.currency_repo, 'get_latest_rates', return_value=mock_rates):
            rates = processor.get_latest_rates()
            assert rates == mock_rates
    
    def test_get_rate_history(self, processor):
        """Test getting rate history."""
        mock_history = [{"currency_code": "USD", "shekel_rate": 0.28, "rate_date": "2024-01-01"}]
        
        with patch.object(processor.currency_repo, 'get_rate_history', return_value=mock_history):
            history = processor.get_rate_history("Israel", "USD", 30)
            assert history == mock_history
    
    def test_get_processing_summary(self, processor):
        """Test getting processing summary."""
        processor.processed_count = 10
        processor.success_count = 8
        processor.error_count = 2
        
        summary = processor.get_processing_summary()
        
        assert 'currencies_processed' in summary
        assert 'currencies_successful' in summary
        assert 'currencies_failed' in summary
        assert summary['currencies_processed'] == 10
        assert summary['currencies_successful'] == 8
        assert summary['currencies_failed'] == 2
