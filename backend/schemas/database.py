from pydantic import BaseModel
from uuid import UUID


class DatabaseBase(BaseModel):
    name: str
    type_sgdb: str
    host: str
    port: int
    user: str
    password: str
    require_ssl: bool
    parameters: dict

class DatabaseCreate(DatabaseBase):
    pass

class Database(DatabaseBase):
    id: UUID
    created_at: str
    updated_at: str = None

    class Config:
        orm_mode = True

class DatabaseUpdate(DatabaseBase):
    id: str

class DatabaseDelete(BaseModel):
    id: str
