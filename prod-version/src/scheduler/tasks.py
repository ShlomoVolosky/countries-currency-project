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
        return {
            'task_name': self.task_name,
            'success': self.success,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration,
            'error': str(self.error) if self.error else None
        }

class ScheduledTask:
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
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.stop_event = Event()
        self.scheduler_thread: Optional[Thread] = None
        
        self.country_processor = CountryProcessor()
        self.currency_processor = CurrencyProcessor()
        
        self._setup_tasks()
    
    def _setup_tasks(self):
        self.logger.info("Starting countries data update...")
        try:
            return self.country_processor.run()
        except Exception as e:
            self.logger.error(f"Error in countries update: {e}", exc_info=True)
            return False
    def _run_currency_update(self) -> bool:
        schedule.clear()
        schedule.every().sunday.at("02:00").do(self.tasks["countries_update"].execute)
        
        schedule.every(6).hours.do(self.tasks["currency_update"].execute)
        
        self.logger.info("Scheduler configured:")
        self.logger.info("- Countries data: Weekly on Sunday at 02:00")
        self.logger.info("- Currency rates: Every 6 hours")
    
    def run_scheduler_loop(self):
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        self.setup_schedule()
        self.running = True
        self.stop_event.clear()
        
        self.scheduler_thread = Thread(target=self.run_scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler started successfully")
    
    def stop(self):
        if task_name not in self.tasks:
            self.logger.error(f"Task {task_name} not found")
            return None
        self.logger.info(f"Running task {task_name} immediately...")
        return self.tasks[task_name].execute()
    
    def get_task_stats(self, task_name: Optional[str] = None) -> Dict[str, Any]:
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
    global _scheduler_manager
    if _scheduler_manager is None:
        _scheduler_manager = SchedulerManager()
    return _scheduler_manager

def start_scheduler():
    scheduler = get_scheduler_manager()
    scheduler.stop()

def run_task_now(task_name: str) -> Optional[TaskResult]:
    scheduler = get_scheduler_manager()
    return scheduler.get_scheduler_status()