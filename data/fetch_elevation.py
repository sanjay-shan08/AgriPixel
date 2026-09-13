import requests
import pandas as pd
from pathlib import Path
import time

# Open-Meteo Elevation API (Returns 90m SRTM global elevation data)
URL = "https://api.open-meteo.com/v1/elevation"

# The same target microclimates we fetched CHIRPS data for
VILLAGES = {
    "Valparai_Hill": (10.3273, 76.9536),
    "Mettupalayam": (11.3000, 76.9500),
    "Sulur_Plains": (11.0261, 77.1261),
    "Pollachi": (10.6620, 77.0065)
}

def fetch_elevations():
    print("Fetching SRTM Elevation data for target microclimates...\n")
    records = []
    
    for village, (lat, lon) in VILLAGES.items():
        params = {
            "latitude": lat,
            "longitude": lon
        }
        
        try:
            response = requests.get(URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # The API returns an array of elevations corresponding to the requested lat/lons
            elevation = data.get("elevation", [None])[0]
            
            print(f"[{village}] Lat: {lat}, Lon: {lon} -> Elevation: {elevation} meters")
            
            records.append({
                "Village": village,
                "Latitude": lat,
                "Longitude": lon,
                "Elevation_m": elevation
            })
            
        except Exception as e:
            print(f"[!] Failed to fetch elevation for {village}: {e}")
            
        # Small delay to respect API rate limits
        time.sleep(1)
        
    df = pd.DataFrame(records)
    
    output_path = Path(__file__).parent / "village_elevations.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\nSuccess! Saved elevation data to {output_path}")
    return df

if __name__ == "__main__":
    fetch_elevations()
