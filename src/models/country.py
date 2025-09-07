from typing import List, Optional, Dict, Any
from pydantic import Field, ConfigDict
from .base import BaseEntity


class Country(BaseEntity):
    country_name: str = Field(..., description="Country name")
    capitals: List[str] = Field(default_factory=list, description="List of capitals")
    continent: Optional[str] = Field(None, description="Continent")
    currencies: List[str] = Field(default_factory=list, description="List of currency codes")
    is_un_member: bool = Field(False, description="UN membership status")
    population: int = Field(0, description="Population count")
    timezone_info: Optional[Dict[str, Any]] = Field(None, description="Timezone information")

    model_config = ConfigDict(from_attributes=True)


class CountryCreate(BaseEntity):
    country_name: str
    capitals: List[str] = Field(default_factory=list)
    continent: Optional[str] = None
    currencies: List[str] = Field(default_factory=list)
    is_un_member: bool = False
    population: int = 0
    timezone_info: Optional[Dict[str, Any]] = None


class CountryUpdate(BaseEntity):
    country_name: Optional[str] = None
    capitals: Optional[List[str]] = None
    continent: Optional[str] = None
    currencies: Optional[List[str]] = None
    is_un_member: Optional[bool] = None
    population: Optional[int] = None
    timezone_info: Optional[Dict[str, Any]] = None
