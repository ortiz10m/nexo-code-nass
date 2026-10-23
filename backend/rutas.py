import math
import heapq

def costo_metabolico(distancia_m, pendiente_pct, peso_kg=70.0):
    """Calcula la energía requerida en kcal."""
    distancia_km = distancia_m / 1000.0
    kcal_plano = 0.5 * peso_kg * distancia_km
    # A mayor pendiente positiva, más energía se gasta
    factor_pendiente = 1 + (pendiente_pct / 100.0) * 3.5 if pendiente_pct > 0 else 1
    return kcal_plano * max(factor_pendiente, 0.5)

def calcular_ruta_astar(puntos, inicio_id, destino_id):
    """
    A* adaptado a la estructura de David.
    Como no hay un grafo de conexiones explícito, asumimos que 
    todos los puntos están conectados entre sí (grafo completo).
    """
    # Diccionario para buscar los datos de cada punto rápido
    nodos = {p["id"]: p for p in puntos}
    
    if inicio_id not in nodos or destino_id not in nodos:
        return None, 0.0, 0.0

    # Cola de prioridad: (costo_total_estimado, id_actual, energia_acumulada, pendiente_maxima)
    abiertos = [(0.0, inicio_id, 0.0, 0.0)]
    visitados = set()

    while abiertos:
        costo_estimado, actual_id, energia_acum, pendiente_max = heapq.heappop(abiertos)

        if actual_id in visitados:
            continue
        visitados.add(actual_id)

        # Si llegamos al destino, retornamos los resultados
        if actual_id == destino_id:
            # Formateamos la ruta como la espera el frontend (x, y)
            ruta_coords = [{"x": nodos[i]["x"], "y": nodos[i]["y"]} for i in visitados]
            return ruta_coords, energia_acum, pendiente_max

        actual = nodos[actual_id]

        # Explorar vecinos (en este caso, todos los demás puntos)
        for vecino_id, vecino in nodos.items():
            if vecino_id in visitados:
                continue

            # Distancia Euclidiana (como usan coordenadas x,y)
            dist = math.sqrt((vecino["x"] - actual["x"])**2 + (vecino["y"] - actual["y"])**2)
            
            # Calcular energía y pendiente
            energia_arco = costo_metabolico(dist, vecino["pendiente"])
            nueva_energia = energia_acum + energia_arco
            nueva_pendiente_max = max(pendiente_max, vecino["pendiente"])

            # Heurística: distancia en línea recta al destino
            dist_destino = math.sqrt((nodos[destino_id]["x"] - vecino["x"])**2 + (nodos[destino_id]["y"] - vecino["y"])**2)
            nuevo_costo_estimado = nueva_energia + dist_destino

            heapq.heappush(abiertos, (nuevo_costo_estimado, vecino_id, nueva_energia, nueva_pendiente_max))

    # Si no encuentra ruta
    return None, 0.0, 0.0