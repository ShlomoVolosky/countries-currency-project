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
        session = requests.Session()
        retry_strategy = Retry(
            total=self.settings.api.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
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
        return self._make_request('POST', endpoint, data=data, **kwargs)
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self._make_request('DELETE', endpoint, **kwargs)
    def health_check(self) -> bool:
        try:
            response = self.get('/health')
            return response is not None
        except Exception:
            return False
    def get_rate_limit_info(self) -> Optional[Dict[str, Any]]:
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
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        Test API connection.
        Returns:
            True if connection is successful, False otherwise