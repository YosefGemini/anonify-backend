

from models import db_model

# from schemas.author import AuthorCreate, AuthorUpdate, Author

from schemas.database import DatabaseBase, DatabaseUpdate, DatabaseDelete

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from uuid import UUID


def create_database(db: Session, database: DatabaseBase):
    
    database_in_db = db.query(db_model.Database).filter(db_model.Database.name == database.name).first()

    if database_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Database with name {database.name} already exists")

    db_database = db_model.Database(
        name=database.name,
        description=database.description,
        dbms=database.dbms,
        host=database.host,
        port=database.port,
        user=database.user,
        password=database.password
    )

    db.add(db_database)
    db.commit()
    db.refresh(db_database)

    return db_database


def get_database(db: Session, database_id: str):
    
    db_database = db.query(db_model.Database).filter(db_model.Database.id == database_id).first()
    return db_database

def get_all_databases(db: Session):
    
    return db.query(db_model.Database).all()


def update_database(db: Session, database: DatabaseUpdate):
    
    db_database = db.query(db_model.Database).filter(db_model.Database.id == database.id).first()
    if not db_database:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Database with id {database.id} not found")

    db_database.name = database.name
    db_database.description = database.description
    db_database.dbms = database.dbms
    db_database.host = database.host
    db_database.port = database.port
    db_database.user = database.user
    db_database.password = database.password

    db.commit()
    db.refresh(db_database)

    return db_database

def delete_database(db: Session, database_id: str):

    db_database = db.query(db_model.Database).filter(db_model.Database.id == database_id).first()
    if not db_database:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Database with id {database_id} not found")

    db.delete(db_database)
    db.commit()
    return db_database

def get_database_by_name(db: Session, database_name: str):
    db_database = db.query(db_model.Database).filter(db_model.Database.name == database_name).first()
    return db_database



