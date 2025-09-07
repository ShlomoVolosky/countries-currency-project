import logging
from typing import List, Dict, Any, Optional, Set
from decimal import Decimal
from datetime import date

from .base_processor import BaseProcessor, APIClientMixin, DataValidatorMixin
from database.connection import get_currency_rate_repository, get_country_repository
from models.currency import CurrencyRate, CurrencyRateCreate

logger = logging.getLogger(__name__)


class CurrencyProcessor(BaseProcessor, APIClientMixin, DataValidatorMixin):
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
            self.supported_currencies = {
                'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP',
                'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR',
                'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK', 'SGD', 'THB', 'TRY', 'USD',
                'ZAR'
            }
            self.logger.warning(f"Using fallback currency list with {len(self.supported_currencies)} currencies")
            return self.supported_currencies
    
    def get_currency_rate(self, currency_code: str) -> Optional[float]:
        try:
            url = f"{self.settings.api.currency_url}/latest"
            params = {'from': 'ILS'}
            data = self.make_request(url, params)
            if not data:
                return {}
            
            rates = data.get('rates', {})
            rates['ILS'] = 1.0
            
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
        return self.currency_repo.get_latest_rates(country_name)
    def get_rate_history(self, country_name: str, currency_code: str, days: int = 30) -> List[Dict[str, Any]]:
        stats = self.get_processing_stats()
        return {
            **stats,
            'currencies_processed': self.processed_count,
            'currencies_successful': self.success_count,
            'currencies_failed': self.error_count
        }