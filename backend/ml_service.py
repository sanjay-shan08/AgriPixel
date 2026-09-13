import torch
import sys
import json
import numpy as np
from pathlib import Path

# Add ml_engine to path so we can import the model
ml_engine_path = Path(__file__).parent.parent / "ml_engine"
sys.path.append(str(ml_engine_path))

from model import MultiTaskRainfallTransformer

class MLService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiTaskRainfallTransformer(in_features=4, static_features=3)
        
        weights_path = ml_engine_path / "weights.pt"
        if weights_path.exists():
            self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
            print("Loaded trained spatio-temporal model weights successfully.")
        else:
            print("Warning: weights.pt not found. Using untrained model.")
            
        self.model.to(self.device)
        self.model.eval()
        
        # Load the normalization scalers generated during training
        scaler_path = ml_engine_path / "scaler.json"
        if scaler_path.exists():
            with open(scaler_path, 'r') as f:
                self.scalers = json.load(f)
        else:
            self.scalers = {}

    def predict(self, village_name: str, lat: float, lon: float, elevation: float, features_sequence: list):
        """
        features_sequence should be shape [14, 4] representing [Temp, Humidity, Wind, Rain]
        """
        # 1. Fetch normalizers
        if village_name in self.scalers:
            mean_t = np.array(self.scalers[village_name]['mean_t'])
            std_t = np.array(self.scalers[village_name]['std_t'])
        else:
            # Fallback to the first available village's scaler if unknown
            first_key = list(self.scalers.keys())[0]
            mean_t = np.array(self.scalers[first_key]['mean_t'])
            std_t = np.array(self.scalers[first_key]['std_t'])

        std_t[std_t == 0] = 1.0
        
        # 2. Scale temporal features
        seq_arr = np.array(features_sequence)
        seq_scaled = (seq_arr - mean_t) / std_t
        
        # 3. Scale spatial features (matching the logic in train.py)
        spat_scaled = np.array([
            (lat - 11.0) / 1.0,
            (lon - 77.0) / 1.0,
            (elevation - 500.0) / 500.0
        ])
        
        # 4. Prepare Tensors
        x_t = torch.tensor(seq_scaled, dtype=torch.float32).unsqueeze(0).to(self.device)
        x_s = torch.tensor(spat_scaled, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # 5. Inference
        with torch.no_grad():
            rain_pred, extreme_logits, quantile_pred = self.model(x_t, x_s)
            extreme_prob = torch.sigmoid(extreme_logits)
            
        return {
            "predicted_rain_mm": rain_pred[0].cpu().tolist(),
            "extreme_probability": extreme_prob[0].cpu().tolist(),
            "q95_threshold": quantile_pred[0].cpu().tolist(),
            "horizon": len(rain_pred[0])
        }

ml_service = MLService()
