#!/usr/bin/env python3
"""
Standalone runner for the Countries DAG
This simulates running the countries_processing DAG without Airflow
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.processors.countries import CountriesProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("countries_dag_runner")

async def setup_database():
    """Initialize database connection"""
    await db_connection.create_pool()
    logger.info("Database connection established")

async def process_countries():
    """Process countries data"""
    processor = CountriesProcessor()
    success = await processor.process()
    if success:
        logger.info("Countries processing completed successfully")
    else:
        raise Exception("Countries processing failed")

async def cleanup_database():
    """Cleanup database connections"""
    await db_connection.close_pool()
    logger.info("Database connections closed")

async def main():
    """Run the countries DAG tasks in sequence"""
    print("=" * 60)
    print("🌍 COUNTRIES DAG RUNNER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Task 1: Setup Database
        print("📊 Task 1: Setting up database connection...")
        await setup_database()
        print("✅ Database connection established")
        print()
        
        # Task 2: Process Countries
        print("🌍 Task 2: Processing countries data...")
        await process_countries()
        print("✅ Countries processing completed")
        print()
        
        # Task 3: Cleanup Database
        print("🧹 Task 3: Cleaning up database connections...")
        await cleanup_database()
        print("✅ Database connections closed")
        print()
        
        print("🎉 Countries DAG completed successfully!")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Countries DAG failed: {e}")
        print(f"❌ Countries DAG failed: {e}")
        # Ensure cleanup even on failure
        try:
            await cleanup_database()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
