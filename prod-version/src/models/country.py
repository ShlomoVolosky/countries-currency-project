from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field, validator

from .base import BaseModelClass, TimestampMixin, DatabaseMixin, ValidationMixin


class CountryData(BaseModelClass, TimestampMixin, ValidationMixin):
        if not v or not v.strip():
            raise ValueError("Country name cannot be empty")
        return v.strip()
    @validator("capitals")
    def validate_capitals(cls, v):
        if not isinstance(v, list):
            return []
        return [str(currency).strip().upper() for currency in v if currency and str(currency).strip()]
    @validator("population")
    def validate_population(cls, v):
        if not isinstance(v, dict):
            return {}
        return {str(k): str(v) for k, v in v.items() if k and v}
    def get_primary_capital(self) -> Optional[str]:
        return currency_code.upper() in [c.upper() for c in self.currencies]
    def get_timezone_count(self) -> int:
        return self.population >= threshold

class CountryCreate(BaseModelClass):
    country_name: Optional[str] = Field(None, min_length=1, max_length=255)
    capitals: Optional[List[str]] = None
    continent: Optional[str] = Field(None, max_length=255)
    currencies: Optional[List[str]] = None
    is_un_member: Optional[bool] = None
    population: Optional[int] = Field(None, ge=0)
    timezone_info: Optional[Dict[str, str]] = None


class CountryFilter(BaseModelClass):
        if v is not None and "min_population" in values and values["min_population"] is not None:
            if v < values["min_population"]:
                raise ValueError("max_population must be greater than min_population")
        return v

class Country(DatabaseMixin):
        return True
    def delete(self) -> bool:
        return True
    @classmethod
    def get_by_id(cls, id: int) -> Optional["Country"]:
        return []
    @classmethod
    def get_by_name(cls, name: str) -> Optional["Country"]:
        return []