"""
Currency data models for the Countries Currency Project.

This module defines the Currency and CurrencyRate models and related data structures.
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import Field, validator

from .base import BaseModelClass, TimestampMixin, DatabaseMixin, ValidationMixin


class CurrencyRate(BaseModelClass, TimestampMixin, ValidationMixin):
    """Currency rate data model."""
    
    id: Optional[int] = Field(None, description="Database ID")
    country_name: str = Field(..., min_length=1, max_length=255, description="Country name")
    currency_code: str = Field(..., min_length=3, max_length=3, description="Currency code")
    shekel_rate: Decimal = Field(..., gt=0, description="Rate to ILS")
    rate_date: date = Field(default_factory=date.today, description="Rate date")
    
    @validator("currency_code")
    def validate_currency_code(cls, v):
        """Validate currency code format."""
        if not v or len(v) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        return v.upper().strip()
    
    @validator("country_name")
    def validate_country_name(cls, v):
        """Validate country name."""
        if not v or not v.strip():
            raise ValueError("Country name cannot be empty")
        return v.strip()
    
    @validator("shekel_rate")
    def validate_shekel_rate(cls, v):
        """Validate shekel rate."""
        if isinstance(v, (int, float)):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("Shekel rate must be positive")
        return v
    
    def get_ils_amount(self, amount: Decimal) -> Decimal:
        """Convert amount to ILS."""
        return amount * self.shekel_rate
    
    def get_currency_amount(self, ils_amount: Decimal) -> Decimal:
        """Convert ILS amount to currency."""
        return ils_amount / self.shekel_rate
    
    def is_recent(self, days: int = 1) -> bool:
        """Check if rate is recent."""
        return (date.today() - self.rate_date).days <= days


class CurrencyRateCreate(BaseModelClass):
    """Model for creating a new currency rate."""
    
    country_name: str = Field(..., min_length=1, max_length=255)
    currency_code: str = Field(..., min_length=3, max_length=3)
    shekel_rate: Decimal = Field(..., gt=0)
    rate_date: Optional[date] = None


class CurrencyRateUpdate(BaseModelClass):
    """Model for updating an existing currency rate."""
    
    shekel_rate: Optional[Decimal] = Field(None, gt=0)
    rate_date: Optional[date] = None


class CurrencyRateFilter(BaseModelClass):
    """Model for filtering currency rates."""
    
    country_name: Optional[str] = None
    currency_code: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_rate: Optional[Decimal] = Field(None, gt=0)
    max_rate: Optional[Decimal] = Field(None, gt=0)
    
    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Validate date range."""
        if v is not None and "start_date" in values and values["start_date"] is not None:
            if v < values["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v
    
    @validator("max_rate")
    def validate_rate_range(cls, v, values):
        """Validate rate range."""
        if v is not None and "min_rate" in values and values["min_rate"] is not None:
            if v < values["min_rate"]:
                raise ValueError("max_rate must be greater than min_rate")
        return v


class CurrencyInfo(BaseModelClass):
    """Currency information model."""
    
    code: str = Field(..., min_length=3, max_length=3, description="Currency code")
    name: str = Field(..., min_length=1, description="Currency name")
    symbol: Optional[str] = Field(None, description="Currency symbol")
    is_supported: bool = Field(default=True, description="Whether currency is supported by API")
    
    @validator("code")
    def validate_code(cls, v):
        """Validate currency code."""
        return v.upper().strip()
    
    @validator("name")
    def validate_name(cls, v):
        """Validate currency name."""
        if not v or not v.strip():
            raise ValueError("Currency name cannot be empty")
        return v.strip()


class CurrencyRateModel(DatabaseMixin):
    """Currency rate model with database operations."""
    
    def __init__(self, data: CurrencyRate):
        self.data = data
    
    def save(self) -> bool:
        """Save currency rate to database."""
        # This would be implemented with actual database operations
        return True
    
    def delete(self) -> bool:
        """Delete currency rate from database."""
        # This would be implemented with actual database operations
        return True
    
    def exists(self) -> bool:
        """Check if currency rate exists in database."""
        # This would be implemented with actual database operations
        return True
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional["CurrencyRateModel"]:
        """Get currency rate by ID."""
        # This would be implemented with actual database operations
        return None
    
    @classmethod
    def get_all(cls, limit: Optional[int] = None, offset: Optional[int] = None) -> List["CurrencyRateModel"]:
        """Get all currency rates."""
        # This would be implemented with actual database operations
        return []
    
    @classmethod
    def get_by_country_and_currency(cls, country_name: str, currency_code: str, rate_date: Optional[date] = None) -> Optional["CurrencyRateModel"]:
        """Get currency rate by country and currency."""
        # This would be implemented with actual database operations
        return None
    
    @classmethod
    def get_latest_rates(cls, country_name: Optional[str] = None) -> List["CurrencyRateModel"]:
        """Get latest currency rates."""
        # This would be implemented with actual database operations
        return []
    
    @classmethod
    def search(cls, filter_data: CurrencyRateFilter) -> List["CurrencyRateModel"]:
        """Search currency rates with filters."""
        # This would be implemented with actual database operations
        return []
    
    @classmethod
    def get_rate_history(cls, country_name: str, currency_code: str, days: int = 30) -> List["CurrencyRateModel"]:
        """Get rate history for a country and currency."""
        # This would be implemented with actual database operations
        return []
