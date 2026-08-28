import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from model import MultiTaskRainfallTransformer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameters
LOOKBACK = 14
HORIZON = 3
BATCH_SIZE = 32
EPOCHS = 10
LR = 1e-3

class WeatherDataset(Dataset):
    def __init__(self, X, Y_rain, Y_ext, Y_q):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.Y_rain = torch.tensor(Y_rain, dtype=torch.float32)
        self.Y_ext = torch.tensor(Y_ext, dtype=torch.float32)
        self.Y_q = torch.tensor(Y_q, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.Y_rain[idx], self.Y_ext[idx], self.Y_q[idx]

def prepare_data():
    data_path = Path(__file__).parent.parent / "data" / "tamil_nadu_weather.csv"
    df = pd.read_csv(data_path)
    
    # Sort by District and Date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=["District", "Date"]).dropna()

    all_X, all_Y_rain, all_Y_ext, all_Y_q = [], [], [], []
    
    # Calculate Q95 per district on full data (for simplicity in this baseline)
    q95_thresholds = df.groupby("District")["Rainfall_mm"].quantile(0.95).to_dict()

    for district, group in df.groupby("District"):
        features = group[["Rainfall_mm", "Temp_C", "Humidity_pct", "WindSpeed_ms"]].values
        
        # Standardize features
        mean = features.mean(axis=0)
        std = features.std(axis=0)
        std[std == 0] = 1.0 # Prevent div zero
        
        # Save scaler stats (in a real app, save these to a JSON for inference)
        # Here we just standardize to train the model
        features_scaled = (features - mean) / std
        
        q95 = q95_thresholds[district]
        
        for i in range(len(features) - LOOKBACK - HORIZON):
            x = features_scaled[i : i + LOOKBACK]
            y_rain = features[i + LOOKBACK : i + LOOKBACK + HORIZON, 0] # Unscaled rainfall
            y_ext = (y_rain > q95).astype(float)
            y_q = np.full(HORIZON, q95)
            
            all_X.append(x)
            all_Y_rain.append(y_rain)
            all_Y_ext.append(y_ext)
            all_Y_q.append(y_q)
            
    return np.array(all_X), np.array(all_Y_rain), np.array(all_Y_ext), np.array(all_Y_q)

def train():
    print("Preparing data...")
    X, Y_rain, Y_ext, Y_q = prepare_data()
    
    dataset = WeatherDataset(X, Y_rain, Y_ext, Y_q)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = MultiTaskRainfallTransformer(in_features=4).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    
    bce_loss = nn.BCEWithLogitsLoss()
    mse_loss = nn.MSELoss()
    
    print(f"Training on {len(dataset)} samples for {EPOCHS} epochs on {DEVICE}...")
    
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        
        for bx, by_rain, by_ext, by_q in loader:
            bx, by_rain, by_ext, by_q = bx.to(DEVICE), by_rain.to(DEVICE), by_ext.to(DEVICE), by_q.to(DEVICE)
            
            optimizer.zero_grad()
            
            pred_rain, pred_ext_logits, pred_q = model(bx)
            
            # Note: Pred rain is trained to predict actual rainfall. For better results,
            # we should standardize the target too, but MSE on raw values works for this baseline.
            loss_rain = mse_loss(pred_rain, by_rain)
            loss_ext = bce_loss(pred_ext_logits, by_ext)
            
            # Pinball loss approximation for quantile
            err = by_rain - pred_q
            loss_q = torch.max(0.95 * err, (0.95 - 1.0) * err).mean()
            
            loss = loss_rain * 0.1 + loss_ext + loss_q * 0.5
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(loader):.4f}")
        
    # Save weights
    weights_path = Path(__file__).parent / "weights.pt"
    torch.save(model.state_dict(), weights_path)
    print(f"\nSuccess! Model trained and weights saved to {weights_path}")

if __name__ == "__main__":
    train()
