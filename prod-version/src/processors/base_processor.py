"""
Base processor class for the Countries Currency Project.

This module provides the base processor class with common functionality
for data processing operations.
"""

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
    """Base processor class with common functionality."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db = get_database_connection()
        self.logger = get_logger(self.__class__.__name__)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.processed_count = 0
        self.error_count = 0
        self.success_count = 0
    
    def start_processing(self):
        """Start processing session."""
        self.start_time = datetime.utcnow()
        self.processed_count = 0
        self.error_count = 0
        self.success_count = 0
        self.logger.info(f"Starting {self.__class__.__name__} processing session")
    
    def end_processing(self):
        """End processing session."""
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
        
        self.logger.info(
            f"Completed {self.__class__.__name__} processing session - "
            f"Processed: {self.processed_count}, "
            f"Success: {self.success_count}, "
            f"Errors: {self.error_count}, "
            f"Duration: {duration:.2f}s"
        )
    
    def log_progress(self, current: int, total: int, item_name: str = ""):
        """Log processing progress."""
        if total > 0:
            percentage = (current / total) * 100
            self.logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {item_name}")
        else:
            self.logger.info(f"Processing: {item_name}")
    
    def handle_error(self, error: Exception, context: str = ""):
        """Handle processing errors."""
        self.error_count += 1
        error_msg = f"Error in {self.__class__.__name__}"
        if context:
            error_msg += f" - {context}"
        error_msg += f": {str(error)}"
        
        self.logger.error(error_msg, exc_info=True)
    
    def record_success(self, item_name: str = ""):
        """Record successful processing."""
        self.success_count += 1
        if item_name:
            self.logger.debug(f"Successfully processed: {item_name}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        duration = 0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "processor": self.__class__.__name__,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": duration,
            "processed_count": self.processed_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / self.processed_count * 100) if self.processed_count > 0 else 0
        }
    
    @abstractmethod
    def process(self) -> bool:
        """Main processing method to be implemented by subclasses."""
        pass
    
    def run(self) -> bool:
        """Run the processor with error handling and logging."""
        try:
            self.start_processing()
            result = self.process()
            self.end_processing()
            return result
        except Exception as e:
            self.handle_error(e, "main processing")
            self.end_processing()
            return False


class APIClientMixin:
    """Mixin for API client functionality."""
    
    def __init__(self):
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.settings.api.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default timeout
        self.session.timeout = self.settings.api.timeout
    
    @retry_with_backoff(max_attempts=3, base_delay=1)
    def make_request(self, url: str, params: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """Make HTTP request with retry logic."""
        try:
            response = self.session.get(url, params=params, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"API request failed for {url}: {e}")
            return None
    
    def close_session(self):
        """Close HTTP session."""
        if self.session:
            self.session.close()


class DataValidatorMixin:
    """Mixin for data validation functionality."""
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    def validate_data_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        """Validate data types."""
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")
        return type_errors
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
