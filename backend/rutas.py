import heapq
import math
from typing import Dict, List, Any

# Radio ecuatorial real de Marte en kilómetros (NASA Planetary Fact Sheet)
RADIO_MARTE_KM = 3396.2
CAPACIDAD_PLSS_KCAL = 3600.0
VELOCIDAD_BASE_KMH = 3.2


def distancia_haversine_marte(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distancia geodésica sobre la esfera marciana en km."""
    rad = math.pi / 180.0
    dlat = (lat2 - lat1) * rad
    dlon = (lon2 - lon1) * rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1 * rad) * math.cos(lat2 * rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RADIO_MARTE_KM * c


def costo_metabolico_tramo(
    nodo_a: Dict[str, Any],
    nodo_b: Dict[str, Any],
    carga_kg: float = 0.0,
    con_rover: bool = False
) -> Dict[str, float]:
    """
    Estima gasto calórico (kcal) y consumo PLSS (%) considerando gravedad 3.72 m/s²,
    rigidez del traje presurizado xEMU (4.3 psi), carga científica y asistencia de rover.
    """
    dist_km = distancia_haversine_marte(nodo_a["lat"], nodo_a["lng"], nodo_b["lat"], nodo_b["lng"])
    pendiente_tramo = max(nodo_a["pendiente"], nodo_b["pendiente"])
    ascenso_m = max(0.0, nodo_b.get("elevacion_m", 0) - nodo_a.get("elevacion_m", 0))

    # Carga científica en mochila incrementa esfuerzo; rover de apoyo absorbe la carga y reduce fatiga
    factor_carga = 1.0 if con_rover else (1.0 + (max(0.0, carga_kg) / 85.0))
    factor_rover = 0.55 if con_rover else 1.0

    # Gasto base en Marte con traje xEMU: ~90 kcal/km en terreno plano + penalización exponencial por pendiente
    factor_pendiente = 1.0 + ((pendiente_tramo / 10.0) ** 1.7) + (ascenso_m / 120.0)
    kcal = dist_km * 90.0 * factor_pendiente * factor_carga * factor_rover
    energia_pct = (kcal / CAPACIDAD_PLSS_KCAL) * 100.0

    return {
        "distancia_km": dist_km,
        "kcal": kcal,
        "energia_pct": energia_pct,
        "pendiente_tramo": pendiente_tramo
    }


def calcular_ruta_a_estrella(
    inicio_id: int,
    destino_id: int,
    puntos: List[Dict[str, Any]],
    modo_seguro: bool = True,
    ida_y_vuelta: bool = False,
    carga_kg: float = 0.0,
    con_rover: bool = False,
    radiacion_msv_hora: float = 0.028
) -> Dict[str, Any]:
    """Ejecuta A* sobre el grafo del Cráter Jezero minimizando desgaste metabólico y riesgos."""
    mapa_nodos = {p["id"]: p for p in puntos}
    if inicio_id not in mapa_nodos or destino_id not in mapa_nodos:
        raise ValueError("IDs de inicio o destino fuera del catálogo de Jezero.")

    if inicio_id == destino_id:
        nodo = mapa_nodos[inicio_id]
        return {
            "estado": "exito",
            "ruta_calculada": [{**nodo, "kcal_acumulado": 0.0, "distancia_acumulada_km": 0.0}],
            "distancia_km": 0.0,
            "tiempo_estimado_min": 0,
            "energia_requerida": 0.0,
            "kcal_totales": 0.0,
            "litros_o2": 0.0,
            "radiacion_msv": 0.0,
            "puntaje_cientifico": 25,
            "pendiente_maxima": nodo["pendiente"],
            "cruza_blackout": nodo.get("sin_comunicacion", False)
        }

    destino = mapa_nodos[destino_id]
    cola = [(0.0, inicio_id)]
    vino_de: Dict[int, int] = {}
    costo_g: Dict[int, float] = {p["id"]: float("inf") for p in puntos}
    costo_g[inicio_id] = 0.0

    while cola:
        _, actual_id = heapq.heappop(cola)
        if actual_id == destino_id:
            break

        nodo_actual = mapa_nodos[actual_id]
        for vecino_id in nodo_actual.get("vecinos", []):
            if vecino_id not in mapa_nodos:
                continue
            nodo_vecino = mapa_nodos[vecino_id]
            tramo = costo_metabolico_tramo(nodo_actual, nodo_vecino, carga_kg=carga_kg, con_rover=con_rover)

            penalizacion_seguridad = 0.0
            # Si modo_seguro está activo, A* evita usar nodos intermedios con pendiente >20° o sin radio
            if modo_seguro and vecino_id != destino_id:
                if nodo_vecino["pendiente"] > 20.0 or nodo_vecino.get("sin_comunicacion", False):
                    penalizacion_seguridad = 50000.0

            nuevo_g = costo_g[actual_id] + tramo["kcal"] + penalizacion_seguridad
            if nuevo_g < costo_g[vecino_id]:
                vino_de[vecino_id] = actual_id
                costo_g[vecino_id] = nuevo_g
                heuristica = distancia_haversine_marte(
                    nodo_vecino["lat"], nodo_vecino["lng"], destino["lat"], destino["lng"]
                ) * 90.0
                heapq.heappush(cola, (nuevo_g + heuristica, vecino_id))

    # Reconstruir camino
    camino_ids = [destino_id]
    curr = destino_id
    while curr in vino_de:
        curr = vino_de[curr]
        camino_ids.append(curr)
    camino_ids.reverse()

    if camino_ids[0] != inicio_id:
        camino_ids = [inicio_id, destino_id]

    if ida_y_vuelta and len(camino_ids) > 1:
        camino_ids = camino_ids + camino_ids[-2::-1]

    # Calcular telemetría acumulada paso a paso
    ruta_detallada = []
    dist_total = 0.0
    kcal_total = 0.0
    pendiente_max = 0.0
    hay_blackout = False

    nodos_unicos = set()
    puntaje_ciencia = 0
    for idx, nid in enumerate(camino_ids):
        nodo = mapa_nodos[nid]
        if idx > 0:
            prev_nodo = mapa_nodos[camino_ids[idx - 1]]
            tramo = costo_metabolico_tramo(prev_nodo, nodo, carga_kg=carga_kg, con_rover=con_rover)
            dist_total += tramo["distancia_km"]
            kcal_total += tramo["kcal"]

        if nid not in nodos_unicos:
            nodos_unicos.add(nid)
            # Nodos de alto valor científico (biofirmas, cañón, muestras) aportan más retorno
            puntaje_ciencia += 35 if nid in (7, 8, 5, 2) else 20

        pendiente_max = max(pendiente_max, nodo["pendiente"])
        if nodo.get("sin_comunicacion", False):
            hay_blackout = True

        ruta_detallada.append({
            "id": nodo["id"],
            "nombre": nodo["nombre"],
            "lat": nodo["lat"],
            "lng": nodo["lng"],
            "elevacion_m": nodo.get("elevacion_m", -2550),
            "pendiente": nodo["pendiente"],
            "sin_comunicacion": nodo.get("sin_comunicacion", False),
            "distancia_acumulada_km": round(dist_total, 2),
            "kcal_acumulado": round(kcal_total, 1)
        })

    energia_pct = round((kcal_total / CAPACIDAD_PLSS_KCAL) * 100.0, 1)
    velocidad_efectiva = max(1.4, VELOCIDAD_BASE_KMH - (pendiente_max * 0.06) + (0.4 if con_rover else 0.0))
    tiempo_min = round((dist_total / velocidad_efectiva) * 60)
    litros_o2 = round(kcal_total * 0.21, 1)  # Equivalente respiratorio ~0.21 L O2 por kcal
    radiacion_msv = round((tiempo_min / 60.0) * radiacion_msv_hora, 3)

    return {
        "estado": "exito",
        "ruta_calculada": ruta_detallada,
        "distancia_km": round(dist_total, 2),
        "tiempo_estimado_min": tiempo_min,
        "energia_requerida": energia_pct,
        "kcal_totales": round(kcal_total, 1),
        "litros_o2": litros_o2,
        "radiacion_msv": radiacion_msv,
        "puntaje_cientifico": min(100, puntaje_ciencia),
        "pendiente_maxima": round(pendiente_max, 1),
        "cruza_blackout": hay_blackout
    }
