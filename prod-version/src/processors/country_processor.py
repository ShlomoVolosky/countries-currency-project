import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pytz

from .base_processor import BaseProcessor, APIClientMixin, DataValidatorMixin
from database.connection import get_country_repository
from utils.timezone_utils import get_current_time_for_timezones
from models.country import CountryData, CountryCreate

logger = logging.getLogger(__name__)


class CountryProcessor(BaseProcessor, APIClientMixin, DataValidatorMixin):
        self.logger.info("Fetching countries data from API...")
        try:
            data = self.make_request(self.settings.api.countries_url)
            if data:
                self.logger.info(f"Successfully fetched {len(data)} countries")
                return data
            else:
                self.logger.error("Failed to fetch countries data")
                return None
        except Exception as e:
            self.handle_error(e, "fetching countries data")
            return None
    
    def validate_country_data(self, country: Dict[str, Any]) -> List[str]:
        try:
            validation_errors = self.validate_country_data(country)
            if validation_errors:
                self.logger.warning(f"Validation errors for country {country.get('name', {}).get('common', 'Unknown')}: {validation_errors}")
            country_name = country.get('name', {}).get('common', '')
            if not country_name:
                self.logger.warning("Country name is empty, skipping")
                return None
            
            capitals = country.get('capital', [])
            if not isinstance(capitals, list):
                capitals = [capitals] if capitals else []
            capitals = [self.sanitize_string(cap, 255) for cap in capitals if cap]
            
            continents = country.get('continents', [])
            continent = continents[0] if continents else ''
            continent = self.sanitize_string(continent, 255)
            
            currencies_dict = country.get('currencies', {})
            currencies = []
            if isinstance(currencies_dict, dict):
                currencies = [self.sanitize_string(code, 3).upper() for code in currencies_dict.keys() if code]
            
            is_un_member = country.get('unMember', False)
            
            population = country.get('population', 0)
            if not isinstance(population, int):
                population = 0
            population = max(0, population)  # Ensure non-negative
            
            timezones = country.get('timezones', [])
            timezone_info = get_current_time_for_timezones(timezones)
            
            country_data = CountryData(
                country_name=self.sanitize_string(country_name, 255),
                capitals=capitals,
                continent=continent,
                currencies=currencies,
                is_un_member=is_un_member,
                population=population,
                timezone_info=timezone_info
            )
            
            return country_data
            
        except Exception as e:
            self.handle_error(e, f"formatting country data for {country.get('name', {}).get('common', 'Unknown')}")
            return None
    
    def save_country_data(self, country_data: CountryData) -> bool:
        batch_stats = {
            'total': len(countries),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        for i, country in enumerate(countries, 1):
            self.processed_count += 1
            batch_stats['processed'] += 1
            
            country_name = country.get('name', {}).get('common', f'Country {i}')
            self.log_progress(i, len(countries), country_name)
            
            try:
                country_data = self.format_country_data(country)
                if not country_data:
                    batch_stats['skipped'] += 1
                    continue
                
                if self.save_country_data(country_data):
                    batch_stats['successful'] += 1
                else:
                    batch_stats['failed'] += 1
                    
            except Exception as e:
                self.handle_error(e, f"processing country {country_name}")
                batch_stats['failed'] += 1
        
        return batch_stats
    
    def process(self) -> bool:
        return self.country_repo.get_country_by_name(country_name)
    def search_countries(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        stats = self.get_processing_stats()
        return {
            **stats,
            'countries_processed': self.processed_count,
            'countries_successful': self.success_count,
            'countries_failed': self.error_count
        }