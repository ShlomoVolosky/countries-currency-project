from typing import Optional, Dict, Any, List, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import logging

from .settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConfig:
    
    def __init__(self):
        self.settings = get_settings()
        self.connection_pool: Optional[SimpleConnectionPool] = None
    
    def _initialize_pool(self):
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=self.settings.database.host,
                database=self.settings.database.name,
                user=self.settings.database.user,
                password=self.settings.database.password,
                port=self.settings.database.port
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
                self._initialize_pool()
            
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
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_results: bool = True) -> Optional[Union[List[Dict], bool]]:
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")

db_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    return db_config