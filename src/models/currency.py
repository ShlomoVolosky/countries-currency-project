from typing import Optional
from decimal import Decimal
from datetime import date
from pydantic import Field, ConfigDict
from .base import BaseEntity


class CurrencyRate(BaseEntity):
    country_name: str = Field(..., description="Country name")
    currency_code: str = Field(..., description="Currency code")
    shekel_rate: Decimal = Field(..., description="Exchange rate to ILS")
    rate_date: date = Field(..., description="Rate date")

    model_config = ConfigDict(from_attributes=True)


class CurrencyRateCreate(BaseEntity):
    country_name: str
    currency_code: str
    shekel_rate: Decimal
    rate_date: date


class CurrencyRateUpdate(BaseEntity):
    country_name: Optional[str] = None
    currency_code: Optional[str] = None
    shekel_rate: Optional[Decimal] = None
    rate_date: Optional[date] = None
