#!/bin/bash

# Deployment script for the Countries Currency Project
# This script handles deployment to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${ENVIRONMENT:-staging}
VERSION=${VERSION:-latest}
DOCKER_BUILD=${DOCKER_BUILD:-false}
DOCKER_PUSH=${DOCKER_PUSH:-false}
SKIP_TESTS=${SKIP_TESTS:-false}
SKIP_DB_MIGRATION=${SKIP_DB_MIGRATION:-false}
BACKUP_DB=${BACKUP_DB:-true}

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

print_deploy() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -e, --environment ENV   Target environment (staging|production)"
    echo "  -v, --version VER       Version to deploy (default: latest)"
    echo "  --docker-build          Build Docker image"
    echo "  --docker-push           Push Docker image to registry"
    echo "  --skip-tests            Skip running tests"
    echo "  --skip-db-migration     Skip database migration"
    echo "  --no-backup             Skip database backup"
    echo "  --dry-run               Show what would be done without executing"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT             Target environment (default: staging)"
    echo "  VERSION                 Version to deploy (default: latest)"
    echo "  DOCKER_REGISTRY         Docker registry URL"
    echo "  DOCKER_IMAGE_NAME       Docker image name"
    echo "  DB_BACKUP_PATH          Database backup path"
    echo ""
    echo "Examples:"
    echo "  $0 --environment staging --version 1.0.0"
    echo "  $0 --docker-build --docker-push --environment production"
    echo "  $0 --dry-run --environment production"
}

# Function to validate environment
validate_environment() {
    case "$ENVIRONMENT" in
        staging|production)
            print_status "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            print_error "Valid environments: staging, production"
            exit 1
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [ ! -f "setup.py" ] || [ ! -d "src" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check Docker if needed
    if [ "$DOCKER_BUILD" = "true" ] && ! command_exists docker; then
        print_error "Docker is required for building images but not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Function to run tests
run_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        print_warning "Skipping tests"
        return 0
    fi
    
    print_deploy "Running tests..."
    
    if [ -f "scripts/run_tests.sh" ]; then
        if ! bash scripts/run_tests.sh; then
            print_error "Tests failed"
            exit 1
        fi
    else
        print_warning "Test script not found, running pytest directly"
        if ! python -m pytest tests/ -v; then
            print_error "Tests failed"
            exit 1
        fi
    fi
    
    print_status "Tests passed"
}

# Function to backup database
backup_database() {
    if [ "$BACKUP_DB" = "false" ]; then
        print_warning "Skipping database backup"
        return 0
    fi
    
    print_deploy "Backing up database..."
    
    if [ -f "scripts/backup_database.sh" ]; then
        if ! bash scripts/backup_database.sh; then
            print_warning "Database backup failed, continuing with deployment"
        else
            print_status "Database backup completed"
        fi
    else
        print_warning "Database backup script not found, skipping backup"
    fi
}

# Function to run database migration
run_database_migration() {
    if [ "$SKIP_DB_MIGRATION" = "true" ]; then
        print_warning "Skipping database migration"
        return 0
    fi
    
    print_deploy "Running database migration..."
    
    if [ -f "scripts/setup_database.sh" ]; then
        if ! bash scripts/setup_database.sh; then
            print_error "Database migration failed"
            exit 1
        fi
    else
        print_warning "Database migration script not found, skipping migration"
    fi
    
    print_status "Database migration completed"
}

# Function to install dependencies
install_dependencies() {
    print_deploy "Installing dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install package in development mode
    pip install -e .
    
    print_status "Dependencies installed"
}

# Function to build Docker image
build_docker_image() {
    if [ "$DOCKER_BUILD" = "false" ]; then
        return 0
    fi
    
    print_deploy "Building Docker image..."
    
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found"
        exit 1
    fi
    
    local image_name="${DOCKER_IMAGE_NAME:-countries-currency-project}"
    local image_tag="${image_name}:${VERSION}"
    
    if ! docker build -t "$image_tag" .; then
        print_error "Docker build failed"
        exit 1
    fi
    
    # Tag as latest if this is the latest version
    if [ "$VERSION" = "latest" ]; then
        docker tag "$image_tag" "${image_name}:latest"
    fi
    
    print_status "Docker image built: $image_tag"
}

# Function to push Docker image
push_docker_image() {
    if [ "$DOCKER_PUSH" = "false" ]; then
        return 0
    fi
    
    print_deploy "Pushing Docker image..."
    
    local image_name="${DOCKER_IMAGE_NAME:-countries-currency-project}"
    local image_tag="${image_name}:${VERSION}"
    local registry="${DOCKER_REGISTRY:-}"
    
    if [ -n "$registry" ]; then
        local full_tag="${registry}/${image_tag}"
        docker tag "$image_tag" "$full_tag"
        docker push "$full_tag"
        print_status "Docker image pushed: $full_tag"
    else
        print_warning "DOCKER_REGISTRY not set, skipping push"
    fi
}

# Function to deploy application
deploy_application() {
    print_deploy "Deploying application..."
    
    # Set environment-specific configuration
    case "$ENVIRONMENT" in
        staging)
            export ENVIRONMENT=staging
            ;;
        production)
            export ENVIRONMENT=production
            ;;
    esac
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    
    # Set permissions
    chmod +x scripts/*.sh 2>/dev/null || true
    
    print_status "Application deployed to $ENVIRONMENT"
}

# Function to verify deployment
verify_deployment() {
    print_deploy "Verifying deployment..."
    
    # Test database connection
    if python -c "from src.database.init_db import get_database_status; print(get_database_status())" 2>/dev/null; then
        print_status "Database connection verified"
    else
        print_warning "Database connection verification failed"
    fi
    
    # Test API endpoints if available
    if python -c "from src.api.countries_api import CountriesAPIClient; api = CountriesAPIClient(); print('Countries API:', api.test_connection())" 2>/dev/null; then
        print_status "Countries API verified"
    else
        print_warning "Countries API verification failed"
    fi
    
    if python -c "from src.api.frankfurter_api import FrankfurterAPIClient; api = FrankfurterAPIClient(); print('Currency API:', api.test_connection())" 2>/dev/null; then
        print_status "Currency API verified"
    else
        print_warning "Currency API verification failed"
    fi
    
    print_status "Deployment verification completed"
}

# Function to show deployment summary
show_summary() {
    print_status "Deployment Summary"
    echo "=================="
    echo "Environment: $ENVIRONMENT"
    echo "Version: $VERSION"
    echo "Docker Build: $DOCKER_BUILD"
    echo "Docker Push: $DOCKER_PUSH"
    echo "Tests Skipped: $SKIP_TESTS"
    echo "DB Migration Skipped: $SKIP_DB_MIGRATION"
    echo "DB Backup: $BACKUP_DB"
    echo ""
    print_status "Deployment completed successfully!"
}

# Parse command line arguments
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        --docker-build)
            DOCKER_BUILD=true
            shift
            ;;
        --docker-push)
            DOCKER_PUSH=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-db-migration)
            SKIP_DB_MIGRATION=true
            shift
            ;;
        --no-backup)
            BACKUP_DB=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
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
    print_status "Starting deployment for Countries Currency Project"
    
    # Validate environment
    validate_environment
    
    # Check prerequisites
    check_prerequisites
    
    if [ "$DRY_RUN" = "true" ]; then
        print_status "DRY RUN - No actual deployment will be performed"
        show_summary
        exit 0
    fi
    
    # Run deployment steps
    run_tests
    backup_database
    install_dependencies
    run_database_migration
    build_docker_image
    push_docker_image
    deploy_application
    verify_deployment
    show_summary
}

# Run main function
main "$@"
