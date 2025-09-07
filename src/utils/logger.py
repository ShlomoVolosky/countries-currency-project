import logging
import sys
from typing import Optional
from pathlib import Path
from src.config.settings import get_settings


class Logger:
    _instances: dict = {}
    
    def __new__(cls, name: str = "countries_currency"):
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]
    
    def __init__(self, name: str = "countries_currency"):
        if hasattr(self, '_initialized'):
            return
        
        self.settings = get_settings()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.settings.logging.level.upper()))
        
        if not self.logger.handlers:
            self._setup_handlers()
        
        self._initialized = True
    
    def _setup_handlers(self):
        formatter = logging.Formatter(self.settings.logging.format)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        if self.settings.logging.file_path:
            file_path = Path(self.settings.logging.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(message, extra=kwargs)


def get_logger(name: str = "countries_currency") -> Logger:
    return Logger(name)
