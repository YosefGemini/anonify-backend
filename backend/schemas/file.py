

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from schemas.column import ColumnCreate, Column
class FileBase(BaseModel):
    name: str
    path: str
    # created_at: str
    size: int
    is_public: bool
    rows: int = None
    


class FileCreate(FileBase):
    datasets_id: UUID
    columns: list[ColumnCreate]
    detail: str


class FileDB(FileBase):
    id: UUID
    datasets_id: UUID
    columns: list[Column]
    detail: str


    class Config:
        # orm_mode = True
        from_attributes = True


class FileUpdate(BaseModel):

    id: str
    name: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    is_public: Optional[bool] = None
    rows: Optional[int] = None
    detail: Optional[str] = None



class FileDelete(BaseModel):
    id: str