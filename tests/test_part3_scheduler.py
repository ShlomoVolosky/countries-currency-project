import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from part3_scheduler import AutomatedScheduler
from unittest.mock import patch, MagicMock
import schedule

class TestPart3Scheduler:
    
    def test_scheduler_init(self):
        """Test AutomatedScheduler initialization"""
        scheduler = AutomatedScheduler()
        assert scheduler.countries_processor is not None
        assert scheduler.currency_processor is not None
    
    @patch('part3_scheduler.CountriesProcessor')
    def test_run_countries_update_success(self, mock_countries_processor):
        """Test successful countries update"""
        # Mock successful processing
        mock_instance = MagicMock()
        mock_instance.process_and_save_countries.return_value = True
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception
        scheduler.run_countries_update()
        mock_instance.process_and_save_countries.assert_called_once()
    
    @patch('part3_scheduler.CountriesProcessor')
    def test_run_countries_update_failure(self, mock_countries_processor):
        """Test countries update failure"""
        # Mock failed processing
        mock_instance = MagicMock()
        mock_instance.process_and_save_countries.return_value = False
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception
        scheduler.run_countries_update()
        mock_instance.process_and_save_countries.assert_called_once()
    
    @patch('part3_scheduler.CurrencyProcessor')
    def test_run_currency_update_success(self, mock_currency_processor):
        """Test successful currency update"""
        # Mock successful processing
        mock_instance = MagicMock()
        mock_instance.process_currency_rates.return_value = True
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception
        scheduler.run_currency_update()
        mock_instance.process_currency_rates.assert_called_once()
    
    @patch('part3_scheduler.CurrencyProcessor')
    def test_run_currency_update_failure(self, mock_currency_processor):
        """Test currency update failure"""
        # Mock failed processing
        mock_instance = MagicMock()
        mock_instance.process_currency_rates.return_value = False
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception
        scheduler.run_currency_update()
        mock_instance.process_currency_rates.assert_called_once()
    
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
    
    @patch('part3_scheduler.AutomatedScheduler.run_countries_update')
    @patch('part3_scheduler.AutomatedScheduler.run_currency_update')
    def test_run_initial_setup(self, mock_currency_update, mock_countries_update):
        """Test initial setup runs both updates"""
        scheduler = AutomatedScheduler()
        
        scheduler.run_initial_setup()
        
        mock_countries_update.assert_called_once()
        mock_currency_update.assert_called_once()
    
    @patch('part3_scheduler.CountriesProcessor')
    def test_run_countries_update_exception_handling(self, mock_countries_processor):
        """Test exception handling in countries update"""
        # Mock exception
        mock_instance = MagicMock()
        mock_instance.process_and_save_countries.side_effect = Exception("Test exception")
        mock_countries_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.countries_processor = mock_instance
        
        # Should not raise exception, should handle it gracefully
        scheduler.run_countries_update()
    
    @patch('part3_scheduler.CurrencyProcessor')
    def test_run_currency_update_exception_handling(self, mock_currency_processor):
        """Test exception handling in currency update"""
        # Mock exception
        mock_instance = MagicMock()
        mock_instance.process_currency_rates.side_effect = Exception("Test exception")
        mock_currency_processor.return_value = mock_instance
        
        scheduler = AutomatedScheduler()
        scheduler.currency_processor = mock_instance
        
        # Should not raise exception, should handle it gracefully
        scheduler.run_currency_update()