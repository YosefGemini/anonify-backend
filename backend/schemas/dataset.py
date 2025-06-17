from pydantic import BaseModel

from uuid import UUID
from schemas.file import FileDB
from schemas.column import ColumnCreate, Column
from typing import List, Dict, Any


class DatasetBase(BaseModel):
    name: str
    

class DatasetCreate(DatasetBase):
    
    project_id: UUID
    query_id: UUID = None
    columns: list[ColumnCreate]
    # status: str = "created"
    

    

class Dataset(DatasetBase):
    id: UUID
    project_id: UUID
    # query_id: UUID = None
    files: list[FileDB]
    columns: list[Column]
    status: str 
    
    class Config:
        from_attributes = True
        # orm_mode = True
        
class DatasetPreviewResponse(BaseModel):
    preview: List[Dict[str, Any]] 
    index: int
    total_rows: int
    total_pages: int


class DatasetUpdate(BaseModel):
    id: UUID
    status: str


                 
    


