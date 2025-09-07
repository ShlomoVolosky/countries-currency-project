import pytest
from datetime import datetime, date
from decimal import Decimal
from src.models.country import Country, CountryCreate, CountryUpdate
from src.models.currency import CurrencyRate, CurrencyRateCreate, CurrencyRateUpdate
from src.models.api import APIResponse, HealthCheckResponse


class TestCountryModels:
    def test_country_create(self):
        country = CountryCreate(
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"}
        )
        assert country.country_name == "Test Country"
        assert country.capitals == ["Test Capital"]
        assert country.continent == "Test Continent"
        assert country.currencies == ["USD"]
        assert country.is_un_member is True
        assert country.population == 1000000

    def test_country_update(self):
        country_update = CountryUpdate(
            id=1,
            country_name="Updated Country",
            population=2000000
        )
        assert country_update.id == 1
        assert country_update.country_name == "Updated Country"
        assert country_update.population == 2000000
        assert country_update.continent is None

    def test_country_full(self):
        country = Country(
            id=1,
            country_name="Test Country",
            capitals=["Test Capital"],
            continent="Test Continent",
            currencies=["USD"],
            is_un_member=True,
            population=1000000,
            timezone_info={"UTC": "2024-01-01 12:00:00 UTC"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert country.id == 1
        assert country.country_name == "Test Country"


class TestCurrencyModels:
    def test_currency_rate_create(self):
        rate = CurrencyRateCreate(
            country_name="Test Country",
            currency_code="USD",
            shekel_rate=Decimal("3.5"),
            rate_date=date.today()
        )
        assert rate.country_name == "Test Country"
        assert rate.currency_code == "USD"
        assert rate.shekel_rate == Decimal("3.5")
        assert rate.rate_date == date.today()

    def test_currency_rate_update(self):
        rate_update = CurrencyRateUpdate(
            id=1,
            shekel_rate=Decimal("4.0")
        )
        assert rate_update.id == 1
        assert rate_update.shekel_rate == Decimal("4.0")
        assert rate_update.country_name is None

    def test_currency_rate_full(self):
        rate = CurrencyRate(
            id=1,
            country_name="Test Country",
            currency_code="USD",
            shekel_rate=Decimal("3.5"),
            rate_date=date.today(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert rate.id == 1
        assert rate.country_name == "Test Country"
        assert rate.currency_code == "USD"


class TestAPIModels:
    def test_api_response(self):
        response = APIResponse(
            success=True,
            message="Test message",
            data={"test": "data"}
        )
        assert response.success is True
        assert response.message == "Test message"
        assert response.data == {"test": "data"}
        assert isinstance(response.timestamp, datetime)

    def test_health_check_response(self):
        response = HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            database_connected=True
        )
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.database_connected is True
        assert isinstance(response.timestamp, datetime)
