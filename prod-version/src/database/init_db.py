import argparse
import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from config.database import get_database_config
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseInitializer:
    def __init__(self):
        self.db = get_database_config()
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    def get_migration_files(self) -> List[Path]:
        migration_files = []
        if self.migrations_dir.exists():
            for file_path in sorted(self.migrations_dir.glob("*.sql")):
                if file_path.is_file():
                    migration_files.append(file_path)
        return migration_files
    
    def read_migration_file(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading migration file {file_path}: {e}")
            raise
    
    def calculate_checksum(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def create_migrations_table(self) -> bool:
        query = """
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        );
        """
        try:
            self.db.execute_query(query, fetch_results=False)
            logger.info("Migrations table created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating migrations table: {e}")
            return False
    
    def is_migration_executed(self, migration_name: str) -> bool:
        query = "SELECT COUNT(*) FROM migrations WHERE migration_name = %s"
        try:
            result = self.db.execute_query(query, (migration_name,))
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False
    
    def mark_migration_executed(self, migration_name: str, checksum: str) -> bool:
        query = """
        INSERT INTO migrations (migration_name, checksum) 
        VALUES (%s, %s) 
        ON CONFLICT (migration_name) DO NOTHING
        """
        try:
            self.db.execute_query(query, (migration_name, checksum), fetch_results=False)
            return True
        except Exception as e:
            logger.error(f"Error marking migration as executed: {e}")
            return False
    
    def run_migration(self, file_path: Path) -> bool:
        migration_name = file_path.name
        logger.info(f"Running migration: {migration_name}")
        
        if self.is_migration_executed(migration_name):
            logger.info(f"Migration {migration_name} already executed, skipping")
            return True
        
        try:
            content = self.read_migration_file(file_path)
            checksum = self.calculate_checksum(content)
            
            self.db.execute_query(content, fetch_results=False)
            self.mark_migration_executed(migration_name, checksum)
            
            logger.info(f"Migration {migration_name} executed successfully")
            return True
        except Exception as e:
            logger.error(f"Error running migration {migration_name}: {e}")
            return False
    
    def run_migrations(self) -> bool:
        if not self.create_migrations_table():
            return False
        
        migration_files = self.get_migration_files()
        if not migration_files:
            logger.info("No migration files found")
            return True
        
        for file_path in migration_files:
            if not self.run_migration(file_path):
                return False
        
        logger.info("All migrations completed successfully")
        return True
    
    def reset_database(self) -> bool:
        logger.warning("Resetting database - this will delete all data!")
        
        try:
            self.db.execute_query("DROP TABLE IF EXISTS migrations CASCADE", fetch_results=False)
            self.db.execute_query("DROP TABLE IF EXISTS currency_rates CASCADE", fetch_results=False)
            self.db.execute_query("DROP TABLE IF EXISTS countries CASCADE", fetch_results=False)
            
            logger.info("Database reset completed")
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False


def initialize_database(reset: bool = False) -> bool:
    initializer = DatabaseInitializer()
    
    if reset:
        if not initializer.reset_database():
            return False
    
    return initializer.run_migrations()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset database before initialization")
    parser.add_argument("--no-reset", action="store_true", help="Skip database reset")
    parser.add_argument("--status", action="store_true", help="Show database status")
    
    args = parser.parse_args()
    
    if args.status:
        db = get_database_config()
        if db.test_connection():
            print("Database connection: OK")
        else:
            print("Database connection: FAILED")
        return
    
    reset_db = args.reset and not args.no_reset
    success = initialize_database(reset=reset_db)
    
    if success:
        print("Database initialization completed successfully")
    else:
        print("Database initialization failed")
        exit(1)


if __name__ == "__main__":
    main()