from pydantic import BaseModel

from uuid import UUID
from schemas.file import FileDB

from typing import List, Dict, Any, Optional
# from schemas.column import Column
from schemas.entity import Entity


class DatasetBase(BaseModel):
    name: str
    

class DatasetCreate(DatasetBase):
    
    project_id: UUID
    # query_id: UUID = None
    # columns: list[ColumnCreate]
    # status: str = "created"
    

class DatasetInfoForAnomination(BaseModel):
    id: UUID
    project_id: UUID
    # columns: list[Column]
    file_to_anonimize: FileDB
    class Config:
        from_attributes = True 

class Dataset(DatasetBase):
    id: UUID
    project_id: UUID
    # query_id: UUID = None
    files: list[FileDB]
    # columns: list[Column]
    status: str
    # rows: int
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
    entity: Optional[UUID] = None
    # rows: int


# TODO ESTO ahy que corregir

class DatasetParameters(BaseModel):
    dataset_status: str
    need_preprocess: bool
    need_imputation: bool
    cleaning_method: str
    # columns: list[Column]
    rows: int




class DatasetPreprocess(BaseModel):
    # userID: str
    projectID: str
    datasetID: str
    parameters: DatasetParameters
    


