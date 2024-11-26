from pydantic import BaseModel
from uuid import UUID

class AuthorBase(BaseModel):
    name = str
    nationality= str

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: UUID

    class Config:
        orm_mode = True

class AuthorUpdate(AuthorBase):
    id: str

class AuthorDelete(BaseModel):
    id: str


