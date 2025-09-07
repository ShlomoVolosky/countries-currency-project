import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import structlog
from structlog.stdlib import LoggerFactory

from config.settings import get_settings


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    return logging.getLogger(name)

def get_structured_logger(name: str):
    @property
    def logger(self) -> logging.Logger:
        return get_structured_logger(self.__class__.__name__)

class LoggingContext:
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}", exc_info=True)
            raise
    
    return wrapper


def log_performance(func):