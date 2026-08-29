import requests
from database import SessionLocal
import models
import time

BASE_URL = "http://127.0.0.1:8000"

def setup_db():
    print("[1] Seeding database with a Village and Farmer...")
    db = SessionLocal()
    
    # Check if village exists
    village = db.query(models.Village).filter(models.Village.name == "Test Village").first()
    if not village:
        village = models.Village(name="Test Village", district="Chennai", latitude=13.08, longitude=80.27)
        db.add(village)
        db.commit()
        db.refresh(village)
        
    # Check if farmer exists
    farmer = db.query(models.Farmer).filter(models.Farmer.phone_number == "+919876543210").first()
    if not farmer:
        farmer = models.Farmer(
            phone_number="+919876543210", 
            language="ta", 
            primary_crop="Rice", 
            village_id=village.id
        )
        db.add(farmer)
        db.commit()
        
    db.close()
    return village.id

def test_endpoints(village_id):
    print("\n[2] Testing GET /villages/")
    resp = requests.get(f"{BASE_URL}/villages/")
    print(f"Status: {resp.status_code}, Response: {resp.json()}")

    print(f"\n[3] Testing GET /advisory/{village_id}")
    resp = requests.get(f"{BASE_URL}/advisory/{village_id}?language=ta")
    print(f"Status: {resp.status_code}")
    advisory_data = resp.json()
    print(f"Advisory Text: {advisory_data.get('advisory_text')}")
    
    print(f"\n[4] Testing POST /advisory/send/{village_id}")
    resp = requests.post(f"{BASE_URL}/advisory/send/{village_id}")
    print(f"Status: {resp.status_code}, Response: {resp.json()}")

    # To test the webhook, we need the forecast_id that was just generated
    db = SessionLocal()
    forecast = db.query(models.Forecast).order_by(models.Forecast.id.desc()).first()
    db.close()
    
    if forecast:
        print(f"\n[5] Simulating Farmer WhatsApp Reply (Webhook) for Forecast ID {forecast.id}...")
        webhook_payload = {
            "from_number": "+919876543210",
            "message_body": "👍",
            "forecast_id": forecast.id
        }
        resp = requests.post(f"{BASE_URL}/pingram/webhook", json=webhook_payload)
        print(f"Status: {resp.status_code}, Response: {resp.json()}")
        
        # Verify in DB
        db = SessionLocal()
        updated_forecast = db.query(models.Forecast).filter(models.Forecast.id == forecast.id).first()
        print(f"Verified Farmer Feedback in DB: {updated_forecast.farmer_feedback} (1 = Thumbs Up)")
        db.close()

if __name__ == "__main__":
    try:
        # Wait for server to start if running via script
        print("Waiting for API server to be reachable...")
        for _ in range(5):
            try:
                requests.get(BASE_URL)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(2)
                
        vid = setup_db()
        test_endpoints(vid)
        print("\n✅ End-to-End Pipeline Test Completed Successfully!")
    except Exception as e:
        print(f"\n❌ E2E Test Failed: {e}")
