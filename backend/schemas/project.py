from pydantic import BaseModel
from uuid import UUID
# from schemas.author import Author

from schemas.dataset import Dataset

class ProjectUsersInfo(BaseModel):
    id:UUID
    name: str

    class Config:
        # orm_mode = True
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    author_id: UUID


class Project(ProjectBase):
    id: UUID
    # author: 

    class Config:
        # orm_mode = True
        from_attributes = True


class ProjectInformation(ProjectBase):
    id: UUID
    author_id: UUID
    datasets: list[Dataset]
    authors: list[ProjectUsersInfo]
    class Config:
        # orm_mode = True
        from_attributes = True


class ProjectUpdate(ProjectBase):
    id: str

class ProjectDelete(BaseModel):
    id: str

class ProjectShare(BaseModel):
    project_id: str
    users_id: list[str]

