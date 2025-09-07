import time
import random
import logging
from functools import wraps
from typing import Callable, List, Type, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class RetryConfig:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0, 
                 jitter: bool = True, exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions


def retry_with_backoff(max_attempts: int = 3, base_delay: float = 1.0, 
                      max_delay: float = 60.0, exponential_base: float = 2.0, 
                      jitter: bool = True, exceptions: tuple = (Exception,),
                      on_retry: Optional[Callable] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    
                    delay = base_delay * (exponential_base ** attempt)
                    delay = min(delay, max_delay)
                    
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}. Retrying in {delay:.2f}s")
                    
                    if on_retry:
                        on_retry(attempt, e, delay)
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class RetryManager:
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def retry(self, func: Callable) -> Callable:
        return retry_with_backoff(
            max_attempts=self.config.max_attempts,
            base_delay=self.config.base_delay,
            max_delay=self.config.max_delay,
            exponential_base=self.config.exponential_base,
            jitter=self.config.jitter,
            exceptions=self.config.exceptions
        )(func)
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        decorated_func = self.retry(func)
        return decorated_func(*args, **kwargs)


def retry_on_exception(exceptions: tuple = (Exception,), max_attempts: int = 3):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}")
                    time.sleep(1)
            
            raise last_exception
        
        return wrapper
    return decorator