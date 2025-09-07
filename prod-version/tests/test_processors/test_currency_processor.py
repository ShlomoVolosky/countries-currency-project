import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from processors.currency_processor import CurrencyProcessor
from models.currency import CurrencyRate
from config.settings import get_settings


class TestCurrencyProcessor:
        with patch('processors.currency_processor.get_currency_rate_repository'), \
             patch('processors.currency_processor.get_country_repository'):
            return CurrencyProcessor()
    @pytest.fixture
    def sample_currency_data(self):
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
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR", "GBP"}), \
             patch.object(processor, 'make_request', return_value=sample_currency_data):
            rate = processor.get_currency_rate("USD")
            
            assert rate is not None
            assert isinstance(rate, float)
            assert rate == 0.28
    
    def test_get_currency_rate_ils(self, processor):
        with patch.object(processor, 'get_supported_currencies', return_value={"USD", "EUR"}):
            rate = processor.get_currency_rate("XYZ")
            assert rate is None
    def test_get_currency_rate_failure(self, processor):
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
        with patch.object(processor.country_repo, 'get_countries_with_currencies', return_value=sample_countries_data):
            countries = processor.get_countries_with_currencies()
            assert countries is not None
            assert len(countries) == 2
            assert countries[0]["country_name"] == "Israel"
            assert countries[0]["currencies"] == ["ILS", "USD"]
    
    def test_get_countries_with_currencies_failure(self, processor):
        result = processor.validate_currency_rate("Israel", "USD", 0.28)
        assert result is True
    def test_validate_currency_rate_invalid_country(self, processor):
        result = processor.validate_currency_rate("Israel", "XY", 0.28)
        assert result is False
    def test_validate_currency_rate_invalid_rate(self, processor):
        with patch.object(processor.currency_repo, 'insert_currency_rate', return_value=1):
            result = processor.save_currency_rate("Israel", "USD", 0.28)
            assert result is True
    def test_save_currency_rate_failure(self, processor):
        result = processor.save_currency_rate("", "USD", 0.28)
        assert result is False
    def test_process_currency_rates_batch(self, processor, sample_countries_data):
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
        with patch.object(processor, 'get_countries_with_currencies', return_value=[]):
            result = processor.process()
            assert result is False
    def test_process_no_rates(self, processor, sample_countries_data):
        mock_rates = [{"currency_code": "USD", "shekel_rate": 0.28}]
        with patch.object(processor.currency_repo, 'get_latest_rates', return_value=mock_rates):
            rates = processor.get_latest_rates()
            assert rates == mock_rates
    
    def test_get_rate_history(self, processor):
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
