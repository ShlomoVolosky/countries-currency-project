import json
import logging
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import sql

from config.database import get_database_config
from utils.retry import retry_with_backoff
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    def __init__(self):
        self.config = get_database_config()
        self.connection_pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self):
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=self.config.settings.database.host,
                database=self.config.settings.database.name,
                user=self.config.settings.database.user,
                password=self.config.settings.database.password,
                port=self.config.settings.database.port
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            self.connection_pool = None

    @contextmanager
    def get_connection(self):
        connection = None
        try:
            if not self.connection_pool:
                raise Exception("Database connection pool not initialized")
            
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            logger.error(f"Error getting database connection: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)

    @contextmanager
    def get_cursor(self, connection=None):
        if connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                try:
                    yield cursor
                finally:
                    cursor.close()

    def test_connection(self) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_results: bool = True) -> Optional[Union[List[Dict], bool]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    
                    if fetch_results:
                        return cursor.fetchall()
                    else:
                        return True
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise

    def close_pool(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")


class CountryRepository:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def insert_country(self, country_data: Dict[str, Any]) -> bool:
        try:
            query = """
            INSERT INTO countries (country_name, capitals, continent, currencies, 
                                 is_un_member, population, timezone_info, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (country_name) DO UPDATE SET
                capitals = EXCLUDED.capitals,
                continent = EXCLUDED.continent,
                currencies = EXCLUDED.currencies,
                is_un_member = EXCLUDED.is_un_member,
                population = EXCLUDED.population,
                timezone_info = EXCLUDED.timezone_info,
                updated_at = EXCLUDED.updated_at
            """
            
            params = (
                country_data.get('name'),
                country_data.get('capital', []),
                country_data.get('continent'),
                list(country_data.get('currencies', {}).keys()) if country_data.get('currencies') else [],
                country_data.get('is_un_member'),
                country_data.get('population'),
                json.dumps(country_data.get('timezones', [])),
                datetime.now(),
                datetime.now()
            )
            
            self.db.execute_query(query, params, fetch_results=False)
            return True
        except Exception as e:
            logger.error(f"Error inserting country: {e}")
            return False

    def get_country_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM countries WHERE country_name = %s"
        result = self.db.execute_query(query, (name,))
        return result[0] if result else None

    def get_all_countries(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        query = "SELECT * FROM countries ORDER BY country_name"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        result = self.db.execute_query(query)
        return result or []

    def get_countries_with_currencies(self, currencies: List[str]) -> List[Dict[str, Any]]:
        query = "SELECT * FROM countries WHERE currencies && %s"
        result = self.db.execute_query(query, (currencies,))
        return result or []

    def search_countries(self, search_term: str) -> List[Dict[str, Any]]:
        query = """
        SELECT * FROM countries 
        WHERE country_name ILIKE %s OR continent ILIKE %s
        ORDER BY country_name
        """
        search_pattern = f"%{search_term}%"
        result = self.db.execute_query(query, (search_pattern, search_pattern))
        return result or []


class CurrencyRateRepository:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def insert_currency_rate(self, country_name: str, currency_code: str, 
                           shekel_rate: float, rate_date: str) -> bool:
        try:
            query = """
            INSERT INTO currency_rates (country_name, currency_code, shekel_rate, rate_date, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (country_name, currency_code, rate_date) DO UPDATE SET
                shekel_rate = EXCLUDED.shekel_rate,
                updated_at = EXCLUDED.updated_at
            """
            
            params = (
                country_name,
                currency_code,
                Decimal(str(shekel_rate)),
                rate_date,
                datetime.now(),
                datetime.now()
            )
            
            self.db.execute_query(query, params, fetch_results=False)
            return True
        except Exception as e:
            logger.error(f"Error inserting currency rate: {e}")
            return False

    def get_currency_rates_by_country(self, country_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT * FROM currency_rates 
        WHERE country_name = %s 
        ORDER BY rate_date DESC, currency_code
        """
        result = self.db.execute_query(query, (country_name,))
        return result or []

    def get_currency_rates_all(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM currency_rates ORDER BY country_name, rate_date DESC"
        result = self.db.execute_query(query)
        return result or []

    def get_latest_rates_by_country(self, country_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT DISTINCT ON (currency_code) * FROM currency_rates 
        WHERE country_name = %s 
        ORDER BY currency_code, rate_date DESC
        """
        result = self.db.execute_query(query, (country_name,))
        return result or []

    def get_latest_rates_all(self) -> List[Dict[str, Any]]:
        query = """
        SELECT DISTINCT ON (country_name, currency_code) * FROM currency_rates 
        ORDER BY country_name, currency_code, rate_date DESC
        """
        result = self.db.execute_query(query)
        return result or []

    def get_rate_history(self, country_name: str, currency_code: str, days: int = 30) -> List[Dict[str, Any]]:
        query = """
        SELECT * FROM currency_rates
        WHERE country_name = %s AND currency_code = %s
        AND rate_date >= %s
        ORDER BY rate_date DESC
        """
        
        start_date = date.today() - timedelta(days=days)
        result = self.db.execute_query(query, (country_name, currency_code, start_date))
        return result or []