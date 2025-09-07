# Production Setup Guide

## Overview

This is a production-grade Countries Currency Exchange Service that fetches country data and currency exchange rates, converting them to Israeli Shekel (ILS).

## Architecture

### Services
- **FastAPI Application**: REST API with async/await patterns
- **PostgreSQL Database**: Data persistence with connection pooling
- **Apache Airflow**: Workflow orchestration and scheduling
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization and dashboards
- **Docker**: Containerization for all services

### Key Features
- **Pydantic v2 Models**: Type-safe data validation
- **Async/Await**: High-performance async operations
- **Abstract Classes**: Clean architecture with interfaces
- **Structured Logging**: Comprehensive logging system
- **Health Checks**: Service monitoring and health endpoints
- **Metrics**: Prometheus metrics for monitoring
- **API Documentation**: Auto-generated OpenAPI docs

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### 2. Environment Setup
Create `.env` file:
```bash
DB_HOST=postgres
DB_NAME=countries_db
DB_USER=countries_user
DB_PASSWORD=password123
DB_PORT=5432
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Airflow**: http://localhost:8080 (admin/admin)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## API Endpoints

### Countries
- `GET /api/v1/countries/` - List countries
- `GET /api/v1/countries/{id}` - Get country by ID
- `GET /api/v1/countries/search/{name}` - Search country by name

### Currencies
- `GET /api/v1/currencies/` - List currency rates
- `GET /api/v1/currencies/latest` - Get latest rates
- `GET /api/v1/currencies/convert/{currency}` - Convert to ILS

### Health
- `GET /api/v1/health/` - Health check

## Airflow DAGs

### Countries DAG
- **Schedule**: Weekly on Sunday at 2 AM
- **Purpose**: Fetch and update country data from REST Countries API

### Currencies DAG
- **Schedule**: Every 6 hours
- **Purpose**: Fetch and update currency exchange rates

### Combined DAG
- **Schedule**: Manual trigger
- **Purpose**: Run both countries and currencies processing

## Monitoring

### Prometheus Metrics
- HTTP request metrics
- Database connection metrics
- Processing duration metrics
- API call metrics

### Grafana Dashboards
- Service health overview
- Request rate and duration
- Processing statistics
- Error rates

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python main.py

# Run processors
python scripts/process_countries.py
python scripts/process_currencies.py

# Run tests
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Production Deployment

### Docker Compose
The `docker-compose.yml` includes all necessary services for production deployment.

### Environment Variables
Configure production environment variables:
- Database credentials
- API endpoints
- Logging levels
- Monitoring settings

### Scaling
- Use multiple API instances behind a load balancer
- Scale Airflow workers for parallel processing
- Configure database connection pooling

## Troubleshooting

### Common Issues
1. **Database Connection**: Check PostgreSQL service status
2. **API Errors**: Check application logs
3. **Airflow DAGs**: Check Airflow logs and DAG status
4. **Metrics**: Verify Prometheus configuration

### Logs
```bash
# Application logs
docker-compose logs app

# Database logs
docker-compose logs postgres

# Airflow logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

## Security Considerations

- Change default passwords
- Use environment variables for secrets
- Configure firewall rules
- Enable SSL/TLS in production
- Regular security updates

## Performance Optimization

- Database indexing
- Connection pooling
- Caching strategies
- Async processing
- Resource monitoring
