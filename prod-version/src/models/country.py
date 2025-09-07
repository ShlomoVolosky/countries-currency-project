"""
Country data models for the Countries Currency Project.

This module defines the Country model and related data structures.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field, validator

from .base import BaseModelClass, TimestampMixin, DatabaseMixin, ValidationMixin


class CountryData(BaseModelClass, TimestampMixin, ValidationMixin):
    """Country data model."""
    
    id: Optional[int] = Field(None, description="Database ID")
    country_name: str = Field(..., min_length=1, max_length=255, description="Country name")
    capitals: List[str] = Field(default_factory=list, description="List of capitals")
    continent: str = Field(default="", max_length=255, description="Continent")
    currencies: List[str] = Field(default_factory=list, description="List of currency codes")
    is_un_member: bool = Field(default=False, description="UN membership status")
    population: int = Field(default=0, ge=0, description="Population count")
    timezone_info: Dict[str, str] = Field(default_factory=dict, description="Timezone information")
    
    @validator("country_name")
    def validate_country_name(cls, v):
        """Validate country name."""
        if not v or not v.strip():
            raise ValueError("Country name cannot be empty")
        return v.strip()
    
    @validator("capitals")
    def validate_capitals(cls, v):
        """Validate capitals list."""
        if not isinstance(v, list):
            return []
        return [str(capital).strip() for capital in v if capital and str(capital).strip()]
    
    @validator("currencies")
    def validate_currencies(cls, v):
        """Validate currencies list."""
        if not isinstance(v, list):
            return []
        return [str(currency).strip().upper() for currency in v if currency and str(currency).strip()]
    
    @validator("population")
    def validate_population(cls, v):
        """Validate population."""
        if v < 0:
            raise ValueError("Population cannot be negative")
        return v
    
    @validator("timezone_info")
    def validate_timezone_info(cls, v):
        """Validate timezone info."""
        if not isinstance(v, dict):
            return {}
        return {str(k): str(v) for k, v in v.items() if k and v}
    
    def get_primary_capital(self) -> Optional[str]:
        """Get the primary capital (first in the list)."""
        return self.capitals[0] if self.capitals else None
    
    def has_currency(self, currency_code: str) -> bool:
        """Check if country uses a specific currency."""
        return currency_code.upper() in [c.upper() for c in self.currencies]
    
    def get_timezone_count(self) -> int:
        """Get the number of timezones."""
        return len(self.timezone_info)
    
    def is_large_country(self, threshold: int = 10000000) -> bool:
        """Check if country has large population."""
        return self.population >= threshold


class CountryCreate(BaseModelClass):
    """Model for creating a new country."""
    
    country_name: str = Field(..., min_length=1, max_length=255)
    capitals: List[str] = Field(default_factory=list)
    continent: str = Field(default="", max_length=255)
    currencies: List[str] = Field(default_factory=list)
    is_un_member: bool = Field(default=False)
    population: int = Field(default=0, ge=0)
    timezone_info: Dict[str, str] = Field(default_factory=dict)


class CountryUpdate(BaseModelClass):
    """Model for updating an existing country."""
    
    country_name: Optional[str] = Field(None, min_length=1, max_length=255)
    capitals: Optional[List[str]] = None
    continent: Optional[str] = Field(None, max_length=255)
    currencies: Optional[List[str]] = None
    is_un_member: Optional[bool] = None
    population: Optional[int] = Field(None, ge=0)
    timezone_info: Optional[Dict[str, str]] = None


class CountryFilter(BaseModelClass):
    """Model for filtering countries."""
    
    continent: Optional[str] = None
    is_un_member: Optional[bool] = None
    min_population: Optional[int] = Field(None, ge=0)
    max_population: Optional[int] = Field(None, ge=0)
    has_currency: Optional[str] = None
    search_term: Optional[str] = None
    
    @validator("max_population")
    def validate_population_range(cls, v, values):
        """Validate population range."""
        if v is not None and "min_population" in values and values["min_population"] is not None:
            if v < values["min_population"]:
                raise ValueError("max_population must be greater than min_population")
        return v


class Country(DatabaseMixin):
    """Country model with database operations."""
    
    def __init__(self, data: CountryData):
        self.data = data
    
    def save(self) -> bool:
        """Save country to database."""
        # This would be implemented with actual database operations
        # For now, return True as placeholder
        return True
    
    def delete(self) -> bool:
        """Delete country from database."""
        # This would be implemented with actual database operations
        return True
    
    def exists(self) -> bool:
        """Check if country exists in database."""
        # This would be implemented with actual database operations
        return True
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional["Country"]:
        """Get country by ID."""
        # This would be implemented with actual database operations
        return None
    
    @classmethod
    def get_all(cls, limit: Optional[int] = None, offset: Optional[int] = None) -> List["Country"]:
        """Get all countries."""
        # This would be implemented with actual database operations
        return []
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional["Country"]:
        """Get country by name."""
        # This would be implemented with actual database operations
        return None
    
    @classmethod
    def search(cls, filter_data: CountryFilter) -> List["Country"]:
        """Search countries with filters."""
        # This would be implemented with actual database operations
        return []
