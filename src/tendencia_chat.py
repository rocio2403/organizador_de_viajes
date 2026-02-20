# -*- coding: utf-8 -*-
import re
from collections import defaultdict

def parsear_chat(ruta):
    datos = defaultdict(lambda: {
        "horarios": [],
        "personas": []
    })

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip().lower()

            if not linea:
                continue

            # 1) HORARIO (solo dos dígitos, antes de "con")
            m_hora = re.search(r"\b(\d{2})\b(?=.*\bcon\b)", linea)
            if not m_hora:
                continue

            hora = m_hora.group(1)

            # 2) CHOFER
            m_chofer = re.search(r"\bcon\s+([a-záéíóúñ]+)", linea)
            if not m_chofer:
                continue

            chofer = m_chofer.group(1).capitalize()
            datos[chofer]["horarios"].append(hora)

           
            m_ingresa = re.search(r"\bingresa\s+(.+)", linea)
            if m_ingresa:
                personas = m_ingresa.group(1).split()
                datos[chofer]["personas"].extend(personas)

    return datos


def estadisticas(datos):
    return {
        "total_choferes": len(datos),
        "choferes_sin_personas": [
            c for c, d in datos.items() if not d["personas"]
        ],
        "total_personas": sum(len(d["personas"]) for d in datos.values()),
        "horarios_por_chofer": {
            c: d["horarios"] for c, d in datos.items()
        }
    }


if __name__ == "__main__":
    datos = parsear_chat("chat_transporte.txt")
    stats = estadisticas(datos)

    print("=== RESUMEN ===")
    print(f"Total choferes: {stats['total_choferes']}")
    print(f"Total personas: {stats['total_personas']}")

    print("\n=== DETALLE ===")
    for chofer, info in datos.items():
        print(f"\n{chofer}")
        print(f"  Horarios: {info['horarios']}")
        if info["personas"]:
            print(f"  Personas: {info['personas']}")
        else:
            print("  Personas: (ninguna)")