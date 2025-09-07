"""
Country data processor for the Countries Currency Project.

This module provides functionality to fetch, process, and store
country data from the REST Countries API.
"""

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
    """Processor for country data operations."""
    
    def __init__(self):
        super().__init__()
        self.country_repo = get_country_repository()
        self.required_fields = ['name', 'capital', 'continents', 'currencies', 'unMember', 'population', 'timezones']
    
    def fetch_countries_data(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch countries data from REST Countries API."""
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
        """Validate country data structure."""
        errors = []
        
        # Check required fields
        missing_fields = self.validate_required_fields(country, self.required_fields)
        if missing_fields:
            errors.extend([f"Missing required fields: {', '.join(missing_fields)}"])
        
        # Validate data types
        field_types = {
            'name': dict,
            'capital': (list, type(None)),
            'continents': list,
            'currencies': (dict, type(None)),
            'unMember': bool,
            'population': (int, type(None)),
            'timezones': list
        }
        
        type_errors = self.validate_data_types(country, field_types)
        if type_errors:
            errors.extend(type_errors)
        
        return errors
    
    def format_country_data(self, country: Dict[str, Any]) -> Optional[CountryData]:
        """Format country data according to requirements."""
        try:
            # Validate data first
            validation_errors = self.validate_country_data(country)
            if validation_errors:
                self.logger.warning(f"Validation errors for country {country.get('name', {}).get('common', 'Unknown')}: {validation_errors}")
                # Continue processing with available data
            
            # Extract country name
            country_name = country.get('name', {}).get('common', '')
            if not country_name:
                self.logger.warning("Country name is empty, skipping")
                return None
            
            # Extract capitals
            capitals = country.get('capital', [])
            if not isinstance(capitals, list):
                capitals = [capitals] if capitals else []
            capitals = [self.sanitize_string(cap, 255) for cap in capitals if cap]
            
            # Extract continent
            continents = country.get('continents', [])
            continent = continents[0] if continents else ''
            continent = self.sanitize_string(continent, 255)
            
            # Extract currencies
            currencies_dict = country.get('currencies', {})
            currencies = []
            if isinstance(currencies_dict, dict):
                currencies = [self.sanitize_string(code, 3).upper() for code in currencies_dict.keys() if code]
            
            # Extract UN membership
            is_un_member = country.get('unMember', False)
            
            # Extract population
            population = country.get('population', 0)
            if not isinstance(population, int):
                population = 0
            population = max(0, population)  # Ensure non-negative
            
            # Extract timezones and get current time
            timezones = country.get('timezones', [])
            timezone_info = get_current_time_for_timezones(timezones)
            
            # Create country data object
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
        """Save country data to database."""
        try:
            # Convert to dictionary for database insertion
            data_dict = country_data.to_dict()
            
            # Insert into database
            country_id = self.country_repo.insert_country(data_dict)
            
            if country_id:
                self.record_success(country_data.country_name)
                return True
            else:
                self.logger.warning(f"Failed to save country: {country_data.country_name}")
                return False
                
        except Exception as e:
            self.handle_error(e, f"saving country {country_data.country_name}")
            return False
    
    def process_countries_batch(self, countries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of countries."""
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
            
            # Log progress
            country_name = country.get('name', {}).get('common', f'Country {i}')
            self.log_progress(i, len(countries), country_name)
            
            try:
                # Format country data
                country_data = self.format_country_data(country)
                if not country_data:
                    batch_stats['skipped'] += 1
                    continue
                
                # Save to database
                if self.save_country_data(country_data):
                    batch_stats['successful'] += 1
                else:
                    batch_stats['failed'] += 1
                    
            except Exception as e:
                self.handle_error(e, f"processing country {country_name}")
                batch_stats['failed'] += 1
        
        return batch_stats
    
    def process(self) -> bool:
        """Main processing method."""
        try:
            # Fetch countries data
            countries_data = self.fetch_countries_data()
            if not countries_data:
                self.logger.error("No countries data to process")
                return False
            
            # Process countries in batches
            batch_size = 50  # Process 50 countries at a time
            total_batches = (len(countries_data) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing {len(countries_data)} countries in {total_batches} batches")
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(countries_data))
                batch = countries_data[start_idx:end_idx]
                
                self.logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch)} countries)")
                
                batch_stats = self.process_countries_batch(batch)
                
                self.logger.info(
                    f"Batch {batch_num + 1} completed - "
                    f"Processed: {batch_stats['processed']}, "
                    f"Successful: {batch_stats['successful']}, "
                    f"Failed: {batch_stats['failed']}, "
                    f"Skipped: {batch_stats['skipped']}"
                )
            
            # Final statistics
            final_stats = self.get_processing_stats()
            self.logger.info(f"Country processing completed: {final_stats}")
            
            return self.success_count > 0
            
        except Exception as e:
            self.handle_error(e, "main country processing")
            return False
    
    def get_country_by_name(self, country_name: str) -> Optional[Dict[str, Any]]:
        """Get country by name from database."""
        return self.country_repo.get_country_by_name(country_name)
    
    def search_countries(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search countries with filters."""
        return self.country_repo.search_countries(filters)
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        stats = self.get_processing_stats()
        return {
            **stats,
            'countries_processed': self.processed_count,
            'countries_successful': self.success_count,
            'countries_failed': self.error_count
        }
