from pydantic import BaseModel

from uuid import UUID
from schemas.file import FileDB
from schemas.column import ColumnCreate, Column
from typing import List, Dict, Any, Optional

from schemas.entity import Entity


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
    rows: int
    entity_id: Optional[UUID] = None
    entity: Optional['Entity'] = None
    
    class Config:
        from_attributes = True
        
class DatasetPreviewResponse(BaseModel):
    preview: List[Dict[str, Any]] 
    index: int
    total_rows: int
    total_pages: int



class DatasetUpdate(BaseModel):
    id: UUID
    status: str
    rows: int



class DatasetParameters(BaseModel):
    need_preprocess: bool
    need_imputation: bool
    imputation_method: str
    columns: int
    len: int



class DatasetPreprocess(BaseModel):
    userID: str
    projectID: str
    datasetID: str
    parameters: DatasetParameters
    


