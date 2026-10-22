# backend/viabilidad.py

def evaluar_mision(energia_astronauta: float, energia_requerida: float, pendiente_maxima: float) -> dict:
    """
    Evalúa si el astronauta puede completar la ruta.
    Regla 1: La energía requerida no debe superar la energía del astronauta.
    Regla 2: La pendiente máxima no debe superar los 20 grados (Zona No-Go).
    """
    es_viable = True
    razones = []

    # 1. Validación de Energía
    if energia_requerida > energia_astronauta:
        es_viable = False
        razones.append(f"Energía insuficiente. Necesitas {energia_requerida} pero tienes {energia_astronauta}.")
    
    # 2. Validación de Terreno (Pendientes peligrosas)
    if pendiente_maxima > 20.0:
        es_viable = False
        razones.append(f"Riesgo de caída: Pendiente de {pendiente_maxima}° supera el límite seguro de 20°.")

    # Si no hay razones de fallo, la misión es un éxito
    if es_viable:
        razones.append("Ruta segura. Terreno y energía dentro de los parámetros.")

    return {
        "viable": es_viable,
        "razones": razones
    }


def comparar_mision_historica(energia_requerida: float) -> str:
    """
    Compara el riesgo de la ruta actual con datos históricos de Marte.
    Esto le da el toque único a nuestro proyecto.
    """
    # TODO: Implementar lectura del JSON de misiones históricas para hacer la comparación dinámica.
    # Por ahora, se usan valores simulados basados en la historia real.
    
    if energia_requerida > 80:
        return "Misión de alto riesgo. Consumo similar a Opportunity durante la tormenta de polvo de 2018."
    elif energia_requerida > 50:
        return "Misión de riesgo moderado. Consumo similar a los últimos días de InSight por acumulación de polvo."
    else:
        return "Misión de bajo riesgo. Consumo óptimo similar a los paseos de Curiosity en terrenos planos."