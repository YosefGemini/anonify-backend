

from pydantic import BaseModel
from uuid import UUID
from schemas.permission import Permission

class RoleBase(BaseModel):
    name: str
    description: str

class RoleCreate(RoleBase):
    permissions: list[str] = []
class Role(RoleBase):
    id: UUID
    permissions: list[Permission] = []
    # projects: list[Project] = []

    class Config:
        # orm_mode = True
        from_attributes = True

class RolePublic(BaseModel):
    id: UUID
    name: str
    description: str
    permissions: list[Permission] = []
    # projects: list[Project] = []

    class Config:
        from_attibutes = True
    

class RoleUpdate(RoleBase):
    id: str
    # permissions: list[Permission] = []

    # projects: list[Project] = []

class RoleDelete(BaseModel):
    id: str