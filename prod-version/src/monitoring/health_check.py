import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from config.settings import get_settings
from database.connection import get_database_connection
from api.countries_api import CountriesAPIClient
from api.frankfurter_api import FrankfurterAPIClient
from utils.logger import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    def __init__(self, name: str, check_func, critical: bool = True):
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.last_check: Optional[datetime] = None
        self.last_status: HealthStatus = HealthStatus.UNKNOWN
        self.last_error: Optional[str] = None
        self.check_duration: Optional[float] = None
    
    def run_check(self) -> HealthStatus:
        return {
            'name': self.name,
            'status': self.last_status.value,
            'critical': self.critical,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'duration_seconds': self.check_duration,
            'error': self.last_error
        }

class HealthChecker:
        self.add_check(
            "database",
            self._check_database,
            critical=True
        )
        self.add_check(
            "countries_api",
            self._check_countries_api,
            critical=True
        )
        
        self.add_check(
            "currency_api",
            self._check_currency_api,
            critical=True
        )
        
        self.add_check(
            "configuration",
            self._check_configuration,
            critical=True
        )
    
    def add_check(self, name: str, check_func, critical: bool = True):
        try:
            db = get_database_connection()
            return db.test_connection()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    def _check_countries_api(self) -> bool:
        try:
            api = FrankfurterAPIClient()
            return api.test_connection()
        except Exception as e:
            logger.error(f"Currency API health check failed: {e}")
            return False
    def _check_configuration(self) -> bool:
        self.logger.info("Running health checks...")
        results = {}
        overall_status = HealthStatus.HEALTHY
        critical_failures = 0
        
        for check in self.checks:
            status = check.run_check()
            results[check.name] = check.to_dict()
            
            if status == HealthStatus.UNHEALTHY:
                if check.critical:
                    critical_failures += 1
                    overall_status = HealthStatus.UNHEALTHY
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': results,
            'summary': {
                'total_checks': len(self.checks),
                'healthy_checks': sum(1 for r in results.values() if r['status'] == HealthStatus.HEALTHY.value),
                'unhealthy_checks': sum(1 for r in results.values() if r['status'] == HealthStatus.UNHEALTHY.value),
                'critical_failures': critical_failures
            }
        }
    
    def run_check(self, name: str) -> Optional[Dict[str, Any]]:
        return {
            'overall_status': self._determine_overall_status(),
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {check.name: check.to_dict() for check in self.checks}
        }
    def _determine_overall_status(self) -> str:
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker

def check_health() -> Dict[str, Any]:
    checker = get_health_checker()
    return checker.get_status()