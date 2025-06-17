from pydantic import BaseModel
from uuid import UUID
from schemas.column_type import ColumnType
from schemas.value_type import ValueType

class ColumnBase(BaseModel):
    name: str
    

class ColumnCreate(ColumnBase):
    dataset_id: UUID
    column_type_id: UUID
    # query_id: str
    value_type_id: UUID

class Column(ColumnBase):
    id: UUID
    dataset_id: UUID
    #column_type_id: UUID
    #value_type_id: UUID
    column_type: ColumnType = None
    value_type: ValueType = None

    class Config:
        # orm_mode = True
        from_attributes = True

class ColumnUpdate(ColumnBase):
    id: str

class ColumnDelete(BaseModel):
    id: str