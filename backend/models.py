from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    district = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float, default=500.0)

    forecasts = relationship("Forecast", back_populates="village")
    farmers = relationship("Farmer", back_populates="village")

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    language = Column(String, default="ta") # ta for Tamil
    primary_crop = Column(String)
    village_id = Column(Integer, ForeignKey("villages.id"))
    
    village = relationship("Village", back_populates="farmers")

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"))
    date = Column(DateTime, default=datetime.utcnow)
    
    predicted_rain_mm = Column(Float)
    extreme_probability = Column(Float)
    q95_threshold = Column(Float)
    
    advisory_sent = Column(Boolean, default=False)
    farmer_feedback = Column(Integer, nullable=True) # 1 for Thumbs Up, -1 for Thumbs Down
    
    village = relationship("Village", back_populates="forecasts")
