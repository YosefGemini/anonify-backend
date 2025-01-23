

from pydantic import BaseModel
from uuid import UUID

class FileBase(BaseModel):
    name: str
    path: str
    # created_at: str
    size: int
    is_public: bool
    


class FileCreate(FileBase):
    datasets_id: UUID


class FileDB(FileBase):
    id: UUID
    datasets_id: UUID

    class Config:
        orm_mode = True


class FileUpdate(FileBase):
    id: str

class FileDelete(BaseModel):
    id: str