# -*- coding: utf-8 -*-
# Esta línea indica que el archivo usa codificación UTF-8
# Sirve para evitar problemas con acentos, ñ, etc.

from geopy.geocoders import Nominatim
# Importa el geocodificador Nominatim (usa OpenStreetMap)
# Sirve para convertir direcciones en coordenadas (latitud, longitud)

from time import sleep
# Importa la función sleep (pausar ejecución)
# Acá no se usa todavía, pero suele usarse para no saturar la API

# =========================
# CONFIGURACIÓN GEOCODER
# =========================

# Se crea una instancia del geocodificador
# user_agent es obligatorio para que la API sepa quién la usa
geolocator = Nominatim(user_agent="organizador_viajes")


# =========================
# NORMALIZAR DIRECCIÓN
# =========================
def normalizar_direccion(direccion, localidad):
    """
    Limpia y estandariza una dirección antes de geocodificarla.
    """

    # Unimos dirección y localidad con coma (clave)
    out = f"{direccion}, {localidad}"

    out = out.strip()

    # Forzamos país y provincia para evitar ambigüedades
    if "argentina" not in out.lower():
        out = f"{out}, Buenos Aires, Argentina"

    return out



# =========================
# GEOCODIFICAR DIRECCIÓN
# =========================
def geocodificar_direccion(direccion,localidad):
    """
    Convierte una dirección en coordenadas (latitud, longitud).
    Devuelve (None, None) si no se puede geocodificar.
    """

    try:
        # Primero se normaliza la dirección
        direccion_norm = normalizar_direccion(direccion,localidad)

        # Se consulta al geocodificador
        # timeout evita que quede colgado si la API tarda
        location = geolocator.geocode(direccion_norm, timeout=10)

        # Si la API devuelve un resultado válido
        if location:
            # Se devuelven latitud y longitud
            return location.latitude, location.longitude

    except Exception as e:
        # Si ocurre cualquier error, se muestra por consola
        print(f"Error geocodificando {direccion}: {e}")

    # Si no se pudo obtener la ubicación
    return None, None

