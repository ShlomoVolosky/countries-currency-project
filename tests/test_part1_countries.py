import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from part1_countries import CountriesProcessor

class TestPart1Countries:
    
    def test_countries_processor_init(self):
        """Test CountriesProcessor initialization"""
        processor = CountriesProcessor()
        assert processor.config is not None
        assert processor.db is not None
    
    @requests_mock.Mocker()
    def test_fetch_countries_data_success(self, m):
        """Test successful API call to countries endpoint"""
        # Mock API response
        mock_data = [
            {
                "name": {"common": "Israel"},
                "capital": ["Jerusalem"],
                "continents": ["Asia"],
                "currencies": {"ILS": {"name": "Israeli new shekel"}},
                "unMember": True,
                "population": 9506000,
                "timezones": ["UTC+02:00"]
            }
        ]
        
        processor = CountriesProcessor()
        m.get(processor.config.COUNTRIES_API_URL, json=mock_data)
        
        result = processor.fetch_countries_data()
        assert result is not None
        assert len(result) == 1
        assert result[0]["name"]["common"] == "Israel"
    
    @requests_mock.Mocker()
    def test_fetch_countries_data_failure(self, m):
        """Test API call failure"""
        processor = CountriesProcessor()
        m.get(processor.config.COUNTRIES_API_URL, status_code=404)
        
        result = processor.fetch_countries_data()
        assert result is None
    
    def test_format_country_data(self):
        """Test country data formatting"""
        processor = CountriesProcessor()
        
        sample_country = {
            "name": {"common": "Israel"},
            "capital": ["Jerusalem"],
            "continents": ["Asia"],
            "currencies": {"ILS": {"name": "Israeli new shekel"}},
            "unMember": True,
            "population": 9506000,
            "timezones": ["UTC+02:00"]
        }
        
        result = processor.format_country_data(sample_country)
        
        assert result is not None
        assert result["country_name"] == "Israel"
        assert result["capitals"] == ["Jerusalem"]
        assert result["continent"] == "Asia"
        assert result["currencies"] == ["ILS"]
        assert result["is_un_member"] == True
        assert result["population"] == 9506000
        assert isinstance(result["current_time"], dict)
    
    def test_format_country_data_missing_fields(self):
        """Test country data formatting with missing fields"""
        processor = CountriesProcessor()
        
        sample_country = {
            "name": {"common": "TestCountry"},
            # Missing other fields
        }
        
        result = processor.format_country_data(sample_country)
        
        assert result is not None
        assert result["country_name"] == "TestCountry"
        assert result["capitals"] == []
        assert result["continent"] == ""
        assert result["currencies"] == []
        assert result["is_un_member"] == False
        assert result["population"] == 0
    
    def test_get_current_time_for_timezones(self):
        """Test timezone processing"""
        processor = CountriesProcessor()
        
        # Test with valid timezone
        timezones = ["UTC"]
        result = processor.get_current_time_for_timezones(timezones)
        assert isinstance(result, dict)
        
        # Test with empty timezones
        result = processor.get_current_time_for_timezones([])
        assert result == {}
        
        # Test with None
        result = processor.get_current_time_for_timezones(None)
        assert result == {}