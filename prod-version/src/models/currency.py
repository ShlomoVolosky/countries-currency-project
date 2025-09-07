from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import Field, validator

from .base import BaseModelClass, TimestampMixin, DatabaseMixin, ValidationMixin


class CurrencyRate(BaseModelClass, TimestampMixin, ValidationMixin):
        if not v or len(v) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        return v.upper().strip()
    @validator("country_name")
    def validate_country_name(cls, v):
        if isinstance(v, (int, float)):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("Shekel rate must be positive")
        return v
    def get_ils_amount(self, amount: Decimal) -> Decimal:
        return ils_amount / self.shekel_rate
    def is_recent(self, days: int = 1) -> bool:
    country_name: str = Field(..., min_length=1, max_length=255)
    currency_code: str = Field(..., min_length=3, max_length=3)
    shekel_rate: Decimal = Field(..., gt=0)
    rate_date: Optional[date] = None


class CurrencyRateUpdate(BaseModelClass):
    country_name: Optional[str] = None
    currency_code: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_rate: Optional[Decimal] = Field(None, gt=0)
    max_rate: Optional[Decimal] = Field(None, gt=0)
    
    @validator("end_date")
    def validate_date_range(cls, v, values):
        if v is not None and "min_rate" in values and values["min_rate"] is not None:
            if v < values["min_rate"]:
                raise ValueError("max_rate must be greater than min_rate")
        return v

class CurrencyInfo(BaseModelClass):
        return v.upper().strip()
    @validator("name")
    def validate_name(cls, v):
    def __init__(self, data: CurrencyRate):
        self.data = data
    
    def save(self) -> bool:
        return True
    def exists(self) -> bool:
        return None
    @classmethod
    def get_all(cls, limit: Optional[int] = None, offset: Optional[int] = None) -> List["CurrencyRateModel"]:
        return None
    @classmethod
    def get_latest_rates(cls, country_name: Optional[str] = None) -> List["CurrencyRateModel"]:
        return []
    @classmethod
    def get_rate_history(cls, country_name: str, currency_code: str, days: int = 30) -> List["CurrencyRateModel"]: