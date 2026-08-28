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
