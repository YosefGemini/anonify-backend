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
    WebSocketDisconnect,
    BackgroundTasks
    
)
import asyncio
import uuid

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
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
from schemas.author import AuthorBase, Author, AuthorCreate, AuthorUpdate, AuthorDelete, AuthorPublic, AuthorToken, AuthCredentials, AuthorPublicInformation
from schemas.role import RoleBase, Role, RoleCreate, RoleUpdate, RoleDelete
from schemas.project import ProjectBase, Project, ProjectCreate, ProjectUpdate, ProjectDelete, ProjectInformation
from schemas.dataset import DatasetBase, Dataset, DatasetCreate, DatasetPreviewResponse, DatasetUpdate
from schemas.column import ColumnBase, Column, ColumnCreate, ColumnUpdate, ColumnDelete
from schemas.column_type import ColumnTypeBase, ColumnType, ColumnTypeCreate, ColumnTypeUpdate, ColumnTypeDelete
from schemas.query import QueryBase, QueryCreate, QueryUpdate, QueryDelete
from schemas.value_type import ValueTypeBase, ValueType, ValueTypeCreate, ValueTypeUpdate, ValueTypeDelete
from schemas.permission import PermissionBase, Permission, PermissionCreate, PermissionUpdate, PermissionDelete
from schemas.entity import EntityCreate, Entity
# este archivo falta crear

from functions.connetions import register_connection, remove_connection, notify_disconnect, send_progress_to_websocket
from functions.dataset_manage import analyze_dataset


from crud import file_crud, author_crud, role_crud ,project_crud, dataset_crud, column_crud, column_type_crud, value_type_crud, permission_crud, entity_crud
# from crud.patada_crud import procesar_patada 
from models import file_model, author_model, column_model, column_type_model, query_model, value_type_model, db_model, dataset_model, entity_model
from functions.init_function import init_roles_and_permissions
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
# active_connections: List[WebSocket] = []


# @app.lifespan("startup")


# evento que se realiza al iniciar la aplicacion

@app.on_event("startup")
async def startup_event():


    # db: Session = Depends(get_db),
    try:
        db_generator = get_db()
        db = next(db_generator) # Obtener la sesión del generador
        try:
            await permission_crud.create_default_permissions(db=db)
            await role_crud.create_default_roles(db=db)
        except Exception as e:
            print(f"Error en startup_event: {e}")
            raise
        finally:
            db_generator.close() # Asegurar que la sesión se cierre.
    except Exception as e:
        print(f"Startup error: {e}")


        

@app.get("/")
def get_main():
    return {"Hello": "World"}


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

# @app.post("/api/agregar_patada")
# async def agregar_patada(
#     body = Form(...),
    
#     # current_user: AuthorToken = Depends(validate_token_header),
# ):
#     return procesar_patada(value=body)


# endpint proyectos con token





# WebSocket endpoint para actualizar el progreso de la subida

@app.websocket("/api/ws/progress/{operation_id}")
async def websocket_endpoint(websocket: WebSocket, operation_id: str):


    """
    WebSocket para enviar actualizaciones de progreso.
    """
    await websocket.accept()
    print("WS Regsitrando conexion")
    register_connection(operation_id=operation_id, websocket=websocket)
    print("WS Conexion registrada con ID ",operation_id)
    # active_connections.append(websocket)
    try:
        # print("WS fase 3")
        while True:
            # Mantén la conexión abierta
            print("WS Recibiendo datos del WebSocket")
            # await websocket.receive_text()
            await websocket.receive_json(mode='text')
    except WebSocketDisconnect:
        print("Iniciando desconexion del WebSocket")
        await notify_disconnect(operation_id)

        # active_connections.remove(websocket)

        print(f"carga de File {operation_id} terminada")


# permissioons endpoint
# Get all Permissions
@app.get("/api/administration/permissions", response_model=list[Permission])
async def get_permissions_endpoint(
    db: Session = Depends(get_db),
    current_user: AuthorToken = Depends(validate_token_header),
):
    return permission_crud.get_permissions(db=db)
#  GET PERMISSION BY ID 
@app.get("/api/administration/permissions/{permission_id}", response_model=Permission)
async def get_permission_endpoint(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: AuthorToken = Depends(validate_token_header),
):
    return permission_crud.get_permission(db=db, permission_id=permission_id)
# CREATE PERMISSSION
@app.post("/api/administration/permissions", response_model=Permission)
async def create_permission_endpoint(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: AuthorToken = Depends(validate_token_header),
):
    return permission_crud.create_permission(db=db, permission=permission)
