"""
Currency data processor for the Countries Currency Project.

This module provides functionality to fetch, process, and store
currency exchange rates from the Frankfurter API.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from decimal import Decimal
from datetime import date

from .base_processor import BaseProcessor, APIClientMixin, DataValidatorMixin
from database.connection import get_currency_rate_repository, get_country_repository
from models.currency import CurrencyRate, CurrencyRateCreate

logger = logging.getLogger(__name__)


class CurrencyProcessor(BaseProcessor, APIClientMixin, DataValidatorMixin):
    """Processor for currency rate operations."""
    
    def __init__(self):
        super().__init__()
        self.currency_repo = get_currency_rate_repository()
        self.country_repo = get_country_repository()
        self.supported_currencies: Optional[Set[str]] = None
    
    def get_supported_currencies(self) -> Set[str]:
        """Get list of currencies supported by Frankfurter API."""
        if self.supported_currencies is not None:
            return self.supported_currencies
        
        try:
            url = f"{self.settings.api.currency_url}/currencies"
            data = self.make_request(url)
            
            if data and isinstance(data, dict):
                self.supported_currencies = set(data.keys())
                self.logger.info(f"Fetched {len(self.supported_currencies)} supported currencies from API")
                return self.supported_currencies
            else:
                raise Exception("Invalid response from currencies API")
                
        except Exception as e:
            self.handle_error(e, "fetching supported currencies")
            # Fallback to known supported currencies
            self.supported_currencies = {
                'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP',
                'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR',
                'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK', 'SGD', 'THB', 'TRY', 'USD',
                'ZAR'
            }
            self.logger.warning(f"Using fallback currency list with {len(self.supported_currencies)} currencies")
            return self.supported_currencies
    
    def get_currency_rate(self, currency_code: str) -> Optional[float]:
        """Get ILS rate for a specific currency using Frankfurter API."""
        if currency_code == 'ILS':
            return 1.0
        
        # Check if currency is supported by Frankfurter API
        supported_currencies = self.get_supported_currencies()
        if currency_code not in supported_currencies:
            self.logger.warning(f"Currency {currency_code} not supported by Frankfurter API")
            return None
        
        try:
            # Frankfurter API endpoint for latest rates
            url = f"{self.settings.api.currency_url}/latest"
            params = {
                'from': 'ILS',
                'to': currency_code
            }
            
            data = self.make_request(url, params)
            if not data:
                return None
            
            # Return the rate (how much of target currency equals 1 ILS)
            rate = data.get('rates', {}).get(currency_code)
            if rate:
                return float(rate)
            else:
                # Try the reverse - from currency to ILS
                params = {
                    'from': currency_code,
                    'to': 'ILS'
                }
                data = self.make_request(url, params)
                if data:
                    rate = data.get('rates', {}).get('ILS')
                    if rate:
                        return float(rate)
            
        except Exception as e:
            self.handle_error(e, f"fetching rate for {currency_code}")
        
        return None
    
    def get_all_currency_rates(self) -> Dict[str, float]:
        """Get all currency rates TO ILS in one API call."""
        try:
            url = f"{self.settings.api.currency_url}/latest"
            params = {'from': 'ILS'}
            
            data = self.make_request(url, params)
            if not data:
                return {}
            
            rates = data.get('rates', {})
            # Add ILS to itself
            rates['ILS'] = 1.0
            
            # Invert the rates to get FROM each currency TO ILS
            # If 1 ILS = X USD, then 1 USD = 1/X ILS
            inverted_rates = {}
            for currency, rate in rates.items():
                if currency == 'ILS':
                    inverted_rates[currency] = 1.0
                else:
                    inverted_rates[currency] = 1.0 / rate
            
            self.logger.info(f"Successfully fetched rates for {len(inverted_rates)} currencies")
            return inverted_rates
            
        except Exception as e:
            self.handle_error(e, "fetching all currency rates")
            return {}
    
    def get_countries_with_currencies(self) -> List[Dict[str, Any]]:
        """Get all countries and their currencies from database."""
        try:
            countries = self.country_repo.get_countries_with_currencies()
            self.logger.info(f"Found {len(countries)} countries with currencies")
            return countries
        except Exception as e:
            self.handle_error(e, "fetching countries with currencies")
            return []
    
    def validate_currency_rate(self, country_name: str, currency_code: str, rate: float) -> bool:
        """Validate currency rate data."""
        if not country_name or not country_name.strip():
            self.logger.warning("Country name is empty")
            return False
        
        if not currency_code or len(currency_code) != 3:
            self.logger.warning(f"Invalid currency code: {currency_code}")
            return False
        
        if rate <= 0:
            self.logger.warning(f"Invalid rate {rate} for {currency_code}")
            return False
        
        return True
    
    def save_currency_rate(self, country_name: str, currency_code: str, rate: float) -> bool:
        """Save currency rate to database."""
        try:
            # Validate data
            if not self.validate_currency_rate(country_name, currency_code, rate):
                return False
            
            # Insert into database
            rate_id = self.currency_repo.insert_currency_rate(country_name, currency_code, rate)
            
            if rate_id:
                self.record_success(f"{country_name}-{currency_code}")
                return True
            else:
                self.logger.warning(f"Failed to save currency rate: {country_name}-{currency_code}")
                return False
                
        except Exception as e:
            self.handle_error(e, f"saving currency rate {country_name}-{currency_code}")
            return False
    
    def process_currency_rates_batch(self, countries: List[Dict[str, Any]], all_rates: Dict[str, float]) -> Dict[str, int]:
        """Process a batch of currency rates."""
        batch_stats = {
            'total_countries': len(countries),
            'total_currencies': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'unsupported': 0
        }
        
        supported_currencies = self.get_supported_currencies()
        
        for i, country in enumerate(countries, 1):
            country_name = country['country_name']
            currencies = country['currencies']
            
            self.log_progress(i, len(countries), country_name)
            
            if not currencies:
                self.logger.debug(f"No currencies for {country_name}")
                continue
            
            # Separate supported and unsupported currencies
            supported_country_currencies = [c for c in currencies if c in supported_currencies]
            unsupported_country_currencies = [c for c in currencies if c not in supported_currencies]
            
            if unsupported_country_currencies:
                self.logger.debug(f"Unsupported currencies for {country_name}: {unsupported_country_currencies}")
                batch_stats['unsupported'] += len(unsupported_country_currencies)
            
            for currency_code in currencies:
                batch_stats['total_currencies'] += 1
                self.processed_count += 1
                batch_stats['processed'] += 1
                
                if currency_code not in supported_currencies:
                    batch_stats['unsupported'] += 1
                    continue
                
                # Get the rate from the pre-fetched rates
                if currency_code in all_rates:
                    shekel_rate = all_rates[currency_code]
                    
                    if self.save_currency_rate(country_name, currency_code, shekel_rate):
                        batch_stats['successful'] += 1
                    else:
                        batch_stats['failed'] += 1
                else:
                    self.logger.warning(f"No rate found for {currency_code}")
                    batch_stats['failed'] += 1
        
        return batch_stats
    
    def process(self) -> bool:
        """Main processing method."""
        try:
            # Get countries with currencies
            countries = self.get_countries_with_currencies()
            if not countries:
                self.logger.warning("No countries with currencies found")
                return False
            
            # Get supported currencies
            supported_currencies = self.get_supported_currencies()
            self.logger.info(f"Frankfurter API supports {len(supported_currencies)} currencies")
            
            # Get all currency rates in one API call
            self.logger.info("Fetching all currency rates TO ILS from Frankfurter API...")
            all_rates = self.get_all_currency_rates()
            
            if not all_rates:
                self.logger.error("Failed to fetch currency rates")
                return False
            
            self.logger.info(f"Successfully fetched rates for {len(all_rates)} currencies")
            
            # Process countries in batches
            batch_size = 100  # Process 100 countries at a time
            total_batches = (len(countries) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing {len(countries)} countries in {total_batches} batches")
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(countries))
                batch = countries[start_idx:end_idx]
                
                self.logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch)} countries)")
                
                batch_stats = self.process_currency_rates_batch(batch, all_rates)
                
                self.logger.info(
                    f"Batch {batch_num + 1} completed - "
                    f"Countries: {batch_stats['total_countries']}, "
                    f"Currencies: {batch_stats['total_currencies']}, "
                    f"Processed: {batch_stats['processed']}, "
                    f"Successful: {batch_stats['successful']}, "
                    f"Failed: {batch_stats['failed']}, "
                    f"Unsupported: {batch_stats['unsupported']}"
                )
            
            # Final statistics
            final_stats = self.get_processing_stats()
            self.logger.info(f"Currency processing completed: {final_stats}")
            
            return self.success_count > 0
            
        except Exception as e:
            self.handle_error(e, "main currency processing")
            return False
    
    def get_latest_rates(self, country_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest currency rates."""
        return self.currency_repo.get_latest_rates(country_name)
    
    def get_rate_history(self, country_name: str, currency_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get rate history for a country and currency."""
        return self.currency_repo.get_rate_history(country_name, currency_code, days)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        stats = self.get_processing_stats()
        return {
            **stats,
            'currencies_processed': self.processed_count,
            'currencies_successful': self.success_count,
            'currencies_failed': self.error_count
        }
