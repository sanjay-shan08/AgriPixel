import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiTaskRainfallTransformer(nn.Module):
    def __init__(
        self,
        in_features,
        lookback=14,
        d_model=64,
        nhead=4,
        num_layers=2,
        dropout=0.1,
        horizon=3
    ):
        super().__init__()
        self.lookback = lookback
        self.horizon = horizon

        self.input_proj = nn.Linear(in_features, d_model)
        self.pos = nn.Parameter(torch.randn(1, lookback, d_model) * 0.02)

        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=2*d_model,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

        # Output predictions for the next `horizon` days
        self.rain_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

        self.extreme_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

        self.quantile_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

    def forward(self, x):
        # x shape: [batch, lookback, features]
        z = self.input_proj(x)
        z = z + self.pos[:, :z.shape[1]]
        z = self.encoder(z)
        
        # Take the output from the last time step
        context = self.norm(z[:, -1])

        rain_pred = self.rain_head(context)           # [batch, horizon]
        extreme_logits = self.extreme_head(context)   # [batch, horizon]
        quantile_pred = F.softplus(self.quantile_head(context)) # [batch, horizon]

        return rain_pred, extreme_logits, quantile_pred
