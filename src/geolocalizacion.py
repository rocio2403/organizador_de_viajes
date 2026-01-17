# -*- coding: utf-8 -*-
from geopy.geocoders import Nominatim
from time import sleep

geolocator = Nominatim(user_agent="organizador_viajes")
def normalizar_direccion(direccion):
    direccion = direccion.strip()

    if "argentina" not in direccion.lower():
        direccion = f"{direccion}, Argentina"

    return direccion

def geocodificar_direccion(direccion):
    try:
        direccion_norm = normalizar_direccion(direccion)
        location = geolocator.geocode(direccion_norm, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error geocodificando {direccion}: {e}")

    return None, None
      