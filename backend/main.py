from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from ml_service import ml_service

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgriPixel API", description="Hyperlocal weather downscaling for agro-advisory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon we allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AgriPixel API"}

@app.post("/predict", response_model=schemas.InferenceResponse)
def predict_weather(request: schemas.InferenceRequest):
    if len(request.features_sequence) != 14:
        raise HTTPException(status_code=400, detail="Must provide exactly 14 days of lookback features.")
    
    # Run inference through our loaded PyTorch model
    result = ml_service.predict(request.features_sequence)
    return result

# --- Village Endpoints ---
@app.post("/villages/", response_model=schemas.Village)
def create_village(village: schemas.VillageCreate, db: Session = Depends(get_db)):
    db_village = models.Village(**village.dict())
    db.add(db_village)
    db.commit()
    db.refresh(db_village)
    return db_village

@app.get("/villages/", response_model=list[schemas.Village])
def read_villages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    villages = db.query(models.Village).offset(skip).limit(limit).all()
    return villages

from advisory_engine import generate_advisory
from open_meteo_api import get_real_features

@app.get("/advisory/{village_id}", response_model=schemas.AdvisoryResponse)
def get_advisory(village_id: int, language: str = "ta", db: Session = Depends(get_db)):
    # Check if village exists
    village = db.query(models.Village).filter(models.Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
        
    # Fetch real 14-day weather sequence from NASA POWER
    features = get_real_features(village.latitude, village.longitude)
    
    # Run ML prediction
    ml_result = ml_service.predict(features)
    
    # Generate NLP Advisory
    advisory_text = generate_advisory(
        ml_result["predicted_rain_mm"], 
        ml_result["extreme_probability"], 
        language=language
    )
    
    # Save forecast and advisory state to DB (mocking sending SMS for now)
    db_forecast = models.Forecast(
        village_id=village.id,
        predicted_rain_mm=sum(ml_result["predicted_rain_mm"])/3.0,
        extreme_probability=max(ml_result["extreme_probability"]),
        q95_threshold=max(ml_result["q95_threshold"]),
        advisory_sent=True
    )
    db.add(db_forecast)
    db.commit()
    
    return {
        "village_id": village_id,
        "language": language,
        "advisory_text": advisory_text,
        "forecast": ml_result
    }

from pingram_service import send_whatsapp_advisory

@app.post("/advisory/send/{village_id}")
def send_advisory(village_id: int, db: Session = Depends(get_db)):
    village = db.query(models.Village).filter(models.Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
        
    # Fetch real 14-day weather sequence from NASA POWER
    features = get_real_features(village.latitude, village.longitude)
    ml_result = ml_service.predict(features)
    
    # Send to all farmers in village
    farmers = db.query(models.Farmer).filter(models.Farmer.village_id == village_id).all()
    
    messages_sent = 0
    for farmer in farmers:
        advisory_text = generate_advisory(
            ml_result["predicted_rain_mm"], 
            ml_result["extreme_probability"], 
            language=farmer.language
        )
        
        # Log forecast to DB
        db_forecast = models.Forecast(
            village_id=village.id,
            predicted_rain_mm=sum(ml_result["predicted_rain_mm"])/3.0,
            extreme_probability=max(ml_result["extreme_probability"]),
            q95_threshold=max(ml_result["q95_threshold"]),
            advisory_sent=True
        )
        db.add(db_forecast)
        db.commit()
        db.refresh(db_forecast)
        
        # Send via Pingram
        success = send_whatsapp_advisory(farmer.phone_number, advisory_text, db_forecast.id)
        if success:
            messages_sent += 1
            
    return {"message": f"Sent advisories to {messages_sent} farmers in {village.name}."}

@app.post("/downscale", response_model=list[schemas.Village])
def downscale_region(req: schemas.DownscaleRequest, db: Session = Depends(get_db)):
    """
    Generates a 5x5 grid (25 panchayats) centered at the given lat/lon.
    """
    grid_size = 5
    step = 0.045
    offset = grid_size // 2
    
    new_villages = []
    for i in range(grid_size):
        for j in range(grid_size):
            lat = req.lat + (i - offset) * step
            lon = req.lon + (j - offset) * step
            
            db_v = models.Village(
                name=f"Dynamic Node P({i},{j})",
                district="On-Demand Downscale",
                latitude=round(lat, 4),
                longitude=round(lon, 4)
            )
            db.add(db_v)
            new_villages.append(db_v)
            
    db.commit()
    
    for v in new_villages:
        db.refresh(v)
        farmer = models.Farmer(
            phone_number=f"+919876000{v.id%1000:03d}", 
            language="ta", 
            primary_crop="Rice", 
            village_id=v.id
        )
        db.add(farmer)
    db.commit()
    
    return new_villages

@app.post("/pingram/webhook")
def pingram_webhook(payload: schemas.PingramWebhookPayload, db: Session = Depends(get_db)):
    """
    Receives farmer feedback (Thumbs Up/Down) from WhatsApp.
    """
    forecast = db.query(models.Forecast).filter(models.Forecast.id == payload.forecast_id).first()
    if not forecast:
        return {"status": "ignored", "reason": "Forecast ID not found"}
        
    body = payload.message_body.strip().lower()
    
    # Simple parsing: 1/yes/thumbs up vs 0/no/thumbs down
    if body in ["1", "yes", "👍", "true"]:
        forecast.farmer_feedback = 1
    elif body in ["0", "no", "👎", "false"]:
        forecast.farmer_feedback = -1
    else:
        # Unable to parse feedback
        return {"status": "ignored", "reason": "Unrecognized feedback"}
        
    db.commit()
    return {"status": "success", "feedback_recorded": forecast.farmer_feedback}
