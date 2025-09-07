"""
Database initialization and migration management.

This module provides functionality to initialize the database,
run migrations, and set up the database schema.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from config.database import get_database_config
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseInitializer:
    """Database initialization and migration manager."""
    
    def __init__(self):
        self.config = get_database_config()
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    def get_migration_files(self) -> List[Path]:
        """Get list of migration files in order."""
        migration_files = []
        
        if self.migrations_dir.exists():
            for file_path in sorted(self.migrations_dir.glob("*.sql")):
                if file_path.is_file():
                    migration_files.append(file_path)
        
        return migration_files
    
    def read_migration_file(self, file_path: Path) -> str:
        """Read migration file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading migration file {file_path}: {e}")
            raise
    
    def create_migrations_table(self) -> bool:
        """Create migrations tracking table."""
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        );
        """
        
        try:
            result = self.config.execute_query(query, fetch_results=False)
            logger.info("Migrations table created or already exists")
            return result is not None
        except Exception as e:
            logger.error(f"Error creating migrations table: {e}")
            return False
    
    def get_executed_migrations(self) -> List[str]:
        """Get list of executed migrations."""
        query = "SELECT migration_name FROM migrations ORDER BY id"
        
        try:
            result = self.config.execute_query(query)
            if result:
                return [row['migration_name'] for row in result]
            return []
        except Exception as e:
            logger.error(f"Error getting executed migrations: {e}")
            return []
    
    def mark_migration_executed(self, migration_name: str, checksum: str = None) -> bool:
        """Mark migration as executed."""
        query = """
        INSERT INTO migrations (migration_name, checksum)
        VALUES (%s, %s)
        ON CONFLICT (migration_name) DO NOTHING
        """
        
        try:
            result = self.config.execute_query(query, (migration_name, checksum), fetch_results=False)
            logger.info(f"Marked migration {migration_name} as executed")
            return result is not None
        except Exception as e:
            logger.error(f"Error marking migration {migration_name} as executed: {e}")
            return False
    
    def calculate_checksum(self, content: str) -> str:
        """Calculate checksum for migration content."""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def run_migration(self, file_path: Path) -> bool:
        """Run a single migration file."""
        migration_name = file_path.name
        
        try:
            # Read migration content
            content = self.read_migration_file(file_path)
            checksum = self.calculate_checksum(content)
            
            # Check if already executed
            executed_migrations = self.get_executed_migrations()
            if migration_name in executed_migrations:
                logger.info(f"Migration {migration_name} already executed, skipping")
                return True
            
            # Execute migration
            logger.info(f"Executing migration: {migration_name}")
            result = self.config.execute_query(content, fetch_results=False)
            
            if result:
                # Mark as executed
                self.mark_migration_executed(migration_name, checksum)
                logger.info(f"Migration {migration_name} executed successfully")
                return True
            else:
                logger.error(f"Migration {migration_name} execution failed")
                return False
                
        except Exception as e:
            logger.error(f"Error running migration {migration_name}: {e}")
            return False
    
    def run_all_migrations(self) -> bool:
        """Run all pending migrations."""
        logger.info("Starting database migrations...")
        
        # Create migrations table first
        if not self.create_migrations_table():
            logger.error("Failed to create migrations table")
            return False
        
        # Get migration files
        migration_files = self.get_migration_files()
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        logger.info(f"Found {len(migration_files)} migration files")
        
        # Run migrations
        success_count = 0
        for file_path in migration_files:
            if self.run_migration(file_path):
                success_count += 1
            else:
                logger.error(f"Failed to run migration: {file_path.name}")
                return False
        
        logger.info(f"Successfully executed {success_count} migrations")
        return True
    
    def reset_database(self) -> bool:
        """Reset database by dropping and recreating tables."""
        logger.warning("Resetting database - this will delete all data!")
        
        # Drop tables in reverse order
        drop_queries = [
            "DROP TABLE IF EXISTS currency_rates CASCADE;",
            "DROP TABLE IF EXISTS countries CASCADE;",
            "DROP TABLE IF EXISTS migrations CASCADE;",
            "DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;",
            "DROP FUNCTION IF EXISTS update_currency_rates_updated_at_column() CASCADE;",
        ]
        
        try:
            for query in drop_queries:
                self.config.execute_query(query, fetch_results=False)
            
            logger.info("Database reset completed")
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False
    
    def initialize_database(self, reset: bool = False) -> bool:
        """Initialize database with all migrations."""
        logger.info("Initializing database...")
        
        # Test connection first
        if not self.config.test_connection():
            logger.error("Database connection test failed")
            return False
        
        # Reset if requested
        if reset:
            if not self.reset_database():
                return False
        
        # Run migrations
        return self.run_all_migrations()
    
    def get_database_status(self) -> dict:
        """Get database status information."""
        status = {
            "connection_ok": False,
            "migrations_executed": [],
            "tables_exist": {
                "countries": False,
                "currency_rates": False,
                "migrations": False
            }
        }
        
        try:
            # Test connection
            status["connection_ok"] = self.config.test_connection()
            
            # Check tables
            table_check_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('countries', 'currency_rates', 'migrations')
            """
            
            result = self.config.execute_query(table_check_query)
            if result:
                for row in result:
                    status["tables_exist"][row['table_name']] = True
            
            # Get executed migrations
            status["migrations_executed"] = self.get_executed_migrations()
            
        except Exception as e:
            logger.error(f"Error getting database status: {e}")
        
        return status


def initialize_database(reset: bool = False) -> bool:
    """Initialize database with all migrations."""
    initializer = DatabaseInitializer()
    return initializer.initialize_database(reset)


def get_database_status() -> dict:
    """Get database status information."""
    initializer = DatabaseInitializer()
    return initializer.get_database_status()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization tool")
    parser.add_argument("--reset", action="store_true", help="Reset database before initialization")
    parser.add_argument("--no-reset", action="store_true", help="Skip database reset")
    parser.add_argument("--status", action="store_true", help="Show database status")
    
    args = parser.parse_args()
    
    if args.status:
        status = get_database_status()
        print("Database Status:")
        print(f"  Connection: {'OK' if status['connection_ok'] else 'FAILED'}")
        print(f"  Tables:")
        for table, exists in status['tables_exist'].items():
            print(f"    {table}: {'EXISTS' if exists else 'MISSING'}")
        print(f"  Migrations executed: {len(status['migrations_executed'])}")
        for migration in status['migrations_executed']:
            print(f"    - {migration}")
    else:
        reset_db = args.reset and not args.no_reset
        success = initialize_database(reset=reset_db)
        if success:
            print("Database initialization completed successfully")
        else:
            print("Database initialization failed")
            exit(1)
