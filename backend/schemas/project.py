from pydantic import BaseModel
from uuid import UUID
# from schemas.author import Author

from schemas.dataset import Dataset

class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    author_id: str


class Project(ProjectBase):
    id: UUID
    # author: 

    class Config:
        orm_mode = True


class ProjectInformation(Project):
    id: UUID
    datasets: list[Dataset]
    class Config:
        orm_mode = True


class ProjectUpdate(ProjectBase):
    id: str

class ProjectDelete(BaseModel):
    id: str