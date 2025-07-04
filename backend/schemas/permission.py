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

# Esquema para un permiso individual dentro del token
class PermissionInToken(BaseModel):
    name: str
    description: str # O solo el nombre si no necesitas la descripción en el token

    # Configuración para permitir que Pydantic maneje objetos ORM
    class Config:
        from_attributes = True # Anteriormente orm_mode = True

