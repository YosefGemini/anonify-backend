

from functions.preprossesing_technics import convert_null_data,show_duplicates, remove_duplicates, identify_number_columns,identify_categorical_columns, aritmetic_mean_imputation, knn_imputation, moda_imputation, saveDataFrame,remove_empty_columns
from schemas.dataset import DatasetParameters, DatasetUpdate
from schemas.file import FileCreate, FileUpdate
from schemas.column import ColumnCreate
import os
from functions.connetions import send_progress_to_websocket, notify_disconnect
from functions.dataset_manage import read_csv_for_all_codifications
from models import dataset_model
from fastapi import HTTPException, status
# from crud.file_crud import create_files
from crud.dataset_crud import update_dataset_status
import asyncio
import pandas as pd
from sqlalchemy.orm import Session
from crud import dataset_crud, file_crud, column_crud,column_type_crud, value_type_crud
from functions.dataset_manage import analyze_dataset
async def preprocess_dataset(db: Session ,datasetID: str,projectID: str, parameters: DatasetParameters, operationID: str ):


    


    #TODO

    try:

        await asyncio.sleep(0.5)
        # await asyncio.sleep(5)
        await send_progress_to_websocket(operationID,10,"Cargando datos..", "Obteniendo informacion de la Base de Datos")

        dataset_in_db = db.query(dataset_model.Dataset).filter(dataset_model.Dataset.id == datasetID).first()

        if not dataset_in_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset with ID {datasetID} not found")

        project_id_in_db =(str(dataset_in_db.project_id))
        files = dataset_in_db.files

        if not parameters.need_preprocess:
            await send_progress_to_websocket(operationID,87,"Analizando Archivo", "Registro de columnas del archivo generado correctamente")
            # agregando registro en base de datos
            #TODO 
            # Falta que envie el dato de la entidad que seva a asociar
            await update_dataset_status(
                db=db,
                dataset=DatasetUpdate(
                    id=dataset_in_db.id,
                    status='no_preprocessed',
                        # Actualiza el número de filas
                    entity=dataset_in_db.entity if dataset_in_db.entity else None  # Mantiene la entidad si existe
                )
            )
            

        origin_file_path = files[0].path
        #TODO
        # hay que hacer que tambien verifique si no esta en los proyectos compartidos
        if not (project_id_in_db == projectID):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        


        await send_progress_to_websocket(operationID,5,"Cargando datos..", "Iniciando la carga del CSV")

        [df, cod] = await read_csv_for_all_codifications(url=origin_file_path)

        print("Contenido del CSV:\n",df.head(5))
        print("Codificacion del CSV:\n",cod)
        print("Cantidad de Filas", len(df))


        # Convertir explícitamente None a NaN en todo el DataFrame
        await send_progress_to_websocket(operationID,10,"Limpiando...", "limpiando valores nulos")
        await convert_null_data(df)
        await asyncio.sleep(1)

        # Verificar y extrar valores duplicados
        await send_progress_to_websocket(operationID,15,"Analizando...", "Identificando valores duplicados")
        duplicates= await show_duplicates(df=df)

        print(duplicates)
        if duplicates != 'No hay valores duplicados.':

            await send_progress_to_websocket(operationID,20,"Analizando...", "Se identificaron Valores duplicados")
            # Eliminar valores duplicados 
            remove_duplicates(df=df)
            await asyncio.sleep(1)

        await send_progress_to_websocket(operationID,20,"Analizando...", "Se identificaron Valores duplicados")
        await asyncio.sleep(1)



        # Limpiar Columnas Vacias
        await send_progress_to_websocket(operationID,25,"Limpiando...", "Limpiando Columnas con datos Vacios")
        df = await remove_empty_columns(df)

        await asyncio.sleep(1)

        # Identificar Columnas numericas y categoricas

        await send_progress_to_websocket(operationID,30,"Analizando...", "Identificando columnas numericas y categoricas")
        numerical = await identify_number_columns(df=df)
        categorical = await identify_categorical_columns(df=df)
        print("Columnas categoricas", categorical, "columnas numericas", numerical)
        await asyncio.sleep(1)

        # Imputacion de valores numericos

        await send_progress_to_websocket(operationID,40,"Analizando...", "Imputando valores numericos")
        #TODO esto hay que definir bien la forma de envio de los datos seria recomendable enviar en un solo dataset
        if parameters.need_imputation == True and parameters.cleaning_method == 'knn-imputation':
            await knn_imputation(df=df, columns=numerical)
        elif parameters.need_imputation == True and parameters.cleaning_method == 'mean-imputation':
            await aritmetic_mean_imputation(df=df,columns=numerical)
        
        else:
            print("\nOpción no válida. Se usará imputación con MEDIA por defecto.\n")
            await aritmetic_mean_imputation(df=df,columns=numerical)

        await asyncio.sleep(1)
        # Imputacion a valores no numericos (Categoricos)
        await send_progress_to_websocket(operationID,60,"Analizando...", "Imputando valores categoricos")

        await moda_imputation(df=df, columns=categorical)


        # Guardando nuevo archivo 

        await send_progress_to_websocket(operationID,70,"Analizando...", "Imputando valores categoricos")

        file_newPath = dataset_in_db.files[0].path.replace(".csv", "_preprocessed.csv")
        print(f"[{operationID}] Guardando archivo preprocesado en: {file_newPath}")
        value=await saveDataFrame(df, file_newPath,cod)

        

        await send_progress_to_websocket(operationID,80,"Guardando archivo", "Guardando archivo preprocesado")
        #despues de guardado el archivo se procede a crear el registor en la base de datos del FILE
        if value:

            file= await file_crud.create_files(db=db,file= FileCreate(
                name=dataset_in_db.files[0].name.replace(".csv", "_preprocessed.csv"),
                path=file_newPath,
                size=os.path.getsize(file_newPath),  # Tamaño real del archivo guardado
                is_public=True,
                datasets_id=dataset_in_db.id,  # Usa el ID del dataset recién creado
                detail="preprocessed",
                columns=[]
            ))

            await send_progress_to_websocket(operationID, 85, "Analyzing File",f"Registro del Archivo creado satisfactoriamente en la base de  con los siguientes datos")
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
                    file_id=file.id,
                    column_type_id=column_type.id,
                    value_type_id=value_type.id,
                )
            )
        
            await send_progress_to_websocket(operationID,87,"Analizando Archivo", "Registro de columnas del archivo generado correctamente")
            # agregando registro en base de datos
            #TODO 
            # Falta que envie el dato de la entidad que seva a asociar
            await update_dataset_status(
                db=db,
                dataset=DatasetUpdate(
                    id=dataset_in_db.id,
                    status='preprocessed',
                      # Actualiza el número de filas
                    entity=dataset_in_db.entity if dataset_in_db.entity else None  # Mantiene la entidad si existe
                )
            )
            await send_progress_to_websocket(operationID, 89, "Refresh", "Actualizando estado del registro del dataset")
            await asyncio.sleep(0.05)
            # actualizando informacion del file
            await file_crud.update_file(db=db, file=FileUpdate(
                id=str(file.id),
                rows=len(df),
                # detail="preprocessed"
            ) )
        
            await asyncio.sleep(1)
            await send_progress_to_websocket(operationID,90,"Guardando Cambios", "Registro de cambios guardado en la base de datos")
        else:
            await asyncio.sleep(1)
            await send_progress_to_websocket(operationID,90,"Cambios no guardados", "Los cambios no se registraron en la base de datos")
        
        await send_progress_to_websocket(operationID,100,"Completed", "Proceso completado con éxito.")

    except Exception as e:
        print(f"[{operationID}] Error during background processing: {e}")
        await send_progress_to_websocket(operationID, 0, "Error",f"Error en el Proceso: {e}")
