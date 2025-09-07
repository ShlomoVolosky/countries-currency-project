#!/usr/bin/env python3

import sys
import argparse
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config.settings import get_settings
from utils.logger import setup_logging
from processors.country_processor import CountryProcessor
from processors.currency_processor import CurrencyProcessor
from scheduler.tasks import SchedulerManager


def setup_application():
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    return settings


def run_countries_update():
    logger = logging.getLogger(__name__)
    logger.info("Starting countries data update...")
    
    try:
        processor = CountryProcessor()
        success = processor.process_and_save_countries()
        
        if success:
            logger.info("Countries data update completed successfully")
            return True
        else:
            logger.error("Countries data update failed")
            return False
    except Exception as e:
        logger.error(f"Error in countries update: {e}", exc_info=True)
        return False


def run_currency_update():
    logger = logging.getLogger(__name__)
    logger.info("Starting currency rates update...")
    
    try:
        processor = CurrencyProcessor()
        success = processor.process_currency_rates()
        
        if success:
            logger.info("Currency rates update completed successfully")
            return True
        else:
            logger.error("Currency rates update failed")
            return False
    except Exception as e:
        logger.error(f"Error in currency update: {e}", exc_info=True)
        return False


def run_scheduler():
    logger = logging.getLogger(__name__)
    logger.info("Starting automated scheduler...")
    
    try:
        scheduler = SchedulerManager()
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduler: {e}", exc_info=True)


def run_initial_setup():
    logger = logging.getLogger(__name__)
    logger.info("Running initial data setup...")
    
    countries_success = run_countries_update()
    currency_success = run_currency_update()
    
    if countries_success and currency_success:
        logger.info("Initial setup completed successfully")
        return True
    else:
        logger.error("Initial setup failed")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["countries", "currency", "scheduler", "setup"])
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    
    args = parser.parse_args()
    
    settings = setup_application()
    
    if args.log_level != settings.LOG_LEVEL:
        setup_logging(args.log_level)
    if args.command == "countries":
        success = run_countries_update()
        sys.exit(0 if success else 1)
    elif args.command == "currency":
        success = run_currency_update()
        sys.exit(0 if success else 1)
    elif args.command == "scheduler":
        run_scheduler()
    elif args.command == "setup":
        success = run_initial_setup()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
