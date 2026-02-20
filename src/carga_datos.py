# -*- coding: utf-8 -*-
import os
import pandas as pd

# =========================
# RUTAS DEL PROYECTO
# =========================

# __file__ es la ruta de este archivo .py
# dirname(dirname(__file__)) sube dos niveles de carpetas
# Esto apunta a la carpeta raíz del proyecto (organizador_de_viajes)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Ruta a la carpeta "data" dentro del proyecto
DATA_DIR = os.path.join(BASE_DIR, "data")

# Rutas completas a los archivos Excel
RUTA_EMPLEADOS = os.path.join(DATA_DIR, "empleados.xlsx")
RUTA_CHOFERES = os.path.join(DATA_DIR, "choferes.xlsx")


# =========================
# COLUMNAS ESPERADAS
# =========================
# Estas son las columnas obligatorias que deben existir
# en cada archivo Excel

COLUMNAS_EMPLEADOS = {
    "id_empleado",
    "nombre",
    "direccion",
    "localidad",
    "horario_ingreso",
    "horario_salida",    
    "preferencia",
    "observaciones"
}

COLUMNAS_CHOFERES = {
    "id_chofer",
    "nombre",
    "direccion",
    "localidad",
    "disponible",
    "plazas",
    "observaciones"
}


# =========================
# NORMALIZACIÓN EMPLEADOS
# =========================
def normalizar_empleados(df):
    """
    Limpia y normaliza los datos del DataFrame de empleados,
    especialmente el horario de ingreso.
    """
    
    def parse_horario(valor):
        """
        Convierte distintos formatos de horario (número, string, vacío)
        a un objeto time o None si no es válido.
        """

        # Si el valor está vacío (NaN)
        if pd.isna(valor):
            return None

        # Si el valor es numérico (ej: 8, 8.0)
        if isinstance(valor, (int, float)):
            hora = int(valor)
            if 0 <= hora <= 23:
                # Convierte 8 -> 08:00
                return pd.to_datetime(
                    f"{hora:02d}:00",
                    format="%H:%M"
                ).time()
            return None

        # Si es string, se limpia
        valor = str(valor).strip()

        # Caso "8" o "08"
        if valor.isdigit():
            hora = int(valor)
            if 0 <= hora <= 23:
                return pd.to_datetime(
                    f"{hora:02d}:00",
                    format="%H:%M"
                ).time()
            return None

        # Caso "8:00", "08:30"
        try:
            return pd.to_datetime(
                valor,
                format="%H:%M"
            ).time()
        except Exception:
            # Si no se puede convertir, se descarta
            return None

    # Aplica la función parse_horario a toda la columna
    df["horario_ingreso"] = df["horario_ingreso"].apply(parse_horario)

    return df


# =========================
# NORMALIZACIÓN CHOFERES
# =========================
def normalizar_choferes(df):
    """
    Limpia y normaliza los datos del DataFrame de choferes.
    """

    # Normaliza la columna "disponible"
    # Convierte SI / NO a True / False
    df["disponible"] = (
        df["disponible"]
        .astype(str)        # Convierte todo a string
        .str.strip()        # Quita espacios
        .str.upper()        # Pasa a mayúsculas
        .map({"SI": True, "NO": False})  # Mapea a booleanos
    )

    # Convierte la columna "plazas" a entero
    # Si no se puede convertir, queda como NaN
    df["plazas"] = pd.to_numeric(
        df["plazas"],
        errors="coerce"
    ).astype("Int64")

    return df


# =========================
# VALIDACIÓN DE COLUMNAS
# =========================
def validar_columnas(df, columnas_esperadas, nombre):
    """
    Verifica que el DataFrame tenga todas las columnas obligatorias.
    Si falta alguna, lanza un error.
    """

    # Columnas que realmente tiene el archivo
    columnas_actuales = set(df.columns)

    # Columnas que faltan
    faltantes = columnas_esperadas - columnas_actuales

    # Si hay columnas faltantes, se detiene el programa
    if faltantes:
        raise ValueError(
            f"El archivo {nombre} no tiene las columnas: {faltantes}"
        )


# =========================
# CARGA DE EMPLEADOS
# =========================
def cargar_empleados():
    """
    Lee el archivo empleados.xlsx,
    valida columnas y normaliza los datos.
    """
    df = pd.read_excel(RUTA_EMPLEADOS)

    validar_columnas(df, COLUMNAS_EMPLEADOS, "empleados.xlsx")

    df = normalizar_empleados(df)

    return df


# =========================
# CARGA DE CHOFERES
# =========================
def cargar_choferes():
    """
    Lee el archivo choferes.xlsx,
    valida columnas y normaliza los datos.
    """
    df = pd.read_excel(RUTA_CHOFERES)
    validar_columnas(df, COLUMNAS_CHOFERES, "choferes.xlsx")
    df = normalizar_choferes(df)

    return df


##HASTA ACÁ PERFECTO, CARGAMOS LOS DATOS Y NORMALIZAMOS
## PRIMER PASO CHECK

##SIGUIENTE PASO, AGREGAR COLUMNA DONDE PASEMOS DE DIRECCION FIJA A COORDENADAS QUE SERAN LEIDAS POR MAPS

# =========================
# CARGA DE DISTANCIAS A PLANTA
# =========================










from src.geolocalizacion import *
# Importa la función que convierte una dirección en (latitud, longitud)
# Viene de tu módulo geolocalizacion.py


# =========================
# COORDENADAS
# =========================
def agregar_coordenadas(df):
    """
    Agrega columnas de latitud y longitud al DataFrame de empleados
    usando la columna 'direccion'.
    """

    # Listas donde se irán guardando las latitudes y longitudes
    lats = []
    lons = []

    # Recorre cada dirección de la columna 'direccion'
    for direccion, localidad in zip(df["direccion"], df["localidad"]):
    # Geocodifica la dirección (puede devolver None, None)
        lat, lon = geocodificar_direccion(direccion,localidad)

        # Guarda los resultados en las listas
        lats.append(lat)
        lons.append(lon)

    # Agrega las listas como nuevas columnas del DataFrame
    df["lat"] = lats
    df["lon"] = lons

    # Devuelve el DataFrame con las nuevas columnas
    return df


def obtener_datos_planta():
    direccion = input("Ingrese la dirección de la planta: ")
    localidad = input("Ingrese la localidad de la planta: ")
    return direccion, localidad
