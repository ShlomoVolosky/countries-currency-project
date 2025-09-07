import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from config.database import get_database_config
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseInitializer:
        migration_files = []
        if self.migrations_dir.exists():
            for file_path in sorted(self.migrations_dir.glob("*.sql")):
                if file_path.is_file():
                    migration_files.append(file_path)
        
        return migration_files
    
    def read_migration_file(self, file_path: Path) -> str:
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        );
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
        INSERT INTO migrations (migration_name, checksum)
        VALUES (%s, %s)
        ON CONFLICT (migration_name) DO NOTHING
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    def run_migration(self, file_path: Path) -> bool:
        logger.info("Starting database migrations...")
        if not self.create_migrations_table():
            logger.error("Failed to create migrations table")
            return False
        
        migration_files = self.get_migration_files()
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        logger.info(f"Found {len(migration_files)} migration files")
        
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
        logger.info("Initializing database...")
        if not self.config.test_connection():
            logger.error("Database connection test failed")
            return False
        
        if reset:
            if not self.reset_database():
                return False
        
        return self.run_all_migrations()
    
    def get_database_status(self) -> dict:
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('countries', 'currency_rates', 'migrations')
    initializer = DatabaseInitializer()
    return initializer.initialize_database(reset)

def get_database_status() -> dict: