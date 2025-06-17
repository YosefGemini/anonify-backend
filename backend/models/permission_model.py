from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    # created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships

    roles = relationship('Role', secondary='role_permission', back_populates='permissions')