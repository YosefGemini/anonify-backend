
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













