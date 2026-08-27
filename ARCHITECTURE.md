# Architecture

## 1. System Layers

### Data Ingestion Layer
*   **Sources:** NASA POWER (Coarse weather), CHIRPS/AWS (Ground-truth), SRTM (Elevation data).
*   **Function:** Scheduled Python scripts that pull latest weather data for the Tamil Nadu bounding box.

### Machine Learning / Processing Layer (Python)
*   **Downscaling Baseline:** Statistical quantile mapping to adjust coarse data against known terrain distributions.
*   **ML Residual Model:** A lightweight tree-based model (XGBoost/Random Forest) that predicts and corrects the remaining error from the baseline.
*   **Advisory NLP Engine:** Rule-based logic that takes final weather arrays and outputs regional language text based on crop calendars.

### Backend Services (FastAPI)
*   **REST API:** Serves downscaled forecasts to the dashboard.
*   **Webhook Receivers:** Listens to Pingram API for incoming farmer SMS/WhatsApp replies.
*   **Task Queue (Optional):** Background workers for running the ML pipeline (if needed).

### Data Storage Layer (PostgreSQL + PostGIS)
*   **Spatial Tables:** Stores villages, blocks, and weather grid geometries.
*   **Timeseries Tables:** Stores daily weather variables and advisory logs.
*   **User/Feedback Tables:** Stores farmer profiles, crops, and feedback scores.

### Frontend Dashboard (React)
*   **Target Audience:** Agricultural Extension Officers.
*   **Features:** Interactive map comparing block-level vs. village-level forecasts, advisory reach metrics, and feedback visualization.

### Delivery Layer
*   **Pingram API:** Handles outbound WhatsApp/SMS routing and inbound replies.

## 2. Core Data Flow
`NASA POWER API` → `Data Ingestion Service` → `ML Downscaling Engine` → `PostgreSQL` → `Advisory Generator` → `Pingram API` → `Farmer`
*(Feedback Flow)*: `Farmer Reply` → `Pingram Webhook` → `FastAPI` → `PostgreSQL` → *(Improves ML Model next cycle)*

## 3. Module Structure (Proposed)
```text
/backend
  /api          # FastAPI routes
  /core         # Configuration, DB connection
  /data         # Data ingestion scripts
  /ml           # Downscaling and ML models
  /services     # Advisory logic, Pingram integration
/frontend
  /src
    /components # Reusable UI components
    /pages      # Dashboard views
    /styles     # Vanilla CSS modules
```