# UPDATE PERMISSION

@app.put("/api/administration/permissions", response_model=Permission)
async def update_permission_endpoint(
    permission: PermissionUpdate,
    db: Session = Depends(get_db),
    # current_user: AuthorToken = Depends(validate_token_header),
):
    return permission_crud.update_permission(db=db, permission=permission)

# DELETE PERMISSION
@app.delete("/api/administration/permissions", response_model=Permission)
async def delete_permission_endpoint(
    permission: PermissionDelete,
    db: Session = Depends(get_db),
    # current_user: AuthorToken = Depends(validate_token_header),
):
    return permission_crud.delete_permission(db=db, permission_id=permission.id)

# Session endopints 



#TODO
@app.get("/api/user/projects", response_model= AuthorPublic)
async def get_project_endpoint(
    db: Session = Depends(get_db),
    # Authorization: str = Header(),
    current_user: AuthorToken = Depends(validate_token_header),
):
    # print("current_user", current_user)
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
    #     )
    # # print("Authorization", Authorization)
    # print("Entrada a la funcion get_project_endpoint")
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

# CREATE AUTHOR (ADMINISTRATION)

@app.post("/api/administration/authors" , response_model=Author)
async def create_author_endpoint(
    author: AuthorCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),   
):
    print("author", author)
    return author_crud.create_author(db=db, author=author)

# GET AUTHOR

@app.get("/api/authors/{author_id}", response_model=Author )
async def get_author_endpoint(
    author_id: str,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
    
    
):
    return author_crud.get_author(db=db, author_id=author_id)

# GET ALL AUTHORS

@app.get("/api/public/test/author", response_model=AuthorPublicInformation)
async def get_author_public_information_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    author_id= str(current_user.id)
    """
    Obtiene la información pública del autor.
    """
    return author_crud.get_author(db=db, author_id=author_id)

@app.get("/api/public/author", response_model=AuthorPublicInformation)
async def get_author_public_information_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    author_id= str(current_user.id)
    """
    Obtiene la información pública del autor.
    """
    return author_crud.get_author(db=db, author_id=author_id)

