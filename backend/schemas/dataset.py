from pydantic import BaseModel
from uuid import UUID
from schemas.file import FileDB
from schemas.column import ColumnCreate, Column

class DatasetBase(BaseModel):
    name: str
    

class DatasetCreate(DatasetBase):
    
    project_id: UUID
    query_id: UUID = None
    columns: list[ColumnCreate]
    

class Dataset(DatasetBase):
    id: UUID
    files: list[FileDB]
    columns: list[Column]
    query_id: UUID = None

    class Config:
        orm_mode = True



