from pydantic import BaseModel
from uuid import UUID
from schemas.project import Project

class AuthorBase(BaseModel):
    name: str
    nationality: str



class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: UUID
    projects: list[Project]

    class Config:
        orm_mode = True


class AuthorPublic(AuthorBase):
    id: UUID

    class Config:
        orm_mode = True

class AuthorUpdate(AuthorBase):
    id: str

class AuthorDelete(BaseModel):
    id: str


