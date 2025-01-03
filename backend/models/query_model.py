from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Query(Base):
    __tablename__ = 'queries'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    query = Column(String, nullable=False)
    db_id = Column(UUID(as_uuid=True), ForeignKey('dbs.id'), nullable=False)
    answer = Column(String(6000), nullable=False)
    query_status = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False, server_default=func.now())
    execution_date = Column(DateTime)


    #relationships
    
    # database = relationship('Database', backref=backref('query', uselist=False))
    # dataset = relationship('Dataset', backref=backref('query', uselist=False))


