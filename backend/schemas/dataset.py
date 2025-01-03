from pydantic import BaseModel
from uuid import UUID
from schemas.file import File_DB
from schemas.column import ColumnCreate, Column

class DatasetBase(BaseModel):
    name: str
    

class DatasetCreate(DatasetBase):
    
    project_id: str
    query_id: str = None
    columns: list[ColumnCreate]
    

class Dataset(DatasetBase):
    id: UUID
    files: list[File_DB]
    columns: list[Column]
    query_id: str = None

    class Config:
        orm_mode = True



