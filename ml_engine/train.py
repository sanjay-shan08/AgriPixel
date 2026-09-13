import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import json

from model import MultiTaskRainfallTransformer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameters
LOOKBACK = 14
HORIZON = 3
BATCH_SIZE = 32
EPOCHS = 15
LR = 1e-3

class SpatioTemporalDataset(Dataset):
    def __init__(self, X_temp, X_spat, Y_rain, Y_ext, Y_q):
        self.X_temp = torch.tensor(X_temp, dtype=torch.float32)
        self.X_spat = torch.tensor(X_spat, dtype=torch.float32)
        self.Y_rain = torch.tensor(Y_rain, dtype=torch.float32)
        self.Y_ext = torch.tensor(Y_ext, dtype=torch.float32)
        self.Y_q = torch.tensor(Y_q, dtype=torch.float32)

    def __len__(self):
        return len(self.X_temp)

    def __getitem__(self, idx):
        return self.X_temp[idx], self.X_spat[idx], self.Y_rain[idx], self.Y_ext[idx], self.Y_q[idx]

def prepare_data():
    data_path = Path(__file__).parent.parent / "data" / "paired_downscaling_dataset.csv"
    df = pd.read_csv(data_path)
    
    # Sort by Village and Date
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df = df.sort_values(by=["Village", "Date"]).dropna()

    all_X_temp, all_X_spat, all_Y_rain, all_Y_ext, all_Y_q = [], [], [], [], []
    
    # Calculate Q95 per village for extremes (based on CHIRPS target data)
    q95_thresholds = df.groupby("Village")["CHIRPS_Rainfall_mm"].quantile(0.95).to_dict()

    # Standardization dictionary to save later for inference
    scalers = {}

    for village, group in df.groupby("Village"):
        # Extract Temporal features (Coarse Weather)
        temp_features = group[["Coarse_Temperature_C", "Coarse_Humidity_pct", "Coarse_WindSpeed_ms", "Coarse_Rainfall_mm"]].values
        
        # Standardize temporal features
        mean_t = temp_features.mean(axis=0)
        std_t = temp_features.std(axis=0)
        std_t[std_t == 0] = 1.0 # Prevent div zero
        temp_features_scaled = (temp_features - mean_t) / std_t
        
        # Extract Spatial features (Lat, Lon, Elevation)
        # Spatial features are static per village, so we can just grab the first row's values
        spat_features = group[["Latitude", "Longitude", "Elevation_m"]].values[0]
        
        # Standardize spatial features (we do it manually here for simplicity, 
        # in production you'd calculate global mean/std across all villages)
        spat_features_scaled = np.array([
            (spat_features[0] - 11.0) / 1.0,  # Lat approx 11
            (spat_features[1] - 77.0) / 1.0,  # Lon approx 77
            (spat_features[2] - 500) / 500.0  # Elev approx 500, range ~1000
        ])
        
        # Save scalers for this village (in reality, we should save global scalers)
        scalers[village] = {
            "mean_t": mean_t.tolist(),
            "std_t": std_t.tolist(),
            "q95": q95_thresholds[village]
        }
        
        # Target variable is the HIGH-RES CHIRPS data
        target_rain = group["CHIRPS_Rainfall_mm"].values
        q95 = q95_thresholds[village]
        
        for i in range(len(temp_features) - LOOKBACK - HORIZON):
            x_t = temp_features_scaled[i : i + LOOKBACK]
            x_s = spat_features_scaled
            
            y_rain = target_rain[i + LOOKBACK : i + LOOKBACK + HORIZON]
            y_ext = (y_rain > q95).astype(float)
            y_q = np.full(HORIZON, q95)
            
            all_X_temp.append(x_t)
            all_X_spat.append(x_s)
            all_Y_rain.append(y_rain)
            all_Y_ext.append(y_ext)
            all_Y_q.append(y_q)
            
    # Save scalers
    scaler_path = Path(__file__).parent / "scaler.json"
    with open(scaler_path, 'w') as f:
        json.dump(scalers, f, indent=4)
            
    return (
        np.array(all_X_temp), 
        np.array(all_X_spat), 
        np.array(all_Y_rain), 
        np.array(all_Y_ext), 
        np.array(all_Y_q)
    )

def train():
    print("Preparing spatio-temporal data...")
    X_temp, X_spat, Y_rain, Y_ext, Y_q = prepare_data()
    
    dataset = SpatioTemporalDataset(X_temp, X_spat, Y_rain, Y_ext, Y_q)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = MultiTaskRainfallTransformer(in_features=4, static_features=3).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    
    bce_loss = nn.BCEWithLogitsLoss()
    mse_loss = nn.MSELoss()
    
    print(f"Training on {len(dataset)} samples for {EPOCHS} epochs on {DEVICE}...")
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for bx_temp, bx_spat, by_rain, by_ext, by_q in loader:
            bx_temp = bx_temp.to(DEVICE)
            bx_spat = bx_spat.to(DEVICE)
            by_rain = by_rain.to(DEVICE)
            by_ext = by_ext.to(DEVICE)
            by_q = by_q.to(DEVICE)
            
            optimizer.zero_grad()
            
            pred_rain, pred_ext_logits, pred_q = model(bx_temp, bx_spat)
            
            loss_rain = mse_loss(pred_rain, by_rain)
            loss_ext = bce_loss(pred_ext_logits, by_ext)
            
            err = by_rain - pred_q
            loss_q = torch.max(0.95 * err, (0.95 - 1.0) * err).mean()
            
            loss = loss_rain * 0.1 + loss_ext + loss_q * 0.5
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(loader):.4f}")
        
    weights_path = Path(__file__).parent / "weights.pt"
    torch.save(model.state_dict(), weights_path)
    print(f"\nSuccess! Spatio-Temporal Model trained and weights saved to {weights_path}")

if __name__ == "__main__":
    train()
