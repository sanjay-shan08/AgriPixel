# AgriPixel 🌾🌤️

**Hyperlocal Weather Downscaling for Panchayat-Level Agro-Advisory**  
*Built for SIH 2026 (PS Code: SIH26074 | Ministry of Earth Sciences)*

---

## 🚨 The Problem
India's current weather forecasts and agro-meteorological advisories are issued at the **block level** (~50km radius). A single block can cover dozens of villages with drastically different microclimates, elevations, and rainfall patterns. 

Currently, a farmer in one corner of a block receives the exact same irrigation, sowing, or pest-spray advisory as a farmer 20+ km away in a completely different rainfall regime. This mismatch leads to:
- Input wastage (water, fertilizer, pesticides)
- Crop stress from mistimed actions
- Low trust in official advisories

## 💡 Our Solution
**AgriPixel** statistically downscales existing coarse block-level weather data (IMD, NASA POWER, ERA5) down to a **panchayat/village-level resolution (~5km)**. 

We then auto-generate a plain-language, crop-specific agro-advisory and deliver it directly to the farmer over SMS and WhatsApp in their regional language using the Pingram API—**no app download or smartphone literacy required.**

### How it works:
1. **Downscaling Engine:** A statistical baseline (quantile-mapping) sharpens coarse gridded forecasts using terrain and elevation data.
2. **ML Residual Correction:** A lightweight Machine Learning model (XGBoost/Random Forest) corrects any systematic local errors the baseline misses.
3. **Advisory Generator:** An NLP rule-engine converts raw forecast variables (rainfall, temp, humidity) into actionable crop-stage advice *(e.g., "Delay sowing", "Spray pesticide today")*.
4. **Delivery & Feedback:** Sent via SMS/WhatsApp (Pingram API). Farmers can reply with a "Thumbs Up/Down" to continuously validate and improve the local model.

## 🌍 The Impact
* **~6.5× Sharper Resolution:** Bringing forecasts down from 50km block-level to 5km village-level.
* **Zero Barrier to Entry:** Regional language advisories via SMS/WhatsApp mean zero app downloads and zero digital literacy barriers.
* **Closed Feedback Loop:** Unlike traditional broadcast advisories, our system learns from direct farmer feedback on the ground.
* **Public Digital Infrastructure:** Designed to sit on top of existing government infrastructure (GKMS, BFS) to close the last-mile delivery gap.

## 🛠️ Tech Stack
* **Data Pipelines:** Python, `xarray`, `scikit-learn`, `xgboost`
* **Data Sources:** NASA POWER, ERA5, CHIRPS, SRTM Elevation
* **Backend API:** Python (FastAPI)
* **Database:** PostgreSQL + PostGIS (Spatial queries)
* **Frontend Dashboard:** React.js (Vite) with Vanilla CSS
* **Delivery Integration:** Pingram API (WhatsApp/SMS)

## 📍 Pilot Region
Our initial models and deployments are calibrated for the diverse agro-climatic zones of **Tamil Nadu, India**.

---

<div align="center">
  <p>Developed for the Smart India Hackathon 2026</p>
  <sub><i>Crafted by <a href="https://www.linkedin.com/in/sanjay-shan">Sanjay Shan</a></i></sub>
</div>