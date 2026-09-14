# Feature & Decision Log

*This file tracks the chronological implementation of features, bug fixes, and critical architectural decisions for the AgriPixel project.*

## Day 1: Project Initialization (2026-08-27)

### Decisions
*   **Target Region:** Selected Tamil Nadu as the pilot region due to distinct agro-climatic zones.
*   **Coarse Data Source:** Chose NASA POWER API for initial development speed (no auth required), with a potential pivot to ERA5 for higher scientific rigor if time permits.
*   **Delivery Layer:** Switched from Twilio to **Pingram API** for SMS/WhatsApp delivery and webhooks.
*   **Frontend Styling:** Decided on Vanilla CSS to ensure maximum control over premium design aesthetics, avoiding TailwindCSS as per guidelines.
*   **Database:** Switched from PostgreSQL to **SQLite** for the initial MVP to simplify setup and development.

### Features Implemented
*   Created foundational documentation:
    *   `PROJECT_CONTEXT.md`
    *   `ARCHITECTURE.md`
    *   `CODING_RULES.md`
    *   `FEATURE_LOG.md`
*   Added Jupyter notebooks (`extreme-rainfall-risk-atlas.ipynb`, `india-weather-analysis-2026-super-el-nino-impac.ipynb`) for initial data exploration and analysis.
*   Developed `nasa_fetch.py` script to pull historical coarse weather data from NASA POWER API.

## Day 2: Backend and ML Scaffolding (2026-08-28)

### Features Implemented
*   Organized project structure into `/backend`, `/data`, `/frontend`, `/ml_engine`, and `/notebooks`.
*   Implemented PyTorch `MultiTaskRainfallTransformer` model in `ml_engine/model.py` for multi-horizon forecasting and extreme weather prediction.
*   Scaffolded FastAPI backend with SQLAlchemy (SQLite) and integrated the ML inference service and advisory engine (`backend/main.py`).

## Day 3: Frontend Initialization (2026-08-29)

### Features Implemented
*   Initialized React frontend dashboard using Vite.
*   Added `react-leaflet` and `leaflet` dependencies for the interactive weather map to compare forecasts.
*   Added `lucide-react` for iconography.
*   Configured standard frontend structure (`src/components`, `index.css`) relying on Vanilla CSS as per coding guidelines.

## Day 4: Model Training Strategy & API Switch (2026-08-30)

### Decisions
*   **Training Data Scaling:** Decided to expand ML model training by fetching 10 years of historical data from NASA POWER for all 38 districts of Tamil Nadu to improve accuracy.
*   **Live Coarse Data Source:** Switched from NASA POWER API to **Open-Meteo API** for real-time inference to eliminate the 2-day latency limitation of NASA POWER.

## Day 5-14: Model Training and Integration (2026-09-01 to 2026-09-14)

### Features Implemented
*   **Data Pipelines:** Developed `fetch_chirps.py` and `fetch_elevation.py` to acquire high-resolution ground truth and terrain data.
*   **Dataset Alignment:** Created `align_datasets.py` to map the coarse NASA POWER weather grids to the high-resolution CHIRPS/Elevation data.
*   **Model Training:** Successfully trained the `MultiTaskRainfallTransformer` model (`ml_engine/train.py`), generating production weights (`weights.pt`) and scalers (`scaler.json`).
*   **Validation:** Added `validate.py` notebook to evaluate model accuracy against ground truth.
*   **Backend Integration:** Integrated the fully trained PyTorch model into the FastAPI backend (`ml_service.py`) and created an integration test suite (`test_integration.py`).

## Day 15: Real Data Seeding & Model Integration Fixes (2026-09-15)

### Features Implemented
*   **Database Schema:** Added `elevation` to the `Village` schema in SQLAlchemy and Pydantic models to feed crucial terrain data to the ML model.
*   **API Alignment:** Corrected `open_meteo_api.py` feature extraction to match the exact `[Temp, Humidity, Wind, Rain]` tensor order expected by the trained PyTorch model.
*   **Seeding:** Refactored `seed.py` from generating generic grids to seeding specific real pilot villages (e.g., Mettupalayam, Valparai) with real baseline elevations.
*   **Inference Pipeline:** Updated `ml_service.py` and `main.py` inference endpoints to pass spatial metadata (latitude, longitude, elevation) directly into the prediction layer.
*   **Bug Fixes:** Resolved UTF-8 encoding issues in the integration test suite for handling Tamil character outputs.
