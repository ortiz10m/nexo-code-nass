import time
from typing import Any, Dict, List, Optional
import httpx

# Caché simple en memoria para evitar rate-limits de NASA DEMO_KEY durante la demo
_CACHE: Dict[str, Dict[str, Any]] = {}
TTL_SEGUNDOS = 900  # 15 minutos

# Radiación basal en superficie marciana medida por Curiosity MSL-RAD (~0.67 mSv/día ≈ 0.028 mSv/h)
RADIACION_BASAL_MSV_H = 0.028
LIMITE_EVA_MSV = 1.5  # Límite operacional por caminata EVA


def _get_cache(clave: str) -> Optional[Any]:
    item = _CACHE.get(clave)
    if item and (time.time() - item["ts"]) < TTL_SEGUNDOS:
        return item["data"]
    return None


def _set_cache(clave: str, data: Any) -> None:
    _CACHE[clave] = {"ts": time.time(), "data": data}


async def obtener_clima_espacial(simular_tormenta: bool = False) -> Dict[str, Any]:
    """
    Consulta la API oficial NASA DONKI (Space Weather Database Of Notifications,
    Knowledge, Information) para evaluar el riesgo de radiación en una EVA marciana.
    """
    if simular_tormenta:
        return {
            "fuente": "Simulación Tormenta Solar (Escenario SEP/CME X-Class)",
            "en_vivo": False,
            "estado_solar": "TORMENTA SOLAR",
            "nivel_alerta": "CRÍTICO (S3)",
            "radiacion_msv_hora": 0.85,
            "limite_eva_msv": LIMITE_EVA_MSV,
            "tiempo_max_eva_min": round((LIMITE_EVA_MSV / 0.85) * 60),
            "eventos_recientes": [
                {
                    "tipo": "SEP / CME",
                    "fecha": "Alerta Activa",
                    "resumen": "Evento simulado de partículas energéticas solares (SEP). Se recomienda ruta corta o retorno inmediato al hábitat blindado."
                }
            ]
        }

    cached = _get_cache("donki_weather")
    if cached:
        return cached

    eventos: List[Dict[str, str]] = []
    fuente = "NASA DONKI Live API"
    en_vivo = False
    radiacion_msv_h = RADIACION_BASAL_MSV_H
    estado = "NOMINAL"
    nivel = "BASAL (G0)"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.nasa.gov/DONKI/notifications",
                params={"type": "all", "api_key": "DEMO_KEY"}
            )
            if resp.status_code == 200:
                raw = resp.json()
                en_vivo = True
                if isinstance(raw, list):
                    for ev in raw[:5]:
                        tipo = ev.get("messageType", "DONKI")
                        fecha = (ev.get("messageIssueTime") or "")[:16].replace("T", " ")
                        cuerpo = (ev.get("messageBody") or "").strip()
                        primera_linea = next(
                            (l.strip() for l in cuerpo.splitlines() if l.strip() and not l.startswith("##")),
                            "Notificación de clima espacial NASA DONKI."
                        )
                        eventos.append({
                            "tipo": tipo,
                            "fecha": fecha,
                            "resumen": primera_linea[:180]
                        })
                        if tipo in ("SEP", "FLR", "RBE"):
                            radiacion_msv_h = max(radiacion_msv_h, 0.14)
                            estado = "PRECAUCIÓN"
                            nivel = "ACTIVIDAD SOLAR (S1)"
    except Exception:
        fuente = "NASA MSL-RAD Baseline (Respaldo Offline)"

    if not eventos:
        eventos.append({
            "tipo": "MSL-RAD",
            "fecha": "Referencia Jezero",
            "resumen": "Flujo cósmico galáctico basal (~0.67 mSv/día) medido por el detector RAD en Marte. Sin tormentas SEP activas."
        })

    resultado = {
        "fuente": fuente,
        "en_vivo": en_vivo,
        "estado_solar": estado,
        "nivel_alerta": nivel,
        "radiacion_msv_hora": round(radiacion_msv_h, 3),
        "limite_eva_msv": LIMITE_EVA_MSV,
        "tiempo_max_eva_min": round((LIMITE_EVA_MSV / radiacion_msv_h) * 60),
        "eventos_recientes": eventos
    }
    if en_vivo:
        _set_cache("donki_weather", resultado)
    return resultado


async def obtener_fotos_perseverance(query: str = "Perseverance Jezero", limit: int = 4) -> Dict[str, Any]:
    """
    Obtiene imágenes reales del rover Perseverance desde la API oficial Mars 2020
    Raw Images y la librería multimedia de la NASA (images-api.nasa.gov).
    """
    clave = f"fotos:{query}:{limit}"
    cached = _get_cache(clave)
    if cached:
        return cached

    fotos_raw: List[Dict[str, Any]] = []
    fotos_galeria: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=6.0) as client:
        # 1. API oficial de imágenes crudas de Perseverance (Mars 2020) - filtrando cámaras panorámicas
        try:
            r_raw = await client.get(
                "https://mars.nasa.gov/rss/api/",
                params={
                    "feed": "raw_images",
                    "category": "mars2020",
                    "feedtype": "json",
                    "ver": "1.2",
                    "num": 30,
                    "page": 0
                }
            )
            if r_raw.status_code == 200:
                data = r_raw.json()
                for img in data.get("images", []):
                    cam = (img.get("camera") or {}).get("instrument", "")
                    if not any(k in cam for k in ("MCZ", "NAVCAM", "MAST")):
                        continue
                    url_img = (img.get("image_files") or {}).get("large") or (img.get("image_files") or {}).get("medium")
                    if url_img:
                        fotos_raw.append({
                            "url": url_img,
                            "sol": img.get("sol"),
                            "camara": cam,
                            "fecha": (img.get("date_taken_utc") or "")[:10],
                            "titulo": img.get("title") or f"Perseverance Sol {img.get('sol')}"
                        })
                    if len(fotos_raw) >= limit:
                        break
        except Exception:
            pass

        # 2. NASA Image and Video Library para el punto geológico específico
        try:
            r_img = await client.get(
                "https://images-api.nasa.gov/search",
                params={"q": query, "media_type": "image"}
            )
            if r_img.status_code == 200:
                items = r_img.json().get("collection", {}).get("items", [])
                for it in items[:8]:
                    titulo = (it.get("data") or [{}])[0].get("title", "")
                    href = (it.get("links") or [{}])[0].get("href")
                    t_low = titulo.lower()
                    if href and not any(x in t_low for x in ("map", "chart", "diagram", "traverse", "route", "annotated", "location", "overview")):
                        fotos_galeria.append({"url": href, "titulo": titulo})
                    if len(fotos_galeria) >= 3:
                        break
        except Exception:
            pass

    resultado = {
        "query": query,
        "raw_perseverance": fotos_raw,
        "galeria_nasa": fotos_galeria
    }
    if fotos_raw or fotos_galeria:
        _set_cache(clave, resultado)
    return resultado
