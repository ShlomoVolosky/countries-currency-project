"""
Data validation utilities for the Countries Currency Project.

This module provides validation functions for various data types
and structures used throughout the application.
"""

import re
import logging
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import pytz

from utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataValidator:
    """Main data validator class."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_country_name(self, name: str) -> bool:
        """Validate country name."""
        if not name or not isinstance(name, str):
            return False
        
        # Remove whitespace and check length
        name = name.strip()
        if len(name) < 1 or len(name) > 255:
            return False
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            return False
        
        return True
    
    def validate_currency_code(self, code: str) -> bool:
        """Validate currency code (ISO 4217 format)."""
        if not code or not isinstance(code, str):
            return False
        
        # Must be exactly 3 uppercase letters
        if not re.match(r"^[A-Z]{3}$", code):
            return False
        
        return True
    
    def validate_capital_name(self, capital: str) -> bool:
        """Validate capital city name."""
        if not capital or not isinstance(capital, str):
            return False
        
        # Remove whitespace and check length
        capital = capital.strip()
        if len(capital) < 1 or len(capital) > 255:
            return False
        
        # Check for valid characters
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", capital):
            return False
        
        return True
    
    def validate_continent(self, continent: str) -> bool:
        """Validate continent name."""
        if not continent or not isinstance(continent, str):
            return False
        
        continent = continent.strip()
        valid_continents = [
            'Africa', 'Antarctica', 'Asia', 'Europe', 
            'North America', 'South America', 'Oceania'
        ]
        
        return continent in valid_continents
    
    def validate_population(self, population: Union[int, str]) -> bool:
        """Validate population count."""
        try:
            if isinstance(population, str):
                population = int(population)
            
            return isinstance(population, int) and population >= 0
        except (ValueError, TypeError):
            return False
    
    def validate_timezone(self, timezone: str) -> bool:
        """Validate timezone string."""
        if not timezone or not isinstance(timezone, str):
            return False
        
        try:
            pytz.timezone(timezone)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            # Check if it's a UTC offset format
            if re.match(r"^UTC[+-]\d{1,2}(:\d{2})?$", timezone):
                return True
            return False
    
    def validate_exchange_rate(self, rate: Union[float, str, Decimal]) -> bool:
        """Validate exchange rate."""
        try:
            if isinstance(rate, str):
                rate = Decimal(rate)
            elif isinstance(rate, float):
                rate = Decimal(str(rate))
            elif isinstance(rate, Decimal):
                pass
            else:
                return False
            
            return rate > 0
        except (ValueError, InvalidOperation, TypeError):
            return False
    
    def validate_date_string(self, date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Validate date string format."""
        if not date_str or not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email address."""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return False
        
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, url))
    
    def validate_json_string(self, json_str: str) -> bool:
        """Validate JSON string format."""
        if not json_str or not isinstance(json_str, str):
            return False
        
        try:
            import json
            json.loads(json_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present."""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        return missing_fields
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        """Validate field types."""
        type_errors = []
        
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")
        
        return type_errors
    
    def validate_country_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete country data structure."""
        errors = []
        
        # Required fields
        required_fields = ['country_name', 'capitals', 'continent', 'currencies', 'is_un_member', 'population']
        missing_fields = self.validate_required_fields(data, required_fields)
        if missing_fields:
            errors.extend([f"Missing required fields: {', '.join(missing_fields)}"])
        
        # Validate individual fields
        if 'country_name' in data and not self.validate_country_name(data['country_name']):
            errors.append("Invalid country name")
        
        if 'capitals' in data and isinstance(data['capitals'], list):
            for capital in data['capitals']:
                if not self.validate_capital_name(capital):
                    errors.append(f"Invalid capital name: {capital}")
        
        if 'continent' in data and not self.validate_continent(data['continent']):
            errors.append("Invalid continent")
        
        if 'currencies' in data and isinstance(data['currencies'], list):
            for currency in data['currencies']:
                if not self.validate_currency_code(currency):
                    errors.append(f"Invalid currency code: {currency}")
        
        if 'population' in data and not self.validate_population(data['population']):
            errors.append("Invalid population")
        
        if 'timezones' in data and isinstance(data['timezones'], list):
            for timezone in data['timezones']:
                if not self.validate_timezone(timezone):
                    errors.append(f"Invalid timezone: {timezone}")
        
        return len(errors) == 0, errors
    
    def validate_currency_rate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate complete currency rate data structure."""
        errors = []
        
        # Required fields
        required_fields = ['country_name', 'currency_code', 'shekel_rate']
        missing_fields = self.validate_required_fields(data, required_fields)
        if missing_fields:
            errors.extend([f"Missing required fields: {', '.join(missing_fields)}"])
        
        # Validate individual fields
        if 'country_name' in data and not self.validate_country_name(data['country_name']):
            errors.append("Invalid country name")
        
        if 'currency_code' in data and not self.validate_currency_code(data['currency_code']):
            errors.append("Invalid currency code")
        
        if 'shekel_rate' in data and not self.validate_exchange_rate(data['shekel_rate']):
            errors.append("Invalid exchange rate")
        
        return len(errors) == 0, errors
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove control characters
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Truncate if too long
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def sanitize_country_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize country data."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, list):
                sanitized[key] = [self.sanitize_string(str(item)) if isinstance(item, str) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized


# Global validator instance
_validator = DataValidator()


def get_validator() -> DataValidator:
    """Get the global validator instance."""
    return _validator


def validate_country_name(name: str) -> bool:
    """Validate country name."""
    return _validator.validate_country_name(name)


def validate_currency_code(code: str) -> bool:
    """Validate currency code."""
    return _validator.validate_currency_code(code)


def validate_country_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate country data."""
    return _validator.validate_country_data(data)


def validate_currency_rate_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate currency rate data."""
    return _validator.validate_currency_rate_data(data)
