import sys
from pathlib import Path

# Add necessary paths
base_path = Path(__file__).parent
sys.path.append(str(base_path))

from ml_service import ml_service
from advisory_engine import generate_advisory

def run_e2e_test():
    print("="*50)
    print(" AGRIPIXEL E2E INTEGRATION TEST")
    print("="*50)

    # 1. Define the Microclimate (Valparai - High Altitude Hill Station)
    village = "Valparai_Hill"
    lat = 10.3273
    lon = 76.9536
    elevation = 1065.0
    
    print(f" Target Microclimate: {village} (Elev: {elevation}m)")
    
    # 2. Mock 14-day Coarse Weather Input (Temp, Humidity, Wind, Rain)
    # We'll simulate a period where the baseline coarse block suggests "Moderate" rain.
    # Because Valparai is a high-altitude hill station, the spatial model should theoretically react to it.
    print("\n Fetching Coarse Weather Sequence (14 days)...")
    mock_sequence = [
        [26.5, 80.0, 3.5, 15.0] for _ in range(14) # Consistent 15mm moderate rain block-level
    ]
    
    # 3. Spatio-Temporal Inference
    print(" Running Spatio-Temporal Downscaling Inference...")
    try:
        preds = ml_service.predict(village, lat, lon, elevation, mock_sequence)
        predicted_rain = preds["predicted_rain_mm"]
        risk = preds["extreme_probability"]
        
        print(f"   -> Downscaled Rain Forecast (Next 3 Days): {[round(r, 2) for r in predicted_rain]} mm")
        print(f"   -> Extreme Weather Risk: {[round(r*100, 1) for r in risk]}%")
    except Exception as e:
        print(f"[!] ML Service Failed: {e}")
        return
        
    # 4. NLP Advisory Generation
    print("\n Generating Localized Advisory (Tamil & English)...")
    try:
        tamil_advisory = generate_advisory(predicted_rain, risk, language="ta")
        english_advisory = generate_advisory(predicted_rain, risk, language="en")
        
        print("\n----- SMS PAYLOAD (TAMIL) -----")
        print(tamil_advisory)
        print("-------------------------------")
        
        print("\n----- SMS PAYLOAD (ENGLISH) -----")
        print(english_advisory)
        print("---------------------------------")
        
    except Exception as e:
        print(f"[!] Advisory Engine Failed: {e}")
        return

    print("\n E2E Pipeline Test Completed Successfully!")

if __name__ == "__main__":
    run_e2e_test()
