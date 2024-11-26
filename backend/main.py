
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

from schemas.file import FileBase, File_DB
from crud import file_crud

from models import file_model, author_model, project_model, column_model, column_type_model, query_model, value_type_model, db_model, dataset_model

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

