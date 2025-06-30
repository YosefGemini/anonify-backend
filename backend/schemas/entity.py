from pydantic import BaseModel

from uuid import UUID
from schemas.file import FileDB
from schemas.column import ColumnCreate, Column
from typing import List, Dict, Any



class EntityBase(BaseModel):
    name: str


class EntityCreate(EntityBase):

    pass

class Entity(EntityBase):
    id: UUID
    name: str
    class Config:
        from_attributes = True



