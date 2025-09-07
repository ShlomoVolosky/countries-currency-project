import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.api.app import app
from src.models.country import Country
from src.models.currency import CurrencyRate

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check_success(self):
        with patch('src.api.routes.health.check_database_connection', return_value=True):
            response = client.get("/api/v1/health/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database_connected"] is True
            assert "version" in data

    def test_health_check_database_failure(self):
        with patch('src.api.routes.health.check_database_connection', return_value=False):
            response = client.get("/api/v1/health/")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database_connected"] is False


class TestCountriesEndpoints:
    @pytest.mark.asyncio
    async def test_get_countries_success(self):
        mock_countries = [
            Country(
                id=1,
                country_name="Test Country",
                capitals=["Test Capital"],
                continent="Test Continent",
                currencies=["USD"],
                is_un_member=True,
                population=1000000,
                timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
            )
        ]
        
        with patch('src.api.routes.countries.repository.list_all', new_callable=AsyncMock, return_value=mock_countries), \
             patch('src.database.connection.db_connection.get_connection') as mock_conn:
            response = client.get("/api/v1/countries/")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["country_name"] == "Test Country"

    @pytest.mark.asyncio
    async def test_get_country_by_id_success(self):
        mock_country = Country(
            id=1,
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
        )
        
        with patch('src.api.routes.countries.repository.get_by_id', new_callable=AsyncMock, return_value=mock_country):
            response = client.get("/api/v1/countries/1")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["country_name"] == "Test Country"

    @pytest.mark.asyncio
    async def test_get_country_by_id_not_found(self):
        with patch('src.api.routes.countries.repository.get_by_id', return_value=None):
            response = client.get("/api/v1/countries/999")
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Country not found"

    @pytest.mark.asyncio
    async def test_search_country_success(self):
        mock_country = Country(
            id=1,
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
        )
        
        with patch('src.api.routes.countries.repository.get_by_name', new_callable=AsyncMock, return_value=mock_country):
            response = client.get("/api/v1/countries/search/Test%20Country")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["country_name"] == "Test Country"


class TestCurrenciesEndpoints:
    @pytest.mark.asyncio
    async def test_get_currency_rates_success(self):
        from decimal import Decimal
        from datetime import date
        
        mock_rates = [
            CurrencyRate(
                id=1,
                country_name="Test Country",
                currency_code="USD",
                shekel_rate=Decimal("3.5"),
                rate_date=date(2024, 1, 1)
            )
        ]
        
        with patch('src.api.routes.currencies.repository.list_all', new_callable=AsyncMock, return_value=mock_rates):
            response = client.get("/api/v1/currencies/")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["currency_code"] == "USD"

    @pytest.mark.asyncio
    async def test_get_latest_rates_success(self):
        from decimal import Decimal
        from datetime import date
        
        mock_rates = [
            CurrencyRate(
                id=1,
                country_name="Test Country",
                currency_code="USD",
                shekel_rate=Decimal("3.5"),
                rate_date=date(2024, 1, 1)
            )
        ]
        
        with patch('src.api.routes.currencies.repository.get_latest_rates', new_callable=AsyncMock, return_value=mock_rates):
            response = client.get("/api/v1/currencies/latest")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_convert_currency_success(self):
        from decimal import Decimal
        from datetime import date
        
        mock_rates = [
            CurrencyRate(
                id=1,
                country_name="Test Country",
                currency_code="USD",
                shekel_rate=Decimal("3.5"),
                rate_date=date(2024, 1, 1)
            )
        ]
        
        with patch('src.api.routes.currencies.repository.get_latest_rates', new_callable=AsyncMock, return_value=mock_rates):
            response = client.get("/api/v1/currencies/convert/USD?amount=100")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["from_currency"] == "USD"
            assert data["data"]["to_currency"] == "ILS"
            assert data["data"]["amount"] == 100
            assert data["data"]["result"] == 350.0

    @pytest.mark.asyncio
    async def test_convert_currency_not_found(self):
        with patch('src.api.routes.currencies.repository.get_latest_rates', return_value=[]):
            response = client.get("/api/v1/currencies/convert/INVALID?amount=100")
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Currency INVALID not found"
