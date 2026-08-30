# Architecture

## 1. System Layers

### Data Ingestion Layer
*   **Sources:** Open-Meteo (Live Coarse weather), NASA POWER (Historical training), CHIRPS/AWS (Ground-truth), SRTM (Elevation data).
*   **Function:** Scheduled Python scripts that pull latest weather data for the Tamil Nadu bounding box.

### Machine Learning / Processing Layer (Python)
*   **Downscaling Baseline:** Statistical quantile mapping to adjust coarse data against known terrain distributions.
*   **ML Residual Model:** A PyTorch-based `MultiTaskRainfallTransformer` that predicts rainfall, extreme weather probabilities, and quantiles using a 14-day lookback.
*   **Advisory NLP Engine:** Rule-based logic that takes final weather arrays and outputs regional language text based on crop calendars.

### Backend Services (FastAPI)
*   **REST API:** Serves downscaled forecasts to the dashboard.
*   **Webhook Receivers:** Listens to Pingram API for incoming farmer SMS/WhatsApp replies.
*   **Task Queue (Optional):** Background workers for running the ML pipeline (if needed).

### Data Storage Layer (SQLite)
*   **Purpose:** Stores villages, blocks, weather grid geometries, daily weather variables, advisory logs, farmer profiles, and feedback scores.
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
/data                 # Data ingestion scripts and CSV datasets
/frontend             # React dashboard (Vite + Leaflet)
/ml_engine            # PyTorch model definitions and training scripts
/notebooks            # Jupyter notebooks for data analysis
```
