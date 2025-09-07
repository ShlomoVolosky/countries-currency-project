#!/bin/bash

# Test execution script for the Countries Currency Project
# This script runs the test suite with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${ENVIRONMENT:-test}
COVERAGE=${COVERAGE:-true}
VERBOSE=${VERBOSE:-false}
PARALLEL=${PARALLEL:-false}
COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD:-80}

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

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [TEST_PATTERN]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -v, --verbose           Verbose output"
    echo "  --no-coverage           Disable coverage reporting"
    echo "  --coverage-threshold N  Set coverage threshold (default: 80)"
    echo "  --parallel              Run tests in parallel"
    echo "  --unit                  Run only unit tests"
    echo "  --integration           Run only integration tests"
    echo "  --database              Run only database tests"
    echo "  --api                   Run only API tests"
    echo "  --processors            Run only processor tests"
    echo "  --fast                  Run tests quickly (skip slow tests)"
    echo "  --html-report           Generate HTML coverage report"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT             Test environment (default: test)"
    echo "  COVERAGE                Enable coverage (default: true)"
    echo "  VERBOSE                 Verbose output (default: false)"
    echo "  PARALLEL                Run in parallel (default: false)"
    echo "  COVERAGE_THRESHOLD      Coverage threshold (default: 80)"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all tests"
    echo "  $0 --unit               # Run only unit tests"
    echo "  $0 --verbose --coverage # Run with verbose output and coverage"
    echo "  $0 test_processors      # Run tests matching pattern"
}

# Function to setup test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Change to the project directory
    cd "$(dirname "$0")/.."
    
    # Set Python path
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    # Set test environment
    export ENVIRONMENT="$ENVIRONMENT"
    
    # Create test database if needed
    if [ "$ENVIRONMENT" = "test" ]; then
        export DB_NAME="${DB_NAME:-countries_test_db}"
        print_status "Using test database: $DB_NAME"
    fi
    
    print_status "Test environment setup complete"
}

# Function to run unit tests
run_unit_tests() {
    print_test "Running unit tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
        
        if [ "$COVERAGE_THRESHOLD" != "0" ]; then
            pytest_args+=("--cov-fail-under=$COVERAGE_THRESHOLD")
        fi
    fi
    
    if [ "$PARALLEL" = "true" ] && command_exists pytest-xdist; then
        pytest_args+=("-n" "auto")
    fi
    
    pytest_args+=("tests/test_processors/" "tests/test_api/" "tests/test_utils/")
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "Unit tests failed"
        return 1
    fi
    
    print_status "Unit tests completed successfully"
}

# Function to run integration tests
run_integration_tests() {
    print_test "Running integration tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
    fi
    
    pytest_args+=("tests/test_integration/")
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "Integration tests failed"
        return 1
    fi
    
    print_status "Integration tests completed successfully"
}

# Function to run database tests
run_database_tests() {
    print_test "Running database tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
    fi
    
    pytest_args+=("tests/test_database/")
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "Database tests failed"
        return 1
    fi
    
    print_status "Database tests completed successfully"
}

# Function to run API tests
run_api_tests() {
    print_test "Running API tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
    fi
    
    pytest_args+=("tests/test_api/")
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "API tests failed"
        return 1
    fi
    
    print_status "API tests completed successfully"
}

# Function to run processor tests
run_processor_tests() {
    print_test "Running processor tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
    fi
    
    pytest_args+=("tests/test_processors/")
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "Processor tests failed"
        return 1
    fi
    
    print_status "Processor tests completed successfully"
}

# Function to run all tests
run_all_tests() {
    print_test "Running all tests..."
    
    local pytest_args=()
    
    if [ "$VERBOSE" = "true" ]; then
        pytest_args+=("-v")
    fi
    
    if [ "$COVERAGE" = "true" ]; then
        pytest_args+=("--cov=src" "--cov-report=term-missing")
        
        if [ "$COVERAGE_THRESHOLD" != "0" ]; then
            pytest_args+=("--cov-fail-under=$COVERAGE_THRESHOLD")
        fi
    fi
    
    if [ "$PARALLEL" = "true" ] && command_exists pytest-xdist; then
        pytest_args+=("-n" "auto")
    fi
    
    if [ "$FAST" = "true" ]; then
        pytest_args+=("-m" "not slow")
    fi
    
    pytest_args+=("tests/")
    
    if [ -n "$TEST_PATTERN" ]; then
        pytest_args+=("-k" "$TEST_PATTERN")
    fi
    
    if ! python -m pytest "${pytest_args[@]}"; then
        print_error "Tests failed"
        return 1
    fi
    
    print_status "All tests completed successfully"
}

# Function to generate HTML coverage report
generate_html_report() {
    if [ "$COVERAGE" = "true" ]; then
        print_status "Generating HTML coverage report..."
        
        if python -m pytest --cov=src --cov-report=html tests/ >/dev/null 2>&1; then
            print_status "HTML coverage report generated in htmlcov/"
        else
            print_warning "Failed to generate HTML coverage report"
        fi
    fi
}

# Parse command line arguments
TEST_PATTERN=""
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_DATABASE=false
RUN_API=false
RUN_PROCESSORS=false
FAST=false
HTML_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --coverage-threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --unit)
            RUN_UNIT=true
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --database)
            RUN_DATABASE=true
            shift
            ;;
        --api)
            RUN_API=true
            shift
            ;;
        --processors)
            RUN_PROCESSORS=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --html-report)
            HTML_REPORT=true
            shift
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            TEST_PATTERN="$1"
            shift
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting test execution for Countries Currency Project"
    print_status "Environment: $ENVIRONMENT"
    print_status "Coverage: $COVERAGE"
    print_status "Verbose: $VERBOSE"
    print_status "Parallel: $PARALLEL"
    
    # Setup test environment
    setup_test_env
    
    # Check if pytest is available
    if ! command_exists python || ! python -c "import pytest" 2>/dev/null; then
        print_error "pytest is not available. Please install test dependencies."
        exit 1
    fi
    
    # Run specific test categories
    if [ "$RUN_UNIT" = true ]; then
        run_unit_tests
    elif [ "$RUN_INTEGRATION" = true ]; then
        run_integration_tests
    elif [ "$RUN_DATABASE" = true ]; then
        run_database_tests
    elif [ "$RUN_API" = true ]; then
        run_api_tests
    elif [ "$RUN_PROCESSORS" = true ]; then
        run_processor_tests
    else
        run_all_tests
    fi
    
    # Generate HTML report if requested
    if [ "$HTML_REPORT" = true ]; then
        generate_html_report
    fi
    
    print_status "Test execution completed successfully!"
}

# Run main function
main "$@"
