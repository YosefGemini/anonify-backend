
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
        'int64': 'number',
        'float64': 'number',
        'bool': 'boolean',
        'datetime64[ns]': 'datetime',
    }
    try:
        # df= pd.read_csv(dataset_url, encoding='utf-8', low_memory=False)
        # Si el archivo es muy grande, podrías considerar leer solo una muestra 
         
        #quiero definir encoding si es utf-8 o latin-1

        dataset = read_csv_for_all_codifications(url=dataset_url)

        df = dataset[0]

        

        
        # df = pd.read_csv(dataset_url, encoding='utf-8', nrows=1000) 

         # Leer solo las primeras 1000 filas

        
        columns_info = []
        for column in df.columns:
            # Inferir el tipo de dato de la columna
            pandas_type = str(df[column].dtype)
            mapped_type = tipo_general.get(pandas_type, pandas_type)
            columns_info.append({
                "name": column,
                "data_type":  pandas_type
            })
        # return {
        #     # "codificacion": c,
        #     "total_col": len(df.columns),
        #     "columns": columns_info
        # }
        return columns_info





    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="El archivo no tiene formato CSV válido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {e}")
    

def detect_codification(ruta):
    with open(ruta, 'rb') as f:
        resultado = chardet.detect(f.read(10000))
    return resultado['encoding']    

def read_csv_for_all_codifications(url):

#     codifications = [
#         'ascii', 'big5','big5hkscs','cp037','cp273','cp424','cp437','cp500','cp720','cp737','cp775','cp850','cp852','cp855','cp856','cp857','cp858','cp860','cp861','cp862','cp863','cp864','cp865','cp866','cp869','cp874','cp875','cp932','cp949',
# 'cp950','cp1006','cp1026','cp1125','cp1140','cp1250','cp1251','cp1252','cp1253','cp1254','cp1255','cp1256','cp1257','cp1258','euc_jp','euc_jis_2004','euc_jisx0213','euc_kr','gb2312','gbk','gb18030','hz','iso2022_jp','iso2022_jp_1','iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext','iso2022_kr','latin_1','iso8859_2','iso8859_3','iso8859_4','iso8859_5','iso8859_6','iso8859_7','iso8859_8','iso8859_9','iso8859_10','iso8859_11','iso8859_13','iso8859_14','iso8859_15','iso8859_16','johab','koi8_r','koi8_t','koi8_u','kz1048','mac_cyrillic','mac_greek','mac_iceland','mac_latin2','mac_roman','mac_turkish','ptcp154','shift_jis','shift_jis_2004','shift_jisx0213','utf_32','utf_32_be','utf_32_le','utf_16','utf_16_be','utf_16_le','utf_7','utf_8','utf_8_sig',
#     ]

    codification= detect_codification(url)

    
    df =pd.read_csv(url, encoding=codification)

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