import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from part2_currencies import CurrencyProcessor
import requests_mock

class TestPart2Currencies:
    
    def test_currency_processor_init(self):
        """Test CurrencyProcessor initialization"""
        processor = CurrencyProcessor()
        assert processor.config is not None
        assert processor.db is not None
    
    @requests_mock.Mocker()
    def test_get_shekel_rate_success(self, m):
        """Test successful currency rate fetching"""
        processor = CurrencyProcessor()
        
        # Mock successful API response
        mock_response = {
            "amount": 1.0,
            "base": "ILS",
            "date": "2024-01-01",
            "rates": {
                "USD": 0.28
            }
        }
        
        m.get(f"{processor.config.CURRENCY_API_URL}/latest", json=mock_response)
        
        rate = processor.get_shekel_rate("USD")
        assert rate is not None
        assert isinstance(rate, float)
        assert rate == 0.28
    
    def test_get_shekel_rate_ils(self):
        """Test ILS to ILS rate (should be 1.0)"""
        processor = CurrencyProcessor()
        rate = processor.get_shekel_rate("ILS")
        assert rate == 1.0
    
    @requests_mock.Mocker()
    def test_get_shekel_rate_failure(self, m):
        """Test currency rate fetching failure"""
        processor = CurrencyProcessor()
        
        # Mock API failure
        m.get(f"{processor.config.CURRENCY_API_URL}/latest", status_code=404)
        
        rate = processor.get_shekel_rate("USD")
        assert rate is None
    
    @requests_mock.Mocker()
    def test_get_shekel_rate_reverse_lookup(self, m):
        """Test reverse currency lookup when direct lookup fails"""
        processor = CurrencyProcessor()
        
        # Mock first request failure (no rate returned)
        m.get(f"{processor.config.CURRENCY_API_URL}/latest", 
              json={"amount": 1.0, "base": "ILS", "date": "2024-01-01", "rates": {}})
        
        # Mock second request success (reverse lookup)
        m.get(f"{processor.config.CURRENCY_API_URL}/latest", 
              json={"amount": 1.0, "base": "USD", "date": "2024-01-01", "rates": {"ILS": 3.5}})
        
        rate = processor.get_shekel_rate("USD")
        assert rate is not None
        assert rate == 3.5
    
    def test_get_all_countries_with_currencies_empty_db(self):
        """Test getting countries when database is empty"""
        processor = CurrencyProcessor()
        
        # This will return empty list if no countries in test DB
        countries = processor.get_all_countries_with_currencies()
        assert isinstance(countries, list)
    
    def test_process_currency_rates_no_countries(self, requests_mock):
        """Test processing when no countries exist"""
        processor = CurrencyProcessor()
        
        # Mock empty countries response
        processor.get_all_countries_with_currencies = lambda: []
        
        result = processor.process_currency_rates()
        assert result == False