@app.get("/api/authors",  response_model=list[AuthorPublic])
async def get_all_authors_endpoint(
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.get_all_authors(db=db)

@app.get("/api/administration/authors",  response_model=list[AuthorPublicInformation])
async def get_all_authors_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.get_all_authors(db=db)


# UPDATE AUTHOR

@app.put("/api/authors", response_model=Author)
async def update_author_endpoint(
    author: AuthorUpdate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.update_author(db=db, author=author)
    
# DELETE AUTHOR
@app.delete("/api/authors", response_model=Author)
async def delete_author(
    author: AuthorDelete,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return author_crud.delete_author(db=db, author_id=author.id)



# ROLES endpoints

# CREATE ROLE
@app.post("/api/administration/roles" , response_model=ColumnType)
async def create_role_endpoint(
    role: ColumnTypeCreate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return role_crud.create_role(db=db, role=role)
# GET ROLE
@app.get("/api/administration/roles/{role_id}", response_model=Role)
async def get_role_endpoint(
    role_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return role_crud.get_role(db=db, role_id=role_id)
# GET ALL ROLES
@app.get("/api/administration/roles", response_model=list[Role])
async def get_all_roles_endpoint(
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return role_crud.get_roles(db=db)

# UPDATE ROLE
@app.put("/api/administration/roles", response_model=Role)
async def update_role_endpoint(
    role: RoleUpdate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return role_crud.update_role(db=db, role=role)
# DELETE ROLE
@app.delete("/api/administration/roles", response_model=Role)
async def delete_role(
    role: RoleDelete,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return role_crud.delete_role(db=db, role_id=role.id)



#entities endpoints
@app.get("/api/administration/entity",response_model=list[Entity])
async def get_all_entities(
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),

):
    return entity_crud.get_entities(db=db)

@app.get("/api/administration/entity/{entity_id}", response_model=Entity)
async def get_entities_by_uuid(
    entity_id: str,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),

):
    return entity_crud.get_entitie_by_id(db=db, entity_id=entity_id)


@app.post("/api/administration/entity", response_model=Entity)
async def create_entity(
    entity: EntityCreate,
    db: Session = Depends(get_db),

):
    return entity_crud.create_entity(db=db, entity=entity)

@app.delete("/api/administration/entity/{entity_id}", response_model=Entity)
async def delete_entity(
    entity_id: str,
    db: Session = Depends(get_db),

):
    return entity_crud.delete_entity(db=db, entity_id=entity_id)
# Project endpoints
# CREATE PROJECT

@app.post("/api/projects" , response_model=Project)
async def create_project_endpoint(
    project: ProjectCreate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.create_project(db=db, project=project)

@app.post("/api/user/projects", response_model=Project)
async def create_project_for_user_endpoint(
    project: ProjectBase,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    data: ProjectCreate = ProjectCreate(
        title=project.title,
        description=project.description,
        author_id=current_user.id
    ) 
    """
    Crea un proyecto para el usuario actual.
    """
    # project.author_id = current_user.id
    return project_crud.create_project(db=db, project=data)

# GET PROJECT
@app.get("/api/projects/{project_id}", response_model=ProjectInformation)
async def get_project_endpoint(
    project_id: str,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.get_project(db=db, project_id=project_id)

# GET ALL PROJECTS
@app.get("/api/projects", response_model=list[Project])
async def get_all_projects_endpoint(
    # current_user: AuthorToken = Depends(validate_token_header),
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
@app.delete("/api/projects/{project_id}", response_model=Project)
async def delete_project(
    project_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return project_crud.delete_project(db=db, project_id=project_id)


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

    # print("Creando archivo",f"file.filename: {file.filename}","\n")
    # totalbytes = 0
    print("con el siguiente path", pathToSave, "\n")
    async def save_file(file: UploadFile, pathToSave: str):
        async with aiofiles.open(pathToSave, "wb") as buffer:
            print("Fase 1 save file")
            count = 0
            print(f"Fase 2 save file, chunk {count} de {file.filename}")
            print("Fase 2 save file despues de abrir el archivo")
            # stream_long = await file.read(chunk_size)
            # print("lectura de chunk size",stream_long)

            while True: 
                print("Fase 2 save file, dentro del while")

                chunk = await file.read(chunk_size)
                print(f"Fase 2 save file, chunk {count} de {file.filename}")
                if not chunk:
                    print("Fase 2 save file, no hay mas chunks")
                    break

                count += 1
                print(f"Fase 2 dentro del while save file, chunk {count} de {file.filename}")
                # es para ver a menor velocidad el flujo 
                await asyncio.sleep(1)
                await buffer.write(chunk)

                yield f"In {count} chunks \n"


            # while chunk := await file.read(chunk_size):
            #     count += 1
            #     print(f"Fase 2 dentro del while save file, chunk {count} de {file.filename}")

            #     # es para ver a menor velocidad el flujo 
            #     await asyncio.sleep(1)
            #     await buffer.write(chunk)
            #     # print(f"Escribiendo chunk {count} de {file.filename} con tamaño {len(chunk)} bytes")
            #     # bytes_received += len(chunk)
            #     yield f"In {count} chunks \n"

            # print(f"Error al guardar el archivo: {e}")
            # raise HTTPException(status_code=500, detail="Error al guardar el archivo:")
    # try:
    return StreamingResponse(save_file(file, pathToSave))


@app.post("/file/test/uploadfile/V2")
async def create_upload_file(file: UploadFile = File(...)):

    chunk_size = 1024 * 1024  # 1 MB
    pathname = os.getcwd()  # Ajusta esto según tu estructura
    base_name, extension = os.path.splitext(file.filename)
    number = 1

    file_name = file.filename
    save_dir = path.join(pathname, "uploads", "files")
    pathToSave = path.join(save_dir, file_name)

    # Evita sobrescribir archivos
    while os.path.exists(pathToSave):
        file_name = f"{base_name}_{number}{extension}"
        number += 1
        pathToSave = path.join(save_dir, file_name)

    # Crea el directorio si no existe
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print("Con el siguiente path:", pathToSave)

    # ✅ Guardar el archivo completamente antes de empezar el streaming
    count = 0
    async with aiofiles.open(pathToSave, "wb") as buffer:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            await buffer.write(chunk)
            count += 1
            await asyncio.sleep(1)  # simulación de proceso lento

    # ✅ Ahora puedes hacer un StreamingResponse desde un generador
    async def streamer():
        for i in range(count):
            await asyncio.sleep(0.5)
            yield f"Chunk {i+1} de {file_name} guardado correctamente\n"

    return StreamingResponse(streamer(), media_type="text/plain")

# Creado y guarda un archivo en la carpeta uploads/files
# @app.post("/api/files/{dataset_id}" , response_model=FileDB)
#TODO
# --- Función de Tarea en Segundo Plano ---
async def process_file_in_background(
    operation_id: str,
    project_id: str,
    file_content: bytes, # Recibe el contenido del archivo, no UploadFile
    original_filename: str,
    db: Session,
    current_user_id: str # Pasa el ID del usuario si lo necesitas
):
    chunk_size = 1024 * 1024  # 1 MB
    pathname = os.getcwd()  # Ajusta esto según tu estructura
    base_name, extension = os.path.splitext(original_filename)
    number = 1

    user_id = str(current_user_id)
    pj_id = str(project_id)
    # print("id de usuario: ",user_id, "id de proyecto", pj_id)

    file_name = original_filename
    save_dir = path.join(pathname,"uploads","files",pj_id) # Usar Path para mejor manejo de rutas
    pathToSave = path.join(save_dir, file_name)

    # Evita sobrescribir archivos
    while os.path.exists(pathToSave):
        file_name = f"{base_name}_{number}{extension}"
        number += 1
        pathToSave = path.join(save_dir, file_name)

    # Crea el directorio si no existe
    # save_dir.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # print("Primer momento que se llama la funcion send_progress_to_websocket")
    await send_progress_to_websocket(operation_id, 0,"Processing", f"Guardando archivo {original_filename}...")
    print(f"[{operation_id}] Saving file to: {pathToSave}")

    await asyncio.sleep(0.5)  # Simulación de proceso lento
    # Guardar el archivo completamente
    total_size = len(file_content)
    bytes_written = 0
    with open(pathToSave, "wb") as buffer:
        for i in range(0, total_size, chunk_size):

            chunk = file_content[i:i + chunk_size]
            buffer.write(chunk)
            bytes_written += len(chunk)
            progress = int((bytes_written / total_size) * 90) # Hasta el 90% para dejar espacio para la DB
            print(f"envio a websocket dentro del bucle [{operation_id}] Progress: {progress}%")
            await send_progress_to_websocket(operation_id, progress, "Saving File", f"Progreso: {progress}%")
            await asyncio.sleep(0.05) # Pequeña pausa para permitir que el loop de eventos envíe mensajes

    # print("tercera vez que se llama la funcion send_progress_to_websocket")
    await send_progress_to_websocket(operation_id, 90, "Creating Dataset", "Archivo guardado. Creando entrada en la base de datos...")
    # await send_steps_to_session(operation_id, "Archivo guardado. Creando entrada en la base de datos...")
    print(f"[{operation_id}] File {original_filename} saved.")

    datasetname = file_name.split(".")[0]  # Nombre del dataset sin extensión
    # Creación del dataset
    try:
        dataset_in_db = await dataset_crud.create_dataset(
            db=db,
            dataset=DatasetCreate(
                name=datasetname,
                project_id=project_id,
                # query_id=None,  # Puedes ajustar esto según tu lógica
                columns=[]  # Inicialmente vacío, puedes agregar columnas más tarde
            ),
        )
        print(f"[{operation_id}] Dataset ID created: {str(dataset_in_db.id)}")
        # print("Cuarta vez que se llama la funcion send_progress_to_websocket")
        await send_progress_to_websocket(operation_id, 95, "Creating File Entry", f"Dataset {dataset_in_db.id} creado. Registrando archivo...")

        file_schema = FileCreate(
            name=file_name,
            path=str(pathToSave),
            size=os.path.getsize(pathToSave), # Tamaño real del archivo guardado # Convierte Path a str
            is_public=True,
            datasets_id=dataset_in_db.id,  # Usa el ID del dataset recién creado
            
            
        )
        print(f"[{operation_id}] File schema for DB: {file_schema}")

        file =await file_crud.create_files(db=db, file=file_schema)
        print(f"[{operation_id}] File entry created successfully in DB.")
        # print('la url del archivo es:', file.path)
        await send_progress_to_websocket(operation_id, 96, "Analyzing File", "Analizando el contenido del dataset")
        [columns_info,total_rows] = await analyze_dataset(file.path)
        print(columns_info)
        for column in columns_info:

            # print("Informacion de la columna:", column)


            column_type= column_type_crud.get_column_type_by_name(db=db, name=column['data_type'])
            value_type = value_type_crud.get_value_type_by_name(db=db,  name='UNDEFINED')
            column_crud.create_column(
                db=db,
                column=ColumnCreate(
                    name=column['name'],
                    dataset_id=dataset_in_db.id,
                    column_type_id=column_type.id,
                    value_type_id=value_type.id,
                )
            )
        
        #actualizacion de estado del dataset
        dataset_to_update = DatasetUpdate(
            id=dataset_in_db.id,
            status='uploaded',
            rows=total_rows
        )


        await dataset_crud.update_dataset_status(db=db,dataset=dataset_to_update)
        # print("Quinta vez que se llama la funcion send_progress_to_websocket")
        await send_progress_to_websocket(operation_id, 100, "Completed", "Proceso completado con éxito.")

    except Exception as e:
        print(f"[{operation_id}] Error during background processing: {e}")
        # print("Error al enviar el mensaje de progreso al WebSocket")
        await send_progress_to_websocket(operation_id, 0, "Error", f"Error en el proceso: {e}")
        


@app.post("/api/testv1/dataset/uploadfile/{project_id}")
async def upload_file_test_endpoint(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AuthorToken = Depends(validate_token_header),
    file: UploadFile = File(...),
):
    

    operation_id = str(uuid.uuid4()) # Genera un ID de operación único

    # Leer el contenido del archivo *antes* de devolver la respuesta
    # Esto es crucial porque 'UploadFile' se cierra después de la respuesta del endpoint.
    file_content = await file.read()
    original_filename = file.filename

    # Añadir la tarea en segundo plano
    background_tasks.add_task(
        process_file_in_background,
        operation_id,
        project_id,
        file_content,
        original_filename,
        db,
        current_user.id # Pasa el ID del usuario si lo necesitas en la tarea de fondo
    )

    # Devolver el operation_id inmediatamente al cliente
    print(f"Operación de carga iniciada con ID:", operation_id,"en el proyecto", project_id)
    return JSONResponse(
        content={
            "message": "Operación de carga iniciada en segundo plano.",
            "operation_id": operation_id,
            "project_id": project_id # Puede ser útil confirmarlo
        },
        status_code=202 # Accepted
    )

    # return StreamingResponse(streamer(), media_type="text/plain")
    

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
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_type_crud.create_column_type(db=db, column_type=column_type)

# GET COLUMN_TYPE

@app.post("/api/value_types" , response_model=ValueType)
async def create_value_type_endpoint(
    value_type: ValueTypeCreate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return value_type_crud.create_value_type(db=db, value_type=value_type)





##############################################################################


# COLUMN endpoints

# CREATE COLUMN

@app.post("/api/columns" , response_model=Column)
async def create_column_endpoint(
    column: ColumnCreate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.create_column(db=db, column=column)



# GET COLUMNS

@app.get("/api/columns/{column_id}", response_model=Column)
async def get_column_endpoint(
    column_id: str,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.get_column(db=db, column_id=column_id)

# GET ALL COLUMNS

@app.get("/api/columns", response_model=list[Column])
async def get_all_columns_endpoint(
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return column_crud.get_all_columns(db=db)


#DATASETS endpoints

# CREATE DATASET

@app.post("/api/datasets" , response_model=Dataset)
async def create_dataset_endpoint(
    dataset: DatasetCreate,
    # current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.create_dataset(db=db, dataset=dataset)

# GET DATASET BY ID
@app.get("/api/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset_endpoint(
    dataset_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db)

):
    return dataset_crud.get_dataset_information(db=db, dataset_id=dataset_id)

# GET DATASET BY ID
@app.get("/api/datasets/test/{dataset_id}", response_model=Dataset)
async def get_dataset_endpoint(
    dataset_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db)

):
    return dataset_crud.get_dataset_information(db=db, dataset_id=dataset_id)
# GET DATASET PREVIEW BY ID

@app.get("/api/datasets/{dataset_id}/preview",response_model=DatasetPreviewResponse )
async def get_dataset_preview_endpoint(
    dataset_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session= Depends(get_db),
    page_index: int = 1,
    rows: int = 10,

):
    return await dataset_crud.get_dataset_preview(dataset_id=dataset_id,db=db, page_index=page_index, rows_per_page=rows)
    
    

# GET DATASETS BY PROJECT ID 

@app.get("/api/datasets/{project_id}", response_model=list[Dataset])
async def get_datasets_by_project_id_endpoint(
    project_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.get_datasets_by_project_id(db=db, project_id=project_id)
@app.delete("/api/datasets/{dataset_id}", response_model=Dataset)
async def delete_dataset_by_id_endpoint(
    dataset_id: str,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.delete_dataset(db=db,dataset_id=dataset_id)

# update dataset 
@app.put("/api/datasets",response_model=Dataset)
async def update_dataset_endpoint(
    dataset: DatasetUpdate,
    current_user: AuthorToken = Depends(validate_token_header),
    db: Session = Depends(get_db),
):
    return dataset_crud.update_dataset_status(db=db,dataset=dataset)
