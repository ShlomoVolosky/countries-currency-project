import re
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation


class DataValidator:
    def __init__(self):
        self.country_name_pattern = re.compile(r'^[a-zA-Z\s\-\'\.]+$')
        self.currency_code_pattern = re.compile(r'^[A-Z]{3}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    def validate_country_name(self, name: str) -> bool:
        if not isinstance(name, str):
            return False
        if not name.strip():
            return False
        if len(name) > 255:
            return False
        return bool(self.country_name_pattern.match(name.strip()))
    
    def validate_currency_code(self, code: str) -> bool:
        if not isinstance(code, str):
            return False
        return bool(self.currency_code_pattern.match(code.strip()))
    
    def validate_email(self, email: str) -> bool:
        if not isinstance(email, str):
            return False
        return bool(self.email_pattern.match(email.strip()))
    
    def validate_url(self, url: str) -> bool:
        if not isinstance(url, str):
            return False
        return bool(self.url_pattern.match(url.strip()))
    
    def validate_population(self, population: Union[int, str]) -> bool:
        try:
            pop = int(population)
            return 0 <= pop <= 10_000_000_000
        except (ValueError, TypeError):
            return False
    
    def validate_latitude(self, lat: Union[float, str]) -> bool:
        try:
            latitude = float(lat)
            return -90 <= latitude <= 90
        except (ValueError, TypeError):
            return False
    
    def validate_longitude(self, lon: Union[float, str]) -> bool:
        try:
            longitude = float(lon)
            return -180 <= longitude <= 180
        except (ValueError, TypeError):
            return False
    
    def validate_decimal(self, value: Union[float, str, Decimal], 
                        min_value: Optional[float] = None, 
                        max_value: Optional[float] = None) -> bool:
        try:
            decimal_value = Decimal(str(value))
            if min_value is not None and decimal_value < Decimal(str(min_value)):
                return False
            if max_value is not None and decimal_value > Decimal(str(max_value)):
                return False
            return True
        except (ValueError, TypeError, InvalidOperation):
            return False
    
    def validate_date_string(self, date_str: str) -> bool:
        try:
            from datetime import datetime
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_iso_code(self, code: str, length: int = 2) -> bool:
        if not isinstance(code, str):
            return False
        pattern = re.compile(f'^[A-Z]{{{length}}}$')
        return bool(pattern.match(code.strip()))
    
    def validate_phone_number(self, phone: str) -> bool:
        if not isinstance(phone, str):
            return False
        pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        return bool(pattern.match(phone.strip()))
    
    def validate_json_string(self, json_str: str) -> bool:
        try:
            import json
            json.loads(json_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_list_of_strings(self, data: List[str]) -> bool:
        if not isinstance(data, list):
            return False
        return all(isinstance(item, str) and item.strip() for item in data)
    
    def validate_dict_keys(self, data: Dict[str, Any], required_keys: List[str]) -> bool:
        if not isinstance(data, dict):
            return False
        return all(key in data for key in required_keys)
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        if not isinstance(value, str):
            return str(value)
        
        value = value.strip()
        
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    def sanitize_country_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        
        if 'name' in data:
            sanitized['name'] = self.sanitize_string(data['name'], 255)
        
        if 'capital' in data and isinstance(data['capital'], list):
            sanitized['capital'] = [self.sanitize_string(cap, 255) for cap in data['capital']]
        
        if 'continent' in data:
            sanitized['continent'] = self.sanitize_string(data['continent'], 255)
        
        if 'currencies' in data and isinstance(data['currencies'], dict):
            sanitized['currencies'] = list(data['currencies'].keys())
        
        if 'population' in data:
            try:
                sanitized['population'] = int(data['population'])
            except (ValueError, TypeError):
                sanitized['population'] = None
        
        if 'timezones' in data and isinstance(data['timezones'], list):
            sanitized['timezones'] = [self.sanitize_string(tz, 50) for tz in data['timezones']]
        
        return sanitized


_validator = DataValidator()


def get_validator() -> DataValidator:
    return _validator


def validate_country_name(name: str) -> bool:
    return _validator.validate_country_name(name)


def validate_currency_code(code: str) -> bool:
    return _validator.validate_currency_code(code)