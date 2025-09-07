import pytest
import asyncio
from src.database.connection import db_connection
from src.config.settings import get_settings

class TestDatabaseConnection:
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection"""
        success = await db_connection.create_pool()
        assert success, "Failed to create database pool"
        await db_connection.close_pool()
    
    def test_database_config(self):
        """Test database configuration"""
        settings = get_settings()
        config = settings.database
        
        assert config.host is not None, "DB_HOST not configured"
        assert config.name is not None, "DB_NAME not configured"
        assert config.user is not None, "DB_USER not configured"
        assert config.port is not None, "DB_PORT not configured"
    
    @pytest.mark.asyncio
    async def test_execute_query(self):
        """Test basic query execution"""
        await db_connection.create_pool()
        
        # Test simple query
        result = await db_connection.execute_query("SELECT 1 as test")
        assert result is not None, "Query execution failed"
        assert len(result) == 1, "Unexpected result length"
        assert result[0]['test'] == 1, "Unexpected result value"
        
        await db_connection.close_pool()
    
    @pytest.mark.asyncio
    async def test_countries_table_exists(self):
        """Test that countries table exists"""
        await db_connection.create_pool()
        
        # Check if countries table exists
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'countries'
        );
        """
        result = await db_connection.execute_query(query)
        assert result is not None, "Query execution failed"
        assert result[0]['exists'], "Countries table does not exist"
        
        await db_connection.close_pool()
    
    @pytest.mark.asyncio
    async def test_currency_rates_table_exists(self):
        """Test that currency_rates table exists"""
        await db_connection.create_pool()
        
        # Check if currency_rates table exists
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'currency_rates'
        );
        """
        result = await db_connection.execute_query(query)
        assert result is not None, "Query execution failed"
        assert result[0]['exists'], "Currency rates table does not exist"
        
        await db_connection.close_pool()