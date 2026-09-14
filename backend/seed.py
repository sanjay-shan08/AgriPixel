from database import SessionLocal, engine
import models

def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Clear existing data
    db.query(models.Farmer).delete()
    db.query(models.Forecast).delete()
    db.query(models.Village).delete()
    db.commit()
    print("Cleared old mock data.")

    # 2. Define real villages that match scaler.json
    real_villages = [
        {
            "name": "Mettupalayam",
            "district": "Coimbatore",
            "latitude": 11.3000,
            "longitude": 76.9500,
            "elevation": 314.0
        },
        {
            "name": "Pollachi",
            "district": "Coimbatore",
            "latitude": 10.6600,
            "longitude": 77.0100,
            "elevation": 293.0
        },
        {
            "name": "Sulur_Plains",
            "district": "Coimbatore",
            "latitude": 11.0300,
            "longitude": 77.1300,
            "elevation": 340.0
        },
        {
            "name": "Valparai_Hill",
            "district": "Coimbatore",
            "latitude": 10.3300,
            "longitude": 76.9500,
            "elevation": 1065.0
        }
    ]
    
    # 3. Insert into DB
    v_id = 1
    for v in real_villages:
        v["id"] = v_id
        new_v = models.Village(**v)
        db.add(new_v)
        
        # Add a mock farmer to each so Pingram sending has a target
        farmer = models.Farmer(
            phone_number=f"+9198765432{str(v_id).zfill(2)}", 
            language="ta", 
            primary_crop="Rice", 
            village_id=v_id
        )
        db.add(farmer)
        v_id += 1
            
    db.commit()
    db.close()
    print(f"Database seeded with {len(real_villages)} downscaled Panchayat-level points.")

if __name__ == "__main__":
    seed()
