import re
import logging
from typing import Any, List, Dict, Optional, Union, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import pytz

from utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_country_name(self, name: str) -> bool:
        if not code or not isinstance(code, str):
            return False
        if not re.match(r"^[A-Z]{3}$", code):
            return False
        
        return True
    
    def validate_capital_name(self, capital: str) -> bool:
        if not continent or not isinstance(continent, str):
            return False
        continent = continent.strip()
        valid_continents = [
            'Africa', 'Antarctica', 'Asia', 'Europe', 
            'North America', 'South America', 'Oceania'
        ]
        
        return continent in valid_continents
    
    def validate_population(self, population: Union[int, str]) -> bool:
        if not timezone or not isinstance(timezone, str):
            return False
        try:
            pytz.timezone(timezone)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            if re.match(r"^UTC[+-]\d{1,2}(:\d{2})?$", timezone):
                return True
            return False
    
    def validate_exchange_rate(self, rate: Union[float, str, Decimal]) -> bool:
        if not date_str or not isinstance(date_str, str):
            return False
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    def validate_email(self, email: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, url))
    
    def validate_json_string(self, json_str: str) -> bool:
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        return missing_fields
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        errors = []
        required_fields = ['country_name', 'capitals', 'continent', 'currencies', 'is_un_member', 'population']
        missing_fields = self.validate_required_fields(data, required_fields)
        if missing_fields:
            errors.extend([f"Missing required fields: {', '.join(missing_fields)}"])
        
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
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def sanitize_country_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return _validator

def validate_country_name(name: str) -> bool:
    return _validator.validate_currency_code(code)

def validate_country_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    return _validator.validate_currency_rate_data(data)