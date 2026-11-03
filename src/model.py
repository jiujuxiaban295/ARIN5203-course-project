"""Small Transformer encoder with a softmax allocation head.

Backbone: torch.nn.TransformerEncoder (PyTorch's built-in implementation).
Head: deepdow.layers.SoftmaxAllocator (long-only weights summing to one).
"""

import torch
from torch import nn
from deepdow.layers import SoftmaxAllocator

from config import ModelConfig


class PortfolioTransformer(nn.Module):
    """Input (B, n_features, lookback, n_assets) -> weights (B, n_assets).

    Each trading day is one token: the n_features x n_assets values of that day are
    projected to d_model, so attention runs over the lookback window.
    """

    def __init__(self, n_features, n_assets, lookback, cfg: ModelConfig):
        super().__init__()
        self.embed = nn.Linear(n_features * n_assets, cfg.d_model)
        self.pos = nn.Parameter(torch.zeros(1, lookback, cfg.d_model))
        nn.init.normal_(self.pos, std=0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=cfg.d_model,
            nhead=cfg.n_heads,
            dim_feedforward=cfg.dim_feedforward,
            dropout=cfg.dropout,
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            layer, cfg.n_layers, norm=nn.LayerNorm(cfg.d_model), enable_nested_tensor=False
        )
        self.head = nn.Linear(cfg.d_model, n_assets)
        self.allocate = SoftmaxAllocator(temperature=1)

    def forward(self, x):
        b, c, t, n = x.shape
        tokens = x.permute(0, 2, 1, 3).reshape(b, t, c * n)  # (B, lookback, n_features*n_assets)
        h = self.encoder(self.embed(tokens) + self.pos)
        return self.allocate(self.head(h[:, -1]))  # last day's token summarizes the window
