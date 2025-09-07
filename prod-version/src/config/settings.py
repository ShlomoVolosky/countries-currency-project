"""
Configuration management for the Countries Currency Project.

This module provides centralized configuration management using Pydantic
for validation and type safety.
"""

import os
from typing import Optional, List
from functools import lru_cache
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    name: str = Field(default="countries_db", env="DB_NAME")
    user: str = Field(default="countries_user", env="DB_USER")
    password: Optional[str] = Field(default=None, env="DB_PASSWORD")
    port: int = Field(default=5432, env="DB_PORT")
    
    @property
    def url(self) -> str:
        """Generate database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    countries_url: str = Field(
        default="https://restcountries.com/v3.1/all?fields=name,capital,continents,currencies,unMember,population,timezones",
        env="COUNTRIES_API_URL"
    )
    currency_url: str = Field(
        default="https://api.frankfurter.app",
        env="CURRENCY_API_URL"
    )
    timeout: int = Field(default=30, env="API_TIMEOUT")
    retry_attempts: int = Field(default=3, env="API_RETRY_ATTEMPTS")
    
    class Config:
        env_prefix = "API_"


class MonitoringSettings(BaseSettings):
    """Monitoring configuration settings."""
    
    prometheus_port: int = Field(default=8000, env="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, env="GRAFANA_PORT")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_prefix = "MONITORING_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    @validator("level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class SchedulerSettings(BaseSettings):
    """Scheduler configuration settings."""
    
    countries_update_cron: str = Field(
        default="0 2 * * 0",  # Every Sunday at 2 AM
        env="COUNTRIES_UPDATE_CRON"
    )
    currency_update_cron: str = Field(
        default="0 */6 * * *",  # Every 6 hours
        env="CURRENCY_UPDATE_CRON"
    )
    timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    
    class Config:
        env_prefix = "SCHEDULER_"


class Settings(PydanticBaseSettings):
    """Main application settings."""
    
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


# Backward compatibility
class Config:
    """Backward compatibility wrapper for old config class."""
    
    def __init__(self):
        self.settings = get_settings()
    
    @property
    def DB_HOST(self) -> str:
        return self.settings.database.host
    
    @property
    def DB_NAME(self) -> str:
        return self.settings.database.name
    
    @property
    def DB_USER(self) -> str:
        return self.settings.database.user
    
    @property
    def DB_PASSWORD(self) -> str:
        return self.settings.database.password
    
    @property
    def DB_PORT(self) -> str:
        return str(self.settings.database.port)
    
    @property
    def DATABASE_URL(self) -> str:
        return self.settings.database.url
    
    @property
    def COUNTRIES_API_URL(self) -> str:
        return self.settings.api.countries_url
    
    @property
    def CURRENCY_API_URL(self) -> str:
        return self.settings.api.currency_url
