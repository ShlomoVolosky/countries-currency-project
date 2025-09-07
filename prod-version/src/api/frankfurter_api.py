import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime

from .base_api import BaseAPIClient
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FrankfurterAPIClient(BaseAPIClient):
        try:
            data = self.get_latest_rates()
            return data is not None
        except Exception as e:
            self.logger.error(f"Frankfurter API connection test failed: {e}")
            return False
    def get_latest_rates(self, base_currency: str = 'EUR') -> Optional[Dict[str, Any]]:
        try:
            self.logger.info(f"Fetching latest rates with base currency: {base_currency}")
            data = self.get('/latest', params={'from': base_currency})
            
            if data and 'rates' in data:
                self.logger.info(f"Successfully fetched rates for {len(data['rates'])} currencies")
                return data
            else:
                self.logger.error("Invalid response format from Frankfurter API")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching latest rates: {e}")
            return None
    
    def get_rates_for_date(self, target_date: date, base_currency: str = 'EUR') -> Optional[Dict[str, Any]]:
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            self.logger.info(f"Fetching rates for date: {date_str}")
            data = self.get(f'/{date_str}', params={'from': base_currency})
            
            if data and 'rates' in data:
                self.logger.info(f"Successfully fetched rates for {date_str}")
                return data
            else:
                self.logger.warning(f"No rates found for date: {date_str}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching rates for date {target_date}: {e}")
            return None
    
    def get_rates_for_period(
        self,
        start_date: date,
        end_date: date,
        base_currency: str = 'EUR'
    ) -> Optional[Dict[str, Any]]:
        try:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            self.logger.info(f"Fetching rates for period: {start_str} to {end_str}")
            data = self.get(
                f'/{start_str}..{end_str}',
                params={'from': base_currency}
            )
            
            if data and 'rates' in data:
                self.logger.info(f"Successfully fetched rates for period")
                return data
            else:
                self.logger.warning(f"No rates found for period: {start_str} to {end_str}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching rates for period: {e}")
            return None
    
    def get_supported_currencies(self) -> Optional[Dict[str, str]]:
        try:
            self.logger.info("Fetching supported currencies")
            data = self.get('/currencies')
            
            if data and isinstance(data, dict):
                self.logger.info(f"Successfully fetched {len(data)} supported currencies")
                return data
            else:
                self.logger.error("Invalid response format for currencies")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching supported currencies: {e}")
            return None
    
    def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            params = {
                'amount': amount,
                'from': from_currency,
                'to': to_currency
            }
            if date:
                date_str = date.strftime('%Y-%m-%d')
                endpoint = f'/{date_str}'
            else:
                endpoint = '/latest'
            
            self.logger.info(f"Converting {amount} {from_currency} to {to_currency}")
            
            data = self.get(endpoint, params=params)
            
            if data and 'result' in data:
                self.logger.info(f"Conversion successful: {data['result']} {to_currency}")
                return data
            else:
                self.logger.warning(f"Conversion failed for {amount} {from_currency} to {to_currency}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting currency: {e}")
            return None
    
    def get_rate_to_ils(self, currency: str, target_date: Optional[date] = None) -> Optional[float]:
        try:
            if currency == 'ILS':
                return 1.0
            conversion = self.convert_currency(1.0, 'ILS', currency, target_date)
            if conversion and 'result' in conversion:
                return conversion['result']
            
            conversion = self.convert_currency(1.0, currency, 'ILS', target_date)
            if conversion and 'result' in conversion:
                return 1.0 / conversion['result']
            
            self.logger.warning(f"Could not get rate for {currency} to ILS")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting rate for {currency} to ILS: {e}")
            return None
    
    def get_all_rates_to_ils(self, target_date: Optional[date] = None) -> Optional[Dict[str, float]]:
        try:
            rates_data = self.get_latest_rates('ILS') if not target_date else self.get_rates_for_date(target_date, 'ILS')
            if not rates_data or 'rates' not in rates_data:
                return None
            
            rates = rates_data['rates']
            
            rates['ILS'] = 1.0
            
            inverted_rates = {}
            for currency, rate in rates.items():
                if currency == 'ILS':
                    inverted_rates[currency] = 1.0
                else:
                    inverted_rates[currency] = 1.0 / rate
            
            self.logger.info(f"Successfully calculated rates for {len(inverted_rates)} currencies to ILS")
            return inverted_rates
            
        except Exception as e:
            self.logger.error(f"Error getting all rates to ILS: {e}")
            return None
    
    def validate_currency_code(self, currency: str) -> bool:
        if not currency or not isinstance(currency, str):
            return False
        return len(currency) == 3 and currency.isalpha() and currency.isupper()
    
    def get_api_info(self) -> Dict[str, Any]:
        return {
            'name': 'Frankfurter API',
            'base_url': self.base_url,
            'description': 'Free API for currency exchange rates',
            'supported_currencies': self.get_supported_currencies(),
            'rate_limit': self.get_rate_limit_info()
        }