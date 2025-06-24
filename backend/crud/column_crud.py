
from models import column_model

from schemas.column import ColumnCreate, ColumnUpdate, Column, ColumnDelete
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from uuid import UUID

def create_column(db: Session, column: ColumnCreate):
    
    # column_in_db = db.query(column_model.Column).filter(column_model.Column.id == column.id).first()

    # if column_in_db:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,
    #                         detail=f"Column with name {column.name} already exists")

    db_column = column_model.Column(
        name=column.name,
        dataset_id=column.dataset_id,
        column_type_id=column.column_type_id,
        # query_id=column.query_id,
        value_type_id=column.value_type_id
    )

    db.add(db_column)
    db.commit()
    db.refresh(db_column)

    return db_column


def get_column(db: Session, column_id: str):
    db_column = db.query(column_model.Column).filter(column_model.Column.id == column_id).first()
    return db_column


def get_all_columns(db: Session ):
    return db.query(column_model.Column).all()

def update_column(db: Session, column: ColumnUpdate):
    db_column = db.query(column_model.Column).filter(column_model.Column.id == column.id).first()
    db_column.name = column.name
    db.commit()
    db.refresh(db_column)
    return db_column

def delete_column(db: Session, column: ColumnDelete):
    db_column = db.query(column_model.Column).filter(column_model.Column.id == column.id).first()

    db.delete(db_column)
    db.commit()
    return db_column




