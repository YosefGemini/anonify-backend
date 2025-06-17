from pydantic import BaseModel
from uuid import UUID


class PermissionBase(BaseModel):
    name: str
    description: str

class PermissionCreate(PermissionBase):
    pass
class Permission(PermissionBase):
    id: UUID
    class Config:
        # orm_mode = True
        from_attributes = True


class PermissionUpdate(PermissionBase):
    id: str

class PermissionDelete(BaseModel):
    id: str