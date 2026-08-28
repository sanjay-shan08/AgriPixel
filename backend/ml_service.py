import torch
import sys
from pathlib import Path

# Add ml_engine to path so we can import the model
ml_engine_path = Path(__file__).parent.parent / "ml_engine"
sys.path.append(str(ml_engine_path))

from model import MultiTaskRainfallTransformer

class MLService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiTaskRainfallTransformer(in_features=4)
        
        weights_path = ml_engine_path / "weights.pt"
        if weights_path.exists():
            self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
            print("Loaded trained model weights successfully.")
        else:
            print("Warning: weights.pt not found. Using untrained model.")
            
        self.model.to(self.device)
        self.model.eval()

    def predict(self, features_sequence: list):
        # features_sequence should be shape [14, 4]
        # We need to add a batch dimension -> [1, 14, 4]
        x = torch.tensor(features_sequence, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            rain_pred, extreme_logits, quantile_pred = self.model(x)
            
            # Convert logits to probability
            extreme_prob = torch.sigmoid(extreme_logits)
            
        return {
            "predicted_rain_mm": rain_pred[0].cpu().tolist(),
            "extreme_probability": extreme_prob[0].cpu().tolist(),
            "q95_threshold": quantile_pred[0].cpu().tolist(),
            "horizon": len(rain_pred[0])
        }

ml_service = MLService()
