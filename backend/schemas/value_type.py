from pydantic import BaseModel
from uuid import UUID

class ValueTypeBase(BaseModel):
    name: str

class ValueTypeCreate(ValueTypeBase):
    pass

class ValueType(ValueTypeBase):
    id: UUID

    class Config:
        orm_mode = True

class ValueTypeUpdate(ValueTypeBase):
    id: str

class ValueTypeDelete(BaseModel):
    id: str

