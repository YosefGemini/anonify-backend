from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func


class Database(Base):
    __tablename__ = 'dbs'


    id= Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name= Column(String(250), nullable=False)
    type_sgdb= Column(String(250), nullable=False)
    host= Column(String(250), nullable=False)
    port= Column(Integer, nullable=False)
    user= Column(String(250), nullable=False)
    password= Column(String(250), nullable=False)
    requier_ssl= Column(Boolean, nullable=False)
    created_at= Column(DateTime, nullable=False, server_default=func.now())
    updated_at= Column(DateTime)
    parameters= Column(JSONB, nullable=False)
    