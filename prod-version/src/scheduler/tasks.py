"""
Scheduled task definitions for the Countries Currency Project.

This module provides the main scheduler and task definitions
for automated data processing.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from threading import Thread, Event
import schedule

from config.settings import get_settings
from processors.country_processor import CountryProcessor
from processors.currency_processor import CurrencyProcessor
from utils.logger import get_logger

logger = get_logger(__name__)


class TaskResult:
    """Result of a task execution."""
    
    def __init__(self, task_name: str, success: bool, start_time: datetime, end_time: Optional[datetime] = None, error: Optional[Exception] = None):
        self.task_name = task_name
        self.success = success
        self.start_time = start_time
        self.end_time = end_time or datetime.utcnow()
        self.error = error
        self.duration = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_name': self.task_name,
            'success': self.success,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration,
            'error': str(self.error) if self.error else None
        }


class ScheduledTask:
    """Wrapper for scheduled tasks with logging and error handling."""
    
    def __init__(self, name: str, func: Callable, *args, **kwargs):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.logger = get_logger(f"Task.{name}")
        self.last_result: Optional[TaskResult] = None
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
    
    def execute(self) -> TaskResult:
        """Execute the task with error handling and logging."""
        start_time = datetime.utcnow()
        self.execution_count += 1
        
        self.logger.info(f"Starting task: {self.name}")
        
        try:
            result = self.func(*self.args, **self.kwargs)
            success = bool(result) if isinstance(result, bool) else True
            
            if success:
                self.success_count += 1
                self.logger.info(f"Task {self.name} completed successfully")
            else:
                self.error_count += 1
                self.logger.warning(f"Task {self.name} completed with warnings")
            
            self.last_result = TaskResult(self.name, success, start_time)
            return self.last_result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Task {self.name} failed: {e}", exc_info=True)
            self.last_result = TaskResult(self.name, False, start_time, error=e)
            return self.last_result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task execution statistics."""
        success_rate = (self.success_count / self.execution_count * 100) if self.execution_count > 0 else 0
        
        return {
            'name': self.name,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'last_result': self.last_result.to_dict() if self.last_result else None
        }


class SchedulerManager:
    """Main scheduler manager for the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.stop_event = Event()
        self.scheduler_thread: Optional[Thread] = None
        
        # Initialize processors
        self.country_processor = CountryProcessor()
        self.currency_processor = CurrencyProcessor()
        
        # Setup tasks
        self._setup_tasks()
    
    def _setup_tasks(self):
        """Setup scheduled tasks."""
        # Countries data update task
        countries_task = ScheduledTask(
            "countries_update",
            self._run_countries_update
        )
        self.tasks["countries_update"] = countries_task
        
        # Currency rates update task
        currency_task = ScheduledTask(
            "currency_update",
            self._run_currency_update
        )
        self.tasks["currency_update"] = currency_task
    
    def _run_countries_update(self) -> bool:
        """Run countries data update."""
        self.logger.info("Starting countries data update...")
        try:
            return self.country_processor.run()
        except Exception as e:
            self.logger.error(f"Error in countries update: {e}", exc_info=True)
            return False
    
    def _run_currency_update(self) -> bool:
        """Run currency rates update."""
        self.logger.info("Starting currency rates update...")
        try:
            return self.currency_processor.run()
        except Exception as e:
            self.logger.error(f"Error in currency update: {e}", exc_info=True)
            return False
    
    def setup_schedule(self):
        """Setup the scheduling configuration."""
        # Clear existing jobs
        schedule.clear()
        
        # Countries data update - weekly on Sunday at 2 AM
        schedule.every().sunday.at("02:00").do(self.tasks["countries_update"].execute)
        
        # Currency rates update - every 6 hours
        schedule.every(6).hours.do(self.tasks["currency_update"].execute)
        
        self.logger.info("Scheduler configured:")
        self.logger.info("- Countries data: Weekly on Sunday at 02:00")
        self.logger.info("- Currency rates: Every 6 hours")
    
    def run_scheduler_loop(self):
        """Main scheduler loop."""
        self.logger.info("Scheduler started")
        
        while not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(60)  # Wait before retrying
        
        self.logger.info("Scheduler stopped")
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.running = True
        self.stop_event.clear()
        
        # Start scheduler in separate thread
        self.scheduler_thread = Thread(target=self.run_scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping scheduler...")
        self.running = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)
        
        self.logger.info("Scheduler stopped")
    
    def run_task_now(self, task_name: str) -> Optional[TaskResult]:
        """Run a specific task immediately."""
        if task_name not in self.tasks:
            self.logger.error(f"Task {task_name} not found")
            return None
        
        self.logger.info(f"Running task {task_name} immediately...")
        return self.tasks[task_name].execute()
    
    def get_task_stats(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """Get task execution statistics."""
        if task_name:
            if task_name not in self.tasks:
                return {}
            return self.tasks[task_name].get_stats()
        else:
            return {name: task.get_stats() for name, task in self.tasks.items()}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status information."""
        return {
            'running': self.running,
            'tasks_count': len(self.tasks),
            'next_run_times': {
                job.job_func.__name__: str(job.next_run) 
                for job in schedule.jobs
            },
            'task_stats': self.get_task_stats()
        }
    
    def run_initial_setup(self) -> bool:
        """Run initial data setup."""
        self.logger.info("Running initial data setup...")
        
        # Run countries update
        countries_result = self.run_task_now("countries_update")
        if not countries_result or not countries_result.success:
            self.logger.error("Initial countries setup failed")
            return False
        
        # Run currency update
        currency_result = self.run_task_now("currency_update")
        if not currency_result or not currency_result.success:
            self.logger.error("Initial currency setup failed")
            return False
        
        self.logger.info("Initial setup completed successfully")
        return True


# Global scheduler instance
_scheduler_manager: Optional[SchedulerManager] = None


def get_scheduler_manager() -> SchedulerManager:
    """Get the global scheduler manager instance."""
    global _scheduler_manager
    if _scheduler_manager is None:
        _scheduler_manager = SchedulerManager()
    return _scheduler_manager


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler_manager()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    scheduler = get_scheduler_manager()
    scheduler.stop()


def run_task_now(task_name: str) -> Optional[TaskResult]:
    """Run a specific task immediately."""
    scheduler = get_scheduler_manager()
    return scheduler.run_task_now(task_name)


def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status."""
    scheduler = get_scheduler_manager()
    return scheduler.get_scheduler_status()
