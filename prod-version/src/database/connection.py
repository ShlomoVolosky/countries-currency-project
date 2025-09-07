"""
Database connection management for the Countries Currency Project.

This module provides enhanced database connection management with
connection pooling, retry mechanisms, and proper error handling.
"""

import json
import logging
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
from datetime import datetime, date
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
    """Enhanced database connection manager."""
    
    def __init__(self):
        self.config = get_database_config()
        self.connection_pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool."""
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
        """Get database connection from pool."""
        connection = None
        try:
            if not self.connection_pool:
                raise Exception("Database connection pool not initialized")
            
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            logger.error(f"Error getting database connection: {e}")
            if connection:
                self.connection_pool.putconn(connection, close=True)
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self, connection=None):
        """Get database cursor."""
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
        """Execute a database query with retry logic."""
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
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            result = self.execute_query("SELECT 1 as test")
            return result is not None and len(result) > 0 and result[0]['test'] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close_pool(self):
        """Close connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")


class CountryRepository:
    """Repository for country data operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert_country(self, country_data: Dict[str, Any]) -> Optional[int]:
        """Insert a new country record."""
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
        RETURNING id
        """
        
        params = (
            country_data['country_name'],
            country_data['capitals'],
            country_data['continent'],
            country_data['currencies'],
            country_data['is_un_member'],
            country_data['population'],
            Json(country_data['timezone_info']),
            datetime.utcnow(),
            datetime.utcnow()
        )
        
        try:
            result = self.db.execute_query(query, params)
            if result and len(result) > 0:
                return result[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error inserting country: {e}")
            return None
    
    def get_country_by_name(self, country_name: str) -> Optional[Dict[str, Any]]:
        """Get country by name."""
        query = "SELECT * FROM countries WHERE country_name = %s"
        result = self.db.execute_query(query, (country_name,))
        return result[0] if result else None
    
    def get_all_countries(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all countries with pagination."""
        query = "SELECT * FROM countries ORDER BY country_name"
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        return self.db.execute_query(query) or []
    
    def get_countries_with_currencies(self) -> List[Dict[str, Any]]:
        """Get countries that have currencies."""
        query = """
        SELECT DISTINCT country_name, currencies 
        FROM countries 
        WHERE currencies IS NOT NULL AND array_length(currencies, 1) > 0
        ORDER BY country_name
        """
        return self.db.execute_query(query) or []
    
    def search_countries(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search countries with filters."""
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
    """Repository for currency rate operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert_currency_rate(self, country_name: str, currency_code: str, shekel_rate: float) -> Optional[int]:
        """Insert a new currency rate record."""
        query = """
        INSERT INTO currency_rates (country_name, currency_code, shekel_rate, rate_date, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (country_name, currency_code, rate_date) 
        DO UPDATE SET 
            shekel_rate = EXCLUDED.shekel_rate,
            updated_at = EXCLUDED.updated_at
        RETURNING id
        """
        
        params = (
            country_name,
            currency_code.upper(),
            Decimal(str(shekel_rate)),
            date.today(),
            datetime.utcnow(),
            datetime.utcnow()
        )
        
        try:
            result = self.db.execute_query(query, params)
            if result and len(result) > 0:
                return result[0]['id']
            return None
        except Exception as e:
            logger.error(f"Error inserting currency rate: {e}")
            return None
    
    def get_currency_rates(self, country_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get currency rates, optionally filtered by country."""
        if country_name:
            query = "SELECT * FROM currency_rates WHERE country_name = %s ORDER BY rate_date DESC"
            return self.db.execute_query(query, (country_name,)) or []
        else:
            query = "SELECT * FROM currency_rates ORDER BY rate_date DESC, country_name"
            return self.db.execute_query(query) or []
    
    def get_latest_rates(self, country_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest currency rates."""
        if country_name:
            query = """
            SELECT DISTINCT ON (currency_code) *
            FROM currency_rates 
            WHERE country_name = %s
            ORDER BY currency_code, rate_date DESC
            """
            return self.db.execute_query(query, (country_name,)) or []
        else:
            query = """
            SELECT DISTINCT ON (country_name, currency_code) *
            FROM currency_rates 
            ORDER BY country_name, currency_code, rate_date DESC
            """
            return self.db.execute_query(query) or []
    
    def get_rate_history(self, country_name: str, currency_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get rate history for a country and currency."""
        query = """
        SELECT * FROM currency_rates 
        WHERE country_name = %s AND currency_code = %s 
        AND rate_date >= %s
        ORDER BY rate_date DESC
        """
        
        start_date = date.today() - timedelta(days=days)
        return self.db.execute_query(query, (country_name, currency_code.upper(), start_date)) or []


# Global database connection instance
db_connection = DatabaseConnection()
country_repo = CountryRepository(db_connection)
currency_rate_repo = CurrencyRateRepository(db_connection)


def get_database_connection() -> DatabaseConnection:
    """Get database connection instance."""
    return db_connection


def get_country_repository() -> CountryRepository:
    """Get country repository instance."""
    return country_repo


def get_currency_rate_repository() -> CurrencyRateRepository:
    """Get currency rate repository instance."""
    return currency_rate_repo
