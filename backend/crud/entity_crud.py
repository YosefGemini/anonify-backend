from models import entity_model
from schemas.entity import EntityCreate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from uuid import UUID

def create_entity(db: Session, entity: EntityCreate):

    entity_in_db = db.query(entity_model.Entity).filter(entity_model.Entity.name == entity.name).first()

    if entity_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Value_Type with name {entity.name} already exists")
    
    entity_to_add = entity_model.Entity(
        name= entity.name
    )
    db.add(entity_to_add)
    db.commit()
    db.refresh(entity_to_add)

    return entity_to_add

def get_entities(db: Session):
    return db.query(entity_model.Entity).all()


def get_entitie_by_id(db: Session, entity_id: UUID):
    db_entity = db .query(entity_model.Entity).filter(entity_model.Entity.id == entity_id).first()

    return db_entity


def delete_entity(db: Session, entity_id: UUID):
    db_entity = db.query(entity_model.Entity).filter(entity_model.Entity.id == entity_id).first()

    if not db_entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity with id {entity_id} not found")
    
    db.delete(db_entity)
    db.commit()

    return db_entity



    


    

