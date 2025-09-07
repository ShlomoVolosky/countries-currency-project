from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pydantic import BaseModel, Field, validator


class BaseModelClass(BaseModel):
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    def to_dict(self) -> Dict[str, Any]:
        return self.json()
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModelClass":
        return cls.parse_raw(json_str)

class TimestampMixin(BaseModel):
        self.updated_at = datetime.utcnow()

class DatabaseMixin(ABC):
        pass
    @abstractmethod
    def delete(self) -> bool:
        pass
    @classmethod
    @abstractmethod
    def get_by_id(cls, id: int) -> Optional["DatabaseMixin"]:
        pass

class ValidationMixin:
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_positive_number(value: Union[int, float], field_name: str) -> float: