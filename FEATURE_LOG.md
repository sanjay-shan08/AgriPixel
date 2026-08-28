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
*   *(Pending)*: Initialize backend and frontend repositories.
