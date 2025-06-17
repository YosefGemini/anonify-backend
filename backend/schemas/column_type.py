from pydantic import BaseModel
from uuid import UUID

class ColumnTypeBase(BaseModel):
    name: str

class ColumnTypeCreate(ColumnTypeBase):
    pass
class ColumnType(ColumnTypeBase):
    id: UUID

    class Config:
        # orm_mode = True
        from_attributes = True

class ColumnTypeUpdate(ColumnTypeBase):
    id: str

class ColumnTypeDelete(BaseModel):
    id: str

