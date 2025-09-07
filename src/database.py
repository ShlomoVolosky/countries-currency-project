import psycopg2
from psycopg2.extras import RealDictCursor
import json
from config import Config

class Database:
    def __init__(self):
        self.config = Config()
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.config.DB_HOST,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                port=self.config.DB_PORT
            )
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch_results=True):
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                if fetch_results:
                    return cursor.fetchall()
                else:
                    return True
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return None
    
    def insert_country(self, country_data):
        query = """
        INSERT INTO countries (country_name, capitals, continent, currencies, 
                             is_un_member, population, timezone_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """
        params = (
            country_data['country_name'],
            country_data['capitals'],
            country_data['continent'],
            country_data['currencies'],
            country_data['is_un_member'],
            country_data['population'],
            json.dumps(country_data['current_time'])
        )
        return self.execute_query(query, params, fetch_results=False)
    
    def insert_currency_rate(self, country_name, currency_code, shekel_rate):
        query = """
        INSERT INTO currency_rates (country_name, currency_code, shekel_rate)
        VALUES (%s, %s, %s)
        ON CONFLICT (country_name, currency_code, rate_date) 
        DO UPDATE SET shekel_rate = EXCLUDED.shekel_rate
        """
        params = (country_name, currency_code, shekel_rate)
        return self.execute_query(query, params, fetch_results=False)
    
    def get_all_countries(self):
        query = "SELECT * FROM countries"
        return self.execute_query(query)
    
    def get_currency_rates(self, country_name=None):
        if country_name:
            query = "SELECT * FROM currency_rates WHERE country_name = %s"
            return self.execute_query(query, (country_name,))
        else:
            query = "SELECT * FROM currency_rates"
            return self.execute_query(query)
    
    def test_connection(self):
        return self.connect()