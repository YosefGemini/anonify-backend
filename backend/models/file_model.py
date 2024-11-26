from db.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(250), nullable=False)
    path = Column(String(1000), nullable=False)
    # project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    datasets_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id'), nullable=False)


    #product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'), nullable=False)

    # relationshiPS

    #product = relationship("Product", back_populates="files")

