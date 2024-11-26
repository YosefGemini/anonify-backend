

from pydantic import BaseModel
from uuid import UUID

class FileBase(BaseModel):
    name: str
    path: str
    


 

class File_DB(FileBase):
    id: UUID

    class Config:
        orm_mode = True

class FileUpdate(FileBase):
    id: str

class FileDelete(BaseModel):
    id: str