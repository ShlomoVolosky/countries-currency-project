import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from database.connection import DatabaseConnection, CountryRepository, CurrencyRateRepository
from config.settings import get_settings


class TestDatabaseConnection:
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.getconn.return_value = mock_connection
        mock_pool.putconn.return_value = None
        return mock_pool, mock_connection
    @pytest.fixture
    def db_connection(self, mock_connection_pool):
        assert db_connection is not None
        assert db_connection.connection_pool is not None
    def test_get_connection_context_manager(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        with db_connection.get_cursor() as cursor:
            assert cursor is not None
        
        mock_pool.getconn.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_connection)
    
    def test_execute_query_success(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        result = db_connection.execute_query("INSERT INTO test VALUES (1)", fetch_results=False)
        
        assert result is True
        mock_connection.commit.assert_called_once()
    
    def test_execute_query_error(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"test": 1}]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        result = db_connection.test_connection()
        assert result is True
    
    def test_test_connection_failure(self, db_connection, mock_connection_pool):
    @pytest.fixture
    def country_repo(self):
        country_data = {
            'country_name': 'Test Country',
            'capitals': ['Test Capital'],
            'continent': 'Test Continent',
            'currencies': ['USD'],
            'is_un_member': True,
            'population': 1000000,
            'timezone_info': {'UTC': '2024-01-01 12:00:00 UTC'}
        }
        country_repo.db.execute_query.return_value = [{'id': 1}]
        
        result = country_repo.insert_country(country_data)
        assert result == 1
        country_repo.db.execute_query.assert_called_once()
    
    def test_insert_country_failure(self, country_repo):
        mock_country = {'id': 1, 'country_name': 'Test Country'}
        country_repo.db.execute_query.return_value = [mock_country]
        result = country_repo.get_country_by_name('Test Country')
        assert result == mock_country
    
    def test_get_country_by_name_not_found(self, country_repo):
        mock_countries = [
            {'id': 1, 'country_name': 'Country 1'},
            {'id': 2, 'country_name': 'Country 2'}
        ]
        country_repo.db.execute_query.return_value = mock_countries
        result = country_repo.get_all_countries()
        assert result == mock_countries
    
    def test_get_all_countries_with_pagination(self, country_repo):
        mock_countries = [
            {'country_name': 'Country 1', 'currencies': ['USD']},
            {'country_name': 'Country 2', 'currencies': ['EUR']}
        ]
        country_repo.db.execute_query.return_value = mock_countries
        result = country_repo.get_countries_with_currencies()
        assert result == mock_countries
    
    def test_search_countries(self, country_repo):
    @pytest.fixture
    def currency_repo(self):
        currency_repo.db.execute_query.return_value = [{'id': 1}]
        result = currency_repo.insert_currency_rate('Test Country', 'USD', 0.28)
        assert result == 1
        currency_repo.db.execute_query.assert_called_once()
    
    def test_insert_currency_rate_failure(self, currency_repo):
        mock_rates = [
            {'currency_code': 'USD', 'shekel_rate': 0.28},
            {'currency_code': 'EUR', 'shekel_rate': 0.25}
        ]
        currency_repo.db.execute_query.return_value = mock_rates
        result = currency_repo.get_currency_rates('Test Country')
        assert result == mock_rates
    
    def test_get_currency_rates_all(self, currency_repo):
        mock_rates = [{'currency_code': 'USD', 'shekel_rate': 0.28}]
        currency_repo.db.execute_query.return_value = mock_rates
        result = currency_repo.get_latest_rates('Test Country')
        assert result == mock_rates
    
    def test_get_latest_rates_all(self, currency_repo):
        mock_history = [
            {'currency_code': 'USD', 'shekel_rate': 0.28, 'rate_date': '2024-01-01'},
            {'currency_code': 'USD', 'shekel_rate': 0.29, 'rate_date': '2024-01-02'}
        ]
        currency_repo.db.execute_query.return_value = mock_history
        result = currency_repo.get_rate_history('Test Country', 'USD', 30)
        assert result == mock_history
