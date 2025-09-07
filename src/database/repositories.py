from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from src.database.connection import db_connection
from src.models.country import Country, CountryCreate, CountryUpdate
from src.models.currency import CurrencyRate, CurrencyRateCreate, CurrencyRateUpdate
from src.models.base import BaseRepository
from src.utils.logger import get_logger

logger = get_logger("repositories")


class CountryRepository(BaseRepository):
    async def create(self, entity: CountryCreate) -> Optional[Country]:
        query = """
        INSERT INTO countries (country_name, capitals, continent, currencies, 
                             is_un_member, population, timezone_info, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, country_name, capitals, continent, currencies, 
                 is_un_member, population, timezone_info, created_at, updated_at
        """
        
        try:
            now = datetime.now()
            row = await db_connection.fetch_one(
                query, entity.country_name, entity.capitals, entity.continent,
                entity.currencies, entity.is_un_member, entity.population,
                entity.timezone_info, now, now
            )
            return Country(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to create country: {e}")
            return None
    
    async def get_by_id(self, entity_id: int) -> Optional[Country]:
        query = """
        SELECT id, country_name, capitals, continent, currencies, 
               is_un_member, population, timezone_info, created_at, updated_at
        FROM countries WHERE id = $1
        """
        
        try:
            row = await db_connection.fetch_one(query, entity_id)
            return Country(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to get country by id: {e}")
            return None
    
    async def get_by_name(self, country_name: str) -> Optional[Country]:
        query = """
        SELECT id, country_name, capitals, continent, currencies, 
               is_un_member, population, timezone_info, created_at, updated_at
        FROM countries WHERE country_name = $1
        """
        
        try:
            row = await db_connection.fetch_one(query, country_name)
            return Country(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to get country by name: {e}")
            return None
    
    async def update(self, entity: CountryUpdate) -> Optional[Country]:
        if not entity.id:
            return None
        
        query = """
        UPDATE countries SET 
            country_name = COALESCE($2, country_name),
            capitals = COALESCE($3, capitals),
            continent = COALESCE($4, continent),
            currencies = COALESCE($5, currencies),
            is_un_member = COALESCE($6, is_un_member),
            population = COALESCE($7, population),
            timezone_info = COALESCE($8, timezone_info),
            updated_at = $9
        WHERE id = $1
        RETURNING id, country_name, capitals, continent, currencies, 
                 is_un_member, population, timezone_info, created_at, updated_at
        """
        
        try:
            now = datetime.now()
            row = await db_connection.fetch_one(
                query, entity.id, entity.country_name, entity.capitals,
                entity.continent, entity.currencies, entity.is_un_member,
                entity.population, entity.timezone_info, now
            )
            return Country(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to update country: {e}")
            return None
    
    async def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM countries WHERE id = $1"
        
        try:
            result = await db_connection.execute_command(query, entity_id)
            return "DELETE" in result
        except Exception as e:
            logger.error(f"Failed to delete country: {e}")
            return False
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Country]:
        query = """
        SELECT id, country_name, capitals, continent, currencies, 
               is_un_member, population, timezone_info, created_at, updated_at
        FROM countries ORDER BY country_name LIMIT $1 OFFSET $2
        """
        
        try:
            rows = await db_connection.execute_query(query, limit, offset)
            return [Country(**row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list countries: {e}")
            return []
    
    async def get_countries_with_currencies(self) -> List[Dict[str, Any]]:
        query = """
        SELECT DISTINCT country_name, currencies 
        FROM countries 
        WHERE currencies IS NOT NULL AND array_length(currencies, 1) > 0
        """
        
        try:
            return await db_connection.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get countries with currencies: {e}")
            return []


class CurrencyRateRepository(BaseRepository):
    async def create(self, entity: CurrencyRateCreate) -> Optional[CurrencyRate]:
        query = """
        INSERT INTO currency_rates (country_name, currency_code, shekel_rate, rate_date, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (country_name, currency_code, rate_date) 
        DO UPDATE SET shekel_rate = EXCLUDED.shekel_rate, created_at = EXCLUDED.created_at
        RETURNING id, country_name, currency_code, shekel_rate, rate_date, created_at, updated_at
        """
        
        try:
            now = datetime.now()
            row = await db_connection.fetch_one(
                query, entity.country_name, entity.currency_code,
                entity.shekel_rate, entity.rate_date, now
            )
            return CurrencyRate(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to create currency rate: {e}")
            return None
    
    async def get_by_id(self, entity_id: int) -> Optional[CurrencyRate]:
        query = """
        SELECT id, country_name, currency_code, shekel_rate, rate_date, created_at, updated_at
        FROM currency_rates WHERE id = $1
        """
        
        try:
            row = await db_connection.fetch_one(query, entity_id)
            return CurrencyRate(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to get currency rate by id: {e}")
            return None
    
    async def update(self, entity: CurrencyRateUpdate) -> Optional[CurrencyRate]:
        if not entity.id:
            return None
        
        query = """
        UPDATE currency_rates SET 
            country_name = COALESCE($2, country_name),
            currency_code = COALESCE($3, currency_code),
            shekel_rate = COALESCE($4, shekel_rate),
            rate_date = COALESCE($5, rate_date),
            updated_at = $6
        WHERE id = $1
        RETURNING id, country_name, currency_code, shekel_rate, rate_date, created_at, updated_at
        """
        
        try:
            now = datetime.now()
            row = await db_connection.fetch_one(
                query, entity.id, entity.country_name, entity.currency_code,
                entity.shekel_rate, entity.rate_date, now
            )
            return CurrencyRate(**row) if row else None
        except Exception as e:
            logger.error(f"Failed to update currency rate: {e}")
            return None
    
    async def delete(self, entity_id: int) -> bool:
        query = "DELETE FROM currency_rates WHERE id = $1"
        
        try:
            result = await db_connection.execute_command(query, entity_id)
            return "DELETE" in result
        except Exception as e:
            logger.error(f"Failed to delete currency rate: {e}")
            return False
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[CurrencyRate]:
        query = """
        SELECT id, country_name, currency_code, shekel_rate, rate_date, created_at, updated_at
        FROM currency_rates ORDER BY rate_date DESC, country_name LIMIT $1 OFFSET $2
        """
        
        try:
            rows = await db_connection.execute_query(query, limit, offset)
            return [CurrencyRate(**row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list currency rates: {e}")
            return []
    
    async def get_latest_rates(self) -> List[CurrencyRate]:
        query = """
        SELECT DISTINCT ON (currency_code) 
               id, country_name, currency_code, shekel_rate, rate_date, created_at, updated_at
        FROM currency_rates 
        ORDER BY currency_code, rate_date DESC
        """
        
        try:
            rows = await db_connection.execute_query(query)
            return [CurrencyRate(**row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get latest rates: {e}")
            return []
