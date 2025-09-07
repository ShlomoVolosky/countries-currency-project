"""
Retry mechanisms for the Countries Currency Project.

This module provides retry functionality with exponential backoff
and various retry strategies for robust error handling.
"""

import time
import random
import logging
from typing import Callable, Any, Optional, Union, List, Type
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        backoff_multiplier: float = 1.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.backoff_multiplier = backoff_multiplier


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], tuple] = Exception,
    on_retry: Optional[Callable] = None
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to catch and retry
        on_retry: Callback function called on each retry
    """
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
                    
                    # Calculate delay
                    delay = calculate_delay(
                        attempt=attempt,
                        base_delay=base_delay,
                        max_delay=max_delay,
                        exponential_base=exponential_base,
                        jitter=jitter
                    )
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e, delay)
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def calculate_delay(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> float:
    """Calculate delay for retry attempt."""
    # Exponential backoff: base_delay * (exponential_base ^ attempt)
    delay = base_delay * (exponential_base ** attempt)
    
    # Cap at max_delay
    delay = min(delay, max_delay)
    
    # Add jitter to prevent thundering herd
    if jitter:
        jitter_amount = delay * 0.1  # 10% jitter
        delay += random.uniform(-jitter_amount, jitter_amount)
    
    # Ensure non-negative delay
    return max(0, delay)


class RetryManager:
    """Manager for retry operations with different strategies."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.stats = {
            'total_attempts': 0,
            'successful_attempts': 0,
            'failed_attempts': 0,
            'total_delay': 0.0
        }
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        exceptions: Union[Type[Exception], tuple] = Exception,
        on_retry: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic."""
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
                
                # Calculate delay
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
                
                # Call retry callback if provided
                if on_retry:
                    on_retry(attempt, e, delay)
                
                time.sleep(delay)
        
        # This should never be reached
        raise last_exception
    
    def get_stats(self) -> dict:
        """Get retry statistics."""
        duration = time.time() - getattr(self, '_start_time', time.time())
        return {
            **self.stats,
            'duration_seconds': duration,
            'success_rate': (
                self.stats['successful_attempts'] / self.stats['total_attempts'] * 100
                if self.stats['total_attempts'] > 0 else 0
            )
        }
    
    def reset_stats(self):
        """Reset retry statistics."""
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
    """Decorator for retrying on network-related errors."""
    import requests
    
    network_exceptions = (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException
    )
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        exceptions=network_exceptions
    )


def retry_on_database_error(
    max_attempts: int = 3,
    base_delay: float = 1.0
):
    """Decorator for retrying on database-related errors."""
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
    """Decorator implementing circuit breaker pattern."""
    def decorator(func: Callable) -> Callable:
        state = {
            'failures': 0,
            'last_failure_time': None,
            'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        }
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            # Check if circuit is open
            if state['state'] == 'OPEN':
                if (state['last_failure_time'] and 
                    current_time - state['last_failure_time'] > recovery_timeout):
                    state['state'] = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset failures and close circuit
                if state['state'] == 'HALF_OPEN':
                    state['state'] = 'CLOSED'
                state['failures'] = 0
                
                return result
                
            except expected_exception as e:
                state['failures'] += 1
                state['last_failure_time'] = current_time
                
                if state['failures'] >= failure_threshold:
                    state['state'] = 'OPEN'
                    logger.error(f"Circuit breaker opened for {func.__name__}")
                
                raise e
        
        return wrapper
    return decorator
