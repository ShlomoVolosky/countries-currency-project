import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler.runner import SchedulerRunner
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("part3_scheduler")


async def main():
    runner = SchedulerRunner()
    
    print("Countries Currency Service - Legacy Scheduler")
    print("=" * 50)
    print("Note: For production use, please use Airflow DAGs instead")
    print("1. Run initial setup (load all data now)")
    print("2. Run countries update only")
    print("3. Run currency update only")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        success = await runner.run_initial_setup()
        if success:
            print("Initial setup completed successfully!")
        else:
            print("Initial setup failed!")
            exit(1)
    elif choice == "2":
        await db_connection.create_pool()
        success = await runner.run_countries_update()
        await db_connection.close_pool()
        if not success:
            exit(1)
    elif choice == "3":
        await db_connection.create_pool()
        success = await runner.run_currency_update()
        await db_connection.close_pool()
        if not success:
            exit(1)
    else:
        print("Invalid choice")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())