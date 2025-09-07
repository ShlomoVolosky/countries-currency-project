import schedule
import time
from datetime import datetime
from part1_countries import CountriesProcessor
from part2_currencies import CurrencyProcessor

class AutomatedScheduler:
    def __init__(self):
        self.countries_processor = CountriesProcessor()
        self.currency_processor = CurrencyProcessor()
    
    def run_countries_update(self):
        """Run countries data update with logging"""
        print(f"[{datetime.now()}] Starting countries data update...")
        try:
            success = self.countries_processor.process_and_save_countries()
            if success:
                print(f"[{datetime.now()}] Countries data update completed successfully")
            else:
                print(f"[{datetime.now()}] Countries data update failed")
        except Exception as e:
            print(f"[{datetime.now()}] Error in countries update: {e}")
    
    def run_currency_update(self):
        """Run currency rates update with logging"""
        print(f"[{datetime.now()}] Starting currency rates update...")
        try:
            success = self.currency_processor.process_currency_rates()
            if success:
                print(f"[{datetime.now()}] Currency rates update completed successfully")
            else:
                print(f"[{datetime.now()}] Currency rates update failed")
        except Exception as e:
            print(f"[{datetime.now()}] Error in currency update: {e}")
    
    def setup_schedule(self):
        """Setup automated schedule for data updates"""
        
        # Countries data update - once a week on Sunday at 02:00
        # (Countries data doesn't change frequently)
        schedule.every().sunday.at("02:00").do(self.run_countries_update)
        
        # Currency rates update - every 6 hours
        # (Exchange rates change frequently during trading hours)
        schedule.every(6).hours.do(self.run_currency_update)
        
        # Alternative scheduling options:
        # Daily currency update at 06:00 (before market opens)
        # schedule.every().day.at("06:00").do(self.run_currency_update)
        
        print("Scheduler configured:")
        print("- Countries data: Weekly on Sunday at 02:00")
        print("- Currency rates: Every 6 hours")
        print("Scheduler started. Press Ctrl+C to stop.")
    
    def run_scheduler(self):
        """Start the scheduler"""
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
    
    def run_initial_setup(self):
        """Run initial data load"""
        print("Running initial data setup...")
        print("Step 1: Loading countries data...")
        self.run_countries_update()
        
        print("\nStep 2: Loading currency rates...")
        self.run_currency_update()
        
        print("\nInitial setup completed!")

def main():
    scheduler = AutomatedScheduler()
    
    print("Automated Data Update Scheduler")
    print("=" * 40)
    print("1. Run initial setup (load all data now)")
    print("2. Start scheduler (automated updates)")
    print("3. Run countries update only")
    print("4. Run currency update only")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        scheduler.run_initial_setup()
    elif choice == "2":
        scheduler.run_scheduler()
    elif choice == "3":
        scheduler.run_countries_update()
    elif choice == "4":
        scheduler.run_currency_update()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()