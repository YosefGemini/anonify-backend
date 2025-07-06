from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from models.shared_projects_model import shared_projects_table


class Project(Base):
    __tablename__ = 'projects'


    id= Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    title= Column(String(255), nullable=False)
    description= Column(String(1000), nullable=False)
    author_id= Column(UUID(as_uuid=True), ForeignKey('authors.id'), nullable=False)
    # file_id= Column(UUID(as_uuid=True), ForeignKey('files.id'), nullable=False)
    # author= relationship('Author', backref=backref('projects', uselist=True))



    # relationships
    
    datasets= relationship('Dataset', backref=backref('project', uselist=True))

    authors = relationship('Author', secondary='shared_projects', back_populates='shared')

    