# Architecture

## 1. System Layers

### Data Ingestion Layer
*   **Sources:** Open-Meteo (Live Coarse weather), NASA POWER (Historical training), CHIRPS/AWS (Ground-truth), SRTM (Elevation data).
*   **Function:** Scheduled Python scripts that pull latest weather data for the Tamil Nadu bounding box.

### Machine Learning / Processing Layer (Python)
*   **Downscaling Engine:** A PyTorch-based spatio-temporal `MultiTaskRainfallTransformer` that fuses 14-day coarse weather lookbacks with precise static geographical features (Latitude, Longitude, Elevation).
*   **Deep Quantile Regression:** Optimizes a pinball loss function to dynamically predict the Q95 extreme weather thresholds for the specific microclimate.
*   **Advisory NLP Engine:** Rule-based logic that takes final weather arrays and outputs regional language text based on crop calendars.

### Backend Services (FastAPI)
*   **REST API:** Serves downscaled forecasts to the dashboard.
*   **Webhook Receivers:** Listens to Pingram API for incoming farmer SMS/WhatsApp replies.
*   **Task Queue (Optional):** Background workers for running the ML pipeline (if needed).

### Data Storage Layer (SQLite)
*   **Purpose:** Stores villages (with elevations), blocks, weather grid geometries, daily weather variables, advisory logs, farmer profiles, and feedback scores.
*   **Note:** Swapped from PostgreSQL to SQLite for Phase 1 to simplify development and setup.

### Frontend Dashboard (React)
*   **Target Audience:** Agricultural Extension Officers.
*   **Features:** Interactive map comparing block-level vs. village-level forecasts, advisory reach metrics, and feedback visualization.

### Delivery Layer
*   **Pingram API:** Handles outbound WhatsApp/SMS routing and inbound replies.

## 2. Core Data Flow
`Open-Meteo API` → `Data Ingestion Service` → `ML Downscaling Engine` → `SQLite` → `Advisory Generator` → `Pingram API` → `Farmer`
*(Feedback Flow)*: `Farmer Reply` → `Pingram Webhook` → `FastAPI` → `SQLite` → *(Improves ML Model next cycle)*

## 3. Module Structure (Actual)
```text
/backend
  main.py             # FastAPI routes
  models.py           # SQLAlchemy DB models
  schemas.py          # Pydantic schemas
  database.py         # SQLite config
  ml_service.py       # PyTorch model inference
  advisory_engine.py  # NLP rule-based logic
  nasa_api.py         # Historical API integration
  open_meteo_api.py   # Live weather API integration
  pingram_service.py  # WhatsApp/SMS delivery integration
  seed.py             # Database seeding script
  test_integration.py # Integration test suite
/data                 # Ingestion scripts (fetch_chirps, fetch_elevation, align_datasets)
/frontend             # React dashboard (Vite + Leaflet)
  /src/components     # AdvisoryPanel, Sidebar, WeatherMap
/ml_engine            # PyTorch model, train.py, weights.pt, scaler.json
/notebooks            # Jupyter notebooks for data analysis and validate.py
```
