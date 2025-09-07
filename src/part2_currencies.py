import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler.runner import SchedulerRunner
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("part2_currencies")


async def main():
    runner = SchedulerRunner()
    await db_connection.create_pool()
    
    try:
        success = await runner.run_currency_update()
        if success:
            logger.info("Currency processing completed successfully")
        else:
            logger.error("Currency processing failed")
            exit(1)
    finally:
        await db_connection.close_pool()


if __name__ == "__main__":
    asyncio.run(main())