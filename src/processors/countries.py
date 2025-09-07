import asyncio
import pytz
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.processors.base import BaseDataProcessor, BaseAPIClient
from src.database.repositories import CountryRepository
from src.models.country import CountryCreate
from src.config.settings import get_settings


class CountriesAPIClient(BaseAPIClient):
    async def fetch_countries(self) -> Optional[List[Dict[str, Any]]]:
        url = self.settings.api.countries_url
        return await self._make_request(url)


class CountriesProcessor(BaseDataProcessor):
    def __init__(self):
        super().__init__()
        self.repository = CountryRepository()
        self.settings = get_settings()
        self.config = self.settings.api
        self.db = self.repository
    
    async def fetch_data(self) -> Optional[List[Dict[str, Any]]]:
        async with CountriesAPIClient() as client:
            return await client.fetch_countries()
    
    def fetch_countries_data(self) -> Optional[List[Dict[str, Any]]]:
        """Synchronous wrapper for fetch_data"""
        try:
            return asyncio.run(self.fetch_data())
        except Exception as e:
            self.logger.error(f"Error fetching countries data: {e}")
            return None
    
    def format_country_data(self, country_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format country data from API response"""
        country_create = self._format_country_data(country_data)
        if country_create:
            return country_create.model_dump()
        return {}
    
    def get_current_time_for_timezones(self, timezones: List[str]) -> Dict[str, str]:
        """Get current time for given timezones"""
        return self._get_current_time_for_timezones(timezones)
    
    def _get_current_time_for_timezones(self, timezones: List[str]) -> Dict[str, str]:
        current_times = {}
        
        if not timezones:
            return current_times
        
        for timezone_str in timezones:
            try:
                # Clean up timezone string
                if timezone_str.startswith('UTC'):
                    if timezone_str == 'UTC':
                        timezone_str = 'UTC'
                    else:
                        timezone_str = timezone_str.replace('UTC+', '+').replace('UTC-', '-')
                        if timezone_str in ['+00:00', '-00:00']:
                            timezone_str = 'UTC'
                
                try:
                    tz = pytz.timezone(timezone_str)
                except pytz.exceptions.UnknownTimeZoneError:
                    if timezone_str.startswith(('+', '-')) and ':' in timezone_str:
                        continue
                    else:
                        continue
                
                current_time = datetime.now(tz)
                current_times[timezone_str] = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                
            except Exception as e:
                self.logger.warning(f"Error processing timezone {timezone_str}: {e}")
                continue
        
        # Ensure we always return a proper dictionary, not empty
        return current_times if current_times else {}
    
    def _format_country_data(self, country: Dict[str, Any]) -> Optional[CountryCreate]:
        try:
            country_name = country.get('name', {}).get('common', '')
            if not country_name:
                return None
            
            capitals = country.get('capital', [])
            if not isinstance(capitals, list):
                capitals = [capitals] if capitals else []
            
            continent = country.get('continents', [''])[0] if country.get('continents') else ''
            
            currencies_dict = country.get('currencies', {})
            currencies = list(currencies_dict.keys()) if currencies_dict else []
            
            is_un_member = country.get('unMember', False)
            population = country.get('population', 0)
            
            timezones = country.get('timezones', [])
            current_time = self._get_current_time_for_timezones(timezones)
            
            return CountryCreate(
                country_name=country_name,
                capitals=capitals,
                continent=continent,
                currencies=currencies,
                is_un_member=is_un_member,
                population=population,
                timezone_info=current_time
            )
        except Exception as e:
            self.logger.error(f"Error formatting country data: {e}")
            return None
    
    async def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[CountryCreate]:
        transformed_data = []
        
        for country in raw_data:
            formatted = self._format_country_data(country)
            if formatted:
                transformed_data.append(formatted)
        
        return transformed_data
    
    async def save_data(self, transformed_data: List[CountryCreate]) -> bool:
        try:
            success_count = 0
            skipped_count = 0
            
            for country_data in transformed_data:
                existing = await self.repository.get_by_name(country_data.country_name)
                if existing:
                    skipped_count += 1
                    self.logger.debug(f"Country {country_data.country_name} already exists, skipping")
                    continue
                
                result = await self.repository.create(country_data)
                if result:
                    success_count += 1
                    self.logger.debug(f"Created country: {country_data.country_name}")
                else:
                    self.logger.warning(f"Failed to create country: {country_data.country_name}")
            
            self.logger.info(f"Successfully processed {success_count} countries, skipped {skipped_count} existing countries")
            # Return True if we processed any countries OR if all countries already existed (skipped_count > 0)
            return success_count > 0 or skipped_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to save countries data: {e}")
            return False
