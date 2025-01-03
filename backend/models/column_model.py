from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Column(Base):
    __tablename__ = 'columns'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name = Column(String(250), nullable=False)
    
    
    column_type_id = Column(UUID(as_uuid=True), ForeignKey('column_types.id'), nullable=True)
    value_type_id = Column(UUID(as_uuid=True), ForeignKey('value_types.id'), nullable=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id'), nullable=False)
    # Relationships
    
    column_type= relationship('ColumnType', backref=backref('column_type', uselist=False))
    value_type= relationship('ValueType', backref=backref('column_type', uselist=False))