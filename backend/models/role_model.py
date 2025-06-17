from db.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from models.role_permission_model import role_permission_table


class Role(Base):
    __tablename__ = 'roles'

    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, nullable=False, server_default=func.gen_random_uuid())
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    # created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    # users = relationship('User', backref=backref('role', uselist=True))
    # permissions = relationship('Permission',secondary='role_permission', back_populates='roles')
    permissions =  relationship("Permission", secondary="role_permission", back_populates="roles" )
    # permissions = relationship(

    #     'Role',
    #     secondary=role_permission_table,
    #     primaryjoin=role_permission_table.c.role_id == id,
    #     secondaryjoin=role_permission_table.c.permission_id == id,

    #     backref='roles'
    #     )

    