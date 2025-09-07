import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import time

from config.settings import get_settings
from utils.logger import get_logger
from utils.retry import retry_with_backoff
from database.connection import get_database_connection

logger = get_logger(__name__)


class BaseProcessor(ABC):
        self.start_time = datetime.utcnow()
        self.processed_count = 0
        self.error_count = 0
        self.success_count = 0
        self.logger.info(f"Starting {self.__class__.__name__} processing session")
    def end_processing(self):
        if total > 0:
            percentage = (current / total) * 100
            self.logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {item_name}")
        else:
            self.logger.info(f"Processing: {item_name}")
    def handle_error(self, error: Exception, context: str = ""):
        self.success_count += 1
        if item_name:
            self.logger.debug(f"Successfully processed: {item_name}")
    def get_processing_stats(self) -> Dict[str, Any]:
        pass
    def run(self) -> bool:
    def __init__(self):
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        try:
            response = self.session.get(url, params=params, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API request failed for {url}: {e}")
            return None
    def close_session(self):
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")
        return type_errors
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str: