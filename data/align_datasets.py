import pandas as pd
from pathlib import Path

def align_and_merge():
    print("Starting Phase 13 & 14: Data Alignment and Construction...\n")
    data_dir = Path(__file__).parent
    
    # 1. Load the Data
    try:
        print("Loading datasets...")
        df_coarse = pd.read_csv(data_dir / "tamil_nadu_weather_10yr.csv")
        df_chirps = pd.read_csv(data_dir / "chirps_high_res_target.csv")
        df_elev = pd.read_csv(data_dir / "village_elevations.csv")
    except FileNotFoundError as e:
        print(f"[!] Error loading data: {e}")
        return

    # Ensure Date columns are the same type (int64 for safety)
    df_coarse['Date'] = df_coarse['Date'].astype(int)
    df_chirps['Date'] = df_chirps['Date'].astype(int)

    # 2. Filter Coarse Data to our target district (Coimbatore)
    # The CHIRPS data dates range from 20190101 to 20231231
    min_date, max_date = df_chirps['Date'].min(), df_chirps['Date'].max()
    df_coarse_cbe = df_coarse[
        (df_coarse['District'] == 'Coimbatore') & 
        (df_coarse['Date'] >= min_date) & 
        (df_coarse['Date'] <= max_date)
    ].copy()

    # Rename coarse columns to clarify they are block-level (Low Res) inputs
    df_coarse_cbe = df_coarse_cbe.rename(columns={
        "Rainfall_mm": "Coarse_Rainfall_mm",
        "Temperature_C": "Coarse_Temperature_C",
        "Humidity_pct": "Coarse_Humidity_pct",
        "WindSpeed_ms": "Coarse_WindSpeed_ms"
    })

    # Drop coarse lat/lon since we only care about the village-level lat/lon now
    if 'Latitude' in df_coarse_cbe.columns:
        df_coarse_cbe = df_coarse_cbe.drop(columns=['Latitude', 'Longitude'])

    # 3. Merge Elevation with CHIRPS data
    print("Merging Elevation with High-Res targets...")
    # Drop lat/lon from elev to avoid duplication, CHIRPS already has it
    df_elev_slim = df_elev.drop(columns=['Latitude', 'Longitude'])
    df_merged = pd.merge(df_chirps, df_elev_slim, on="Village", how="left")

    # 4. Merge Coarse Weather with the Village Data
    # Since all our test villages are in Coimbatore, we can map them directly
    # We assign a temporary key to map the coarse data
    print("Aligning Coarse block-level weather to Village coordinates...")
    df_merged['District'] = 'Coimbatore'
    df_final = pd.merge(df_merged, df_coarse_cbe, on=['District', 'Date'], how="inner")

    # Reorder columns for logical flow: [Context, Spatial X, Temporal X, Target Y]
    final_cols = [
        "Date", "District", "Village", "Latitude", "Longitude", "Elevation_m",
        "Coarse_Temperature_C", "Coarse_Humidity_pct", "Coarse_WindSpeed_ms", "Coarse_Rainfall_mm",
        "CHIRPS_Rainfall_mm"
    ]
    df_final = df_final[final_cols]

    # Handle any potential NA values from the API fetches
    df_final = df_final.fillna(0.0)

    # 5. Save the finalized Paired Dataset
    output_path = data_dir / "paired_downscaling_dataset.csv"
    df_final.to_csv(output_path, index=False)
    
    print(f"\nSuccess! Created unified spatio-temporal dataset: {output_path}")
    print(f"Total Rows: {len(df_final)}")
    print("\nSample Data (First 3 Rows):")
    print(df_final.head(3).to_string())

if __name__ == "__main__":
    align_and_merge()
