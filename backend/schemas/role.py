

from pydantic import BaseModel
from uuid import UUID
from schemas.permission import Permission, PermissionInToken
from typing import List
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

# Esquema para el rol dentro del token
class RoleInToken(BaseModel):
    id: UUID # Si el ID del rol viene en el token
    name: str
    permissions: List[PermissionInToken] # Lista de los esquemas de permiso

    # Configuración para permitir que Pydantic maneje objetos ORM
    class Config:
        from_attributes = True # Anteriormente orm_mode = True

