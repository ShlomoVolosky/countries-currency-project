import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

# Get the absolute path to the .env file
ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", alias="DB_HOST")
    name: str = Field(default="countries_db", alias="DB_NAME")
    user: str = Field(default="countries_user", alias="DB_USER")
    password: Optional[str] = Field(default=None, alias="DB_PASSWORD")
    port: int = Field(default=5432, alias="DB_PORT")
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = {"env_file": ENV_FILE_PATH, "extra": "ignore"}


class APISettings(BaseSettings):
    countries_url: str = Field(
        default="https://restcountries.com/v3.1/all?fields=name,capital,continents,currencies,unMember,population,timezones"
    )
    currency_url: str = Field(
        default="https://api.frankfurter.app"
    )
    timeout: int = Field(default=30)
    retry_attempts: int = Field(default=3)

    model_config = {"env_file": ENV_FILE_PATH, "extra": "ignore"}


class LoggingSettings(BaseSettings):
    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_path: Optional[str] = Field(default=None)

    model_config = {"env_file": ENV_FILE_PATH, "extra": "ignore"}


class MonitoringSettings(BaseSettings):
    prometheus_port: int = Field(default=8000)
    grafana_port: int = Field(default=3000)
    metrics_enabled: bool = Field(default=True)

    model_config = {"env_file": ENV_FILE_PATH, "extra": "ignore"}


class Settings(BaseSettings):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    app_name: str = Field(default="Countries Currency Service")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    model_config = {"env_file": ENV_FILE_PATH, "extra": "ignore"}


def get_settings() -> Settings:
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv(ENV_FILE_PATH)
    return Settings()
