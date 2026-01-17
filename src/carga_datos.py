# -*- coding: utf-8 -*-
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # carpeta organizador_de_viajes
DATA_DIR = os.path.join(BASE_DIR, "data")

RUTA_EMPLEADOS = os.path.join(DATA_DIR, "empleados.xlsx")
RUTA_CHOFERES = os.path.join(DATA_DIR, "choferes.xlsx")


COLUMNAS_EMPLEADOS = {
    "id_empleado",
    "nombre",
    "direccion",
    "horario_ingreso",
    "preferencia",
    "observaciones"
}

COLUMNAS_CHOFERES = {
    "id_chofer",
    "nombre",
    "direccion",
    "disponible",
    "plazas",
    "observaciones"
}


def normalizar_empleados(df):
    def parse_horario(valor):
        if pd.isna(valor):
            return None

        # Si es número (8, 8.0)
        if isinstance(valor, (int, float)):
            hora = int(valor)
            if 0 <= hora <= 23:
                return pd.to_datetime(f"{hora:02d}:00", format="%H:%M").time()
            return None

        # Si es string
        valor = str(valor).strip()

        # Caso "8" o "08"
        if valor.isdigit():
            hora = int(valor)
            if 0 <= hora <= 23:
                return pd.to_datetime(f"{hora:02d}:00", format="%H:%M").time()
            return None

        # Caso "8:00", "08:30"
        try:
            return pd.to_datetime(valor, format="%H:%M").time()
        except Exception:
            return None

    df["horario_ingreso"] = df["horario_ingreso"].apply(parse_horario)

    return df

##normalizacion
def normalizar_choferes(df):
    # Normalizar disponible (SI/NO -> True/False)
    df["disponible"] = (
        df["disponible"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map({"SI": True, "NO": False})
    )

    # Plazas a entero
    df["plazas"] = pd.to_numeric(
        df["plazas"],
        errors="coerce"
    ).astype("Int64")

    return df


def validar_columnas(df, columnas_esperadas, nombre):
    columnas_actuales = set(df.columns)
    faltantes = columnas_esperadas - columnas_actuales

    if faltantes:
        raise ValueError(
            f"El archivo {nombre} no tiene las columnas: {faltantes}"
        )

def cargar_empleados():
    df = pd.read_excel(RUTA_EMPLEADOS)
    validar_columnas(df, COLUMNAS_EMPLEADOS, "empleados.xlsx")
    df = normalizar_empleados(df)
    return df


def cargar_choferes():
    df = pd.read_excel(RUTA_CHOFERES)
    validar_columnas(df, COLUMNAS_CHOFERES, "choferes.xlsx")
    df = normalizar_choferes(df)
    return df

#%%
##PARTE DE GEOLOCALIZACION

from geolocalizacion import geocodificar_direccion

def agregar_coordenadas_empleados(df):
    lats = []
    lons = []

    for direccion in df["direccion"]:
        lat, lon = geocodificar_direccion(direccion)
        lats.append(lat)
        lons.append(lon)

    df["lat"] = lats
    df["lon"] = lons
    return df


def agregar_coordenadas_choferes(df):
    lats = []
    lons = []

    for direccion in df["direccion"]:
        lat, lon = geocodificar_direccion(direccion)
        lats.append(lat)
        lons.append(lon)

    df["lat"] = lats
    df["lon"] = lons
    return df


#%% 
##MAIN


if __name__ == "__main__":
    empleados = cargar_empleados()
    choferes = cargar_choferes()
    print("Datos cargados correctamente ✅")

    empleados = agregar_coordenadas_empleados(empleados)
    choferes = agregar_coordenadas_choferes(choferes)

    print(empleados[["nombre", "lat", "lon"]])
    print(choferes[["nombre", "lat", "lon"]])
#%%
from asignaciones import asignar_por_horario

asignaciones, choferes_final = asignar_por_horario(
    empleados, choferes
)

print(asignaciones)
