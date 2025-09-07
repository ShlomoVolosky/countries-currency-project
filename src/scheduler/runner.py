import asyncio
from src.processors.countries import CountriesProcessor
from src.processors.currencies import CurrencyProcessor
from src.database.connection import db_connection
from src.utils.logger import get_logger

logger = get_logger("scheduler")


class SchedulerRunner:
    def __init__(self):
        self.countries_processor = CountriesProcessor()
        self.currency_processor = CurrencyProcessor()
    
    async def run_countries_update(self):
        logger.info("Starting countries data update")
        try:
            success = await self.countries_processor.process()
            if success:
                logger.info("Countries data update completed successfully")
            else:
                logger.error("Countries data update failed")
            return success
        except Exception as e:
            logger.error(f"Error in countries update: {e}")
            return False
    
    async def run_currency_update(self):
        logger.info("Starting currency rates update")
        try:
            success = await self.currency_processor.process()
            if success:
                logger.info("Currency rates update completed successfully")
            else:
                logger.error("Currency rates update failed")
            return success
        except Exception as e:
            logger.error(f"Error in currency update: {e}")
            return False
    
    async def run_initial_setup(self):
        logger.info("Running initial data setup")
        
        await db_connection.create_pool()
        logger.info("Database connection established")
        
        try:
            logger.info("Step 1: Loading countries data")
            countries_success = await self.run_countries_update()
            
            logger.info("Step 2: Loading currency rates")
            currency_success = await self.run_currency_update()
            
            if countries_success and currency_success:
                logger.info("Initial setup completed successfully")
                return True
            else:
                logger.error("Initial setup failed")
                return False
                
        except Exception as e:
            logger.error(f"Initial setup failed: {e}")
            return False
        finally:
            await db_connection.close_pool()
            logger.info("Database connection closed")
    
    def run_initial_setup_sync(self):
        """Synchronous wrapper for run_initial_setup"""
        return asyncio.run(self.run_initial_setup())
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        import schedule
        import time
        
        # Schedule countries update every 6 hours
        schedule.every(6).hours.do(lambda: asyncio.run(self.run_countries_update()))
        
        # Schedule currency update every hour
        schedule.every().hour.do(lambda: asyncio.run(self.run_currency_update()))
        
        logger.info("Schedule setup completed")


async def main():
    runner = SchedulerRunner()
    
    print("Countries Currency Service - Scheduler")
    print("=" * 40)
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
