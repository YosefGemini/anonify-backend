from db.db import Base
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID

shared_projects_table = Table (

    'shared_projects',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('authors.id'), primary_key=True),
    Column('project_id', UUID(as_uuid=True), ForeignKey('projects.id'), primary_key=True)
)