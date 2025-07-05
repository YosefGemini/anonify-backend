

from models import author_model

from schemas.author import AuthorCreate, AuthorUpdate, Author, AuthCredentials
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from functions import auth_token
from functions.auth import get_password_hash , verify_password

from uuid import UUID
from models.role_model import Role




async def create_default_user(db):

    try:
        default_admin: AuthorCreate = {
        "name": "DefaultAdmin",
        "nationality": "No Especificado",
        "username": "admin",
        "password": "admin",
        "mail": "admin@mail.com",
        "cell_phone": "123456789",
        "role_id": db.query(Role).filter_by(name="admin").first().id,

        }
        def_name= str(default_admin["name"])

        # print(def_name)

        author_in_db = db.query(author_model.Author).filter(author_model.Author.name == def_name).first()


        if not author_in_db:
            passwordhash = get_password_hash(str(default_admin["password"]))
            author_to_add = author_model.Author(

                name=default_admin["name"],
                username=default_admin["username"],
                password=passwordhash,
                mail=default_admin["mail"],
                cell_phone=default_admin["cell_phone"] if default_admin["cell_phone"] else None,
                nationality=default_admin["nationality"],
                role_id=default_admin["role_id"]
            )
            db.add(author_to_add)
            db.commit()
            db.refresh(author_to_add)
            print("Default User created")
        else:
            print(f"Default user {default_admin['name']} already exists")

    except Exception as e:
        print(f"Error creating default User: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating default user")

def create_author(db: Session, author: AuthorCreate):


    print("Fase 1 de la funcion de creacion: \n")


    author_in_db = db.query(author_model.Author).filter(author_model.Author.name == author.name).first()


    print("Fase 2 de la funcion de creacion: \n")


    if author_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Author with name {author.name} already exists")
    
    passwordhash = get_password_hash(author.password)


    db_author = author_model.Author(
        name=author.name,
        username=author.username,
        password=passwordhash,
        mail=author.mail,
        cell_phone=author.cell_phone if author.cell_phone else None,
        nationality=author.nationality,
        role_id=author.role_id
    )

    print ("Fase 3 de la funcion de creacion: \n")
    db.add(db_author)
    db.commit()
    db.refresh(db_author)

    print ("Fase 4 de la funcion de creacion \n")

    return db_author



# FUNCIONA


#TODO definir bien los objetos que son realmente necesarios y que se van a devolver
def login_user(db: Session, auth_credentials: AuthCredentials):
    user_in_db = (
        db.query(author_model.Author)
        .filter(author_model.Author.username == auth_credentials.username)
        # .options(joinedload(author_model.User.gender))
        # .options(joinedload(author_model.User.albums))
        # .options(joinedload(author_model.User.friends))

        .first()
    )

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials ERROR 404"
        )
    # recordar que el password de la base es un hash
    verified_password = verify_password(
        auth_credentials.password, user_in_db.password
    )

    # print(verified_password)

    if not verified_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials "
        )

    # print("***********************Este es el user_in_db", user_in_db.__dict__)
    # print("###", user_in_db.cargo.area.area_name)

    return user_in_db


def change_password(db: Session, current_user: str, password: str):
    # print("Esto ya es en la funcion del CRUD ")
    # print("password enviada \n", password)
    # print("Este es el current user ", current_user)
    # print(" Este es el current_user-user_id", current_user.user_id)
    # print(
    #     "Contraseña hasheada: ",
    # )

    # get_password_hash(password)

    user_in_db = (
        db.query(author_model.Author)
        .filter(author_model.Author.id == current_user.id)
        .first()
    )
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User NOT FOUND"
        )

    # if not user_in_db.is_default == 1:
    #     raise HTTPException(
    #         status_code=400, detail="User does not have a default password"
    #     )

    #user_in_db.is_default = 0
    user_in_db.password = get_password_hash(password)

    db.commit()
    db.refresh(user_in_db)

    return user_in_db

    # print("----------------------------------------------------------")
    # print(info_user)

    # user_in_db = db.query(user_model.User_public).filter(user_model.User.user_id ==  info_user.user_id )




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


