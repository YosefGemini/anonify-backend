from pydantic import BaseModel
from uuid import UUID

from schemas.column import Column


class QueryBase(BaseModel):
    query: str
    answer: str
    query_status: str

    query: str

class QueryCreate(QueryBase):
    db_id: UUID
    columns: list[Column]

class Query(QueryCreate):
    id: UUID
    columns: list[Column]

    class Config:
        orm_mode = True
class QueryUpdate(QueryBase):
    id: str

class QueryDelete(BaseModel):
    id: str
    


