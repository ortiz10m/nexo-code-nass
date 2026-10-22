from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Nexo Code - Mars Marswalk API")

# Configuración de CORS: Permite que el frontend (React/Leaflet) haga peticiones sin bloqueos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---
# Definen la estructura exacta del JSON que el frontend debe enviar.

class PuntoMarte(BaseModel):
    id: int
    nombre: str
    x: float
    y: float
    pendiente: float

class RutaRequest(BaseModel):
    inicio_id: int
    destino_id: int
    energia_astronauta: float

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    """Verifica que el servidor esté en línea."""
    return {"status": "ok", "mensaje": "API de Nexo Code operativa"}

@app.get("/puntos", response_model=List[PuntoMarte])
def get_puntos():
    """Retorna los puntos de interés. Temporalmente usa datos quemados (mock)."""
    # TODO: Reemplazar por lectura del archivo JSON de Maylyn y Samuel.
    return [
        {"id": 1, "nombre": "Cráter Jezero", "x": 10, "y": 20, "pendiente": 5.0},
        {"id": 2, "nombre": "Delta Oeste", "x": 15, "y": 25, "pendiente": 22.5},
        {"id": 3, "nombre": "Zona de Aterrizaje", "x": 5, "y": 5, "pendiente": 1.0}
    ]

@app.post("/calcular_ruta")
def calcular_ruta(req: RutaRequest):
    """Calcula la ruta entre dos puntos y estima el costo energético."""
    # TODO (Daniel): Implementar algoritmo A* o Dijkstra.
    
    distancia_km = 12.5
    energia_requerida = distancia_km * 1.5

    return {
        "estado": "exito",
        "ruta_calculada": [
            {"x": 10, "y": 20},
            {"x": 15, "y": 25},
            {"x": 20, "y": 30}
        ],
        "distancia_km": distancia_km,
        "energia_requerida": energia_requerida
    }

@app.post("/evaluar_viabilidad")
def evaluar_viabilidad(req: RutaRequest):
    """Determina si el astronauta puede completar la ruta y compara el riesgo histórico."""
    # TODO (David): Comparar energía requerida vs disponible y evaluar misiones históricas.
    
    es_viable = req.energia_astronauta > 50
    
    return {
        "viable": es_viable,
        "razon": "Energía suficiente" if es_viable else "Energía insuficiente para el trayecto",
        "comparacion_historica": "Riesgo similar a la misión InSight por acumulación de polvo."
    }
