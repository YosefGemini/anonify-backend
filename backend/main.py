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
    WebSocket, 
    WebSocketDisconnect
)
import asyncio
from sqlalchemy.orm import Session
from typing import List
from db.db import engine, get_db, Base
# from fastapi.staticfiles import StaticFiles
#from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import aiofiles
from os import path
from functions import auth_token, auth





# Schemas import
from schemas.file import FileBase, FileDB, FileCreate
from schemas.author import AuthorBase, Author, AuthorCreate, AuthorUpdate, AuthorDelete, AuthorPublic, AuthorToken, AuthCredentials
from schemas.project import ProjectBase, Project, ProjectCreate, ProjectUpdate, ProjectDelete, ProjectInformation
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

# Lista para rastrear conexiones de WebSockets
active_connections: List[WebSocket] = []

@app.get("/")
def get_main():
    return {"Hello": "World"}




async def notify_progress(file_size: int, bytes_received: int, websocket: WebSocket):
    """
    Notifica al cliente el progreso de la subida.
    """
    progress = (bytes_received / file_size) * 100
    await websocket.send_json({"bytes_received": bytes_received, "progress": f"{progress:.2f}%"})

# WebSocket endpoint para actualizar el progreso de la subida

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para enviar actualizaciones de progreso.
    """
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Mantén la conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)



# Session endopints 

async def validate_token_header(
    Authorization: str = Header(),

) -> AuthorToken:
    try:
        authorization_token = Authorization.split(" ")[1]
        print(authorization_token)
        if not authorization_token:
            raise HTTPException(status_code=400, detail="Token is missing")
        current_user = auth_token.decode_access_token(authorization_token)
        # if current_user == None:  # el token no es valido
        print(current_user)
        if not current_user:  # el token no es valido
            raise HTTPException(status_code=404, detail="Session not found")
        user_token = AuthorToken(**current_user)
        print(user_token)
        return user_token
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Token is missing")

# **************************** VALIDATE TOKEN **************************
@app.get("/api/validate_token", response_model=AuthorToken)
async def validate_token_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
):
    return current_user


# endpint proyectos con token
@app.get("/api/user/projects/", response_model= AuthorPublic)
async def get_project_endpoint(
    db: Session = Depends(get_db),
    # Authorization: str = Header(),
    current_user: AuthorToken = Depends(validate_token_header),
):
    return author_crud.get_author(db=db, author_id=current_user.id)

@app.post("/api/login")
async def login_endpoint(
    response: Response, auth_credentials: AuthCredentials, db: Session = Depends(get_db)
):
    user_info = author_crud.login_user(db=db, auth_credentials=auth_credentials)
    # print(user_info.__dict__)
    current_token = auth_token.generate_access_token(
        {
            "id": str(user_info.id),
            "name": user_info.name,
            "username": user_info.username,
            "mail": user_info.mail,
            # "profile_pic": user_info.profile_pic if user_info.profile_pic else None
            #"password": user_info.password,
        }
    )
    return {
        "msg": "Login successful",
        "token": current_token,
    }

# Change password

@app.post("/api/user/change_password")
async def change_password_endpoint(
    password: str = Body(embed=True),
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):

    return author_crud.change_password(
        db=db, current_user=current_user, password=password
    )


# Author endpoints

# CREATE AUTHOR

@app.post("/api/authors" , response_model=Author)
async def create_author_endpoint(
    author: AuthorCreate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),   
):
    print("author", author)
    return author_crud.create_author(db=db, author=author)

# GET AUTHOR

@app.get("/api/authors/{author_id}", response_model=Author )
async def get_author_endpoint(
    author_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
    
    
):
    return author_crud.get_author(db=db, author_id=author_id)

# GET ALL AUTHORS

@app.get("/api/authors",  response_model=list[AuthorPublic])
async def get_all_authors_endpoint(
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.get_all_authors(db=db)

# UPDATE AUTHOR

@app.put("/api/authors", response_model=Author)
async def update_author_endpoint(
    author: AuthorUpdate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.update_author(db=db, author=author)
    
# DELETE AUTHOR
@app.delete("/api/authors", response_model=Author)
async def delete_author(
    author: AuthorDelete,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.delete_author(db=db, author_id=author.id)



# Project endpoints

# CREATE PROJECT

@app.post("/api/projects" , response_model=Project)
async def create_project_endpoint(
    project: ProjectCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.create_project(db=db, project=project)

# GET PROJECT
@app.get("/api/projects/{project_id}", response_model=ProjectInformation)
async def get_project_endpoint(
    project_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.get_project(db=db, project_id=project_id)

# GET ALL PROJECTS
@app.get("/api/projects", response_model=list[Project])
async def get_all_projects_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.get_all_projects(db=db)

# GET ALL PROJECTS BY AUTHOR
@app.get("/api/projects/author/{author_id}", response_model=list[Project])

async def get_all_projects_by_author_endpoint(
    author_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.get_all_projects_by_author(db=db, author_id=author_id)

# UPDATE PROJECT
@app.put("/api/projects", response_model=Project)
async def update_project_endpoint(
    project: ProjectUpdate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.update_project(db=db, project=project)

# DELETE PROJECT
@app.delete("/api/projects", response_model=Project)
async def delete_project(
    project: ProjectDelete,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.delete_project(db=db, project_id=project.id)


# Files endpoints

# Upload File in the folder uploads/files when the files are bigger than 100MB


@app.post("/file/uploadfile/V3")
async def create_upload_file(websocket_id: str, file: UploadFile = File(...)):
    chunk_size = 1024 * 1024  # 1 MB
    # base_name, extension = os.path.splitext(file.filename)
    pathToSave = path.join(pathname, "uploads", "files", file.filename)
    file_size = file.size
    bytes_received = 0

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

    print("Creando archivo",f"file.filename: {file.filename}","\n")
    # totalbytes = 0
    print("con el siguiente path", pathToSave, "\n")



    # Busca el WebSocket correspondiente al cliente
    websocket = next((ws for ws in active_connections if str(ws.id) == websocket_id), None)
    if not websocket:
        return {"error": "WebSocket no conectado."}
    

    
    # Abrimos el archivo en modo escritura binaria
    with open(pathToSave, "wb") as buffer:
        # Leemos el archivo en partes para no sobrecargar la memoria
        while chunk := await file.read(chunk_size):
            counter+=1 
            print(f"counter: {counter}")
            # Lee 1MB por iteración
            buffer.write(chunk)
            bytes_received += len(chunk)
            await notify_progress(file_size, bytes_received, websocket)

            # yield f"Uploaded in {counter}  chunks \n"  # Corrected calculation

    return {"message": f"Archivo {file.filename} guardado exitosamente."}



# Upload File in the folder uploads/files when the files are smaller than 100MB

@app.post("/file/uploadfile/V2")
async def create_upload_file(file: UploadFile = File(...)):
    chunk_size = 1024 * 1024  # 1 MB
    # base_name, extension = os.path.splitext(file.filename)
    pathToSave = path.join(pathname, "uploads", "files", file.filename)
    file_size = file.size
    bytes_received = 0


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
        pathToSave = path.join(pathname, "uploads", "files", file.filename )

        # la funcion os.makedirs(path) crea un directorio en el path especificado
        
    if not path.exists(os.path.dirname(pathToSave)):
        os.makedirs(os.path.dirname(pathToSave))

    print("Creando archivo",f"file.filename: {file.filename}","\n")
    # totalbytes = 0
    print("con el siguiente path", pathToSave, "\n")



    async def save_file(file: UploadFile, pathToSave: str):
        async with aiofiles.open(pathToSave, "wb") as buffer:
            count = 0
            while chunk := await file.read(chunk_size):
                count += 1

                # es para ver a menor velocidad el flujo 
                await asyncio.sleep(1)
                await buffer.write(chunk)
                # bytes_received += len(chunk)
                yield f"In {count} chunks \n"

    return StreamingResponse(save_file(file, pathToSave))




# Creado y guarda un archivo en la carpeta uploads/files
# @app.post("/api/files/{dataset_id}" , response_model=FileDB)
@app.post("/api/files/V1/{dataset_id}")
async def upload_file_endpoint(
    dataset_id: str,
    db: Session = Depends(get_db),
    # current_user: AuthorToken = Depends(validate_token_header),
    file: UploadFile = File(...),
    ):
    # Validacion si el token es valido
    # if not current_user:
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
        pathToSave = path.join(pathname, "uploads", "files",dataset_id, file.filename)



        # la funcion os.path.exists(path) devuelve True si el path existe, y False si no existe
        while os.path.exists(pathToSave):
            file.fllename = f"{base_name}_{number}{extension}"
            number += 1
            pathToSave = path.join(pathname, "uploads", "files",dataset_id, file.filename)

        # la funcion os.makedirs(path) crea un directorio en el path especificado
        
        if not path.exists(os.path.dirname(pathToSave)):
            os.makedirs(os.path.dirname(pathToSave))
        print("Creando archivo",f"file.filename: {file.filename}")
        # chunk_size = 1024 * 1024  # 1 MB
        with open(pathToSave, "wb") as buffer:
            

            print("Creando archivo",f"file.filename: {file.filename}")
            # la funcion buffer.write(bytes) escribe los bytes en el archivo
            buffer.write(contents)
            print("Archivo creado")
            # la funcion buffer.close() cierra el archivo
            buffer.close()
        # buffer.close()


        file_schema = FileCreate( 
            name=file.filename,
            path=pathToSave,
            datasets_id=dataset_id,
            is_public=True,
            size=len(contents),
            )

        print("file_schema",file_schema,"\n")

        # yield await file_crud.create_files(db=db, file=file_schema)
        return file_crud.create_files(db=db, file=file_schema)
        # return
        # return StreamingResponse(iter([]), media_type="text/plain")
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))



##################################################################

# COLUMN and VALUE TYPES endpoints

# CREATE COLUMN_Types

@app.post("/api/column_types" , response_model=ColumnType)
async def create_column_type_endpoint(
    column_type: ColumnTypeCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_type_crud.create_column_type(db=db, column_type=column_type)

# GET COLUMN_TYPE

@app.post("/api/value_types" , response_model=ValueType)
async def create_value_type_endpoint(
    value_type: ValueTypeCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return value_type_crud.create_value_type(db=db, value_type=value_type)





##############################################################################


# COLUMN endpoints

# CREATE COLUMN

@app.post("/api/columns" , response_model=Column)
async def create_column_endpoint(
    column: ColumnCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.create_column(db=db, column=column)



# GET COLUMNS

@app.get("/api/columns/{column_id}", response_model=Column)
async def get_column_endpoint(
    column_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.get_column(db=db, column_id=column_id)

# GET ALL COLUMNS

@app.get("/api/columns", response_model=list[Column])
async def get_all_columns_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.get_all_columns(db=db)


#DATASETS endpoints

# CREATE DATASET

@app.post("/api/datasets" , response_model=Dataset)
async def create_dataset_endpoint(
    dataset: DatasetCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.create_dataset(db=db, dataset=dataset)

# GET DATASETS BY PROJECT ID

@app.get("/api/datasets/{project_id}", response_model=Dataset)

async def get_datasets_by_project_id_endpoint(
    project_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.get_datasets_by_project_id(db=db, project_id=project_id)
