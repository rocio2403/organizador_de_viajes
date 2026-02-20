# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:18:53 2026

@author: Rocio
"""
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


def distancia_extra(chofer, emp, planta_lat, planta_lon):
    directa = distancia_metros(
        chofer["lat"], chofer["lon"],
        planta_lat, planta_lon
    )

    con_desvio = (
        distancia_metros(
            chofer["lat"], chofer["lon"],
            emp["lat"], emp["lon"]
        )
        +
        distancia_metros(
            emp["lat"], emp["lon"],
            planta_lat, planta_lon
        )
    )

    return con_desvio - directa


def asignar_empleados_a_choferes(
    empleados,
    choferes,
    columna_horario,
    planta_lat,
    planta_lon,
    capacidad_maxima=4,
    tolerancia_camino=5000  # 5 km extra permitido
):
    
    viajes = []
    empleados_restantes = empleados.copy()

    # Agrupar por horario
    for horario, grupo_horario in empleados_restantes.groupby(columna_horario):

        grupo_horario = grupo_horario.copy()

        # Ordenar por distancia a planta (más lejos primero)
        grupo_horario = grupo_horario.sort_values(
            "distancia_planta",
            ascending=False
        )

        while not grupo_horario.empty:

            # Tomamos el más lejano como semilla
            semilla = grupo_horario.iloc[0]
            grupo = [semilla]

            grupo_horario = grupo_horario.drop(semilla.name)

            # Buscar cercanos a la semilla
            for idx, emp in grupo_horario.iterrows():

                if len(grupo) >= capacidad_maxima:
                    break

                dist = distancia_metros(
                    semilla["lat"], semilla["lon"],
                    emp["lat"], emp["lon"]
                )

                if dist < 8000:  # 8 km entre empleados
                    grupo.append(emp)

            # Quitar del grupo_horario los que ya están en el grupo
            grupo_horario = grupo_horario.drop(
                [emp.name for emp in grupo if emp.name in grupo_horario.index],
                errors="ignore"
            )

            # Buscar mejor chofer para el grupo
            mejor_chofer = None
            mejor_distancia = float("inf")

            for idx_chofer, chofer in choferes.iterrows():

                if not chofer["disponible"] or chofer["plazas"] < len(grupo):
                    continue

                # distancia al centro del grupo
                lat_prom = sum(emp["lat"] for emp in grupo) / len(grupo)
                lon_prom = sum(emp["lon"] for emp in grupo) / len(grupo)

                dist = distancia_metros(
                    chofer["lat"], chofer["lon"],
                    lat_prom, lon_prom
                )

                if dist < mejor_distancia:
                    mejor_distancia = dist
                    mejor_chofer = idx_chofer

            if mejor_chofer is not None:

                chofer = choferes.loc[mejor_chofer]

                viajes.append({
                    "id_chofer": chofer["id_chofer"],
                    "chofer": chofer["nombre"],
                    "horario": horario,
                    "empleados": grupo
                })

                # actualizar plazas
                choferes.loc[mejor_chofer, "plazas"] -= len(grupo)

                if choferes.loc[mejor_chofer, "plazas"] <= 0:
                    choferes.loc[mejor_chofer, "disponible"] = False

    return viajes
