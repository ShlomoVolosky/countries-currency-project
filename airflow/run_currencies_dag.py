import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.currencies import CurrencyProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("currencies_dag_runner")

async def setup_database():
    """Initialize database connection"""
    await db_connection.create_pool()
    logger.info("Database connection established")

async def process_currencies():
    """Process currency rates"""
    processor = CurrencyProcessor()
    success = await processor.process()
    if success:
        logger.info("Currency processing completed successfully")
    else:
        raise Exception("Currency processing failed")

async def cleanup_database():
    """Cleanup database connections"""
    await db_connection.close_pool()
    logger.info("Database connections closed")

async def main():
    """Run the currencies DAG tasks in sequence"""
    print("=" * 60)
    print("💰 CURRENCIES DAG RUNNER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Task 1: Setup Database
        print("📊 Task 1: Setting up database connection...")
        await setup_database()
        print("✅ Database connection established")
        print()
        
        # Task 2: Process Currencies
        print("💰 Task 2: Processing currency rates...")
        await process_currencies()
        print("✅ Currency processing completed")
        print()
        
        # Task 3: Cleanup Database
        print("🧹 Task 3: Cleaning up database connections...")
        await cleanup_database()
        print("✅ Database connections closed")
        print()
        
        print("🎉 Currencies DAG completed successfully!")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Currencies DAG failed: {e}")
        print(f"❌ Currencies DAG failed: {e}")
        # Ensure cleanup even on failure
        try:
            await cleanup_database()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
