
from sqlalchemy.orm import Session


import os
import asyncio
from functions.connetions import send_progress_to_websocket

from crud import dataset_crud, file_crud, column_crud,column_type_crud, value_type_crud
from functions.dataset_manage import analyze_dataset

from schemas.dataset import DatasetCreate, DatasetUpdate
from schemas.file import FileCreate
from schemas.column import ColumnCreate
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
    save_dir = os.path.join(pathname,"uploads","files",pj_id) # Usar Path para mejor manejo de rutas
    pathToSave = os.path.join(save_dir, file_name)

    # Evita sobrescribir archivos
    while os.path.exists(pathToSave):
        file_name = f"{base_name}_{number}{extension}"
        number += 1
        pathToSave = os.path.join(save_dir, file_name)

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