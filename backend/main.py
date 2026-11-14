import json
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from rutas import calcular_ruta_a_estrella
from viabilidad import evaluar_mision, comparar_mision_historica
from nasa_apis import obtener_clima_espacial, obtener_fotos_perseverance

app = FastAPI(
    title="Nexo Code - Marswalk Tactical Survival API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def cargar_json(nombre_archivo: str):
    ruta = BASE_DIR / "datos" / nombre_archivo
    if not ruta.exists():
        raise HTTPException(status_code=500, detail=f"Archivo no encontrado: {nombre_archivo}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


class PuntoMarte(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    elevacion_m: float
    pendiente: float
    sin_comunicacion: bool
    query_nasa: str
    valor_cientifico: str
    vecinos: List[int]


class RutaRequest(BaseModel):
    inicio_id: int
    destino_id: int
    energia_astronauta: float = 100.0
    modo_seguro: Optional[bool] = True
    ida_y_vuelta: Optional[bool] = False
    carga_kg: Optional[float] = 0.0
    con_rover: Optional[bool] = False
    radiacion_msv_hora: Optional[float] = 0.028


class EvaluacionRequest(BaseModel):
    energia_astronauta: float
    energia_requerida: float
    pendiente_maxima: float
    cruza_blackout: Optional[bool] = False
    radiacion_msv: Optional[float] = 0.0


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "proyecto": "Nexo Code - Neiva, Colombia",
        "motor": "A* Geodésico Marciano + CSRM Viabilidad Humana"
    }


@app.get("/puntos", response_model=List[PuntoMarte])
def get_puntos():
    return cargar_json("puntos_interes.json")


@app.get("/misiones")
def get_misiones():
    return cargar_json("misiones_historicas.json")


@app.get("/jezero-hi-res.jpg")
def servir_jezero_hd():
    return FileResponse("frontend/jezero-hi-res.jpg")

@app.get("/panos/{nombre}")
def servir_pano_local(nombre: str):
    return FileResponse(BASE_DIR.parent / "frontend" / "panos" / Path(nombre).name)

@app.get("/app")
def serve_frontend():
    ruta_html = BASE_DIR.parent / "frontend" / "index.html"
    if not ruta_html.exists():
        raise HTTPException(status_code=404, detail="Frontend no encontrado")
    return FileResponse(ruta_html)


@app.get("/slides")
def serve_slides():
    ruta_slides = BASE_DIR.parent / "frontend" / "slides.html"
    if not ruta_slides.exists():
        raise HTTPException(status_code=404, detail="Presentación no encontrada")
    return FileResponse(ruta_slides)


@app.get("/clima_espacial")
async def get_clima_espacial(simular_tormenta: bool = False):
    return await obtener_clima_espacial(simular_tormenta=simular_tormenta)


@app.get("/fotos_perseverance")
async def get_fotos_perseverance(query: str = "Perseverance Jezero", limit: int = 4):
    return await obtener_fotos_perseverance(query=query, limit=limit)


@app.post("/calcular_ruta")
def calcular_ruta(req: RutaRequest):
    puntos = cargar_json("puntos_interes.json")
    try:
        return calcular_ruta_a_estrella(
            inicio_id=req.inicio_id,
            destino_id=req.destino_id,
            puntos=puntos,
            modo_seguro=bool(req.modo_seguro),
            ida_y_vuelta=bool(req.ida_y_vuelta),
            carga_kg=float(req.carga_kg or 0.0),
            con_rover=bool(req.con_rover),
            radiacion_msv_hora=float(req.radiacion_msv_hora or 0.028)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/evaluar_viabilidad")
def evaluar_viabilidad(req: EvaluacionRequest):
    misiones = cargar_json("misiones_historicas.json")
    resultado = evaluar_mision(
        energia_astronauta=req.energia_astronauta,
        energia_requerida=req.energia_requerida,
        pendiente_maxima=req.pendiente_maxima,
        cruza_blackout=bool(req.cruza_blackout),
        radiacion_msv=float(req.radiacion_msv or 0.0)
    )
    autopsia = comparar_mision_historica(
        energia_requerida=req.energia_requerida,
        pendiente_maxima=req.pendiente_maxima,
        cruza_blackout=bool(req.cruza_blackout),
        energia_astronauta=req.energia_astronauta,
        catalogo_misiones=misiones
    )

    return {
        "viable": resultado["viable"],
        "nivel_riesgo": resultado["nivel_riesgo"],
        "energia_restante": resultado["energia_restante"],
        "razones": resultado["razones"],
        "comparacion_historica": autopsia["resumen"],
        "detalle_historico": autopsia
    }
