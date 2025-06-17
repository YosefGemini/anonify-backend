from typing import Dict
from fastapi import WebSocket

active_connections: Dict[str, WebSocket] = {}

def register_connection(operation_id: str, websocket: WebSocket):
    print("registrando sesion con ID:", operation_id)
    active_connections[operation_id] = websocket
    print("conexion registrada", active_connections)


def remove_connection(operation_id: str):

    if operation_id in active_connections:

        del active_connections[operation_id]
    print("Conexion Eliminada", active_connections)

async def send_steps_to_session(dataset_id: str, data: str):
    print("Conexion activa", active_connections)
    ws= active_connections.get(str(dataset_id))
    print ("Sesion que envio en el file:", dataset_id, "\n envio el ws:",ws)

    # print("Session id", session_id, "data", data)
    print("lista de conexiones activas:", active_connections)
    if ws:
        print("Si existe ws")
        await ws.send_text(str(data))

async def send_progress_to_websocket(operation_id: str, progress: int, status: str, message: str = ""):
    """Envía un mensaje de progreso a través del WebSocket."""
    if operation_id in active_connections:
        websocket = active_connections[operation_id]
        print("WebSocket activo para operación:", operation_id)
        try:
            print(f"Enviando mensaje WebSocket para {operation_id}: {progress}, {status}, {message}")
            await websocket.send_json({"progress": progress, "status": status, "message": message})
        except RuntimeError as e:
            # RuntimeError: WebSocket is not connected or closed.
            print(f"Error al enviar mensaje WebSocket para {operation_id}: {e}")
            # Considerar eliminar la conexión rota si persiste el error
        except Exception as e:
            print(f"Error inesperado al enviar mensaje WebSocket para {operation_id}: {e}")

async def notify_disconnect(session_id: str):
    ws = active_connections.get(str(session_id))

    if ws:
        print("si existe el ws para cerrar conexion")
        # message= 
        # await ws.send_text("_CLOSE_")  # señal especial
        
        # await ws.close()  # opcional si quieres forzar el cierre desde el backend también
    remove_connection(session_id)
