
from functions import knn_algorithm 



def procesar_patada(value):

    print("Procesando patada")
    valor_patada = knn_algorithm.procesar_patada_con_knn()
    print(value)
    
    return{ "processed": True, "valor_patada": valor_patada }




    # Aquí se procesa la patada
    