from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from rutas import calcular_ruta_astar

# Importamos la lógica de viabilidad
from viabilidad import evaluar_mision, comparar_mision_historica

app = FastAPI(title="Nexo Code - Mars Marswalk API")

# Configuración de CORS: Permite que el frontend (React) se conecte.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS ---
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

# NUEVO MODELO: Para conectar /calcular_ruta con /evaluar_viabilidad
class EvaluacionRequest(BaseModel):
    energia_astronauta: float
    energia_requerida: float
    pendiente_maxima: float

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "ok", "mensaje": "API de Nexo Code operativa"}

@app.get("/puntos", response_model=List[PuntoMarte])
def get_puntos():
    """Retorna los puntos de interés."""
    # TODO: Conectar con el archivo JSON real.
    return [
        {"id": 1, "nombre": "Cráter Jezero", "x": 10, "y": 20, "pendiente": 5.0},
        {"id": 2, "nombre": "Delta Oeste", "x": 15, "y": 25, "pendiente": 22.5},
        {"id": 3, "nombre": "Zona de Aterrizaje", "x": 5, "y": 5, "pendiente": 1.0}
    ]

@app.post("/calcular_ruta")
def calcular_ruta(req: RutaRequest):
    """Calcula la ruta y devuelve la energía requerida."""
    
    # 1. Obtenemos los puntos (usando la misma función de arriba)
    puntos = get_puntos()
    
    # 2. Llamamos a tu algoritmo A*
    ruta, energia_req, pend_max = calcular_ruta_astar(
        puntos=puntos, 
        inicio_id=req.inicio_id, 
        destino_id=req.destino_id
    )
    
    # 3. Validamos si se encontró ruta
    if ruta is None:
        return {"error": "No se pudo calcular la ruta"}

    # 4. Devolvemos el JSON con los datos reales
    return {
        "estado": "exito",
        "ruta_calculada": ruta,
        "energia_requerida": energia_req,
        "pendiente_maxima": pend_max
    }

@app.post("/evaluar_viabilidad")
def evaluar_viabilidad(req: EvaluacionRequest):
    """
    Recibe los datos del cálculo de ruta y evalúa si es viable.
    Aquí es donde TU lógica (viabilidad.py) se conecta con la API.
    """
    # 1. Llamamos a tu función de viabilidad
    resultado_viabilidad = evaluar_mision(
        energia_astronauta=req.energia_astronauta,
        energia_requerida=req.energia_requerida,
        pendiente_maxima=req.pendiente_maxima
    )

    # 2. Llamamos a tu función de comparación histórica
    comparacion = comparar_mision_historica(req.energia_requerida)

    # 3. Devolvemos todo empaquetado
    return {
        "viable": resultado_viabilidad["viable"],
        "razones": resultado_viabilidad["razones"],
        "comparacion_historica": comparacion
    }