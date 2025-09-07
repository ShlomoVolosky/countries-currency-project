# Countries Currency Project

A production-grade system for processing country and currency data from external APIs, with automated scheduling, monitoring, and data persistence.

## Features

- **Country Data Processing**: Fetches and processes country information from REST Countries API
- **Currency Rate Processing**: Retrieves and processes exchange rates from Frankfurter API
- **Automated Scheduling**: Configurable scheduling for data updates using APScheduler
- **Database Management**: PostgreSQL with migration support and connection pooling
- **Monitoring**: Health checks, metrics collection, and alerting
- **Docker Support**: Full containerization with Docker Compose
- **Airflow Integration**: Optional Apache Airflow for advanced workflow management
- **Production Ready**: Logging, error handling, retry mechanisms, and configuration management

## Architecture

```
├── src/
│   ├── main.py                          # Main application entry point
│   ├── config/                          # Configuration management
│   ├── models/                          # Data models
│   ├── processors/                      # Data processing logic
│   ├── database/                        # Database operations
│   ├── api/                            # External API clients
│   ├── utils/                          # Utility functions
│   ├── monitoring/                     # Health checks and metrics
│   └── scheduler/                      # Task scheduling
├── tests/                              # Test suite
├── scripts/                            # Deployment and maintenance scripts
├── monitoring/                         # Prometheus and Grafana configs
├── airflow/                           # Airflow DAGs and plugins
└── docker-compose.yml                 # Container orchestration
```

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd countries-currency-project/prod-version
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup database**
   ```bash
   bash scripts/setup_database.sh
   ```

6. **Run the application**
   ```bash
   python -m src.main setup    # Initial data load
   python -m src.main scheduler # Start automated scheduler
   ```

### Docker Deployment

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database**
   ```bash
   docker-compose exec app bash scripts/setup_database.sh
   ```

3. **Access services**
   - Application: http://localhost:8000
   - Airflow: http://localhost:8080
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_NAME` | Database name | countries_db |
| `DB_USER` | Database user | countries_user |
| `DB_PASSWORD` | Database password | (required) |
| `DB_PORT` | Database port | 5432 |
| `ENVIRONMENT` | Environment | development |
| `LOG_LEVEL` | Logging level | INFO |

### Configuration Files

- `config/development.yml` - Development settings
- `config/staging.yml` - Staging settings
- `config/production.yml` - Production settings
- `config/logging.yml` - Logging configuration

## Usage

### Command Line Interface

```bash
# Run initial data setup
python -m src.main setup

# Run countries data update
python -m src.main countries

# Run currency rates update
python -m src.main currency

# Start automated scheduler
python -m src.main scheduler
```

### Programmatic Usage

```python
from src.processors.country_processor import CountryProcessor
from src.processors.currency_processor import CurrencyProcessor

# Process countries data
country_processor = CountryProcessor()
country_processor.run()

# Process currency rates
currency_processor = CurrencyProcessor()
currency_processor.run()
```

## API Endpoints

### Health Check
- `GET /health` - Application health status
- `GET /health/detailed` - Detailed health information

### Data Endpoints
- `GET /countries` - List all countries
- `GET /countries/{name}` - Get country by name
- `GET /currencies` - List all currencies
- `GET /currencies/{code}` - Get currency by code
- `GET /rates` - List exchange rates
- `GET /rates/{country}` - Get rates for country

## Monitoring

### Health Checks

The application includes comprehensive health checks for:
- Database connectivity
- External API availability
- Application configuration
- System resources

### Metrics

Prometheus metrics are available at `/metrics`:
- Request counts and durations
- Database query performance
- API call success rates
- Processing statistics

### Dashboards

Grafana dashboards are provided for:
- Application performance
- Database metrics
- API usage statistics
- Error rates and trends

## Testing

### Run Tests

```bash
# Run all tests
bash scripts/run_tests.sh

# Run specific test categories
bash scripts/run_tests.sh --unit
bash scripts/run_tests.sh --integration
bash scripts/run_tests.sh --database

# Run with coverage
bash scripts/run_tests.sh --coverage --coverage-threshold 80
```

### Test Structure

```
tests/
├── test_processors/     # Processor tests
├── test_api/           # API client tests
├── test_database/      # Database tests
├── test_integration/   # Integration tests
└── fixtures/           # Test data
```

## Deployment

### Production Deployment

1. **Prepare environment**
   ```bash
   export ENVIRONMENT=production
   export DB_PASSWORD=your_secure_password
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Deploy manually**
   ```bash
   bash scripts/deploy.sh --environment production
   ```

### Database Management

```bash
# Backup database
bash scripts/backup_database.sh

# Restore database
bash scripts/backup_database.sh --restore backup_file.dump

# Cleanup old backups
bash scripts/backup_database.sh --cleanup
```

## Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### Adding New Features

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Run quality checks
5. Submit pull request

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials
   - Ensure PostgreSQL is running
   - Verify network connectivity

2. **API Rate Limiting**
   - Check API key configuration
   - Implement rate limiting
   - Use retry mechanisms

3. **Memory Issues**
   - Monitor memory usage
   - Implement data pagination
   - Optimize data processing

### Logs

Application logs are available in:
- `logs/application.log` - General application logs
- `logs/errors.log` - Error logs
- `logs/api_calls.log` - API call logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting guide

## Changelog

### Version 1.0.0
- Initial release
- Country data processing
- Currency rate processing
- Automated scheduling
- Database management
- Monitoring and health checks
- Docker support
- Airflow integration
