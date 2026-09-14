from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Village Schemas ---
class VillageBase(BaseModel):
    name: str
    district: str
    latitude: float
    longitude: float
    elevation: float

class VillageCreate(VillageBase):
    pass

class Village(VillageBase):
    id: int

    class Config:
        orm_mode = True

# --- Inference Schemas ---
class InferenceRequest(BaseModel):
    # Expects a sequence of [lookback] days of features: [Temp, Humidity, Wind, Rain]
    # For a real system, we'd query NASA POWER on the fly, but for the endpoint we accept it here
    features_sequence: List[List[float]] 
    village_name: str
    lat: float
    lon: float
    elevation: float

class InferenceResponse(BaseModel):
    predicted_rain_mm: List[float]
    extreme_probability: List[float]
    q95_threshold: List[float]
    horizon: int

class AdvisoryResponse(BaseModel):
    village_id: int
    language: str
    advisory_text: str
    forecast: InferenceResponse

class PingramWebhookPayload(BaseModel):
    from_number: str
    message_body: str
    forecast_id: int # Extracted from the metadata we sent

class DownscaleRequest(BaseModel):
    lat: float
    lon: float
