import requests
import pandas as pd
import time
from pathlib import Path
import json

# ClimateSERV API Endpoints
SUBMIT_URL = "https://climateserv.servirglobal.net/api/submitDataRequest"
PROGRESS_URL = "https://climateserv.servirglobal.net/api/getDataRequestProgress"
DATA_URL = "https://climateserv.servirglobal.net/api/getDataFromRequest"

# To prove spatial downscaling, we pick villages inside a single district (Coimbatore)
# with vastly different microclimates and elevations.
# The coarse block model would give them all the same prediction. Our goal is to train on this specific ground truth.
VILLAGES = {
    "Valparai_Hill": (10.3273, 76.9536),    # High elevation, high rainfall
    "Mettupalayam": (11.3000, 76.9500),     # Foothills
    "Sulur_Plains": (11.0261, 77.1261),     # Dry plains
    "Pollachi": (10.6620, 77.0065)          # Wet plains
}

START_DATE = "01/01/2019"
END_DATE = "12/31/2023"

def fetch_chirps_for_point(village_name, lat, lon):
    print(f"\n[{village_name}] Requesting CHIRPS data ({lat}, {lon})...")
    
    # datatype=0 is CHIRPS Daily
    # operationtype=5 is Point Extraction
    geometry = json.dumps({"type": "Point", "coordinates": [lon, lat]})
    params = {
        "datatype": 0,
        "begintime": START_DATE,
        "endtime": END_DATE,
        "intervaltype": 0,
        "operationtype": 5,
        "geometry": geometry
    }
    
    # 1. Submit Request
    res = requests.get(SUBMIT_URL, params=params)
    if res.status_code != 200:
        print(f"  [!] Submit Failed: {res.text}")
        return None
        
    req_id = res.json()[0]
    print(f"  -> Job ID: {req_id}. Waiting for processing...")
    
    # 2. Poll for Progress
    while True:
        prog_res = requests.get(PROGRESS_URL, params={"id": req_id})
        if prog_res.status_code == 200:
            progress = prog_res.json()[0]
            print(f"  -> Progress: {progress}%")
            if progress == 100:
                break
            if progress == -1:
                print("  [!] Job failed on ClimateSERV server.")
                return None
        time.sleep(2)
        
    # 3. Retrieve Data
    print(f"  -> Downloading data for {village_name}...")
    data_res = requests.get(DATA_URL, params={"id": req_id})
    if data_res.status_code != 200:
        print("  [!] Data fetch failed.")
        return None
        
    payload = data_res.json()
    records = []
    
    for item in payload.get("data", []):
        raw_val = item.get("value", {})
        rain_val = raw_val.get("avg", 0.0) 
        date_str = item.get("date")
        
        records.append({
            "Date": date_str,
            "Village": village_name,
            "Latitude": lat,
            "Longitude": lon,
            "CHIRPS_Rainfall_mm": rain_val
        })
        
    df = pd.DataFrame(records)
    # Convert date strings to datetime objects
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y%m%d')
    return df

def main():
    all_data = []
    
    for village, (lat, lon) in VILLAGES.items():
        df = fetch_chirps_for_point(village, lat, lon)
        if df is not None and not df.empty:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Sort chronologically and by village
        final_df = final_df.sort_values(by=["Village", "Date"]).reset_index(drop=True)
        
        output_path = Path(__file__).parent / "chirps_high_res_target.csv"
        final_df.to_csv(output_path, index=False)
        print(f"\n✅ Success! Saved {len(final_df)} CHIRPS high-res records to {output_path}")
        print(final_df.head())
    else:
        print("\n❌ Failed to fetch any CHIRPS data.")

if __name__ == "__main__":
    main()
