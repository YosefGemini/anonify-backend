from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func



class Author(Base):
    __tablename__ = 'authors'


    id= Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name= Column(String(250), nullable=False)
    nationality= Column(String(250), nullable=False)

    #Relationships

    projects= relationship('Project', backref=backref('author', uselist=True))
