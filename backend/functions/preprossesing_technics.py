
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from pathlib import Path # Importa Path

## Convertir explícitamente None a NaN en todo el DataFrame
async def convert_null_data(df: pd.DataFrame ):
  
    val = df.replace({None: np.nan}, inplace=True)
    return val

# Eliminar valores duplicados
async def show_duplicates(df: pd.DataFrame):

    print("\n🔍 Valores Duplicados Antes de Eliminar:")
    duplicates= df[df.duplicated(keep=False)] 
    return duplicates if not duplicates.empty else "No hay valores duplicados."

async def remove_duplicates(df: pd.DataFrame):
    initial_count = len(df)
    dataframe_rem = df.drop_duplicates(inplace=True)
    final_count = len(df)
    print(f"/n✅ Valores Duplicados Eliminados: {initial_count - final_count} filas eliminadas.")

    return dataframe_rem

    # return dataframe_rem



async def identify_number_columns(df: pd.DataFrame):
    numeric_columns = df.select_dtypes(include=["number"]).columns
    if numeric_columns.empty:
        print("No hay columnas numéricas en el DataFrame.")
        return []

    return  numeric_columns.tolist()

async def identify_categorical_columns(df: pd.DataFrame):
    categorical_columns = df.select_dtypes(exclude=["number"]).columns
    if categorical_columns.empty:
        print("No hay columnas categóricas en el DataFrame.")
        return []

    return categorical_columns.tolist()

# Metodos de Imputacion de datos faltantes


#Imputacion por media aritmetica

async def aritmetic_mean_imputation(df: pd.DataFrame, columns: list[str]):

    # especifico para columnas numericas
    # columnas_numericas = identify_number_columns(df=df)


    imputer_numerico = SimpleImputer(strategy="mean")
    print("\n🔹 Usando imputación con MEDIA.\n")

    df[columns] = imputer_numerico.fit_transform(df[columns])

    return df

async def knn_imputation(df: pd.DataFrame, columns: list[str]):

    # especifico para valores numericos

    imputer_numerico = KNNImputer(n_neighbors=2)
    print("\n🔹 Usando imputación con KNN-Imputer.\n")

    df[columns] = imputer_numerico.fit_transform(df[columns])
    return df


async def moda_imputation(df: pd.DataFrame, columns: list[str]):
    # Aplicar imputación a valores categóricos con moda (valor más frecuente)
    imputer_categorico = SimpleImputer(strategy="most_frequent")
    df[columns] = imputer_categorico.fit_transform(df[columns])

    return df

async def saveDataFrame(df: pd.DataFrame, url: str, encoding: str):
    # df.to_csv()
    try:
        file_path = Path(url)

        df.to_csv(file_path, index=False, encoding=encoding)
        return True
    except Exception as e:
        print("Error al guardar CSV", e)
        return False


async def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:

    if not isinstance(df, pd.DataFrame):
        raise TypeError("La entrada debe ser un DataFrame de Pandas.")

    # Identificar columnas donde TODOS los valores son NaN/null
    # df.isnull() devuelve un DataFrame booleano (True si es NaN, False si no)
    # .all() aplicado a un DataFrame booleano, por defecto, comprueba si TODAS
    # las entradas en cada columna son True (es decir, todas son NaN).
    # [df.isnull().all()] obtiene una Serie booleana donde el índice son los
    # nombres de las columnas y el valor es True si la columna está completamente vacía.
    
    # df.columns[df.isnull().all()] te da los nombres de las columnas que cumplen esta condición.
    columns_to_drop = df.columns[df.isnull().all()].tolist()

    if columns_to_drop:
        print(f"Detectadas y eliminando columnas completamente vacías: {columns_to_drop}")
        # df.drop() elimina las columnas especificadas.
        # axis=1 indica que queremos eliminar columnas (axis=0 es para filas).
        df_cleaned = df.drop(columns=columns_to_drop)
    else:
        print("No se encontraron columnas completamente vacías para eliminar.")
        df_cleaned = df.copy() # Devolvemos una copia si no hay cambios para evitar SettingWithCopyWarning

    return df_cleaned










