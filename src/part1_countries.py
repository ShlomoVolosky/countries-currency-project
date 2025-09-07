import requests
import pytz
from datetime import datetime
from database import Database
from config import Config

class CountriesProcessor:
    def __init__(self):
        self.config = Config()
        self.db = Database()
    
    def fetch_countries_data(self):
        """Fetch countries data from REST Countries API"""
        try:
            response = requests.get(self.config.COUNTRIES_API_URL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching countries data: {e}")
            return None
    
    def get_current_time_for_timezones(self, timezones):
        """Get current time for each timezone in the country"""
        current_times = {}
        
        if not timezones:
            return current_times
        
        for timezone_str in timezones:
            try:
                # Handle UTC format
                if timezone_str.startswith('UTC'):
                    if timezone_str == 'UTC':
                        timezone_str = 'UTC'
                    else:
                        # Convert UTC+X or UTC-X to proper format
                        timezone_str = timezone_str.replace('UTC+', '+').replace('UTC-', '-')
                        if timezone_str in ['+00:00', '-00:00']:
                            timezone_str = 'UTC'
                
                # Try to get timezone
                try:
                    tz = pytz.timezone(timezone_str)
                except pytz.exceptions.UnknownTimeZoneError:
                    # If timezone not found, try to handle UTC offset format
                    if timezone_str.startswith(('+', '-')) and ':' in timezone_str:
                        # Skip invalid timezone formats
                        continue
                    else:
                        continue
                
                current_time = datetime.now(tz)
                current_times[timezone_str] = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                
            except Exception as e:
                print(f"Error processing timezone {timezone_str}: {e}")
                continue
        
        return current_times
    
    def format_country_data(self, country):
        """Format country data according to requirements"""
        try:
            # Extract country name
            country_name = country.get('name', {}).get('common', '')
            
            # Extract capitals (can be multiple)
            capitals = country.get('capital', [])
            if not isinstance(capitals, list):
                capitals = [capitals] if capitals else []
            
            # Extract continent
            continent = country.get('continents', [''])[0] if country.get('continents') else ''
            
            # Extract currencies
            currencies_dict = country.get('currencies', {})
            currencies = list(currencies_dict.keys()) if currencies_dict else []
            
            # Extract UN membership
            is_un_member = country.get('unMember', False)
            
            # Extract population
            population = country.get('population', 0)
            
            # Extract timezones and get current time
            timezones = country.get('timezones', [])
            current_time = self.get_current_time_for_timezones(timezones)
            
            return {
                'country_name': country_name,
                'capitals': capitals,
                'continent': continent,
                'currencies': currencies,
                'is_un_member': is_un_member,
                'population': population,
                'current_time': current_time
            }
        except Exception as e:
            print(f"Error formatting country data: {e}")
            return None
    
    def process_and_save_countries(self):
        """Main function to process and save countries data"""
        print("Fetching countries data...")
        countries_data = self.fetch_countries_data()
        
        if not countries_data:
            print("Failed to fetch countries data")
            return False
        
        print(f"Processing {len(countries_data)} countries...")
        
        if not self.db.connect():
            print("Failed to connect to database")
            return False
        
        successful_inserts = 0
        total_countries = len(countries_data)
        
        for i, country in enumerate(countries_data, 1):
            print(f"[{i}/{total_countries}] Processing {country.get('name', {}).get('common', 'Unknown')}...")
            
            formatted_data = self.format_country_data(country)
            if formatted_data and formatted_data['country_name']:
                result = self.db.insert_country(formatted_data)
                if result is not None:
                    successful_inserts += 1
                    print(f"  Inserted: {formatted_data['country_name']}")
        
        self.db.disconnect()
        print(f"Successfully processed {successful_inserts} countries")
        return True

def main():
    processor = CountriesProcessor()
    processor.process_and_save_countries()

if __name__ == "__main__":
    main()