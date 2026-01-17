# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 23:09:44 2026

@author: Rocio
"""
import pandas as pd
from distancias import haversine
def asignar_empleados(empleados, choferes):
    asignaciones = []

    # Copia para no modificar el df original
    choferes = choferes.copy()
    choferes["plazas_restantes"] = choferes["plazas"]

    # Recorremos empleados (puede ordenarse luego)
    for _, emp in empleados.iterrows():

        if pd.isna(emp["lat"]) or pd.isna(emp["lon"]):
            continue

        candidatos = []

        for idx, ch in choferes.iterrows():

            if not ch["disponible"]:
                continue

            if ch["plazas_restantes"] <= 0:
                continue

            distancia = haversine(
                emp["lat"], emp["lon"],
                ch["lat"], ch["lon"]
            )

            candidatos.append((distancia, idx))

        if not candidatos:
            continue

        # Elegimos el chofer más cercano
        candidatos.sort(key=lambda x: x[0])
        _, idx_chofer = candidatos[0]

        choferes.loc[idx_chofer, "plazas_restantes"] -= 1

        if choferes.loc[idx_chofer, "plazas_restantes"] == 0:
            choferes.loc[idx_chofer, "disponible"] = False

        asignaciones.append({
            "id_empleado": emp["id_empleado"],
            "nombre_empleado": emp["nombre"],
            "id_chofer": choferes.loc[idx_chofer, "id_chofer"],
            "nombre_chofer": choferes.loc[idx_chofer, "nombre"],
            "distancia_km": round(candidatos[0][0], 2),
            "horario": emp["horario_ingreso"]
        })

    return pd.DataFrame(asignaciones), choferes

def asignar_por_horario(empleados, choferes):
    todas_las_asignaciones = []
    choferes_actuales = choferes.copy()

    horarios = empleados["horario_ingreso"].dropna().unique()

    for horario in horarios:
        empleados_h = empleados[
            empleados["horario_ingreso"] == horario
        ]

        asignaciones_h, choferes_actuales = asignar_empleados(
            empleados_h,
            choferes_actuales
        )

        todas_las_asignaciones.append(asignaciones_h)

    return pd.concat(todas_las_asignaciones, ignore_index=True), choferes_actuales
