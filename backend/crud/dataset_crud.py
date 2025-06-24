from models import dataset_model 
from models import query_model
from models import column_model
from schemas.dataset import DatasetBase, DatasetCreate, DatasetPreviewResponse, DatasetUpdate
from schemas.column import ColumnDelete
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from pathlib import Path

from crud.column_crud import delete_column
from crud.file_crud import delete_file
import math

from functions.dataset_manage import read_csv_for_all_codifications



async def create_dataset(db: Session, dataset: DatasetCreate):
    # dataset_in_db = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.name == dataset.name).first()

    # if dataset_in_db:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,
    #                         detail=f"Dataset with name {dataset.name} already exists")


    db_dataset = dataset_model.Dataset(
        name=dataset.name,
        project_id=dataset.project_id,
        query_id=dataset.query_id if dataset.query_id else None
    )

    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)

    # creacion de columnas
    print("Fase 0 tipo de dato"+str(type(db_dataset.id)))

    print("Fase 1")

    return db_dataset

async def update_dataset_status(db: Session, dataset: DatasetUpdate):
    dataset_in_db = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.id == dataset.id).first()
    if not dataset_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Dataset with id {dataset.id} not found")
    
    dataset_in_db.status = dataset.status
    dataset_in_db.rows = dataset.rows
    db.commit()
    db.refresh(dataset_in_db)

    return dataset_in_db

def delete_dataset(db:Session, dataset_id: UUID):
    dataset_in_db = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.id == dataset_id).first()

    if not dataset_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Dataset with di {dataset_id} not found")
    
    files_to_delete = dataset_in_db.files
    columns_to_delete = dataset_in_db.columns

    print("Flies a eliminar",files_to_delete)
    print("columnas a eliminar", columns_to_delete)
    print("tamaño del arreglo de archivos:", len(files_to_delete))
    print("tamaño del arreglo de archivos:", len(columns_to_delete))

    print("tamaño del arreglo es diferente de cero?:", len(files_to_delete) !=0)
    print("tamaño del arreglo es diferente de cero?:", len(columns_to_delete)!=0)


    if (len(files_to_delete) != 0):
        print("Entra al if del file")
        for file in files_to_delete:
            try:

                print("eliminando FILE:", file.id)
                delete_file(db=db, file_id=file.id)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error with file {file.id} while try to be deleted with error: {e}")
            continue
    if (len(columns_to_delete) != 0):
        print("Entra al if del column")
        for column in columns_to_delete:
            try:
                print("eliminando COLUMN:", column.id)
                column_id = str(column.id)
                delete_column(db=db, column=ColumnDelete(id=column_id))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error with file {column.id} while try to be deleted with error: {e}")
            continue

    db.delete(dataset_in_db)
    db.commit()

    return dataset_in_db

def get_datasets_by_project_id(db: Session, project_id: str):

    # print("fase 1")
    db_dataset = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.project_id == project_id).all()

    # print("fase 2")
    # print("Dataset encontrado: " + str(db_dataset))
    if not db_dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Dataset with project_id {project_id} not found")

    return db_dataset


def get_dataset_information(db: Session, dataset_id:str):

    db_dataset = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.id == dataset_id).first()

    if not db_dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset with id: {dataset_id} not found")
    
    return db_dataset


async def get_dataset_preview(db: Session, dataset_id: str, page_index: int, rows_per_page: int):
    db_dataset = get_dataset_information(db=db, dataset_id=dataset_id)

    #manejo de errores
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not db_dataset.files:
        raise HTTPException(status_code=404, detail="No file associated with this dataset")
    
    file_path = Path(db_dataset.files[0].path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found at path: {file_path}")
    try:
        print("[TEST]: Tamaño del Dataset:",db_dataset.rows,"Indice de Consulta:",page_index,"Filas por pagina",rows_per_page)
        dataset_tuple =await read_csv_for_all_codifications(url=str(file_path),nrows=rows_per_page,skiprows=(page_index-1)*rows_per_page)
        df = dataset_tuple[0]
        print("[TEST]: Tamaño del Fragmento enviado", len(df))
        total_rows = db_dataset.rows
        total_pages = math.ceil(total_rows / rows_per_page)

        # Calculo del indice de inicio y fin de la paginacion
        # se toma en cuenta que se cuenta desde cero pero se envia el nuemro 1 al endpoint

        start_index = (page_index - 1) * rows_per_page
        end_index = start_index + rows_per_page

        # Obtener las filas del DataFrame de Pandas
        # .iloc[] es para indexación basada en posición
        # preview_df = df.iloc[start_index:end_index]
        preview_df = df

        # Convertir el DataFrame de Pandas a una lista de diccionarios
        # .to_dict(orient='records') es perfecto para esto

        preview_data = preview_df.to_dict(orient='records')

        

        return DatasetPreviewResponse( 
            preview= preview_data,
            index= page_index,
            total_rows= total_rows,
            total_pages= total_pages)
    except Exception as e:
        print(f"Error reading or processing dataset preview for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file for preview: {e}")


