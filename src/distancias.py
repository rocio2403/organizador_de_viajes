# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:09:17 2026

@author: Rocio
"""
from geopy.distance import geodesic

PLANTA_LAT = -34.589
PLANTA_LON = -58.87275

def distancia_a_planta(lat, lon, planta_lat, planta_lon):
    """
    Devuelve la distancia en metros entre un punto y la planta.
    """
    return geodesic(
        (lat, lon),
        (planta_lat, planta_lon)
    ).meters



def agregar_distancia_planta(df, planta_lat, planta_lon):
    """
    Agrega una columna con la distancia a la planta (en metros).
    """
    df["distancia_planta"] = df.apply(
        lambda fila: distancia_a_planta(
            fila["lat"],
            fila["lon"],
            planta_lat,
            planta_lon
        ),
        axis=1
    )
    return df
