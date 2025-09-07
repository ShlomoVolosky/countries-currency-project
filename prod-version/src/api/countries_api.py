"""
REST Countries API client for the Countries Currency Project.

This module provides functionality to interact with the REST Countries API
for fetching country data.
"""

import logging
from typing import Optional, List, Dict, Any

from .base_api import BaseAPIClient
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CountriesAPIClient(BaseAPIClient):
    """Client for REST Countries API."""
    
    def __init__(self):
        settings = get_settings()
        super().__init__(settings.api.countries_url)
        self.logger = get_logger(__name__)
    
    def test_connection(self) -> bool:
        """Test connection to REST Countries API."""
        try:
            # Try to fetch a small sample of countries
            data = self.get_all_countries(limit=1)
            return data is not None and len(data) > 0
        except Exception as e:
            self.logger.error(f"Countries API connection test failed: {e}")
            return False
    
    def get_all_countries(self, limit: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get all countries from the API.
        
        Args:
            limit: Optional limit on number of countries to fetch
            
        Returns:
            List of country data or None if error
        """
        try:
            self.logger.info("Fetching all countries from REST Countries API")
            
            # The API endpoint already includes the fields we need
            data = self.get('/')
            
            if data and isinstance(data, list):
                if limit:
                    data = data[:limit]
                
                self.logger.info(f"Successfully fetched {len(data)} countries")
                return data
            else:
                self.logger.error("Invalid response format from countries API")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching countries: {e}")
            return None
    
    def get_country_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get country by name.
        
        Args:
            name: Country name
            
        Returns:
            Country data or None if not found
        """
        try:
            self.logger.info(f"Fetching country by name: {name}")
            
            data = self.get(f'/name/{name}')
            
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
            else:
                self.logger.warning(f"Country not found: {name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching country {name}: {e}")
            return None
    
    def get_countries_by_region(self, region: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get countries by region.
        
        Args:
            region: Region name (e.g., 'Asia', 'Europe')
            
        Returns:
            List of country data or None if error
        """
        try:
            self.logger.info(f"Fetching countries by region: {region}")
            
            data = self.get(f'/region/{region}')
            
            if data and isinstance(data, list):
                self.logger.info(f"Found {len(data)} countries in region {region}")
                return data
            else:
                self.logger.warning(f"No countries found in region: {region}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching countries by region {region}: {e}")
            return None
    
    def get_countries_by_currency(self, currency: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get countries that use a specific currency.
        
        Args:
            currency: Currency code (e.g., 'USD', 'EUR')
            
        Returns:
            List of country data or None if error
        """
        try:
            self.logger.info(f"Fetching countries by currency: {currency}")
            
            data = self.get(f'/currency/{currency}')
            
            if data and isinstance(data, list):
                self.logger.info(f"Found {len(data)} countries using currency {currency}")
                return data
            else:
                self.logger.warning(f"No countries found using currency: {currency}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching countries by currency {currency}: {e}")
            return None
    
    def search_countries(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Search countries by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching country data or None if error
        """
        try:
            self.logger.info(f"Searching countries with query: {query}")
            
            data = self.get(f'/name/{query}')
            
            if data and isinstance(data, list):
                self.logger.info(f"Found {len(data)} countries matching query: {query}")
                return data
            else:
                self.logger.warning(f"No countries found matching query: {query}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error searching countries with query {query}: {e}")
            return None
    
    def get_supported_fields(self) -> List[str]:
        """
        Get list of supported fields for the API.
        
        Returns:
            List of supported field names
        """
        return [
            'name',
            'capital',
            'continents',
            'currencies',
            'unMember',
            'population',
            'timezones',
            'region',
            'subregion',
            'languages',
            'flags',
            'area',
            'borders'
        ]
    
    def validate_country_data(self, country: Dict[str, Any]) -> bool:
        """
        Validate country data structure.
        
        Args:
            country: Country data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'capital', 'continents', 'currencies', 'unMember', 'population', 'timezones']
        
        for field in required_fields:
            if field not in country:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate name structure
        if not isinstance(country.get('name'), dict) or 'common' not in country['name']:
            self.logger.warning("Invalid name structure")
            return False
        
        # Validate other field types
        if not isinstance(country.get('continents'), list):
            self.logger.warning("Continents should be a list")
            return False
        
        if not isinstance(country.get('currencies'), dict):
            self.logger.warning("Currencies should be a dictionary")
            return False
        
        if not isinstance(country.get('unMember'), bool):
            self.logger.warning("unMember should be a boolean")
            return False
        
        if not isinstance(country.get('population'), int):
            self.logger.warning("Population should be an integer")
            return False
        
        if not isinstance(country.get('timezones'), list):
            self.logger.warning("Timezones should be a list")
            return False
        
        return True
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get information about the API.
        
        Returns:
            Dictionary with API information
        """
        return {
            'name': 'REST Countries API',
            'base_url': self.base_url,
            'version': 'v3.1',
            'description': 'REST API for country information',
            'supported_fields': self.get_supported_fields(),
            'rate_limit': self.get_rate_limit_info()
        }
