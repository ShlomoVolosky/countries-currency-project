# Countries Currency Project

A Python application that fetches country data and currency exchange rates, stores them in PostgreSQL, and provides automated updates.

## Project Versions

This repository contains two different implementations:

### 🚀 POC Version (Branch: `poc-version`)
Simple, minimal implementation with 5 core files for quick development and testing.

```
countries-currency-project/
├── src/
│   ├── config.py
│   ├── database.py
│   ├── part1_countries.py
│   ├── part2_currencies.py
│   └── part3_scheduler.py
├── tests/
├── sql/
└── requirements.txt
```

### 🏭 Production Version (Branch: `prod-version`)
Enterprise-ready structure with comprehensive organization, monitoring, testing, and deployment capabilities.

```
countries-currency-project/
├── src/
│   ├── config/
│   ├── models/
│   ├── processors/
│   ├── database/
│   ├── api/
│   ├── utils/
│   ├── monitoring/
│   └── scheduler/
├── tests/
├── scripts/
├── monitoring/
├── airflow/
├── docs/
└── config/
```

## Getting Started

Choose the version that fits your needs:

- **For homework/learning**: Use `poc-version`
- **For production deployment**: Use `prod-version`

```bash
# Clone and switch to POC version
git clone <repository-url>
git checkout poc-version

# Or switch to production version
git checkout prod-version
```# countries-currency-project
