from pydantic import BaseModel
from uuid import UUID

class ColumnBase(BaseModel):
    name: str
    

class ColumnCreate(ColumnBase):
    dataset_id: str
    column_type_id: str
    query_id: str
    value_type_id: str

class Column(ColumnCreate):
    id: UUID

    class Config:
        orm_mode = True

class ColumnUpdate(ColumnBase):
    id: str

class ColumnDelete(BaseModel):
    id: str