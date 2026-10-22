# Nexo Code - NASA 🚀

**Reto:** Guía de supervivencia interplanetaria: Mapa marciano (NASA Space Apps Challenge 2026)
**Equipo:** Maylyn Juliana Rojas, Samuel Ramirez, Daniel Zea Tamayo, David Santiago Ortiz Rincon, Diego Vargas

## 🎯 El Problema
La NASA ha mapeado Marte, pero los futuros astronautas necesitan más que un mapa topográfico. Necesitan una herramienta que les ayude a planificar una caminata marciana (Marswalk) segura y científicamente valiosa, sin quedarse sin energía ni entrar en zonas de peligro.

## 💡 Nuestra Solución
Una vista integrada y por capas de la superficie marciana que traduce los datos del terreno en **viabilidad humana**.
- **Motor de Costo Metabólico:** Calcula el gasto energético basado en la pendiente y la distancia (inspirado en el modelo CSRM de la NASA).
- **Zonas de Riesgo (No-Go):** Marca pendientes peligrosas (>20°) y zonas sin comunicación.
- **Autopsia Histórica:** Compara la ruta del usuario con misiones históricas reales de la NASA en Marte para evaluar la viabilidad y aprender de los fracasos del pasado.

## 🛠️ Tecnologías
- **Backend:** Python + FastAPI
- **Lógica:** Búsqueda de rutas A*, simulación de costo metabólico
- **Datos:** WMTS de Mars Trek, datos históricos de la NASA (JSON)
- **Frontend:** React + Leaflet (En progreso)
