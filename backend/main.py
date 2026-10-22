from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

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
    # TODO: Implementar algoritmo A* real.
    # Retornamos datos simulados para que el frontend pueda avanzar.
    return {
        "estado": "exito",
        "ruta_calculada": [
            {"x": 10, "y": 20},
            {"x": 15, "y": 25},
            {"x": 20, "y": 30}
        ],
        "energia_requerida": 65.5, # Energía simulada que gastará el astronauta
        "pendiente_maxima": 22.0   # Pendiente simulada del terreno
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