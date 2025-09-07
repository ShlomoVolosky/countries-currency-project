import requests
from database import Database
from config import Config

class CurrencyProcessor:
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.supported_currencies = None
    
    def get_supported_currencies(self):
        """Get list of currencies supported by Frankfurter API"""
        if self.supported_currencies is not None:
            return self.supported_currencies
        
        try:
            response = requests.get(f"{self.config.CURRENCY_API_URL}/currencies")
            response.raise_for_status()
            data = response.json()
            self.supported_currencies = set(data.keys())
            return self.supported_currencies
        except Exception as e:
            print(f"Error fetching supported currencies: {e}")
            # Fallback to known supported currencies
            self.supported_currencies = {
                'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'EUR', 'GBP',
                'HKD', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR',
                'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'SEK', 'SGD', 'THB', 'TRY', 'USD',
                'ZAR'
            }
            return self.supported_currencies

    def get_shekel_rate(self, currency_code):
        """Get ILS rate for a specific currency using Frankfurter API"""
        if currency_code == 'ILS':
            return 1.0
        
        # Check if currency is supported by Frankfurter API
        supported_currencies = self.get_supported_currencies()
        if currency_code not in supported_currencies:
            return None
        
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
        
        # Use DISTINCT to ensure no duplicates
        query = "SELECT DISTINCT country_name, currencies FROM countries WHERE currencies IS NOT NULL AND array_length(currencies, 1) > 0"
        countries = self.db.execute_query(query)
        self.db.disconnect()
        
        if not countries:
            print("No countries found in database")
            return []
        
        return countries
    
    def get_all_currency_rates(self):
        """Get all currency rates TO ILS in one API call"""
        try:
            url = f"{self.config.CURRENCY_API_URL}/latest"
            params = {'from': 'ILS'}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            rates = data.get('rates', {})
            # Add ILS to itself
            rates['ILS'] = 1.0
            
            # Invert the rates to get FROM each currency TO ILS
            # If 1 ILS = X USD, then 1 USD = 1/X ILS
            inverted_rates = {}
            for currency, rate in rates.items():
                if currency == 'ILS':
                    inverted_rates[currency] = 1.0
                else:
                    inverted_rates[currency] = 1.0 / rate
            
            return inverted_rates
        except Exception as e:
            print(f"Error fetching all currency rates: {e}")
            return {}

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
        
        # Get supported currencies once
        supported_currencies = self.get_supported_currencies()
        print(f"Frankfurter API supports {len(supported_currencies)} currencies")
        
        # Get all currency rates in one API call
        print("Fetching all currency rates TO ILS from Frankfurter API...")
        all_rates = self.get_all_currency_rates()
        
        if not all_rates:
            print("Failed to fetch currency rates")
            self.db.disconnect()
            return False
        
        print(f"Successfully fetched rates for {len(all_rates)} currencies (FROM each currency TO ILS)")
        
        successful_updates = 0
        total_currencies = 0
        unsupported_currencies = 0
        total_countries = len(countries)
        
        for i, country in enumerate(countries, 1):
            country_name = country['country_name']
            currencies = country['currencies']
            
            print(f"[{i}/{total_countries}] Processing {country_name}...")
            
            if not currencies:
                print(f"  No currencies for {country_name}")
                continue
            
            # Separate supported and unsupported currencies
            supported_country_currencies = [c for c in currencies if c in supported_currencies]
            unsupported_country_currencies = [c for c in currencies if c not in supported_currencies]
            
            if unsupported_country_currencies:
                print(f"  Currencies: {currencies}")
                print(f"    Supported: {supported_country_currencies}")
                print(f"    Unsupported: {unsupported_country_currencies}")
            
            for currency_code in currencies:
                total_currencies += 1
                
                if currency_code not in supported_currencies:
                    unsupported_currencies += 1
                    continue
                
                # Get the rate from the pre-fetched rates
                if currency_code in all_rates:
                    shekel_rate = all_rates[currency_code]
                    
                    result = self.db.insert_currency_rate(
                        country_name, 
                        currency_code, 
                        shekel_rate
                    )
                    if result is not None:
                        successful_updates += 1
                        print(f"    Updated rate: 1 {currency_code} = {shekel_rate:.4f} ILS")
        
        self.db.disconnect()
        print(f"\nSummary:")
        print(f"  Total countries processed: {total_countries}")
        print(f"  Total currencies found: {total_currencies}")
        print(f"  Supported by API: {total_currencies - unsupported_currencies}")
        print(f"  Unsupported by API: {unsupported_currencies}")
        print(f"  Successfully updated: {successful_updates}")
        return True

def main():
    processor = CurrencyProcessor()
    processor.process_currency_rates()

if __name__ == "__main__":
    main()