from database import SessionLocal
import models
import math

def generate_grid(center_name, center_lat, center_lon, grid_size=3, step=0.045):
    """
    Generates a grid of villages around a center point.
    step = 0.045 is approx 5km in degrees.
    grid_size = 3 creates a 3x3 grid (9 villages).
    """
    villages = []
    offset = grid_size // 2
    
    vid = 1 if center_name == "Coimbatore" else 100 # just for unique fake ids
    
    for i in range(grid_size):
        for j in range(grid_size):
            lat = center_lat + (i - offset) * step
            lon = center_lon + (j - offset) * step
            
            # Simple naming: N/S/E/W based on position relative to center
            ns = "North" if i > offset else "South" if i < offset else "Central"
            ew = "East" if j > offset else "West" if j < offset else ""
            if ns == "Central" and ew == "":
                name = f"{center_name} Main Panchayat"
            else:
                name = f"{center_name} {ns} {ew} Panchayat".strip()
                
            villages.append({
                "name": name,
                "district": center_name,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4)
            })
            vid += 1
    return villages

def seed():
    db = SessionLocal()
    
    # 1. Clear existing data
    db.query(models.Farmer).delete()
    db.query(models.Forecast).delete()
    db.query(models.Village).delete()
    db.commit()
    print("Cleared old mock data.")

    # 2. Generate Coimbatore Block (3x3 = 9 villages)
    cbe_villages = generate_grid("Coimbatore", 11.0168, 76.9558, 3)
    
    # 3. Generate Madurai Block (3x3 = 9 villages)
    mdu_villages = generate_grid("Madurai", 9.9252, 78.1198, 3)
    
    all_villages = cbe_villages + mdu_villages
    
    # 4. Insert into DB
    v_id = 1
    for v in all_villages:
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
    print(f"Database seeded with {len(all_villages)} downscaled Panchayat-level points.")

if __name__ == "__main__":
    seed()
