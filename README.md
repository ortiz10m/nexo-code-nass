# Mars Maps — Nexo Code 🚀

**NASA Space Apps Challenge 2026 (Neiva, Colombia)**  
**Challenge:** *Marswalk Surface Exploration Mapping*  
**Team Nexo Code:** David Santiago Ortiz Rincon, Samuel Esteban Ramirez, Daniel Zea Tamayo, Mailyn Yuliana Rojas, Diego Fernando Vargas Ramirez

## 🎯 Overview
**Mars Maps** translates multi-layer NASA planetary data into human survivability, metabolic routing, and point-of-view surface intelligence for the first astronauts exploring **Jezero Crater**.

## ✨ Key Features
- **Multi-Layer Tactical Map (4+ NASA Layers):**
  - **Optical HD:** Caltech CTX (`5 m/px`) + Viking Color Mosaic (`232 m/px`) via NASA Mars Trek WMTS.
  - **Topographic:** MGS MOLA Altimetry (`463 m/px`) + 40% fusion overlay + SVG elevation profile.
  - **Thermal & Hazards:** Surface thermal estimation, `>20°` xEMU slope limits, and UHF radio blackout zones.
  - **Live Space Weather:** Real-time **NASA DONKI API** solar notifications + MSL-RAD radiation baseline (`0.028 mSv/h`) and Solar Storm Simulator (`0.85 mSv/h`).
- **A\* Geodesic & CSRM Metabolic Engine:** Calculates optimal routes across 12 real Jezero Crater waypoints, accounting for payload weight (`0 kg`, `+12 kg`, `+25 kg`), **Rover Companion** mode (`-45%` metabolic load), mandatory `30%` PLSS O₂ reserve, and `1.5 mSv` EVA radiation limit.
- **Mars Street View & Post-EVA Report:** Ground-level imagery from **NASA Mars 2020 Perseverance Raw Images API (Mastcam-Z)** and **NASA Image Library**, plus a live walking HUD and Post-EVA mission report.
- **3D Mars Mission Globe & 7-Slide Pitch Deck:** Interactive Three.js Mars globe with historical NASA anomaly pins (*Spirit*, *Opportunity*, *InSight*, *Curiosity*, *Perseverance*) and an auditorium-ready 7-slide deck at `/slides`.

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, HTTPX (async NASA API proxy with 15-min cache & offline fallback)
- **Frontend:** HTML5, CSS3, JavaScript, Leaflet (EPSG:4326 Mars Trek WMTS), Three.js

## ▶️ Quick Start
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
Open in your browser:
- **App:** `http://127.0.0.1:8000/app`
- **7-Slide Deck:** `http://127.0.0.1:8000/slides`
- **API Docs:** `http://127.0.0.1:8000/docs`

## 📚 Official NASA Data Sources
- **NASA JPL Mars Trek WMTS:** `CTX_beta01_uncontrolled_5m_Caltech`, `Mars_Viking_MDIM21_ClrMosaic_global_232m`, `Mars_MGS_MOLA_ClrShade_merge_global_463m`
- **NASA DONKI API:** `https://api.nasa.gov/DONKI/notifications` + Curiosity MSL-RAD baseline
- **NASA Mars 2020 Perseverance Raw Images & Image Library:** `https://mars.nasa.gov/rss/api` & `https://images-api.nasa.gov`

## 🤖 AI Disclosure
AI coding assistants were used to accelerate FastAPI/Leaflet integration, UI/UX layout, and presentation formatting. All NASA API integrations, routing logic, and safety thresholds were verified locally.
