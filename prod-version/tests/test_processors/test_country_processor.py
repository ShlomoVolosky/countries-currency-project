import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from processors.country_processor import CountryProcessor
from models.country import CountryData
from config.settings import get_settings


class TestCountryProcessor:
        with patch('processors.country_processor.get_country_repository'):
            return CountryProcessor()
    @pytest.fixture
    def sample_country_data(self):
        assert processor is not None
        assert processor.settings is not None
        assert processor.country_repo is not None
        assert processor.required_fields is not None
    def test_fetch_countries_data_success(self, processor):
        with patch.object(processor, 'make_request', return_value=None):
            result = processor.fetch_countries_data()
            assert result is None
    def test_validate_country_data_valid(self, processor, sample_country_data):
        invalid_data = {"name": {"common": "Test"}}  # Missing other fields
        errors = processor.validate_country_data(invalid_data)
        assert len(errors) > 0
        assert any("Missing required fields" in error for error in errors)
    def test_validate_country_data_wrong_types(self, processor):
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
        data = {"name": {"common": ""}}
        result = processor.format_country_data(data)
        assert result is None
    def test_save_country_data_success(self, processor):
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
        data = {"field1": "value1", "field2": "value2"}
        required = ["field1", "field2", "field3"]
        missing = processor.validate_required_fields(data, required)
        assert missing == ["field3"]
    
    def test_validate_field_types(self, processor):