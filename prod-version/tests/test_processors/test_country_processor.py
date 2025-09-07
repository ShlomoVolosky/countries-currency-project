"""
Tests for the CountryProcessor class.

This module contains comprehensive tests for country data processing functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from processors.country_processor import CountryProcessor
from models.country import CountryData
from config.settings import get_settings


class TestCountryProcessor:
    """Test cases for CountryProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a CountryProcessor instance for testing."""
        with patch('processors.country_processor.get_country_repository'):
            return CountryProcessor()
    
    @pytest.fixture
    def sample_country_data(self):
        """Sample country data for testing."""
        return {
            "name": {"common": "Israel"},
            "capital": ["Jerusalem"],
            "continents": ["Asia"],
            "currencies": {"ILS": {"name": "Israeli new shekel"}},
            "unMember": True,
            "population": 9506000,
            "timezones": ["UTC+02:00"]
        }
    
    def test_processor_initialization(self, processor):
        """Test processor initialization."""
        assert processor is not None
        assert processor.settings is not None
        assert processor.country_repo is not None
        assert processor.required_fields is not None
    
    def test_fetch_countries_data_success(self, processor):
        """Test successful API call to countries endpoint."""
        mock_data = [self.sample_country_data]
        
        with patch.object(processor, 'make_request', return_value=mock_data):
            result = processor.fetch_countries_data()
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["name"]["common"] == "Israel"
    
    def test_fetch_countries_data_failure(self, processor):
        """Test API call failure."""
        with patch.object(processor, 'make_request', return_value=None):
            result = processor.fetch_countries_data()
            assert result is None
    
    def test_validate_country_data_valid(self, processor, sample_country_data):
        """Test validation of valid country data."""
        errors = processor.validate_country_data(sample_country_data)
        assert len(errors) == 0
    
    def test_validate_country_data_missing_fields(self, processor):
        """Test validation with missing required fields."""
        invalid_data = {"name": {"common": "Test"}}  # Missing other fields
        errors = processor.validate_country_data(invalid_data)
        assert len(errors) > 0
        assert any("Missing required fields" in error for error in errors)
    
    def test_validate_country_data_wrong_types(self, processor):
        """Test validation with wrong data types."""
        invalid_data = {
            "name": "Invalid",  # Should be dict
            "capital": "Invalid",  # Should be list
            "continents": "Invalid",  # Should be list
            "currencies": "Invalid",  # Should be dict
            "unMember": "Invalid",  # Should be bool
            "population": "Invalid",  # Should be int
            "timezones": "Invalid"  # Should be list
        }
        errors = processor.validate_country_data(invalid_data)
        assert len(errors) > 0
        assert any("must be of type" in error for error in errors)
    
    def test_format_country_data_success(self, processor, sample_country_data):
        """Test successful country data formatting."""
        result = processor.format_country_data(sample_country_data)
        
        assert result is not None
        assert isinstance(result, CountryData)
        assert result.country_name == "Israel"
        assert result.capitals == ["Jerusalem"]
        assert result.continent == "Asia"
        assert result.currencies == ["ILS"]
        assert result.is_un_member is True
        assert result.population == 9506000
        assert isinstance(result.timezone_info, dict)
    
    def test_format_country_data_missing_fields(self, processor):
        """Test formatting with missing fields."""
        incomplete_data = {
            "name": {"common": "TestCountry"},
            # Missing other fields
        }
        
        result = processor.format_country_data(incomplete_data)
        
        assert result is not None
        assert result.country_name == "TestCountry"
        assert result.capitals == []
        assert result.continent == ""
        assert result.currencies == []
        assert result.is_un_member is False
        assert result.population == 0
    
    def test_format_country_data_empty_name(self, processor):
        """Test formatting with empty country name."""
        data = {"name": {"common": ""}}
        result = processor.format_country_data(data)
        assert result is None
    
    def test_save_country_data_success(self, processor):
        """Test successful country data saving."""
        country_data = CountryData(
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
        )
        
        with patch.object(processor.country_repo, 'insert_country', return_value=1):
            result = processor.save_country_data(country_data)
            assert result is True
    
    def test_save_country_data_failure(self, processor):
        """Test country data saving failure."""
        country_data = CountryData(
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
        )
        
        with patch.object(processor.country_repo, 'insert_country', return_value=None):
            result = processor.save_country_data(country_data)
            assert result is False
    
    def test_process_countries_batch(self, processor):
        """Test processing a batch of countries."""
        countries_data = [self.sample_country_data]
        
        with patch.object(processor, 'format_country_data') as mock_format, \
             patch.object(processor, 'save_country_data') as mock_save:
            
            mock_format.return_value = CountryData(
                country_name="Israel",
                capitals=["Jerusalem"],
                continent="Asia",
                currencies=["ILS"],
                is_un_member=True,
                population=9506000,
                timezone_info={}
            )
            mock_save.return_value = True
            
            stats = processor.process_countries_batch(countries_data)
            
            assert stats['total'] == 1
            assert stats['processed'] == 1
            assert stats['successful'] == 1
            assert stats['failed'] == 0
            assert stats['skipped'] == 0
    
    def test_process_success(self, processor):
        """Test successful main processing."""
        mock_countries = [self.sample_country_data]
        
        with patch.object(processor, 'fetch_countries_data', return_value=mock_countries), \
             patch.object(processor, 'process_countries_batch') as mock_batch:
            
            mock_batch.return_value = {
                'total': 1,
                'processed': 1,
                'successful': 1,
                'failed': 0,
                'skipped': 0
            }
            
            result = processor.process()
            assert result is True
    
    def test_process_no_data(self, processor):
        """Test processing with no data."""
        with patch.object(processor, 'fetch_countries_data', return_value=None):
            result = processor.process()
            assert result is False
    
    def test_get_processing_summary(self, processor):
        """Test getting processing summary."""
        processor.processed_count = 10
        processor.success_count = 8
        processor.error_count = 2
        
        summary = processor.get_processing_summary()
        
        assert 'countries_processed' in summary
        assert 'countries_successful' in summary
        assert 'countries_failed' in summary
        assert summary['countries_processed'] == 10
        assert summary['countries_successful'] == 8
        assert summary['countries_failed'] == 2
    
    def test_sanitize_string(self, processor):
        """Test string sanitization."""
        # Test normal string
        result = processor.sanitize_string("  Test String  ")
        assert result == "Test String"
        
        # Test with max length
        result = processor.sanitize_string("Very Long String", max_length=10)
        assert result == "Very Long S"
        
        # Test non-string input
        result = processor.sanitize_string(123)
        assert result == "123"
    
    def test_validate_required_fields(self, processor):
        """Test required fields validation."""
        data = {"field1": "value1", "field2": "value2"}
        required = ["field1", "field2", "field3"]
        
        missing = processor.validate_required_fields(data, required)
        assert missing == ["field3"]
    
    def test_validate_field_types(self, processor):
        """Test field types validation."""
        data = {"field1": "string", "field2": 123, "field3": "string"}
        field_types = {"field1": str, "field2": int, "field3": int}
        
        errors = processor.validate_field_types(data, field_types)
        assert len(errors) == 1
        assert "field3 must be of type int" in errors[0]
