

from models import column_type_model

# from schemas.author import AuthorCreate, AuthorUpdate, Author
from schemas.column_type import ColumnTypeCreate, ColumnTypeUpdate, ColumnType
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from uuid import UUID


def create_column_type(db: Session, column_type: ColumnTypeCreate):
    
    print("Fase 1 de la funcion de creacion: \n")

    column_type_in_db = db.query(column_type_model.ColumnType).filter(column_type_model.ColumnType.name == column_type.name).first()

    print("Fase 2 de la funcion de creacion: \n")

    if column_type_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Column_Type with name {column_type.name} already exists")

    db_column_type = column_type_model.ColumnType(
        name=column_type.name
    )

    # print ("Fase 3 de la funcion de creacion: \n")
    db.add(db_column_type)
    db.commit()
    db.refresh(db_column_type)

    # print ("Fase 4 de la funcion de creacion \n")

    return db_column_type


def get_column_types(db: Session):
    return db.query(column_type_model.ColumnType).all()

def get_column_type_by_name(db: Session, name: str):
    db_column_type = db.query(column_type_model.ColumnType).filter(column_type_model.ColumnType.name == name).first()

    if not db_column_type:

        try:

            new_column_type= create_column_type(db=db,column_type=ColumnTypeCreate(
                name=name
            ))
            return new_column_type
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Column_Type with name: {name} had an error when tried to be created")


        
        
        

    return db_column_type
def update_column_type(db: Session, column_type: ColumnTypeUpdate):
    db_column_type = db.query(column_type_model.ColumnType).filter(column_type_model.ColumnType.id == column_type.id).first()
    db_column_type.name = column_type.name
    db.commit()
    db.refresh(db_column_type)
    return db_column_type

def delete_column_type(db: Session, column_type_id: UUID):

    db_column_type = db.query(column_type_model.ColumnType).filter(column_type_model.ColumnType.id == column_type_id).first()
    db.delete(db_column_type)
    db.commit()
    return db_column_type

