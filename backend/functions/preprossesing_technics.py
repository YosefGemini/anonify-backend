
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from pathlib import Path # Importa Path
from schemas.column import Column

def fit_transform_with_column_names(transformer, X: pd.DataFrame):
    # Ajustamos y transformamos los datos
    X_transformed = transformer.fit_transform(X)

    # Obtenemos las columnas procesadas y las que pasaron por passthrough
    new_feature_names = transformer.get_feature_names_out()

    # Reparar nombres: eliminar prefijos del transformer
    clean_names = [
        name.split("__")[1] if "__" in name else name
        for name in new_feature_names
    ]

    # Convertimos a DataFrame con los nombres originales
    return pd.DataFrame(X_transformed, columns=clean_names, index=X.index)

# --- Función auxiliar para convertir tipos (reutilizable) ---
def ensure_numeric_types(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Intenta convertir las columnas especificadas a un tipo numérico (int o float).
    Si una columna puede ser representada como entero sin perder información (y puede contener NaN),
    se convertirá a Int64 (el tipo entero de Pandas que soporta NaN).
    De lo contrario, se convertirá a float64.
    Los valores que no puedan convertirse a número se reemplazarán con NaN.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        columns (list): Lista de nombres de columnas a convertir.

    Returns:
        pd.DataFrame: El DataFrame con las columnas convertidas. Retorna una copia para evitar side effects.
    """
    df_copy = df.copy() # Trabajar siempre en una copia

    print("\n--- Asegurando Tipos Numéricos ---")

    for col in columns:
        if col not in df_copy.columns:
            print(f"  Advertencia: La columna '{col}' no se encontró en el DataFrame. Saltando conversión.")
            continue

        original_dtype = df_copy[col].dtype

        try:
            # Primero, intenta convertir a numérico, forzando errores a NaN
            # Esto es clave para limpiar cualquier string o valor no convertible
            temp_series = pd.to_numeric(df_copy[col], errors='coerce')

            # --- Lógica para decidir entre Int64 y float64 ---
            # 1. Verificar si hay NaNs después de la conversión.
            # 2. Si no hay NaNs y todos los valores son enteros (sin parte decimal),
            #    entonces podemos intentar convertir a 'Int64' (el tipo entero de Pandas que maneja NaNs).
            #    Si hay decimales o NaNs, generalmente float es más seguro.

            # Identificar si todos los valores no nulos son "enteros" (sin parte fraccional)
            # Y si la columna no estaba ya como un tipo flotante que introdujo decimales
            is_pure_integer = (temp_series.dropna() == temp_series.dropna().astype(int)).all()

            if temp_series.isnull().any() or not is_pure_integer:
                # Si hay NaNs (incluyendo los 'coerce') O si hay valores no enteros (decimales),
                # la convertimos a float64. Float64 es el tipo seguro para decimales y NaNs.
                df_copy[col] = temp_series.astype(float)
                print(f"  Columna '{col}': Convertida de {original_dtype} a {df_copy[col].dtype} (contiene decimales o NaNs, o no es puramente entera).")
            else:
                # Si no hay NaNs y todos los valores son puramente enteros, podemos usar Int64.
                # 'Int64' es el tipo entero de Pandas que soporta valores nulos (pd.NA).
                df_copy[col] = temp_series.astype('Int64')
                print(f"  Columna '{col}': Convertida de {original_dtype} a {df_copy[col].dtype} (todos los valores son enteros, sin NaNs, o NaNs coercidos fueron tratados).")

        except Exception as e:
            # Esto es una red de seguridad si algo inesperado ocurre durante la conversión
            print(f"  Advertencia: No se pudo convertir la columna '{col}' a numérica debido a un error inesperado: {e}. Se mantiene el tipo actual ({original_dtype}).")
            df_copy[col] = df[col] # Revertir a la original si hay un error crítico

    return df_copy

## Convertir explícitamente None a NaN en todo el DataFrame
async def convert_null_data(df: pd.DataFrame ):
  
    val = df.replace({None: np.nan}, inplace=True)
    return val

async def convert_null_data_with_value(df: pd.DataFrame, value: int | float, columns: list[Column] ):

    # columnas filtradas
    col_names = [col.name for col in columns]
    df_filtered = df[col_names]


    # Identificar columnas numéricas y categóricas Dataset con columnas vacias eliminadas
    numerical_cols = df_filtered.select_dtypes(include=np.number).columns
    categorical_cols = df_filtered.select_dtypes(include='object').columns

    numerical_imputer_zero = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value=value))
    ])
    #TODO esto hay que definir como parámetro, no como valor fijo
    categorical_imputer_none = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='Missing'))
    ])

    preprocessor_minimal_expressive = ColumnTransformer(
    transformers=[
        ('num_imp', numerical_imputer_zero, numerical_cols),
        ('cat_imp', categorical_imputer_none, categorical_cols) # Usar las columnas filtradas
    ],
    remainder='passthrough'
)
    df_transformado = fit_transform_with_column_names(preprocessor_minimal_expressive, df)
    return df_transformado

async def drop_rows_by_missing_threshold(
    df: pd.DataFrame,
    threshold_percentage: float,  # porcentaje de columnas con NaN para eliminar la fila (0-100)
    columns: list  # lista de columnas a evaluar
) -> pd.DataFrame:
    """
    Elimina filas si el porcentaje de valores faltantes en las columnas especificadas
    supera el umbral threshold_percentage. Las demás filas quedan intactas.

    Args:
        df (pd.DataFrame): DataFrame original
        threshold_percentage (float): porcentaje (0-100) de columnas con NaN para eliminar fila
        columns (list): columnas a evaluar (lista de Column o str)

    Returns:
        pd.DataFrame: DataFrame resultante, mismo índice que el original
    """

    # Obtener nombres de columnas si recibimos objetos tipo Column
    col_names = [col.name if hasattr(col, 'name') else col for col in columns]

    # Filtramos solo las columnas que realmente existen en el DataFrame
    col_names = [col for col in col_names if col in df.columns]

    if not col_names:
        # Si no hay columnas válidas, devolvemos el df original
        return df.copy()

    # Número de columnas a considerar
    total_cols = len(col_names)

    # Umbral absoluto: cuántos NaN equivalen al porcentaje dado
    threshold_count = int(np.floor((threshold_percentage / 100) * total_cols))

    # Boolean mask: True si fila cumple con superar el umbral de NaN
    mask = df[col_names].isna().sum(axis=1) > threshold_count

    # Eliminamos filas que superan el umbral
    df_result = df.loc[~mask].copy()

    return df_result

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


async def arithmetic_mean_imputation_with_specification(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Imputa los valores NaN de las columnas numéricas especificadas usando la media.
    Solo aplica imputación a columnas que realmente son numéricas.
    
    Args:
        df (pd.DataFrame): DataFrame sobre el que se trabaja
        columns (list[str]): columnas a evaluar
    
    Returns:
        pd.DataFrame: DataFrame con las columnas numéricas imputadas, mismo índice y nombres de columnas intactos
    """

    # Filtramos columnas que existen en el DataFrame
    col_names = [col for col in columns if col in df.columns]

    if not col_names:
        return df  # No hay columnas válidas

    # Filtramos solo las columnas numéricas
    numerical_cols = df[col_names].select_dtypes(include=np.number).columns

    if len(numerical_cols) == 0:
        return df  # No hay columnas numéricas para imputar

    # Imputador por media
    imputer = SimpleImputer(strategy="mean")

    # Aplicamos imputación solo a las columnas numéricas seleccionadas
    df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

    return df


async def knn_imputation(df: pd.DataFrame, columns: list[str]):

    # especifico para valores numericos

    imputer_numerico = KNNImputer(n_neighbors=2)
    print("\n🔹 Usando imputación con KNN-Imputer.\n")

    df[columns] = imputer_numerico.fit_transform(df[columns])
    return df


async def knn_imputation_with_specifications(df: pd.DataFrame, columns: list[str], n_neighbors: int = 5) -> pd.DataFrame:
    """
    Imputa valores NaN en columnas numéricas usando KNNImputer.
    
    Args:
        df (pd.DataFrame): DataFrame sobre el que se trabaja
        columns (list[str]): columnas a evaluar
        n_neighbors (int): número de vecinos para KNN
    
    Returns:
        pd.DataFrame: DataFrame con columnas numéricas imputadas, mismo índice y nombres de columnas intactos
    """

    # Filtrar columnas que existen en el DataFrame
    col_names = [col for col in columns if col in df.columns]

    if not col_names:
        return df  # No hay columnas válidas

    # Seleccionar solo columnas numéricas
    numerical_cols = df[col_names].select_dtypes(include=np.number).columns

    if len(numerical_cols) == 0:
        return df  # No hay columnas numéricas para imputar

    # Crear el imputador KNN
    imputer = KNNImputer(n_neighbors=n_neighbors)

    # Aplicar imputación solo a las columnas numéricas seleccionadas
    df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

    return df

async def moda_imputation(df: pd.DataFrame, columns: list[str]):
    # Aplicar imputación a valores categóricos con moda (valor más frecuente)
    imputer_categorico = SimpleImputer(strategy="most_frequent")
    df[columns] = imputer_categorico.fit_transform(df[columns])

    return df

async def mode_imputation_with_specifications(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Imputa los valores NaN de columnas categóricas usando la moda (valor más frecuente).
    Solo se aplica a columnas de tipo object o categóricas.
    
    Args:
        df (pd.DataFrame): DataFrame sobre el que se trabaja
        columns (list[str]): columnas a evaluar
    
    Returns:
        pd.DataFrame: DataFrame con las columnas categóricas imputadas, mismo índice y nombres de columnas intactos
    """

    # Filtramos columnas que existen en el DataFrame
    col_names = [col for col in columns if col in df.columns]

    if not col_names:
        return df  # No hay columnas válidas

    # Filtrar solo columnas categóricas
    categorical_cols = df[col_names].select_dtypes(include=['object', 'category']).columns

    if len(categorical_cols) == 0:
        return df  # No hay columnas categóricas para imputar

    # Imputador por moda
    imputer = SimpleImputer(strategy='most_frequent')

    # Aplicar imputación solo a columnas categóricas
    df[categorical_cols] = imputer.fit_transform(df[categorical_cols])

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










