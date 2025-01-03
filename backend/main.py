from fastapi import (
    FastAPI,
    Request,
    Response,
    Header,
    Depends,
    HTTPException,
    Form,
    File,
    Body,
    status,
    UploadFile,
)
from sqlalchemy.orm import Session
from db.db import engine, get_db, Base
# from fastapi.staticfiles import StaticFiles
#from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from os import path



# Schemas import
from schemas.file import FileBase, File_DB
from schemas.author import AuthorBase, Author, AuthorCreate, AuthorUpdate, AuthorDelete, AuthorPublic
from schemas.project import ProjectBase, Project, ProjectCreate, ProjectUpdate, ProjectDelete
from schemas.dataset import DatasetBase, Dataset, DatasetCreate
from schemas.column import ColumnBase, Column, ColumnCreate, ColumnUpdate, ColumnDelete
from schemas.column_type import ColumnTypeBase, ColumnType, ColumnTypeCreate, ColumnTypeUpdate, ColumnTypeDelete
from schemas.query import QueryBase, Query, QueryCreate, QueryUpdate, QueryDelete
from schemas.value_type import ValueTypeBase, ValueType, ValueTypeCreate, ValueTypeUpdate, ValueTypeDelete

from crud import file_crud, author_crud, project_crud, dataset_crud, column_crud, column_type_crud, value_type_crud

from models import file_model, author_model, column_model, column_type_model, query_model, value_type_model, db_model, dataset_model

app = FastAPI()
Base.metadata.create_all(bind=engine)

pathname = os.path.dirname(path.realpath(__file__))
## Middlewares
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_main():
    return {"Hello": "World"}

# Author endpoints

# CREATE AUTHOR

@app.post("/api/authors" , response_model=Author)
async def create_author_endpoint(
    author: AuthorCreate,
    db: Session = Depends(get_db),   
):
    print("author", author)
    return author_crud.create_author(db=db, author=author)

# GET AUTHOR

@app.get("/api/authors/{author_id}", response_model=Author )
async def get_author_endpoint(
    author_id: str,
    db: Session = Depends(get_db),
    
    
):
    return author_crud.get_author(db=db, author_id=author_id)

# GET ALL AUTHORS

@app.get("/api/authors",  response_model=list[AuthorPublic])
async def get_all_authors_endpoint(
    db: Session = Depends(get_db),
):
    return author_crud.get_all_authors(db=db)

# UPDATE AUTHOR

@app.put("/api/authors", response_model=Author)
async def update_author_endpoint(
    author: AuthorUpdate,
    db: Session = Depends(get_db),
):
    return author_crud.update_author(db=db, author=author)
    
# DELETE AUTHOR
@app.delete("/api/authors", response_model=Author)
async def delete_author(
    author: AuthorDelete,
    db: Session = Depends(get_db),
):
    return author_crud.delete_author(db=db, author_id=author.id)



# Project endpoints

# CREATE PROJECT

@app.post("/api/projects" , response_model=Project)
async def create_project_endpoint(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    return project_crud.create_project(db=db, project=project)

# GET PROJECT
@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    return project_crud.get_project(db=db, project_id=project_id)

# GET ALL PROJECTS
@app.get("/api/projects", response_model=list[Project])
async def get_all_projects_endpoint(
    db: Session = Depends(get_db),
):
    return project_crud.get_all_projects(db=db)

# UPDATE PROJECT
@app.put("/api/projects", response_model=Project)
async def update_project_endpoint(
    project: ProjectUpdate,
    db: Session = Depends(get_db),
):
    return project_crud.update_project(db=db, project=project)

# DELETE PROJECT
@app.delete("/api/projects", response_model=Project)
async def delete_project(
    project: ProjectDelete,
    db: Session = Depends(get_db),
):
    return project_crud.delete_project(db=db, project_id=project.id)


# Files endpoints

# Creado y guarda un archivo en la carpeta uploads/files

@app.post("/api/files" , response_model=list[File_DB])
async def upload_file_endpoint(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    #product_id: str = Form(...),
    #current_user: UserToken = Depends(validate_token_header),
    ):

    #if not current_user:
    #    raise HTTPException(
    #        status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
    #    )

    

    try:

        
            # contents es un objeto de tipo bytes que contiene el contenido del archivo
        contents = await file.read()
        # la funcion os.path.splitext(path) devuelve una tupla con el nombre del archivo y su extension
        base_name, extension = os.path.splitext(file.filename)

        print(f"base_name: {base_name}")
        print(f"extension: {extension}")
        number = 1
        # la funcion os.path.join(path1, path2, ...) une los paths en un solo path
        pathToSave = path.join(pathname, "uploads", "files", file.filename)



        # la funcion os.path.exists(path) devuelve True si el path existe, y False si no existe
        while os.path.exists(pathToSave):
            file.fllename = f"{base_name}_{number}{extension}"
            number += 1
            pathToSave = path.join(pathname, "uploads", "files", file.filename)

        # la funcion os.makedirs(path) crea un directorio en el path especificado
        
        if not path.exists(os.path.dirname(pathToSave)):
            os.makedirs(os.path.dirname(pathToSave))
        
        with open(pathToSave, "wb") as buffer:

            print("Creando archivo",f"file.filename: {file.filename}")
            # la funcion buffer.write(bytes) escribe los bytes en el archivo
            buffer.write(contents)
            print("Archivo creado")
            # la funcion buffer.close() cierra el archivo
            buffer.close()


        file_schema = FileBase(
            name=file.filename,
            path=pathToSave,
            #product_id=product_id
        )

        print("file_schema",file_schema)
        return file_crud.create_files(db=db, file=file_schema)
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))



##################################################################

# COLUMN and VALUE TYPES endpoints

# CREATE COLUMN_Types

@app.post("/api/column_types" , response_model=ColumnType)
async def create_column_type_endpoint(
    column_type: ColumnTypeCreate,
    db: Session = Depends(get_db),
):
    return column_type_crud.create_column_type(db=db, column_type=column_type)

# GET COLUMN_TYPE

@app.post("/api/value_types" , response_model=ValueType)
async def create_value_type_endpoint(
    value_type: ValueTypeCreate,
    db: Session = Depends(get_db),
):
    return value_type_crud.create_value_type(db=db, value_type=value_type)





##############################################################################


# COLUMN endpoints

# CREATE COLUMN

@app.post("/api/columns" , response_model=Column)
async def create_column_endpoint(
    column: ColumnCreate,
    db: Session = Depends(get_db),
):
    return column_crud.create_column(db=db, column=column)



# GET COLUMNS

@app.get("/api/columns/{column_id}", response_model=Column)
async def get_column_endpoint(
    column_id: str,
    db: Session = Depends(get_db),
):
    return column_crud.get_column(db=db, column_id=column_id)

# GET ALL COLUMNS

@app.get("/api/columns", response_model=list[Column])
async def get_all_columns_endpoint(
    db: Session = Depends(get_db),
):
    return column_crud.get_all_columns(db=db)


#DATASETS endpoints

# CREATE DATASET

@app.post("/api/datasets" , response_model=Dataset)
async def create_dataset_endpoint(
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
):
    return dataset_crud.create_dataset(db=db, dataset=dataset)

# GET DATASETS BY PROJECT ID

@app.get("/api/datasets/{project_id}", response_model=Dataset)

async def get_datasets_by_project_id_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
):
    return dataset_crud.get_datasets_by_project_id(db=db, project_id=project_id)
