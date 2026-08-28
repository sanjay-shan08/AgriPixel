import requests
import pandas as pd
import time
from pathlib import Path

# NASA POWER API Endpoint for single point daily data
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Tamil Nadu Pilot Districts (Lat, Lon)
DISTRICTS = {
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Tiruchirappalli": (10.7905, 78.7047)
}

# Date Range (Last 5 years for training data)
START_DATE = "20190101"
END_DATE = "20231231"

# Parameters: 
# PRECTOTCORR: Precipitation Corrected (mm/day)
# T2M: Temperature at 2 Meters (C)
# RH2M: Relative Humidity at 2 Meters (%)
# WS2M: Wind Speed at 2 Meters (m/s)
PARAMETERS = "PRECTOTCORR,T2M,RH2M,WS2M"

def fetch_data():
    all_data = []
    
    print(f"Fetching NASA POWER weather data for {len(DISTRICTS)} districts in Tamil Nadu...")
    
    for district, (lat, lon) in DISTRICTS.items():
        print(f"  -> Fetching data for {district} ({lat}, {lon})...")
        
        params = {
            "parameters": PARAMETERS,
            "community": "AG",
            "longitude": lon,
            "latitude": lat,
            "start": START_DATE,
            "end": END_DATE,
            "format": "JSON"
        }
        
        response = requests.get(URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # The data is nested under properties.parameter
            timeseries = data.get("properties", {}).get("parameter", {})
            
            # Timeseries keys are like '20190101', '20190102', etc.
            # Convert to a list of dicts
            dates = timeseries.get("PRECTOTCORR", {}).keys()
            
            for date in dates:
                row = {
                    "Date": pd.to_datetime(date, format="%Y%m%d"),
                    "District": district,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Rainfall_mm": timeseries.get("PRECTOTCORR", {}).get(date, -999),
                    "Temp_C": timeseries.get("T2M", {}).get(date, -999),
                    "Humidity_pct": timeseries.get("RH2M", {}).get(date, -999),
                    "WindSpeed_ms": timeseries.get("WS2M", {}).get(date, -999)
                }
                all_data.append(row)
        else:
            print(f"  [!] Failed to fetch data for {district}. Status Code: {response.status_code}")
            print(response.text)
        
        # Polite delay to avoid hammering the API
        time.sleep(2)
        
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Filter out missing values (NASA represents missing as -999.0)
    df = df.replace(-999.0, pd.NA)
    
    # Sort by date and district
    df = df.sort_values(by=["District", "Date"]).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    output_dir = Path(__file__).parent
    output_file = output_dir / "tamil_nadu_weather.csv"
    
    df = fetch_data()
    
    if not df.empty:
        df.to_csv(output_file, index=False)
        print(f"\n✅ Success! Saved {len(df)} daily weather records to {output_file}")
        print(df.head())
    else:
        print("\n❌ Failed to fetch any data.")
