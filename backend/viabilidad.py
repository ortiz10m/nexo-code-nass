from typing import Dict, List, Any

LIMITE_PENDIENTE_SEGURA = 20.0
RESERVA_MINIMA_PLSS = 30.0
LIMITE_RADIACION_EVA_MSV = 1.5


def evaluar_mision(
    energia_astronauta: float,
    energia_requerida: float,
    pendiente_maxima: float,
    cruza_blackout: bool = False,
    radiacion_msv: float = 0.0
) -> Dict[str, Any]:
    """
    Evalúa supervivencia humana bajo parámetros CSRM y soporte vital PLSS de la NASA.
    """
    es_viable = True
    nivel_riesgo = "NOMINAL"
    razones: List[str] = []
    energia_restante = round(energia_astronauta - energia_requerida, 1)

    # Regla 1: Zonas sin comunicación (UHF Blackout)
    if cruza_blackout:
        es_viable = False
        nivel_riesgo = "NO-GO CRÍTICO"
        razones.append(
            "Pérdida de enlace UHF: La ruta ingresa en un cráter con sombra de radio sin línea de vista al hábitat."
        )

    # Regla 2: Estabilidad biomecánica del traje xEMU (> 20°)
    if pendiente_maxima > LIMITE_PENDIENTE_SEGURA:
        es_viable = False
        nivel_riesgo = "NO-GO CRÍTICO"
        razones.append(
            f"Riesgo de caída en traje xEMU: Pendiente de {pendiente_maxima}° supera el límite humano seguro de 20°."
        )

    # Regla 3: Agotamiento energético y reserva reglamentaria del 30% PLSS
    if energia_restante < 0:
        es_viable = False
        nivel_riesgo = "NO-GO MORTAL"
        razones.append(
            f"Agotamiento total PLSS: El trayecto exige {energia_requerida}% de capacidad y dispones de {energia_astronauta}%."
        )
    elif energia_restante < RESERVA_MINIMA_PLSS:
        es_viable = False
        nivel_riesgo = "NO-GO RESERVA"
        razones.append(
            f"Violación de protocolo EVA: Quedarías con {energia_restante}% de soporte vital (mínimo obligatorio NASA: 30%)."
        )
    elif energia_restante < 48.0 and es_viable:
        nivel_riesgo = "PRECAUCIÓN"
        razones.append(
            f"Desgaste moderado CSRM: Reserva final de {energia_restante}%. Monitorear refrigeración líquida y fatiga."
        )

    # Regla 4: Exposición a radiación solar/cósmica (NASA DONKI / MSL-RAD)
    if radiacion_msv > LIMITE_RADIACION_EVA_MSV:
        es_viable = False
        nivel_riesgo = "NO-GO RADIACIÓN"
        razones.append(
            f"Dosis de radiación ({radiacion_msv} mSv) supera el límite operacional EVA ({LIMITE_RADIACION_EVA_MSV} mSv) por tormenta solar activa."
        )
    elif radiacion_msv > 0.5 and es_viable:
        nivel_riesgo = "PRECAUCIÓN"
        razones.append(
            f"Exposición solar elevada ({radiacion_msv} mSv). Se recomienda acortar tiempo en superficie."
        )

    if es_viable and nivel_riesgo == "NOMINAL":
        razones.append(
            f"Ruta certificada para Marswalk. Pendiente máxima ({pendiente_maxima}°) y reserva PLSS ({energia_restante}%) en rango óptimo."
        )

    return {
        "viable": es_viable,
        "nivel_riesgo": nivel_riesgo,
        "energia_restante": max(0.0, energia_restante),
        "razones": razones
    }


def comparar_mision_historica(
    energia_requerida: float,
    pendiente_maxima: float,
    cruza_blackout: bool,
    energia_astronauta: float,
    catalogo_misiones: List[Dict[str, Any]]
) -> Dict[str, str]:
    """Cruza los riesgos detectados con el archivo histórico de anomalías en Marte."""
    por_codigo = {m["codigo"]: m for m in catalogo_misiones}
    energia_restante = energia_astronauta - energia_requerida

    if cruza_blackout and "blackout" in por_codigo:
        m = por_codigo["blackout"]
    elif pendiente_maxima > 20.0 and "pendiente" in por_codigo:
        m = por_codigo["pendiente"]
    elif energia_restante < 30.0 and "energia_critica" in por_codigo:
        m = por_codigo["energia_critica"]
    elif energia_requerida > 45.0 and "moderado" in por_codigo:
        m = por_codigo["moderado"]
    else:
        m = por_codigo.get("optimo", {
            "mision": "Perseverance Mars 2020",
            "sol_evento": "Operación Nominal",
            "leccion": "Parámetros dentro de márgenes comprobados en el Cráter Jezero."
        })

    return {
        "mision": m["mision"],
        "sol_evento": m["sol_evento"],
        "leccion": m["leccion"],
        "resumen": f"{m['mision']} ({m['sol_evento']}): {m['leccion']}"
    }
