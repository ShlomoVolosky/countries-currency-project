import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

class TestDatabaseConnection:
    
    def test_database_connection(self):
        """Test database connection"""
        db = Database()
        assert db.test_connection(), "Failed to connect to database"
        db.disconnect()
    
    def test_database_config(self):
        """Test database configuration"""
        db = Database()
        config = db.config
        
        assert config.DB_HOST is not None, "DB_HOST not configured"
        assert config.DB_NAME is not None, "DB_NAME not configured"
        assert config.DB_USER is not None, "DB_USER not configured"
        assert config.DB_PASSWORD is not None, "DB_PASSWORD not configured"
        assert config.DB_PORT is not None, "DB_PORT not configured"
    
    def test_execute_query(self):
        """Test basic query execution"""
        db = Database()
        assert db.connect(), "Failed to connect to database"
        
        # Test simple query
        result = db.execute_query("SELECT 1 as test")
        assert result is not None, "Query execution failed"
        assert len(result) == 1, "Unexpected result length"
        assert result[0]['test'] == 1, "Unexpected result value"
        
        db.disconnect()
    
    def test_countries_table_exists(self):
        """Test that countries table exists"""
        db = Database()
        assert db.connect(), "Failed to connect to database"
        
        # Check if countries table exists
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'countries'
        );
        """
        result = db.execute_query(query)
        assert result is not None, "Query execution failed"
        assert result[0]['exists'], "Countries table does not exist"
        
        db.disconnect()
    
    def test_currency_rates_table_exists(self):
        """Test that currency_rates table exists"""
        db = Database()
        assert db.connect(), "Failed to connect to database"
        
        # Check if currency_rates table exists
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'currency_rates'
        );
        """
        result = db.execute_query(query)
        assert result is not None, "Query execution failed"
        assert result[0]['exists'], "Currency rates table does not exist"
        
        db.disconnect()