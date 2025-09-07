#!/bin/bash

# Database backup script for the Countries Currency Project
# This script creates backups of the database with compression and rotation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-countries_db}
DB_USER=${DB_USER:-countries_user}
BACKUP_DIR=${BACKUP_DIR:-./backups}
RETENTION_DAYS=${RETENTION_DAYS:-30}
COMPRESS=${COMPRESS:-true}
FORMAT=${FORMAT:-custom}

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

print_backup() {
    echo -e "${BLUE}[BACKUP]${NC} $1"
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
    echo "  -d, --database DB       Database name (default: $DB_NAME)"
    echo "  -u, --user USER         Database user (default: $DB_USER)"
    echo "  -H, --host HOST         Database host (default: $DB_HOST)"
    echo "  -p, --port PORT         Database port (default: $DB_PORT)"
    echo "  -o, --output DIR        Backup directory (default: $BACKUP_DIR)"
    echo "  -r, --retention DAYS    Retention days (default: $RETENTION_DAYS)"
    echo "  --no-compress           Disable compression"
    echo "  --format FORMAT         Backup format (custom|plain|sql) (default: $FORMAT)"
    echo "  --cleanup               Only cleanup old backups"
    echo ""
    echo "Environment variables:"
    echo "  DB_HOST                 Database host"
    echo "  DB_PORT                 Database port"
    echo "  DB_NAME                 Database name"
    echo "  DB_USER                 Database user"
    echo "  DB_PASSWORD             Database password"
    echo "  BACKUP_DIR              Backup directory"
    echo "  RETENTION_DAYS          Retention days"
    echo "  COMPRESS                Enable compression (true|false)"
    echo "  FORMAT                  Backup format"
    echo ""
    echo "Examples:"
    echo "  $0                      # Basic backup"
    echo "  $0 --database mydb --user myuser"
    echo "  $0 --retention 7 --no-compress"
    echo "  $0 --cleanup            # Only cleanup old backups"
}

# Function to create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        print_status "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Function to generate backup filename
generate_backup_filename() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local extension="dump"
    
    if [ "$COMPRESS" = "true" ]; then
        extension="dump.gz"
    fi
    
    echo "${DB_NAME}_${timestamp}.${extension}"
}

