"""
Base API client for the Countries Currency Project.

This module provides the base API client with common functionality
for making HTTP requests with retry logic and error handling.
"""

import logging
import time
from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import get_settings
from utils.retry import retry_with_backoff
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAPIClient(ABC):
    """Base API client with common functionality."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry configuration."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.settings.api.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'Countries-Currency-Project/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    @retry_with_backoff(max_attempts=3, base_delay=1)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data or None if error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except ValueError:
                self.logger.warning(f"Response is not valid JSON: {response.text[:100]}")
                return {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in request: {e}")
            return None
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        return self._make_request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        return self._make_request('POST', endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Make PUT request."""
        return self._make_request('PUT', endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def health_check(self) -> bool:
        """
        Check if the API is healthy.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.get('/health')
            return response is not None
        except Exception:
            return False
    
    def get_rate_limit_info(self) -> Optional[Dict[str, Any]]:
        """
        Get rate limit information from response headers.
        
        Returns:
            Rate limit information or None
        """
        try:
            response = self.session.head(self.base_url)
            headers = response.headers
            
            rate_limit_info = {}
            
            if 'X-RateLimit-Limit' in headers:
                rate_limit_info['limit'] = int(headers['X-RateLimit-Limit'])
            
            if 'X-RateLimit-Remaining' in headers:
                rate_limit_info['remaining'] = int(headers['X-RateLimit-Remaining'])
            
            if 'X-RateLimit-Reset' in headers:
                rate_limit_info['reset'] = int(headers['X-RateLimit-Reset'])
            
            return rate_limit_info if rate_limit_info else None
            
        except Exception as e:
            self.logger.warning(f"Could not get rate limit info: {e}")
            return None
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
            self.logger.debug("HTTP session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass
