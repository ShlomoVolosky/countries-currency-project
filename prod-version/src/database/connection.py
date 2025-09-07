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
    @retry_with_backoff(max_attempts=3, base_delay=1)
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_results: bool = True) -> Optional[Union[List[Dict], bool]]:
        try:
            result = self.execute_query("SELECT 1 as test")
            return result is not None and len(result) > 0 and result[0]['test'] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    def close_pool(self):
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert_country(self, country_data: Dict[str, Any]) -> Optional[int]:
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
        RETURNING id
        query = "SELECT * FROM countries WHERE country_name = %s"
        result = self.db.execute_query(query, (country_name,))
        return result[0] if result else None
    def get_all_countries(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        query = """
        SELECT DISTINCT country_name, currencies 
        FROM countries 
        WHERE currencies IS NOT NULL AND array_length(currencies, 1) > 0
        ORDER BY country_name
        conditions = []
        params = []
        if filters.get('continent'):
            conditions.append("continent = %s")
            params.append(filters['continent'])
        
        if filters.get('is_un_member') is not None:
            conditions.append("is_un_member = %s")
            params.append(filters['is_un_member'])
        
        if filters.get('min_population'):
            conditions.append("population >= %s")
            params.append(filters['min_population'])
        
        if filters.get('max_population'):
            conditions.append("population <= %s")
            params.append(filters['max_population'])
        
        if filters.get('has_currency'):
            conditions.append("%s = ANY(currencies)")
            params.append(filters['has_currency'])
        
        if filters.get('search_term'):
            conditions.append("country_name ILIKE %s")
            params.append(f"%{filters['search_term']}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM countries WHERE {where_clause} ORDER BY country_name"
        
        return self.db.execute_query(query, tuple(params)) or []


class CurrencyRateRepository:
        query = """
        INSERT INTO currency_rates (country_name, currency_code, shekel_rate, rate_date, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (country_name, currency_code, rate_date) 
        DO UPDATE SET 
            shekel_rate = EXCLUDED.shekel_rate,
            updated_at = EXCLUDED.updated_at
        RETURNING id
        if country_name:
            query = "SELECT * FROM currency_rates WHERE country_name = %s ORDER BY rate_date DESC"
            return self.db.execute_query(query, (country_name,)) or []
        else:
            query = "SELECT * FROM currency_rates ORDER BY rate_date DESC, country_name"
            return self.db.execute_query(query) or []
    def get_latest_rates(self, country_name: Optional[str] = None) -> List[Dict[str, Any]]:
            SELECT DISTINCT ON (currency_code) *
            FROM currency_rates 
            WHERE country_name = %s
            ORDER BY currency_code, rate_date DESC
            SELECT DISTINCT ON (country_name, currency_code) *
            FROM currency_rates 
            ORDER BY country_name, currency_code, rate_date DESC
        query = """
        SELECT * FROM currency_rates 
        WHERE country_name = %s AND currency_code = %s 
        AND rate_date >= %s
        ORDER BY rate_date DESC
    return db_connection

def get_country_repository() -> CountryRepository:
    return currency_rate_repo