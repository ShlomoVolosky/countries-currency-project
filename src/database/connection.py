import asyncio
from typing import Optional, Dict, Any, List
import asyncpg
from contextlib import asynccontextmanager
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger("database")


class DatabaseConnection:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    @property
    def settings(self):
        return get_settings()
    
    async def create_pool(self) -> bool:
        try:
            self.pool = await asyncpg.create_pool(
                self.settings.database.url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                init=self._init_connection
            )
            logger.info("Database connection pool created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            return False
    
    async def _init_connection(self, conn):
        """Initialize connection with proper JSONB handling"""
        await conn.set_type_codec(
            'jsonb',
            encoder=lambda x: x,
            decoder=lambda x: x,
            schema='pg_catalog'
        )
    
    async def close_pool(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        if not self.pool:
            await self.create_pool()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        async with self.get_connection() as conn:
            try:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def execute_command(self, command: str, *args) -> str:
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        async with self.get_connection() as conn:
            try:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Fetch one failed: {e}")
                raise


db_connection = DatabaseConnection()
