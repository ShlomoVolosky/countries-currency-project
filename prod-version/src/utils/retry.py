import time
import random
import logging
from typing import Callable, Any, Optional, Union, List, Type
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetryConfig:
    Decorator for retrying functions with exponential backoff.
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to catch and retry
        on_retry: Callback function called on each retry
    delay = base_delay * (exponential_base ** attempt)
    delay = min(delay, max_delay)
    
    if jitter:
        jitter_amount = delay * 0.1  # 10% jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    return max(0, delay)


class RetryManager:
        last_exception = None
        start_time = time.time()
        for attempt in range(self.config.max_attempts):
            self.stats['total_attempts'] += 1
            
            try:
                result = func(*args, **kwargs)
                self.stats['successful_attempts'] += 1
                return result
            except exceptions as e:
                last_exception = e
                self.stats['failed_attempts'] += 1
                
                if attempt == self.config.max_attempts - 1:
                    logger.error(f"Function {func.__name__} failed after {self.config.max_attempts} attempts: {e}")
                    raise e
                
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=self.config.base_delay,
                    max_delay=self.config.max_delay,
                    exponential_base=self.config.exponential_base,
                    jitter=self.config.jitter
                )
                
                self.stats['total_delay'] += delay
                
                logger.warning(
                    f"Function {func.__name__} failed (attempt {attempt + 1}/{self.config.max_attempts}): {e}. "
                    f"Retrying in {delay:.2f}s"
                )
                
                if on_retry:
                    on_retry(attempt, e, delay)
                
                time.sleep(delay)
        
        raise last_exception
    
    def get_stats(self) -> dict:
        self.stats = {
            'total_attempts': 0,
            'successful_attempts': 0,
            'failed_attempts': 0,
            'total_delay': 0.0
        }

def retry_on_network_error(
    max_attempts: int = 3,
    base_delay: float = 1.0
):
    import psycopg2
    database_exceptions = (
        psycopg2.OperationalError,
        psycopg2.InterfaceError,
        psycopg2.DatabaseError
    )
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        exceptions=database_exceptions
    )


def retry_with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: Type[Exception] = Exception
):