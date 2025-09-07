import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Optional
import structlog
from structlog.stdlib import LoggerFactory

from config.settings import get_settings


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    settings = get_settings()
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=settings.logging.format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count
        )
        file_handler.setFormatter(logging.Formatter(settings.logging.format))
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_structured_logger(name: str):
    return structlog.get_logger(name)


class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)


class LoggingContext:
    def __init__(self, logger: logging.Logger, message: str):
        self.logger = logger
        self.message = message

    def __enter__(self):
        self.logger.debug(f"Starting: {self.message}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.debug(f"Completed: {self.message}")
        else:
            self.logger.error(f"Failed: {self.message} - {exc_val}")


def log_function_calls(func):
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
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger = get_logger(func.__module__)
        logger.info(f"Function {func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper