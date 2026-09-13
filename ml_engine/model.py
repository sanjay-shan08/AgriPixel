import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiTaskRainfallTransformer(nn.Module):
    def __init__(
        self,
        in_features,
        static_features=3, # Lat, Lon, Elevation
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

        # Temporal Embedding
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

        # Spatial Embedding (Conditioning Vector)
        self.spatial_proj = nn.Sequential(
            nn.Linear(static_features, d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model)
        )

        # Output predictions for the next `horizon` days
        # Input dim is 2 * d_model because we concatenate the temporal and spatial embeddings
        combined_dim = d_model * 2

        self.rain_head = nn.Sequential(
            nn.Linear(combined_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

        self.extreme_head = nn.Sequential(
            nn.Linear(combined_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

        self.quantile_head = nn.Sequential(
            nn.Linear(combined_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, horizon)
        )

    def forward(self, x_temporal, x_spatial):
        # x_temporal shape: [batch, lookback, features]
        # x_spatial shape: [batch, static_features]
        
        # 1. Process Temporal Sequence
        z = self.input_proj(x_temporal)
        z = z + self.pos[:, :z.shape[1]]
        z = self.encoder(z)
        context = self.norm(z[:, -1]) # [batch, d_model]

        # 2. Process Spatial Features
        spatial_emb = self.spatial_proj(x_spatial) # [batch, d_model]

        # 3. Fuse Spatial and Temporal Contexts
        fused_context = torch.cat([context, spatial_emb], dim=-1) # [batch, 2 * d_model]

        # 4. Predict
        rain_pred = F.relu(self.rain_head(fused_context)) # relu prevents negative rain prediction
        extreme_logits = self.extreme_head(fused_context)
        quantile_pred = F.softplus(self.quantile_head(fused_context))

        return rain_pred, extreme_logits, quantile_pred
