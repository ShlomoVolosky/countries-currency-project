"""
Base model classes for the Countries Currency Project.

This module provides base classes and utilities for data models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pydantic import BaseModel, Field, validator


class BaseModelClass(BaseModel):
    """Base model class with common functionality."""
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModelClass":
        """Create model instance from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseModelClass":
        """Create model instance from JSON string."""
        return cls.parse_raw(json_str)


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class DatabaseMixin(ABC):
    """Mixin for database operations."""
    
    @abstractmethod
    def save(self) -> bool:
        """Save the model to database."""
        pass
    
    @abstractmethod
    def delete(self) -> bool:
        """Delete the model from database."""
        pass
    
    @abstractmethod
    def exists(self) -> bool:
        """Check if the model exists in database."""
        pass
    
    @classmethod
    @abstractmethod
    def get_by_id(cls, id: int) -> Optional["DatabaseMixin"]:
        """Get model by ID."""
        pass
    
    @classmethod
    @abstractmethod
    def get_all(cls, limit: Optional[int] = None, offset: Optional[int] = None) -> List["DatabaseMixin"]:
        """Get all models."""
        pass


class ValidationMixin:
    """Mixin for validation utilities."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate that required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        """Validate field types."""
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")
        return type_errors
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string value."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Truncate if too long
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_positive_number(value: Union[int, float], field_name: str) -> float:
        """Validate that a number is positive."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number")
        
        if value < 0:
            raise ValueError(f"{field_name} must be positive")
        
        return float(value)
