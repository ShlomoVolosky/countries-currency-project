#!/bin/bash

# Environment setup script for Countries Currency Project
# This script helps you set up the environment and run the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create .env file
create_env_file() {
    print_step "Creating .env file..."
    
    cat > .env << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_NAME=countries_db
DB_USER=countries_user
DB_PASSWORD=countries_password
DB_PORT=5432

# API Configuration
COUNTRIES_API_URL=https://restcountries.com/v3.1/all?fields=name,capital,continents,currencies,unMember,population,timezones
CURRENCY_API_URL=https://api.frankfurter.app

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development

# Monitoring Configuration
PROMETHEUS_PORT=8000
GRAFANA_PORT=3000

# Airflow Configuration
AIRFLOW_HOME=/opt/airflow
AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/dags
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://countries_user:countries_password@localhost:5432/airflow_db
EOF
    
    print_status ".env file created successfully"
}

# Function to setup virtual environment
setup_venv() {
    print_step "Setting up virtual environment..."
    
    # Check if we're in the right directory
    if [ ! -f "setup.py" ] || [ ! -d "src" ]; then
        print_error "Please run this script from the prod-version directory"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    pip install -e .
    
    print_status "Virtual environment setup complete"
}

# Function to check PostgreSQL
check_postgresql() {
    print_step "Checking PostgreSQL installation..."
    
    if command_exists psql; then
        print_status "PostgreSQL client found"
    else
        print_warning "PostgreSQL client not found. Please install PostgreSQL:"
        print_warning "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        print_warning "  CentOS/RHEL: sudo yum install postgresql postgresql-server"
        print_warning "  macOS: brew install postgresql"
        return 1
    fi
    
    # Check if PostgreSQL is running
    if pg_isready -q; then
        print_status "PostgreSQL is running"
    else
        print_warning "PostgreSQL is not running. Please start it:"
        print_warning "  Ubuntu/Debian: sudo systemctl start postgresql"
        print_warning "  CentOS/RHEL: sudo systemctl start postgresql"
        print_warning "  macOS: brew services start postgresql"
        return 1
    fi
    
    return 0
}

# Function to create database user and database
create_database() {
    print_step "Creating database and user..."
    
    # Create user if it doesn't exist
    sudo -u postgres psql -c "CREATE USER countries_user WITH PASSWORD 'countries_password';" 2>/dev/null || true
    
    # Create database if it doesn't exist
    sudo -u postgres psql -c "CREATE DATABASE countries_db OWNER countries_user;" 2>/dev/null || true
    
    # Grant privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE countries_db TO countries_user;" 2>/dev/null || true
    
    print_status "Database and user created successfully"
}

# Function to run database setup
run_database_setup() {
    print_step "Running database setup..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Set environment variables
    export $(cat .env | xargs)
    
    # Run database setup
    bash scripts/setup_database.sh
}

# Function to show next steps
show_next_steps() {
    print_status "Setup completed successfully!"
    echo ""
    print_step "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Set environment variables:"
    echo "   export \$(cat .env | xargs)"
    echo ""
    echo "3. Run the application:"
    echo "   python -m src.main setup    # Initial data load"
    echo "   python -m src.main scheduler # Start automated scheduler"
    echo ""
    echo "4. Or use Docker:"
    echo "   docker-compose up -d"
    echo ""
    print_status "Happy coding! 🚀"
}

# Main execution
main() {
    print_status "Setting up Countries Currency Project environment"
    echo ""
    
    # Create .env file
    create_env_file
    
    # Setup virtual environment
    setup_venv
    
    # Check PostgreSQL
    if check_postgresql; then
        # Create database
        create_database
        
        # Run database setup
        run_database_setup
    else
        print_warning "Skipping database setup. Please install and start PostgreSQL first."
    fi
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@"
