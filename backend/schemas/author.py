from pydantic import BaseModel
from uuid import UUID
from schemas.project import Project
from schemas.role import RolePublic

class AuthorBase(BaseModel):
    name: str
    nationality: str
    mail: str
    username: str
    password: str
    cell_phone: str = None





class AuthorCreate(AuthorBase):
    role_id: UUID
    pass

class AuthorToken(BaseModel):
    id: UUID
    name: str
    cell_phone: str = None
    mail: str
    # profile_pic: str = None
    username: str
    # role: RolePublic
    #password: str

class AuthCredentials(BaseModel):
    username: str
    password: str

class Author(AuthorBase):
    id: UUID
    projects: list[Project]
    role: RolePublic

    class Config:
        # orm_mode = True
        from_attributes = True



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

class AuthorPublicInformation(BaseModel):
    id: UUID
    name: str
    nationality: str
    mail: str
    username: str
    cell_phone: str = None
    # projects: list[Project]
    role: RolePublic

    class Config:
        from_attributes = True
        # orm_mode = True

class AuthorUpdate(AuthorBase):
    id: str

class AuthorDelete(BaseModel):
    id: str


