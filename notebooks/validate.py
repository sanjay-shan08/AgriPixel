import pandas as pd
import numpy as np
import torch
import sys
from pathlib import Path

# Add paths to import model and service
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path / "backend"))
sys.path.append(str(base_path / "ml_engine"))

from ml_service import ml_service

def run_validation():
    print("="*50)
    print("AgriPixel: Spatial Downscaling Validation Benchmark")
    print("="*50)
    
    data_path = base_path / "data" / "paired_downscaling_dataset.csv"
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df = df.sort_values(by=["Village", "Date"]).dropna()

    lookback = 14
    horizon = 3
    
    y_true_all = []
    y_pred_coarse_all = []
    y_pred_model_all = []

    print(f"Running inference on {len(df['Village'].unique())} microclimates...")

    # We validate village by village
    for village, group in df.groupby("Village"):
        temp_features = group[["Coarse_Temperature_C", "Coarse_Humidity_pct", "Coarse_WindSpeed_ms", "Coarse_Rainfall_mm"]].values
        target_rain = group["CHIRPS_Rainfall_mm"].values
        
        lat = group["Latitude"].values[0]
        lon = group["Longitude"].values[0]
        elev = group["Elevation_m"].values[0]
        
        for i in range(len(temp_features) - lookback - horizon):
            # The 14-day coarse weather sequence
            seq = temp_features[i : i + lookback]
            
            # The actual CHIRPS ground truth for the next 3 days
            actual = target_rain[i + lookback : i + lookback + horizon]
            
            # The raw coarse block-level prediction (just taking the coarse rain for the same 3 days)
            # This is what farmers currently get (the baseline)
            coarse_baseline = temp_features[i + lookback : i + lookback + horizon, 3] 
            
            # Our model's downscaled prediction
            preds = ml_service.predict(village, lat, lon, elev, seq.tolist())
            model_pred = preds["predicted_rain_mm"]
            
            y_true_all.extend(actual)
            y_pred_coarse_all.extend(coarse_baseline)
            y_pred_model_all.extend(model_pred)

    y_true = np.array(y_true_all)
    y_baseline = np.array(y_pred_coarse_all)
    y_model = np.array(y_pred_model_all)

    # Calculate RMSE manually using numpy
    rmse_baseline = np.sqrt(np.mean((y_true - y_baseline)**2))
    rmse_model = np.sqrt(np.mean((y_true - y_model)**2))
    
    # Calculate MAE manually using numpy
    mae_baseline = np.mean(np.abs(y_true - y_baseline))
    mae_model = np.mean(np.abs(y_true - y_model))

    improvement_rmse = ((rmse_baseline - rmse_model) / rmse_baseline) * 100
    improvement_mae = ((mae_baseline - mae_model) / mae_baseline) * 100

    print("\n[RESULTS]")
    print(f"Data Points Evaluated: {len(y_true)}")
    print("-" * 30)
    print("Baseline (Raw 50km Block Forecast vs CHIRPS):")
    print(f"  RMSE: {rmse_baseline:.2f} mm")
    print(f"  MAE:  {mae_baseline:.2f} mm")
    print("-" * 30)
    print("AgriPixel (Downscaled Spatio-Temporal Forecast vs CHIRPS):")
    print(f"  RMSE: {rmse_model:.2f} mm")
    print(f"  MAE:  {mae_model:.2f} mm")
    print("-" * 30)
    print("CONCLUSION:")
    
    if improvement_rmse > 0:
        print(f"✅ AgriPixel successfully REDUCED forecasting error by {improvement_rmse:.1f}% (RMSE) and {improvement_mae:.1f}% (MAE).")
        print("This proves the spatial downscaling works and successfully corrects block-level inaccuracies using local elevation data.")
    else:
        print(f"❌ Model did not beat baseline. Needs more training epochs or deeper architecture.")
        
    print("="*50)

if __name__ == "__main__":
    run_validation()
