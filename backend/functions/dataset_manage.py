
import csv # Importa el módulo csv
import os
import pandas as pd
from typing import List, Dict
from pathlib import Path
from fastapi import HTTPException
# def charge_dataset(db: Sessdataset)

import chardet
async def analyze_dataset(dataset_url):
    if not dataset_url:
        raise HTTPException(status_code=400, detail="Dataset URL is required")
    
    if not os.path.exists(dataset_url):
        raise HTTPException(status_code=404, detail="Dataset file not found")
    # Mapear tipos de pandas a tipos generales
    tipo_general = {
        'object': 'string',
        'int64': 'number(integer)',
        'float64': 'number(float)',
        'bool': 'boolean',
        'datetime64[ns]': 'datetime',
    }
    try:
        # df= pd.read_csv(dataset_url, encoding='utf-8', low_memory=False)
        # Si el archivo es muy grande, podrías considerar leer solo una muestra 
        #quiero definir encoding si es utf-8 o latin-1
        dataset =await read_csv_for_all_codifications(url=dataset_url)

        df = dataset[0]
        total_rows = len(df)

        print("codification", dataset[1])
        # df = pd.read_csv(dataset_url, encoding='utf-8', nrows=1000) 

         # Leer solo las primeras 1000 filas

        
        columns_info = []
        for column in df.columns:
            # Inferir el tipo de dato de la columna
            pandas_type = str(df[column].dtype)
            mapped_type = tipo_general.get(pandas_type, pandas_type)
            columns_info.append({
                "name": column,
                "data_type":  mapped_type
            })
        # return {
        #     # "codificacion": c,
        #     "total_col": len(df.columns),
        #     "columns": columns_info
        # }
        return columns_info, total_rows





    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=F"El archivo no tiene formato CSV válido {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {e}")
    

def detect_codification(ruta):
    with open(ruta, 'rb') as f:
        resultado = chardet.detect(f.read(10000))

        print("Codificacion:",resultado['encoding'])
    return resultado['encoding']    


def detect_delimiter(file_path: str, encoding: str, sample_size: int = 1024 * 5) -> str:

    common_delimiters = [',', ';', '\t', '|'] # Delimitadores a probar

    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            # Lee un trozo del archivo con la codificación detectada
            sample_content = f.read(sample_size)
            
            sniffer = csv.Sniffer()
            dialect = None
            try:
                # Intentar detectar el delimitador usando el sniffer
                dialect = sniffer.sniff(sample_content, delimiters=common_delimiters)
                return dialect.delimiter
            except csv.Error:
                # Si Sniffer falla, intenta manualmente con los delimitadores comunes
                print(f"Sniffer no pudo detectar el delimitador con '{encoding}'. Probando manualmente...")
                for sep in common_delimiters:
                    # Intenta leer unas pocas líneas con este separador
                    # Usamos io.StringIO para simular un archivo para pd.read_csv desde el sample
                    try:
                        temp_df = pd.read_csv(io.StringIO(sample_content), sep=sep, nrows=5)
                        if len(temp_df.columns) > 1:
                            return sep # Delimitador encontrado
                    except Exception:
                        continue
                # Si nada funciona, retorna el delimitador más común como fallback
                print("No se detectó un delimitador claro, usando coma como fallback.")
                return ',' 
    except Exception as e:
        print(f"Error al intentar detectar el delimitador para {file_path}: {e}")
        # En caso de error, puedes lanzar o retornar un delimitador por defecto
        return ',' # Fallback si hay un error en la lectura de la muestra



async def read_csv_for_all_codifications(
        url: str,
        skiprows: int=0,
        nrows: int=None

                                         ):


#     codifications = [
#         'ascii', 'big5','big5hkscs','cp037','cp273','cp424','cp437','cp500','cp720','cp737','cp775','cp850','cp852','cp855','cp856','cp857','cp858','cp860','cp861','cp862','cp863','cp864','cp865','cp866','cp869','cp874','cp875','cp932','cp949',
# 'cp950','cp1006','cp1026','cp1125','cp1140','cp1250','cp1251','cp1252','cp1253','cp1254','cp1255','cp1256','cp1257','cp1258','euc_jp','euc_jis_2004','euc_jisx0213','euc_kr','gb2312','gbk','gb18030','hz','iso2022_jp','iso2022_jp_1','iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext','iso2022_kr','latin_1','iso8859_2','iso8859_3','iso8859_4','iso8859_5','iso8859_6','iso8859_7','iso8859_8','iso8859_9','iso8859_10','iso8859_11','iso8859_13','iso8859_14','iso8859_15','iso8859_16','johab','koi8_r','koi8_t','koi8_u','kz1048','mac_cyrillic','mac_greek','mac_iceland','mac_latin2','mac_roman','mac_turkish','ptcp154','shift_jis','shift_jis_2004','shift_jisx0213','utf_32','utf_32_be','utf_32_le','utf_16','utf_16_be','utf_16_le','utf_7','utf_8','utf_8_sig',
#     ]

    codification= detect_codification(url)

    print("[NOTA] la codificacion es", codification)

    delimiter = detect_delimiter(url, codification)
    print(f"[NOTA] El delimitador detectado es: '{delimiter}'")


    if skiprows == 0:
            # Si es la primera "página" (o se quiere leer desde el inicio),
            # Pandas lee el encabezado automáticamente por defecto.
            df = pd.read_csv(
                url,
                encoding=codification,
                sep=delimiter,
                on_bad_lines='skip',
                nrows=nrows # Limita las filas a leer
            )

    else:
        df_header = pd.read_csv(
                url,
                encoding=codification,
                sep=delimiter,
                on_bad_lines='skip',
                nrows=0 # Lee solo el encabezado
            )
        columns = df_header.columns.tolist()
        df = pd.read_csv(
                url,
                encoding=codification,
                sep=delimiter,
                on_bad_lines='skip',
                skiprows=skiprows + 1, # Salta las filas de datos anteriores + la fila del encabezado
                nrows=nrows,
                header=None, # Ya hemos leído los encabezados, no queremos que Pandas los infiera
                names=columns # Asignar los nombres de las columnas que ya detectamos
            )

    # df =pd.read_csv(url, encoding=codification,sep=delimiter, on_bad_lines='skip')

    return df,codification


    # for encoding in codifications:
    #     try:
    #         df = pd.read_csv(url,encoding=encoding)
    #         print("Se codifica con el encoding ", encoding)
    #         return df, encoding
    #     except UnicodeDecodeError:
    #         print("no funciono con la codificacion",encoding )
    #         continue
    # raise UnicodeDecodeError("No se pudo leer el archivo con las codificaciones estandar")