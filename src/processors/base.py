from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import asyncio
import aiohttp
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.models.base import BaseProcessor


class BaseAPIClient(ABC):
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.api.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        for attempt in range(self.settings.api.retry_attempts):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"API request failed with status {response.status}")
            except Exception as e:
                self.logger.error(f"API request attempt {attempt + 1} failed: {e}")
                if attempt < self.settings.api.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None


class BaseDataProcessor(BaseProcessor):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    async def fetch_data(self) -> Optional[List[Dict[str, Any]]]:
        pass
    
    @abstractmethod
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Any]:
        pass
    
    @abstractmethod
    async def save_data(self, transformed_data: List[Any]) -> bool:
        pass
    
    async def process(self) -> bool:
        try:
            self.logger.info("Starting data processing")
            
            raw_data = await self.fetch_data()
            if not raw_data:
                self.logger.error("Failed to fetch data")
                return False
            
            transformed_data = await self.transform_data(raw_data)
            if not transformed_data:
                self.logger.error("Failed to transform data")
                return False
            
            success = await self.save_data(transformed_data)
            if success:
                self.logger.info(f"Successfully processed {len(transformed_data)} items")
            else:
                self.logger.error("Failed to save data")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return False
    
    async def validate(self) -> bool:
        try:
            self.logger.info("Validating processor")
            return True
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False
