from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BaseEntity(BaseModel):
    id: Optional[int] = Field(None, description="Database ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class BaseProcessor(ABC):
    @abstractmethod
    async def process(self) -> bool:
        pass

    @abstractmethod
    async def validate(self) -> bool:
        pass


class BaseRepository(ABC):
    @abstractmethod
    async def create(self, entity: BaseEntity) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    async def update(self, entity: BaseEntity) -> Optional[BaseEntity]:
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[BaseEntity]:
        pass
