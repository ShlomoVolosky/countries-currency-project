import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'countries_db')
    DB_USER = os.getenv('DB_USER', 'countries_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # API URLs
    COUNTRIES_API_URL = "https://restcountries.com/v3.1/all?fields=name,capital,continents,currencies,unMember,population,timezones"
    CURRENCY_API_URL = "https://api.frankfurter.app"
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"