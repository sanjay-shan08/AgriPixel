# Project Context: AgriPixel

## Overview
AgriPixel is a hyperlocal weather downscaling and agro-advisory system being built for the SIH 2026 Hackathon (PS Code: SIH26074, Ministry of Earth Sciences). 

## Problem
Current weather forecasts (IMD) are provided at a coarse block-level (~50km radius), causing farmers in different microclimates within the same block to receive mismatched advisories.

## Solution
AgriPixel statistically downscales coarse meteorological data to a panchayat/village-level resolution (~5km). It then auto-generates localized agro-advisories based on the crop stage and delivers them directly to farmers via SMS/WhatsApp in their regional language, bypassing the need for app downloads or smartphone literacy.

## Target / Pilot Region
**Tamil Nadu**, India.

## Tech Stack
*   **Historical Training Data:** NASA POWER API (10 years of data for all 38 TN districts).
*   **Live Coarse Data Source:** Open-Meteo API (Switched from NASA POWER to eliminate the 2-day latency).
*   **Ground-Truth Data:** High-resolution CHIRPS satellite data and SRTM Elevation data.
*   **Machine Learning / Data Pipeline:** Python, `xarray`, `PyTorch` (Multi-Task Transformer for rainfall and extreme weather prediction).
*   **Backend:** Python with FastAPI.
*   **Database:** SQLite (Initial prototype for faster development).
*   **Frontend Dashboard:** React.js (Vite) with Vanilla CSS (Premium Aesthetics).
*   **Delivery Layer:** Pingram API for SMS and WhatsApp integration.

## Key Flows
1.  **Ingestion:** Fetch daily live weather data from Open-Meteo API.
2.  **Downscaling:** Apply quantile-mapping and ML residual correction using Tamil Nadu elevation and historical ground-truth data.
3.  **Advisory Generation:** NLP rule-engine translates the highly accurate, downscaled weather variables into actionable farming advice.
4.  **Delivery:** Send advisory via Pingram API to farmer's WhatsApp/SMS.
5.  **Feedback Loop:** Farmer replies with thumbs up/down, which is caught via Pingram webhooks to refine the model's accuracy.
