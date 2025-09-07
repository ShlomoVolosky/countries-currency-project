#!/bin/bash

# Database setup script for the Countries Currency Project
# This script initializes the database and runs migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-countries_db}
DB_USER=${DB_USER:-countries_user}
ENVIRONMENT=${ENVIRONMENT:-development}
RESET_DB=${RESET_DB:-false}

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check database connection
check_db_connection() {
    print_status "Checking database connection..."
    
    if command_exists psql; then
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
            print_status "Database connection successful"
            return 0
        else
            print_error "Database connection failed"
            return 1
        fi
    else
        print_warning "psql not found, skipping connection test"
        return 0
    fi
}

# Function to create database if it doesn't exist
create_database() {
    print_status "Creating database if it doesn't exist..."
    
    if command_exists createdb; then
        if createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>/dev/null; then
            print_status "Database created successfully"
        else
            print_warning "Database might already exist or creation failed"
        fi
    else
        print_warning "createdb not found, please create database manually"
    fi
}

# Function to run database initialization
run_db_init() {
    print_status "Running database initialization..."
    
    # Change to the project directory
    cd "$(dirname "$0")/.."
    
    # Set Python path
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    # Run database initialization
    if python -m src.database.init_db --reset="$RESET_DB"; then
        print_status "Database initialization completed successfully"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running database tests..."
    
    # Change to the project directory
    cd "$(dirname "$0")/.."
    
    # Set Python path
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    if python -m pytest tests/test_database/ -v; then
        print_status "Database tests passed"
    else
        print_warning "Some database tests failed"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  --reset                 Reset database before initialization"
    echo "  --test                  Run tests after setup"
    echo "  --no-init               Skip database initialization"
    echo "  --no-tests              Skip running tests"
    echo ""
    echo "Environment variables:"
    echo "  DB_HOST                 Database host (default: localhost)"
    echo "  DB_PORT                 Database port (default: 5432)"
    echo "  DB_NAME                 Database name (default: countries_db)"
    echo "  DB_USER                 Database user (default: countries_user)"
    echo "  DB_PASSWORD             Database password (required)"
    echo "  ENVIRONMENT             Environment (default: development)"
    echo ""
    echo "Examples:"
    echo "  $0                      # Basic setup"
    echo "  $0 --reset --test       # Reset database and run tests"
    echo "  DB_PASSWORD=mypass $0   # Set password via environment"
}

# Parse command line arguments
RESET_DB=false
RUN_TESTS=false
SKIP_INIT=false
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --reset)
            RESET_DB=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --no-init)
            SKIP_INIT=true
            shift
            ;;
        --no-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting database setup for Countries Currency Project"
    print_status "Environment: $ENVIRONMENT"
    print_status "Database: $DB_NAME@$DB_HOST:$DB_PORT"
    
    # Check if DB_PASSWORD is set
    if [ -z "$DB_PASSWORD" ]; then
        print_error "DB_PASSWORD environment variable is required"
        exit 1
    fi
    
    # Check database connection
    if ! check_db_connection; then
        print_warning "Database connection failed, attempting to create database..."
        create_database
        
        if ! check_db_connection; then
            print_error "Cannot connect to database. Please check your configuration."
            exit 1
        fi
    fi
    
    # Run database initialization
    if [ "$SKIP_INIT" = false ]; then
        run_db_init
    else
        print_status "Skipping database initialization"
    fi
    
    # Run tests
    if [ "$SKIP_TESTS" = false ] && ([ "$RUN_TESTS" = true ] || [ "$ENVIRONMENT" = "development" ]); then
        run_tests
    else
        print_status "Skipping tests"
    fi
    
    print_status "Database setup completed successfully!"
    print_status "You can now run the application with: python -m src.main"
}

# Run main function
main "$@"
