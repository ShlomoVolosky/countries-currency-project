import pytest
from unittest.mock import MagicMock, patch
from database.connection import DatabaseConnection, CountryRepository, CurrencyRateRepository
from config.settings import get_settings


class TestDatabaseConnection:
    @pytest.fixture
    def mock_connection_pool(self):
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.getconn.return_value = mock_connection
        mock_pool.putconn.return_value = None
        return mock_pool, mock_connection

    @pytest.fixture
    def db_connection(self, mock_connection_pool):
        from database.connection import DatabaseConnection
        return DatabaseConnection()

    def test_connection_initialization(self, db_connection):
        assert db_connection is not None
        assert db_connection.connection_pool is not None

    def test_get_connection_context_manager(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        with db_connection.get_cursor() as cursor:
            assert cursor is not None
        
        mock_pool.getconn.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_connection)
    
    def test_execute_query_success(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        result = db_connection.execute_query("SELECT 1", fetch_results=False)
        
        assert result is True
        mock_connection.commit.assert_called_once()

    def test_execute_query_no_results(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = db_connection.execute_query("SELECT 1")
        
        assert result == []
        mock_connection.commit.assert_called_once()

    def test_execute_query_error(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        with pytest.raises(Exception):
            db_connection.execute_query("SELECT 1")
        
        assert mock_connection.rollback.call_count >= 1

    def test_test_connection_success(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = db_connection.test_connection()
        
        assert result is True

    def test_test_connection_failure(self, db_connection, mock_connection_pool):
        mock_pool, mock_connection = mock_connection_pool
        db_connection.connection_pool = mock_pool
        
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Connection failed")
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        result = db_connection.test_connection()
        
        assert result is False


class TestCountryRepository:
    @pytest.fixture
    def country_repo(self):
        mock_db = MagicMock()
        return CountryRepository(mock_db)

    def test_insert_country_success(self, country_repo):
        country_repo.db.execute_query.return_value = True
        
        result = country_repo.insert_country({
            'name': 'Test Country',
            'capital': ['Test City'],
            'continent': 'Test Continent',
            'currencies': {'TEST': {'name': 'Test Dollar', 'symbol': '$'}},
            'is_un_member': True,
            'population': 1000000,
            'timezones': ['UTC+1']
        })
        
        assert result is True
        country_repo.db.execute_query.assert_called_once()

    def test_insert_country_failure(self, country_repo):
        country_repo.db.execute_query.side_effect = Exception("Database error")
        
        result = country_repo.insert_country({
            'name': 'Test Country',
            'capital': ['Test City']
        })
        
        assert result is False

    def test_get_country_by_name_success(self, country_repo):
        mock_country = {'name': 'Test Country', 'capital': ['Test City']}
        country_repo.db.execute_query.return_value = [mock_country]
        
        result = country_repo.get_country_by_name('Test Country')
        
        assert result == mock_country

    def test_get_country_by_name_not_found(self, country_repo):
        country_repo.db.execute_query.return_value = []
        
        result = country_repo.get_country_by_name('Non-existent')
        
        assert result is None

    def test_get_all_countries(self, country_repo):
        mock_countries = [
            {'name': 'Country 1', 'capital': ['City 1']},
            {'name': 'Country 2', 'capital': ['City 2']}
        ]
        country_repo.db.execute_query.return_value = mock_countries
        
        result = country_repo.get_all_countries()
        
        assert result == mock_countries

    def test_get_all_countries_with_pagination(self, country_repo):
        mock_countries = [{'name': f'Country {i}'} for i in range(5)]
        country_repo.db.execute_query.return_value = mock_countries
        
        result = country_repo.get_all_countries(limit=5, offset=0)
        
        assert len(result) == 5

    def test_get_countries_with_currencies(self, country_repo):
        mock_countries = [
            {'name': 'Country 1', 'currencies': ['USD']},
            {'name': 'Country 2', 'currencies': ['EUR']}
        ]
        country_repo.db.execute_query.return_value = mock_countries
        
        result = country_repo.get_countries_with_currencies(['USD', 'EUR'])
        
        assert result == mock_countries

    def test_search_countries(self, country_repo):
        mock_countries = [{'name': 'Test Country', 'capital': ['Test City']}]
        country_repo.db.execute_query.return_value = mock_countries
        
        result = country_repo.search_countries('Test')
        
        assert result == mock_countries


class TestCurrencyRateRepository:
    @pytest.fixture
    def currency_repo(self):
        mock_db = MagicMock()
        return CurrencyRateRepository(mock_db)

    def test_insert_currency_rate_success(self, currency_repo):
        currency_repo.db.execute_query.return_value = True
        
        result = currency_repo.insert_currency_rate('Test Country', 'USD', 0.28, '2024-01-01')
        
        assert result is True
        currency_repo.db.execute_query.assert_called_once()

    def test_insert_currency_rate_failure(self, currency_repo):
        currency_repo.db.execute_query.side_effect = Exception("Database error")
        
        result = currency_repo.insert_currency_rate('Test Country', 'USD', 0.28, '2024-01-01')
        
        assert result is False

    def test_get_currency_rates_by_country(self, currency_repo):
        mock_rates = [
            {'currency_code': 'USD', 'shekel_rate': 0.28, 'rate_date': '2024-01-01'},
            {'currency_code': 'EUR', 'shekel_rate': 0.30, 'rate_date': '2024-01-01'}
        ]
        currency_repo.db.execute_query.return_value = mock_rates
        
        result = currency_repo.get_currency_rates_by_country('Test Country')
        
        assert result == mock_rates

    def test_get_currency_rates_all(self, currency_repo):
        mock_rates = [
            {'country_name': 'Country 1', 'currency_code': 'USD', 'shekel_rate': 0.28},
            {'country_name': 'Country 2', 'currency_code': 'EUR', 'shekel_rate': 0.30}
        ]
        currency_repo.db.execute_query.return_value = mock_rates
        
        result = currency_repo.get_currency_rates_all()
        
        assert result == mock_rates

    def test_get_latest_rates_by_country(self, currency_repo):
        mock_rates = [
            {'currency_code': 'USD', 'shekel_rate': 0.28, 'rate_date': '2024-01-01'}
        ]
        currency_repo.db.execute_query.return_value = mock_rates
        
        result = currency_repo.get_latest_rates_by_country('Test Country')
        
        assert result == mock_rates

    def test_get_latest_rates_all(self, currency_repo):
        mock_rates = [
            {'country_name': 'Country 1', 'currency_code': 'USD', 'shekel_rate': 0.28}
        ]
        currency_repo.db.execute_query.return_value = mock_rates
        
        result = currency_repo.get_latest_rates_all()
        
        assert result == mock_rates

    def test_get_rate_history(self, currency_repo):
        mock_history = [
            {'currency_code': 'USD', 'shekel_rate': 0.28, 'rate_date': '2024-01-01'},
            {'currency_code': 'USD', 'shekel_rate': 0.29, 'rate_date': '2024-01-02'}
        ]
        currency_repo.db.execute_query.return_value = mock_history
        
        result = currency_repo.get_rate_history('Test Country', 'USD', 30)
        
        assert result == mock_history