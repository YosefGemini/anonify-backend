from pydantic import BaseModel
from uuid import UUID
from schemas.project import Project

class AuthorBase(BaseModel):
    name: str
    nationality: str
    mail: str
    username: str
    password: str
    cell_phone: str = None




class AuthorCreate(AuthorBase):
    pass

class AuthorToken(BaseModel):
    id: UUID
    name: str
    cell_phone: str = None
    mail: str
    # profile_pic: str = None
    username: str
    #password: str

class AuthCredentials(BaseModel):
    username: str
    password: str

class Author(AuthorBase):
    id: UUID
    projects: list[Project]

    class Config:
        orm_mode = True



class AuthorPublic(BaseModel):
    id: UUID
    name: str
    projects: list[Project]

    class Config:
        orm_mode = True
    


# class AuthorPublic(AuthorBase):
#     id: UUID

#     class Config:
#         orm_mode = True

class AuthorUpdate(AuthorBase):
    id: str

class AuthorDelete(BaseModel):
    id: str


