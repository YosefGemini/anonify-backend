from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from schemas.file import FileBase , FileDB, FileUpdate, FileDelete, FileCreate
from models import file_model
from pathlib import Path
from schemas.column import ColumnDelete
from crud.column_crud import delete_column
import os


# No necesitas configurar las credenciales manualmente

# Crea un cliente de S3 (o cualquier otro servicio de AWS)


async def create_files(db: Session, file: FileCreate):
    file_in_db = db.query(file_model.File).filter(file_model.File.path == file.path).first()
    if file_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"File with path {file.path} already exists")
        
    db_file = file_model.File(
        name=file.name,
        path=file.path,
        size=file.size,
        is_public=file.is_public,
        datasets_id=file.datasets_id,
        detail=file.detail,
        columns=file.columns

        #product_id=file.product_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    # por cada iteracion guarda el archivo en la lista
    

    return db_file


# def create_files(db: Session, files: list[FileBase]):
#     response_files = []

#     for file in files:
#         file_in_db = db.query(file_model.File).filter(file_model.File.path == file.path).first()
#         if file_in_db:
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT,
#                                 detail=f"File with path {file.path} already exists")

#         product_in_db = db.query(product_model.Product).get(file.product_id)
#         if not product_in_db:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                 detail=f"Product with id {file.product_id} not found")

#         db_file = file_model.File(
#             name=file.name,
#             path=file.path,
#             product_id=file.product_id
#         )
#         db.add(db_file)
#         db.commit()
#         db.refresh(db_file)
#         response_files.append(db_file)

#         # Subir el archivo al bucket S3
#         upload_to_s3(file.path, file.content)

#     return response_files


def get_file(db: Session, file_id: UUID):
    file_in_db = db.query(file_model.File).filter(file_model.File.id == file_id).first()

    if not file_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"File with id {file_id} not found")
    return file_in_db


async def update_file(db: Session, file: FileUpdate):
    file_in_db = db.query(file_model.File).filter(file_model.File.id == file.id).first()

    if not file_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"File with id {file.id} not found")

    # Iterar por los atributos definidos en el modelo y actualizarlos si no son None
    for field, value in file.dict(exclude_unset=True).items():
        if field != "id":
            setattr(file_in_db, field, value)

    db.commit()
    db.refresh(file_in_db)

    return file_in_db


def delete_file(db: Session, file_id: UUID):

    print("Este es el FileID",file_id)
    file_in_db = db.query(file_model.File).filter(file_model.File.id == file_id).first()

    print("este es el archivo recuperado del DB:", file_in_db)

    if not file_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"file register with id {file_id} not found in db")



    print("File Path", file_in_db.path)

    file_path_str =file_in_db.path

    print("dentro de la funcion del path del File este es el PATH",file_path_str)
    # convierto el string en un tipo 
    file_path = Path(file_path_str)


    # eliminacion de columnas

    
    

    file_deleted_physically = False

    if file_path.exists():

        try:
            os.remove(file_path)
            file_deleted_physically = True
            print(f"File '{file_path}' physically deleted.")

        except OSError as e:
            print(f"Error deleting physical file {file_path}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete physical file: {e}"
            )
        except Exception as e:
            print(f"error desconocido {e}")
            raise HTTPException(
                
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete physical file: {e}"
            )
    else:
        print(f"Physical file '{file_path}' does not exist. Proceeding with DB record deletion.")
        file_deleted_physically = True # Si no existe, es como si ya estuviera borrado 
        


    if file_deleted_physically:


        columns_to_delete = file_in_db.columns

        for column in columns_to_delete:
            try:
                print("eliminando COLUMN:", column.id)
                column_id = str(column.id)
                delete_column(db=db, column=ColumnDelete(id=column_id))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error with file {column.id} while try to be deleted with error: {e}")
            continue

        # ya eliminadas todas las columnas se procede a realizar la eliminacion del file en el DB
        db.delete(file_in_db)
        db.commit()



    return file_in_db



    


    

    
     
    
    