import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


def get_current_time_for_timezones(timezones: List[str]) -> Dict[str, str]:
    current_times = {}
    if not timezones:
        return current_times
    
    for timezone_str in timezones:
        try:
            if timezone_str.startswith('UTC'):
                if timezone_str == 'UTC':
                    timezone_str = 'UTC'
                else:
                    timezone_str = timezone_str.replace('UTC+', '+').replace('UTC-', '-')
                    if timezone_str in ['+00:00', '-00:00']:
                        timezone_str = 'UTC'
            
            try:
                tz = pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                if timezone_str.startswith(('+', '-')) and ':' in timezone_str:
                    continue
                else:
                    continue
            
            current_time = datetime.now(tz)
            current_times[timezone_str] = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            
        except Exception as e:
            logger.warning(f"Error processing timezone {timezone_str}: {e}")
            continue
    
    return current_times


def normalize_timezone(timezone_str: str) -> Optional[str]:
    if not timezone_str:
        return None
    if timezone_str.startswith('UTC'):
        if timezone_str == 'UTC':
            return 'UTC'
        else:
            normalized = timezone_str.replace('UTC+', '+').replace('UTC-', '-')
            if normalized in ['+00:00', '-00:00']:
                return 'UTC'
            return normalized
    
    try:
        pytz.timezone(timezone_str)
        return timezone_str
    except pytz.exceptions.UnknownTimeZoneError:
        return None


def get_timezone_info(timezone_str: str) -> Optional[Dict[str, Union[str, int]]]:
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        return {
            'timezone': timezone_str,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'utc_offset': now.strftime('%z'),
            'dst_active': now.dst() != timedelta(0),
            'timezone_name': now.tzname()
        }
    except Exception as e:
        logger.warning(f"Error getting timezone info for {timezone_str}: {e}")
        return None


def convert_time_to_timezone(dt: datetime, target_timezone: str) -> Optional[datetime]:
    try:
        tz = pytz.timezone(target_timezone)
        return dt.astimezone(tz)
    except Exception as e:
        logger.warning(f"Error converting time to {target_timezone}: {e}")
        return None

def get_common_timezones() -> List[str]:
    return [
        'UTC',
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Kolkata',
        'Australia/Sydney',
        'Pacific/Auckland'
    ]

def is_timezone_valid(timezone_str: str) -> bool:
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False

def get_timezone_offset(timezone_str: str) -> Optional[int]:
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        offset = now.utcoffset()
        return int(offset.total_seconds() / 60) if offset else 0
    except Exception as e:
        logger.warning(f"Error getting timezone offset for {timezone_str}: {e}")
        return None

def group_timezones_by_offset(timezones: List[str]) -> Dict[int, List[str]]:
    groups = {}
    for tz_str in timezones:
        offset = get_timezone_offset(tz_str)
        if offset is not None:
            if offset not in groups:
                groups[offset] = []
            groups[offset].append(tz_str)
    
    return groups


def get_timezone_abbreviations() -> Dict[str, str]:
    return {
        'UTC': 'UTC',
        'GMT': 'Europe/London',
        'EST': 'America/New_York',
        'CST': 'America/Chicago',
        'MST': 'America/Denver',
        'PST': 'America/Los_Angeles',
        'CET': 'Europe/Paris',
        'JST': 'Asia/Tokyo',
        'IST': 'Asia/Kolkata',
        'AEST': 'Australia/Sydney',
        'NZST': 'Pacific/Auckland'
    }