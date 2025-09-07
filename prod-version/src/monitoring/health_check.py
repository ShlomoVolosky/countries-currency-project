"""
Health check functionality for the Countries Currency Project.

This module provides health check endpoints and monitoring
for the application components.
"""

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
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthCheck:
    """Individual health check component."""
    
    def __init__(self, name: str, check_func, critical: bool = True):
        self.name = name
        self.check_func = check_func
        self.critical = critical
        self.last_check: Optional[datetime] = None
        self.last_status: HealthStatus = HealthStatus.UNKNOWN
        self.last_error: Optional[str] = None
        self.check_duration: Optional[float] = None
    
    def run_check(self) -> HealthStatus:
        """Run the health check."""
        start_time = datetime.utcnow()
        
        try:
            result = self.check_func()
            self.check_duration = (datetime.utcnow() - start_time).total_seconds()
            
            if result:
                self.last_status = HealthStatus.HEALTHY
                self.last_error = None
            else:
                self.last_status = HealthStatus.UNHEALTHY
                self.last_error = "Check returned False"
            
        except Exception as e:
            self.check_duration = (datetime.utcnow() - start_time).total_seconds()
            self.last_status = HealthStatus.UNHEALTHY
            self.last_error = str(e)
            logger.error(f"Health check {self.name} failed: {e}")
        
        self.last_check = datetime.utcnow()
        return self.last_status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'status': self.last_status.value,
            'critical': self.critical,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'duration_seconds': self.check_duration,
            'error': self.last_error
        }


class HealthChecker:
    """Main health checker for the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.checks: List[HealthCheck] = []
        self._setup_checks()
    
    def _setup_checks(self):
        """Setup health checks."""
        # Database health check
        self.add_check(
            "database",
            self._check_database,
            critical=True
        )
        
        # Countries API health check
        self.add_check(
            "countries_api",
            self._check_countries_api,
            critical=True
        )
        
        # Currency API health check
        self.add_check(
            "currency_api",
            self._check_currency_api,
            critical=True
        )
        
        # Application configuration check
        self.add_check(
            "configuration",
            self._check_configuration,
            critical=True
        )
    
    def add_check(self, name: str, check_func, critical: bool = True):
        """Add a health check."""
        check = HealthCheck(name, check_func, critical)
        self.checks.append(check)
    
    def _check_database(self) -> bool:
        """Check database connectivity."""
        try:
            db = get_database_connection()
            return db.test_connection()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _check_countries_api(self) -> bool:
        """Check REST Countries API connectivity."""
        try:
            api = CountriesAPIClient()
            return api.test_connection()
        except Exception as e:
            logger.error(f"Countries API health check failed: {e}")
            return False
    
    def _check_currency_api(self) -> bool:
        """Check Frankfurter API connectivity."""
        try:
            api = FrankfurterAPIClient()
            return api.test_connection()
        except Exception as e:
            logger.error(f"Currency API health check failed: {e}")
            return False
    
    def _check_configuration(self) -> bool:
        """Check application configuration."""
        try:
            settings = get_settings()
            
            # Check required settings
            if not settings.database.host:
                return False
            
            if not settings.database.name:
                return False
            
            if not settings.api.countries_url:
                return False
            
            if not settings.api.currency_url:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Configuration health check failed: {e}")
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
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
        """Run a specific health check."""
        for check in self.checks:
            if check.name == name:
                check.run_check()
                return check.to_dict()
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health status without running checks."""
        return {
            'overall_status': self._determine_overall_status(),
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {check.name: check.to_dict() for check in self.checks}
        }
    
    def _determine_overall_status(self) -> str:
        """Determine overall status from last check results."""
        if not self.checks:
            return HealthStatus.UNKNOWN.value
        
        critical_failures = sum(
            1 for check in self.checks 
            if check.critical and check.last_status == HealthStatus.UNHEALTHY
        )
        
        if critical_failures > 0:
            return HealthStatus.UNHEALTHY.value
        
        unhealthy_checks = sum(
            1 for check in self.checks 
            if check.last_status == HealthStatus.UNHEALTHY
        )
        
        if unhealthy_checks > 0:
            return HealthStatus.DEGRADED.value
        
        return HealthStatus.HEALTHY.value


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def check_health() -> Dict[str, Any]:
    """Check application health."""
    checker = get_health_checker()
    return checker.run_all_checks()


def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    checker = get_health_checker()
    return checker.get_status()
