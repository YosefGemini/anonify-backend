from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Dataset(Base):
    __tablename__ = 'datasets'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name = Column(String(250), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id'), nullable=True)
    status = Column(String(20), nullable=False, default='created')
    rows = Column(Integer, nullable=False, default=0)
    # file_id = Column(UUID(as_uuid=True), ForeignKey('files.id'), nullable=False)
    # column_id = Column(UUID(as_uuid=True), ForeignKey('columns.id'), nullable=False)
    

    # Relationships
    query = relationship('Query', backref=backref('dataset', uselist=False))
        

    files = relationship('File', backref=backref('dataset', uselist=True))
    columns = relationship('Column', backref=backref('query', uselist=True), cascade="all, delete-orphan")
    # query = relationship('Query', backref=backref('dataset', uselist=False))