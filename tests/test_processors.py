import pytest
from unittest.mock import AsyncMock, patch
from src.processors.countries import CountriesProcessor
from src.processors.currencies import CurrencyProcessor
from src.models.country import CountryCreate
from src.models.currency import CurrencyRateCreate


class TestCountriesProcessor:
    @pytest.fixture
    def processor(self):
        return CountriesProcessor()

    @pytest.mark.asyncio
    async def test_fetch_data_success(self, processor):
        mock_data = [
            {
                "name": {"common": "Test Country"},
                "capital": ["Test Capital"],
                "continents": ["Test Continent"],
                "currencies": {"USD": {"name": "US Dollar"}},
                "unMember": True,
                "population": 1000000,
                "timezones": ["UTC"]
            }
        ]
        
        with patch.object(processor, 'fetch_data', return_value=mock_data):
            result = await processor.fetch_data()
            assert result == mock_data

    @pytest.mark.asyncio
    async def test_transform_data(self, processor):
        raw_data = [
            {
                "name": {"common": "Test Country"},
                "capital": ["Test Capital"],
                "continents": ["Test Continent"],
                "currencies": {"USD": {"name": "US Dollar"}},
                "unMember": True,
                "population": 1000000,
                "timezones": ["UTC"]
            }
        ]
        
        result = await processor.transform_data(raw_data)
        assert len(result) == 1
        assert isinstance(result[0], CountryCreate)
        assert result[0].country_name == "Test Country"
        assert result[0].capitals == ["Test Capital"]
        assert result[0].continent == "Test Continent"
        assert result[0].currencies == ["USD"]

    @pytest.mark.asyncio
    async def test_process_success(self, processor):
        mock_data = [
            {
                "name": {"common": "Test Country"},
                "capital": ["Test Capital"],
                "continents": ["Test Continent"],
                "currencies": {"USD": {"name": "US Dollar"}},
                "unMember": True,
                "population": 1000000,
                "timezones": ["UTC"]
            }
        ]
        
        with patch.object(processor, 'fetch_data', return_value=mock_data), \
             patch.object(processor, 'save_data', return_value=True):
            result = await processor.process()
            assert result is True

    @pytest.mark.asyncio
    async def test_process_failure(self, processor):
        with patch.object(processor, 'fetch_data', return_value=None):
            result = await processor.process()
            assert result is False


class TestCurrencyProcessor:
    @pytest.fixture
    def processor(self):
        return CurrencyProcessor()

    @pytest.mark.asyncio
    async def test_fetch_data_success(self, processor):
        mock_data = [
            {
                "country_name": "Test Country",
                "currencies": ["USD", "EUR"]
            }
        ]
        
        with patch.object(processor, 'fetch_data', return_value=mock_data):
            result = await processor.fetch_data()
            assert result == mock_data

    @pytest.mark.asyncio
    async def test_transform_data(self, processor):
        raw_data = [
            {
                "country_name": "Test Country",
                "currencies": ["USD", "EUR"]
            }
        ]
        
        with patch('src.processors.currencies.CurrencyAPIClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_supported_currencies.return_value = {"USD", "EUR"}
            mock_client.get_all_currency_rates.return_value = {"USD": 0.3, "EUR": 0.25}
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await processor.transform_data(raw_data)
            assert len(result) == 2
            assert all(isinstance(item, CurrencyRateCreate) for item in result)
            assert result[0].country_name == "Test Country"
            assert result[0].currency_code in ["USD", "EUR"]

    @pytest.mark.asyncio
    async def test_process_success(self, processor):
        mock_data = [
            {
                "country_name": "Test Country",
                "currencies": ["USD"]
            }
        ]
        
        with patch.object(processor, 'fetch_data', return_value=mock_data), \
             patch.object(processor, 'save_data', return_value=True):
            result = await processor.process()
            assert result is True

    @pytest.mark.asyncio
    async def test_process_failure(self, processor):
        with patch.object(processor, 'fetch_data', return_value=None):
            result = await processor.process()
            assert result is False
