from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class APIResponse(BaseModel):
    success: bool = Field(..., description="Response success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    model_config = ConfigDict(from_attributes=True)


class CountriesListResponse(APIResponse):
    data: List[Dict[str, Any]] = Field(..., description="List of countries")


class CurrencyRatesResponse(APIResponse):
    data: List[Dict[str, Any]] = Field(..., description="List of currency rates")


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="Service version")
    database_connected: bool = Field(..., description="Database connection status")

    model_config = ConfigDict(from_attributes=True)
