# Countries Data Processing Project

This project fetches country data from REST Countries API, processes currency exchange rates, and stores the information in a PostgreSQL database with automated scheduling capabilities.

## Features

- **Part 1**: Fetch and process countries data including names, capitals, continents, currencies, UN membership, population, and current times by timezone
- **Part 2**: Fetch currency exchange rates relative to Israeli Shekel (ILS) for all countries' currencies
- **Part 3**: Automated scheduling system for periodic data updates

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Zorin OS (or any Debian/Ubuntu-based Linux distribution)

## Installation Instructions

### 1. Install PostgreSQL on Zorin OS

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE countries_db;
CREATE USER countries_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE countries_db TO countries_user;
\q
```

### 3. Setup Project

```bash
# Clone or create project directory
mkdir countries-project
cd countries-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install psycopg2-binary requests schedule pytest python-dotenv pytz
```

### 4. Configure Environment

Create `.env` file in project root:
```bash
DB_HOST=localhost
DB_NAME=countries_db
DB_USER=countries_user
DB_PASSWORD=your_password_here
DB_PORT=5432
```

### 5. Create Database Tables

```bash
# Create tables using the provided SQL script
psql -U countries_user -d countries_db -h localhost -f sql/create_tables.sql
```

## Project Structure

```
countries-project/
├── .env                     # Environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── config.py          # Configuration management
│   ├── database.py        # Database operations
│   ├── part1_countries.py # Countries data processing
│   ├── part2_currencies.py # Currency rates processing
│   └── part3_scheduler.py # Automated scheduling
├── tests/                 # Test files
│   ├── test_db_connection.py
│   ├── test_part1.py
│   ├── test_part2.py
│   └── test_part3.py
└── sql/
    └── create_tables.sql  # Database schema
```

## Usage

### Running Individual Components

1. **Process Countries Data (Part 1)**:
   ```bash
   python src/part1_countries.py
   ```

2. **Process Currency Rates (Part 2)**:
   ```bash
   python src/part2_currencies.py
   ```

3. **Run Automated Scheduler (Part 3)**:
   ```bash
   python src/part3_scheduler.py
   ```

### Scheduler Options

When running the scheduler, you'll see these options:
- **Option 1**: Run initial setup (loads all data immediately)
- **Option 2**: Start automated scheduler (runs updates on schedule)
- **Option 3**: Run countries update only
- **Option 4**: Run currency update only

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_db_connection.py -v
pytest tests/test_part1.py -v
pytest tests/test_part2.py -v
pytest tests/test_part3.py -v
```

## Scheduled Updates

The automated scheduler runs:
- **Countries Data**: Weekly on Sunday at 02:00 (countries data changes infrequently)
- **Currency Rates**: Every 6 hours (exchange rates change frequently)

## Database Schema

### Countries Table
- `country_name`: Name of the country
- `capitals`: Array of capital cities
- `continent`: Continent where country is located
- `currencies`: Array of currency codes
- `is_un_member`: Boolean indicating UN membership
- `population`: Country population
- `current_time`: JSON object with timezone information
- `created_at`, `updated_at`: Timestamps

### Currency Rates Table
- `country_name`: Name of the country
- `currency_code`: Currency code (e.g., USD, EUR)
- `shekel_rate`: Exchange rate relative to ILS
- `rate_date`: Date of the rate
- `created_at`: Timestamp

## APIs Used

1. **REST Countries API**: https://restcountries.com/v3.1/all
   - Provides comprehensive country information
   
2. **Frankfurter API**: https://api.frankfurter.app
   - Provides currency exchange rates

## Architecture Design

### Data Flow
1. **Countries Data**: REST Countries API → Data Processing → PostgreSQL
2. **Currency Rates**: Database (countries) → Frankfurter API → Data Processing → PostgreSQL
3. **Scheduling**: Automated cron-like scheduler manages both workflows

### Key Components
- **Configuration Management**: Centralized config with environment variables
- **Database Layer**: PostgreSQL with connection pooling and error handling
- **API Clients**: HTTP clients with retry logic and error handling
- **Scheduler**: Python schedule library for automated execution
- **Testing**: Comprehensive test suite with mocking

### Error Handling
- Database connection failures
- API rate limiting and timeouts
- Missing or invalid data fields
- Timezone processing errors
- Currency rate lookup failures

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check PostgreSQL service: `sudo systemctl status postgresql`
   - Verify credentials in `.env` file
   - Ensure database and user exist

2. **API Rate Limiting**:
   - The Frankfurter API has rate limits
   - Scheduler spacing helps avoid hitting limits
   - Implement backoff strategies if needed

3. **Missing Dependencies**:
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

4. **Timezone Processing Errors**:
   - Some countries have invalid timezone data
   - The code handles these gracefully and continues processing

### Performance Considerations

- Countries data: ~250 countries processed in ~30 seconds
- Currency rates: Depends on API response time, typically 2-5 minutes for all currencies
- Database operations: Optimized with indexes and batch operations

## Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation as needed
4. Follow Python PEP 8 style guidelines

## License

This project is for educational purposes.