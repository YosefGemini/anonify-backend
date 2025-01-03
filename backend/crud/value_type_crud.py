from models import value_type_model

from schemas.value_type import ValueTypeCreate, ValueTypeUpdate, ValueType
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from uuid import UUID


def create_value_type(db: Session, value_type: ValueTypeCreate):
    
    # print("Fase 1 de la funcion de creacion: \n")

    value_type_in_db = db.query(value_type_model.ValueType).filter(value_type_model.ValueType.name == value_type.name).first()

    # print("Fase 2 de la funcion de creacion: \n")

    if value_type_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Value_Type with name {value_type.name} already exists")

    db_value_type = value_type_model.ValueType(
        name=value_type.name
    )

    # print ("Fase 3 de la funcion de creacion: \n")
    db.add(db_value_type)
    db.commit()
    db.refresh(db_value_type)

    # print ("Fase 4 de la funcion de creacion \n")

    return db_value_type


def get_value_types(db: Session):
    return db.query(value_type_model.ValueType).all()


def update_value_type(db: Session, value_type: ValueTypeUpdate):
    db_value_type = db.query(value_type_model.ValueType).filter(value_type_model.ValueType.id == value_type.id).first()
    db_value_type.name = value_type.name
    db.commit()
    db.refresh(db_value_type)
    return db_value_type

def delete_value_type(db: Session, value_type_id: UUID):
    
    db_value_type = db.query(value_type_model.ValueType).filter(value_type_model.ValueType.id == value_type_id).first()
    db.delete(db_value_type)
    db.commit()
    return db_value_type

