import requests
from database import Database
from config import Config

class CurrencyProcessor:
    def __init__(self):
        self.config = Config()
        self.db = Database()
    
    def get_shekel_rate(self, currency_code):
        """Get ILS rate for a specific currency using Frankfurter API"""
        if currency_code == 'ILS':
            return 1.0
        
        try:
            # Frankfurter API endpoint for latest rates
            url = f"{self.config.CURRENCY_API_URL}/latest"
            params = {
                'from': 'ILS',
                'to': currency_code
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Return the rate (how much of target currency equals 1 ILS)
            rate = data.get('rates', {}).get(currency_code)
            if rate:
                return float(rate)
            else:
                # Try the reverse - from currency to ILS
                params = {
                    'from': currency_code,
                    'to': 'ILS'
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                rate = data.get('rates', {}).get('ILS')
                if rate:
                    return float(rate)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching rate for {currency_code}: {e}")
        except Exception as e:
            print(f"Error processing rate for {currency_code}: {e}")
        
        return None
    
    def get_all_countries_with_currencies(self):
        """Get all countries and their currencies from database"""
        if not self.db.connect():
            print("Failed to connect to database")
            return []
        
        countries = self.db.get_all_countries()
        self.db.disconnect()
        
        if not countries:
            print("No countries found in database")
            return []
        
        return countries
    
    def process_currency_rates(self):
        """Process and save currency rates for all countries"""
        print("Fetching countries and currencies...")
        countries = self.get_all_countries_with_currencies()
        
        if not countries:
            print("No countries to process")
            return False
        
        if not self.db.connect():
            print("Failed to connect to database")
            return False
        
        successful_updates = 0
        total_currencies = 0
        
        for country in countries:
            country_name = country['country_name']
            currencies = country['currencies']
            
            if not currencies:
                print(f"No currencies for {country_name}")
                continue
            
            print(f"Processing {country_name} with currencies: {currencies}")
            
            for currency_code in currencies:
                total_currencies += 1
                
                # Get the shekel rate for this currency
                shekel_rate = self.get_shekel_rate(currency_code)
                
                if shekel_rate is not None:
                    result = self.db.insert_currency_rate(
                        country_name, 
                        currency_code, 
                        shekel_rate
                    )
                    if result is not None:
                        successful_updates += 1
                        print(f"Updated rate for {country_name} - {currency_code}: {shekel_rate}")
                else:
                    print(f"Could not get rate for {country_name} - {currency_code}")
        
        self.db.disconnect()
        print(f"Successfully updated {successful_updates} out of {total_currencies} currency rates")
        return True

def main():
    processor = CurrencyProcessor()
    processor.process_currency_rates()

if __name__ == "__main__":
    main()