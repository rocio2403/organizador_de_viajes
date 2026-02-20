# -*- coding: utf-8 -*-
# Indica que el archivo usa codificación UTF-8 (acentos, ñ, etc.)


# -*- coding: utf-8 -*-
# Indica que el archivo usa codificación UTF-8 (acentos, ñ, etc.)

from src.carga_datos import *
from src.geolocalizacion import *
from src.asignaciones import *
from src.distancias import agregar_distancia_planta
from src.resultados import *

import pandas as pd




def main():

    direccion, localidad = obtener_datos_planta()
    planta_lat, planta_lon = geocodificar_direccion(direccion, localidad)
    
    empleados = cargar_empleados()
    choferes = cargar_choferes()
    print("Datos cargados correctamente ✅")

    empleados = agregar_coordenadas(empleados)
    choferes = agregar_coordenadas(choferes)

    empleados = agregar_distancia_planta(
        empleados,
        planta_lat,
        planta_lon
    )
    
    choferes = agregar_distancia_planta(
        choferes,
        planta_lat,
        planta_lon
    )

    empleados = clusterizar_empleados(
        empleados
    )
        
    viajes_ingreso = asignar_empleados_a_choferes(
        empleados,
        choferes.copy(),
        columna_horario="horario_ingreso"
    )
    
    viajes_egreso = asignar_empleados_a_choferes(
        empleados,
        choferes.copy(),
        columna_horario="horario_salida"
    )
    
    # Convertimos los viajes a DataFrame
    df_ingreso = viajes_a_dataframe(
        viajes_ingreso,
        "ingreso"
    ).sort_values("horario")

    df_egreso = viajes_a_dataframe(
        viajes_egreso,
        "egreso"
    ).sort_values("horario")
    
    # Unimos ingreso y egreso en un solo DataFrame
    df_final = pd.concat(
        [df_ingreso, df_egreso],
        ignore_index=True
    )

    
    # Exportamos a Excel (una sola hoja)
    ruta_salida = "viajes_organizados.xlsx"

    df_final.to_excel(
        ruta_salida,
        index=False
    )

    print(f"Archivo Excel generado correctamente: {ruta_salida} 📊")


if __name__ == "__main__":
    main()
