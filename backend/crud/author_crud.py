

from models import author_model

from schemas.author import AuthorCreate, AuthorUpdate, Author
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from uuid import UUID


def create_author(db: Session, author: AuthorCreate):


    print("Fase 1 de la funcion de creacion: \n")


    author_in_db = db.query(author_model.Author).filter(author_model.Author.name == author.name).first()


    print("Fase 2 de la funcion de creacion: \n")


    if author_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Author with name {author.name} already exists")

    db_author = author_model.Author(
        name=author.name,
        nationality=author.nationality
    )

    print ("Fase 3 de la funcion de creacion: \n")
    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    print ("Fase 4 de la funcion de creacion \n")

    return db_author


def get_author(db: Session, author_id: str):

    # se carga la informacion del autor como de los proyectos que tiene a cargo 

    db_author = db.query(author_model.Author).filter(author_model.Author.id == author_id).options(joinedload(author_model.Author.projects)).first()
    return db_author



def get_all_authors(db: Session ):

    # este es sin los proyectos 
    return db.query(author_model.Author).all()


def update_author(db: Session, author: AuthorUpdate):

    db_author = db.query(author_model.Author).filter(author_model.Author.id == author.id).first()
    if not db_author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Author with id {author.id} not found")

    db_author.name = author.name
    db_author.nationality = author.nationality

    db.commit()
    db.refresh(db_author)

    return db_author


def delete_author(db: Session, author_id: UUID):
    db_author = db.query(author_model.Author).filter(author_model.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Author with id {author_id} not found")

    db.delete(db_author)
    db.commit()

    return db_author
