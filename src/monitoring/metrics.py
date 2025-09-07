from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Optional
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger("metrics")
settings = get_settings()

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

COUNTRIES_PROCESSED = Counter(
    'countries_processed_total',
    'Total number of countries processed'
)

CURRENCY_RATES_PROCESSED = Counter(
    'currency_rates_processed_total',
    'Total number of currency rates processed'
)

API_CALLS_TOTAL = Counter(
    'api_calls_total',
    'Total API calls made to external services',
    ['service', 'status']
)

PROCESSING_DURATION = Histogram(
    'processing_duration_seconds',
    'Processing duration in seconds',
    ['process_type']
)


class MetricsCollector:
    def __init__(self):
        self.metrics_enabled = settings.monitoring.metrics_enabled
        self.server_started = False
    
    def start_metrics_server(self):
        if self.metrics_enabled and not self.server_started:
            try:
                start_http_server(settings.monitoring.prometheus_port)
                self.server_started = True
                logger.info(f"Prometheus metrics server started on port {settings.monitoring.prometheus_port}")
            except Exception as e:
                logger.error(f"Failed to start metrics server: {e}")
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        if self.metrics_enabled:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_countries_processed(self, count: int):
        if self.metrics_enabled:
            COUNTRIES_PROCESSED.inc(count)
    
    def record_currency_rates_processed(self, count: int):
        if self.metrics_enabled:
            CURRENCY_RATES_PROCESSED.inc(count)
    
    def record_api_call(self, service: str, status: str):
        if self.metrics_enabled:
            API_CALLS_TOTAL.labels(service=service, status=status).inc()
    
    def record_processing_duration(self, process_type: str, duration: float):
        if self.metrics_enabled:
            PROCESSING_DURATION.labels(process_type=process_type).observe(duration)
    
    def set_database_connections(self, count: int):
        if self.metrics_enabled:
            DATABASE_CONNECTIONS.set(count)


metrics_collector = MetricsCollector()
