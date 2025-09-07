"""
Frankfurter API client for the Countries Currency Project.

This module provides functionality to interact with the Frankfurter API
for fetching currency exchange rates.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime

from .base_api import BaseAPIClient
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FrankfurterAPIClient(BaseAPIClient):
    """Client for Frankfurter API."""
    
    def __init__(self):
        settings = get_settings()
        super().__init__(settings.api.currency_url)
        self.logger = get_logger(__name__)
    
    def test_connection(self) -> bool:
        """Test connection to Frankfurter API."""
        try:
            # Try to fetch latest rates
            data = self.get_latest_rates()
            return data is not None
        except Exception as e:
            self.logger.error(f"Frankfurter API connection test failed: {e}")
            return False
    
    def get_latest_rates(self, base_currency: str = 'EUR') -> Optional[Dict[str, Any]]:
        """
        Get latest exchange rates.
        
        Args:
            base_currency: Base currency for rates (default: EUR)
            
        Returns:
            Latest rates data or None if error
        """
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
        """
        Get exchange rates for a specific date.
        
        Args:
            target_date: Date to get rates for
            base_currency: Base currency for rates
            
        Returns:
            Rates data for the date or None if error
        """
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
        """
        Get exchange rates for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            base_currency: Base currency for rates
            
        Returns:
            Rates data for the period or None if error
        """
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
        """
        Get list of supported currencies.
        
        Returns:
            Dictionary mapping currency codes to names or None if error
        """
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
        """
        Convert currency amount.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            date: Optional date for conversion (default: latest)
            
        Returns:
            Conversion result or None if error
        """
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
        """
        Get exchange rate from a currency to ILS.
        
        Args:
            currency: Source currency code
            target_date: Optional date for rate (default: latest)
            
        Returns:
            Exchange rate or None if error
        """
        try:
            if currency == 'ILS':
                return 1.0
            
            # Try direct conversion
            conversion = self.convert_currency(1.0, 'ILS', currency, target_date)
            if conversion and 'result' in conversion:
                return conversion['result']
            
            # Try reverse conversion
            conversion = self.convert_currency(1.0, currency, 'ILS', target_date)
            if conversion and 'result' in conversion:
                return 1.0 / conversion['result']
            
            self.logger.warning(f"Could not get rate for {currency} to ILS")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting rate for {currency} to ILS: {e}")
            return None
    
    def get_all_rates_to_ils(self, target_date: Optional[date] = None) -> Optional[Dict[str, float]]:
        """
        Get all exchange rates to ILS.
        
        Args:
            target_date: Optional date for rates (default: latest)
            
        Returns:
            Dictionary of currency rates to ILS or None if error
        """
        try:
            # Get latest rates with ILS as base
            rates_data = self.get_latest_rates('ILS') if not target_date else self.get_rates_for_date(target_date, 'ILS')
            
            if not rates_data or 'rates' not in rates_data:
                return None
            
            rates = rates_data['rates']
            
            # Add ILS to itself
            rates['ILS'] = 1.0
            
            # Invert rates to get FROM each currency TO ILS
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
        """
        Validate currency code format.
        
        Args:
            currency: Currency code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not currency or not isinstance(currency, str):
            return False
        
        return len(currency) == 3 and currency.isalpha() and currency.isupper()
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get information about the API.
        
        Returns:
            Dictionary with API information
        """
        return {
            'name': 'Frankfurter API',
            'base_url': self.base_url,
            'description': 'Free API for currency exchange rates',
            'supported_currencies': self.get_supported_currencies(),
            'rate_limit': self.get_rate_limit_info()
        }
