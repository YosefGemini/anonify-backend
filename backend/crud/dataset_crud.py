from models import dataset_model 
from models import query_model
from models import column_model
from schemas.dataset import DatasetBase, DatasetCreate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID



def create_dataset(db: Session, dataset: DatasetCreate):
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


    id_toColumn = str(db_dataset.id)

    print("Fase 1.1")
    print("tipo de dato"+str(type(id_toColumn)))
    print("Dato:"+id_toColumn)
    print("Fase 1.2")
    print("Dato Columnas:"+str(dataset.columns))
    for column in dataset.columns:
        print("Fase 2")
        db_column = column_model.Column(
            name=column.name,
            column_type_id=column.column_type_id if column.column_type_id else None,
            value_type_id=column.value_type_id if column.value_type_id else None,
            dataset_id=id_toColumn
            
        )
        print("Fase 3")
        db.add(db_column)
        print("Fase 4")
        

    print("Fin de la funcion de creacion del dataset")
        
    
    print("Despues del commit")
    db.commit()
        
    print("Despues del refresh")
    db.refresh(db_column)
    # print(str(db_column))
    print("Despues del print")
    print(str(db_dataset))

    return db_dataset



def get_datasets_by_project_id(db: Session, project_id: str):
    db_dataset = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.project_id == project_id).all()

    if not db_dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Dataset with project_id {project_id} not found")

    return db_dataset
