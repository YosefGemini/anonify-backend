from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Column(Base):
    __tablename__ = 'columns'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id'), nullable=False)
    name = Column(String, nullable=False)
    column_type_id = Column(UUID(as_uuid=True), ForeignKey('column_types.id'), nullable=False)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id'), nullable=False)
    file_id = Column(UUID(as_uuid=True), ForeignKey('files.id'), nullable=False)
    value_type_id = Column(UUID(as_uuid=True), ForeignKey('value_types.id'), nullable=False)
    