# -*- coding: utf-8 -*-
# Indica que el archivo usa codificación UTF-8 (acentos, ñ, etc.)

"""
Created on Fri Jan 16 23:09:44 2026

@author: Rocio
"""
# Metadata del archivo (no afecta la ejecución)


# ============================================================
# IDEA GENERAL
# ============================================================
# Un empleado B es compatible con A si subirlo no empeora
# significativamente la ruta hacia la planta.
#
# En esta versión:
# - Se asigna cada empleado al chofer más cercano disponible
# - Se respetan plazas máximas
# - Se agrupa por horario de ingreso


############################
#
#ES UN ALGORTIMO GREEDY, buscas una version mas optima con algoritmos de camino minimo
#
##############################
import pandas as pd
# Pandas para manejar DataFrames


# ============================================================
# DIRECCIÓN DE LA PLANTA
# ============================================================
# (todavía no se usa en este código, pero queda definida
#  para futuras mejoras del ruteo)




import numpy as np
from sklearn.cluster import DBSCAN


# =========================
# CLUSTERIZAR EMPLEADOS
# =========================
def clusterizar_empleados(
    df,
    eps_metros=15000, #tomamos de radio 15 km
    min_samples=3
):
    """
    Aplica DBSCAN sobre empleados usando lat/lon.
    
    - eps_metros: distancia máxima entre empleados (en metros)
    - min_samples: mínimo de empleados para formar un cluster
    
    Devuelve el DataFrame con una columna 'cluster'
    """

    # Radio de la Tierra en metros
    RADIO_TIERRA = 6371000

    # Convierte eps de metros a radianes
    eps_radianes = eps_metros / RADIO_TIERRA

    # Extrae lat/lon y las pasa a radianes
    coords = np.radians(
        df[["lat", "lon"]].values
    )

    # Aplica DBSCAN con métrica haversine
    db = DBSCAN(
        eps=eps_radianes,
        min_samples=min_samples,
        metric="haversine"
    )

    # Ejecuta clustering
    clusters = db.fit_predict(coords)

    # Agrega columna de cluster
    df = df.copy()
    df["cluster"] = clusters

    return df


#aca genero grupos de hasta 4, si hay grupos aislados, despues en otra funcion concatenamos



##ahora toca asignar empleados a choferes, aca hay que tener dos cosas en cuenta, para agrupar en un chofer, tenemos como maximo 4 plazas, y ademas, se puede levantar pasajeros en el camino, como los aislados

# distancias.py

from math import radians, sin, cos, sqrt, atan2

def distancia_metros(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en metros entre dos puntos geográficos
    usando la fórmula de Haversine (distancia en línea recta sobre la Tierra).
    """

    # Radio promedio de la Tierra en metros
    R = 6371000

    # Las funciones trigonométricas trabajan en radianes,
    # así que convertimos grados → radianes
    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    # Diferencias de latitud y longitud
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distancia final en metros
    return R * c


# =========================
# ASIGNAR EMPLEADOS A CHOFERES
# =========================
def asignar_empleados_a_choferes(
    empleados,
    choferes,
    columna_horario,
    max_distancia_chofer=60000  # 60 km
):
    """
    Asigna empleados a choferes considerando:
    - disponibilidad del chofer
    - plazas libres
    - cercanía geográfica
    - todos los empleados del viaje tienen el mismo horario
    """

    viajes = []
    empleados_disponibles = empleados.copy()

    # Recorremos chofer por chofer
    for idx_chofer, chofer in choferes.iterrows():

        if not chofer["disponible"] or chofer["plazas"] <= 0:
            continue

        plazas_libres = int(chofer["plazas"])
        pasajeros = []

        # Copia defensiva
        empleados_disponibles = empleados_disponibles.copy()

        # Distancia chofer → empleado
        empleados_disponibles["distancia_chofer"] = empleados_disponibles.apply(
            lambda emp: distancia_metros(
                chofer["lat"], chofer["lon"],
                emp["lat"], emp["lon"]
            ),
            axis=1
        )

        # Ordenamos por cercanía
        empleados_cercanos = empleados_disponibles.sort_values(
            "distancia_chofer"
        )

        horario_viaje = None  # lo define el primer empleado

        for idx_emp, emp in empleados_cercanos.iterrows():

            if plazas_libres == 0:
                break

            if emp["distancia_chofer"] > max_distancia_chofer:
                continue

            # Primer empleado define el horario
            if horario_viaje is None:
                horario_viaje = emp[columna_horario]

            # Si no coincide el horario, se saltea
            if emp[columna_horario] != horario_viaje:
                continue

            pasajeros.append(emp)
            plazas_libres -= 1

        if pasajeros:
            viajes.append({
                "id_chofer": chofer["id_chofer"],
                "chofer": chofer["nombre"],
                "horario": horario_viaje,
                "empleados": pasajeros
            })

            empleados_disponibles = empleados_disponibles.drop(
                [emp.name for emp in pasajeros]
            )

            choferes.loc[idx_chofer, "plazas"] = plazas_libres

            if plazas_libres == 0:
                choferes.loc[idx_chofer, "disponible"] = False

    return viajes

