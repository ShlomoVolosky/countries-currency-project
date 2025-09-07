"""
Monitoring middleware for FastAPI application
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .metrics import http_requests_total, http_request_duration_seconds


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics for Prometheus"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request information
        method = request.method
        endpoint = request.url.path
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(response.status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response