# Function to perform database backup
perform_backup() {
    local backup_file="$1"
    local backup_path="$BACKUP_DIR/$backup_file"
    
    print_backup "Starting database backup..."
    print_status "Database: $DB_NAME@$DB_HOST:$DB_PORT"
    print_status "Backup file: $backup_path"
    
    # Check if pg_dump is available
    if ! command_exists pg_dump; then
        print_error "pg_dump is required but not installed"
        exit 1
    fi
    
    # Set PGPASSWORD if not already set
    if [ -z "$PGPASSWORD" ] && [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Perform backup
    local pg_dump_args=(
        "--host=$DB_HOST"
        "--port=$DB_PORT"
        "--username=$DB_USER"
        "--dbname=$DB_NAME"
        "--format=$FORMAT"
        "--verbose"
        "--no-password"
    )
    
    if [ "$COMPRESS" = "true" ]; then
        if ! pg_dump "${pg_dump_args[@]}" | gzip > "$backup_path"; then
            print_error "Database backup failed"
            exit 1
        fi
    else
        if ! pg_dump "${pg_dump_args[@]}" > "$backup_path"; then
            print_error "Database backup failed"
            exit 1
        fi
    fi
    
    # Verify backup file
    if [ -f "$backup_path" ] && [ -s "$backup_path" ]; then
        local file_size=$(du -h "$backup_path" | cut -f1)
        print_status "Backup completed successfully: $backup_path ($file_size)"
    else
        print_error "Backup file is empty or missing"
        exit 1
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "Backup directory does not exist: $BACKUP_DIR"
        return 0
    fi
    
    local deleted_count=0
    
    # Find and delete old backup files
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            rm "$file"
            deleted_count=$((deleted_count + 1))
            print_status "Deleted old backup: $(basename "$file")"
        fi
    done < <(find "$BACKUP_DIR" -name "${DB_NAME}_*.dump*" -type f -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    if [ $deleted_count -eq 0 ]; then
        print_status "No old backups to clean up"
    else
        print_status "Cleaned up $deleted_count old backup(s)"
    fi
}

# Function to list backups
list_backups() {
    print_status "Available backups:"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "Backup directory does not exist: $BACKUP_DIR"
        return 0
    fi
    
    local backup_files=($(find "$BACKUP_DIR" -name "${DB_NAME}_*.dump*" -type f -printf "%T@ %Tc %p\n" 2>/dev/null | sort -n | awk '{print $3}'))
    
    if [ ${#backup_files[@]} -eq 0 ]; then
        print_warning "No backups found"
        return 0
    fi
    
    for file in "${backup_files[@]}"; do
        local file_size=$(du -h "$file" | cut -f1)
        local file_date=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
        echo "  $(basename "$file") - $file_size - $file_date"
    done
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    local backup_path="$BACKUP_DIR/$backup_file"
    
    if [ ! -f "$backup_path" ]; then
        print_error "Backup file not found: $backup_path"
        exit 1
    fi
    
    print_backup "Restoring database from: $backup_file"
    print_warning "This will overwrite the existing database!"
    
    # Check if pg_restore is available
    if ! command_exists pg_restore; then
        print_error "pg_restore is required but not installed"
        exit 1
    fi
    
    # Set PGPASSWORD if not already set
    if [ -z "$PGPASSWORD" ] && [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Perform restore
    local pg_restore_args=(
        "--host=$DB_HOST"
        "--port=$DB_PORT"
        "--username=$DB_USER"
        "--dbname=$DB_NAME"
        "--verbose"
        "--no-password"
        "--clean"
        "--if-exists"
    )
    
    if [ "$COMPRESS" = "true" ] && [[ "$backup_file" == *.gz ]]; then
        if ! gunzip -c "$backup_path" | pg_restore "${pg_restore_args[@]}"; then
            print_error "Database restore failed"
            exit 1
        fi
    else
        if ! pg_restore "${pg_restore_args[@]}" "$backup_path"; then
            print_error "Database restore failed"
            exit 1
        fi
    fi
    
    print_status "Database restored successfully"
}

# Parse command line arguments
CLEANUP_ONLY=false
RESTORE_FILE=""
LIST_BACKUPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -u|--user)
            DB_USER="$2"
            shift 2
            ;;
        -H|--host)
            DB_HOST="$2"
            shift 2
            ;;
        -p|--port)
            DB_PORT="$2"
            shift 2
            ;;
        -o|--output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --no-compress)
            COMPRESS=false
            shift
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP_ONLY=true
            shift
            ;;
        --restore)
            RESTORE_FILE="$2"
            shift 2
            ;;
        --list)
            LIST_BACKUPS=true
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
    print_status "Database Backup Script for Countries Currency Project"
    
    # Check if DB_PASSWORD is set
    if [ -z "$DB_PASSWORD" ] && [ -z "$PGPASSWORD" ]; then
        print_error "DB_PASSWORD or PGPASSWORD environment variable is required"
        exit 1
    fi
    
    # Create backup directory
    create_backup_dir
    
    # Handle special operations
    if [ "$LIST_BACKUPS" = true ]; then
        list_backups
        exit 0
    fi
    
    if [ -n "$RESTORE_FILE" ]; then
        restore_database "$RESTORE_FILE"
        exit 0
    fi
    
    if [ "$CLEANUP_ONLY" = true ]; then
        cleanup_old_backups
        exit 0
    fi
    
    # Perform backup
    local backup_file=$(generate_backup_filename)
    perform_backup "$backup_file"
    
    # Cleanup old backups
    cleanup_old_backups
    
    # List current backups
    list_backups
    
    print_status "Backup process completed successfully!"
}

# Run main function
main "$@"
