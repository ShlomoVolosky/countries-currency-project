"""
Prometheus metrics definitions for the Countries Currency Service
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable, Any
from fastapi import Request, Response

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Business Logic Metrics
countries_processed_total = Counter(
    'countries_processed_total',
    'Total number of countries processed',
    ['status']
)

currency_rates_processed_total = Counter(
    'currency_rates_processed_total',
    'Total number of currency rates processed',
    ['status']
)

api_calls_total = Counter(
    'api_calls_total',
    'Total number of API calls',
    ['service', 'status']
)

# System Metrics
active_connections = Gauge(
    'active_connections',
    'Number of active database connections'
)

# Application Info
app_info = Info(
    'app_info',
    'Application information'
)

# Set application info
app_info.info({
    'version': '1.0.0',
    'name': 'countries-currency-service'
})


def track_http_requests(func: Callable) -> Callable:
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request info if available
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            return await func(*args, **kwargs)
        
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Record error metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code='500'
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)
            
            raise
    
    return wrapper


def track_countries_processed(status: str = 'success'):
    """Track countries processing metrics"""
    countries_processed_total.labels(status=status).inc()


def track_currency_rates_processed(status: str = 'success'):
    """Track currency rates processing metrics"""
    currency_rates_processed_total.labels(status=status).inc()


def track_api_call(service: str, status: str = 'success'):
    """Track API call metrics"""
    api_calls_total.labels(service=service, status=status).inc()


def update_active_connections(count: int):
    """Update active database connections metric"""
    active_connections.set(count)
