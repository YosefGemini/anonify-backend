from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func



class Author(Base):
    __tablename__ = 'authors'


    id= Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name= Column(String(250), nullable=False)
    nationality= Column(String(250), nullable=False)
    mail= Column(String(250), nullable=False)
    username= Column(String(250), nullable=False)
    password= Column(String(250), nullable=False)
    cell_phone= Column(String(250), nullable=True)
    created_at= Column(DateTime, nullable=False,server_default=func.now())

    #Relationships

    projects= relationship('Project', backref=backref('author', uselist=True))
