#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.countries import CountriesProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("process_countries")


async def main():
    try:
        await db_connection.create_pool()
        logger.info("Database connection established")
        
        processor = CountriesProcessor()
        success = await processor.process()
        
        if success:
            logger.info("Countries processing completed successfully")
        else:
            logger.error("Countries processing failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        await db_connection.close_pool()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
