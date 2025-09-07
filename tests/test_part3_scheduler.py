import pytest
from src.scheduler.runner import SchedulerRunner
from unittest.mock import patch, MagicMock
import schedule

# Alias for backward compatibility
AutomatedScheduler = SchedulerRunner

class TestPart3Scheduler:
    
    def test_scheduler_init(self):
        """Test AutomatedScheduler initialization"""
        scheduler = AutomatedScheduler()
        assert scheduler.countries_processor is not None
        assert scheduler.currency_processor is not None
    
    @patch('src.processors.countries.CountriesProcessor')
    def test_run_countries_update_success(self, mock_countries_processor):
        """Test successful countries update"""
        # Mock successful processing
        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception
        import asyncio
        asyncio.run(scheduler.run_countries_update())
        mock_instance.process.assert_called_once()
    
    @patch('src.processors.countries.CountriesProcessor')
    def test_run_countries_update_failure(self, mock_countries_processor):
        """Test countries update failure"""
        # Mock failed processing
        mock_instance = MagicMock()
        mock_instance.process.return_value = False
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception
        import asyncio
        asyncio.run(scheduler.run_countries_update())
        mock_instance.process.assert_called_once()
    
    @patch('src.processors.currencies.CurrencyProcessor')
    def test_run_currency_update_success(self, mock_currency_processor):
        """Test successful currency update"""
        # Mock successful processing
        mock_instance = MagicMock()
        mock_instance.process.return_value = True
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception
        import asyncio
        asyncio.run(scheduler.run_currency_update())
        mock_instance.process.assert_called_once()
    
    @patch('src.processors.currencies.CurrencyProcessor')
    def test_run_currency_update_failure(self, mock_currency_processor):
        """Test currency update failure"""
        # Mock failed processing
        mock_instance = MagicMock()
        mock_instance.process.return_value = False
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception
        import asyncio
        asyncio.run(scheduler.run_currency_update())
        mock_instance.process.assert_called_once()
    
    def test_setup_schedule(self):
        """Test schedule setup"""
        scheduler = AutomatedScheduler()
        
        # Clear any existing schedules
        schedule.clear()
        
        scheduler.setup_schedule()
        
        # Check that jobs were scheduled
        jobs = schedule.get_jobs()
        assert len(jobs) > 0
        
        # Clear schedules after test
        schedule.clear()
    
    @patch('src.scheduler.runner.SchedulerRunner.run_countries_update')
    @patch('src.scheduler.runner.SchedulerRunner.run_currency_update')
    def test_run_initial_setup(self, mock_currency_update, mock_countries_update):
        """Test initial setup runs both updates"""
        scheduler = AutomatedScheduler()
        
        scheduler.run_initial_setup_sync()
        
        mock_countries_update.assert_called_once()
        mock_currency_update.assert_called_once()
    
    @patch('src.processors.countries.CountriesProcessor')
    def test_run_countries_update_exception_handling(self, mock_countries_processor):
        """Test exception handling in countries update"""
        # Mock exception
        mock_instance = MagicMock()
        mock_instance.process.side_effect = Exception("Test exception")
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception, should handle it gracefully
        import asyncio
        asyncio.run(scheduler.run_countries_update())
    
    @patch('src.processors.currencies.CurrencyProcessor')
    def test_run_currency_update_exception_handling(self, mock_currency_processor):
        """Test exception handling in currency update"""
        # Mock exception
        mock_instance = MagicMock()
        mock_instance.process.side_effect = Exception("Test exception")
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception, should handle it gracefully
        import asyncio
        asyncio.run(scheduler.run_currency_update())