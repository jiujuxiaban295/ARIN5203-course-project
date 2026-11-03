"""Experiment settings, matching proposal_merged.md."""

from dataclasses import dataclass, field

PROPOSAL_TICKERS = ["SPY", "EFA", "EEM", "IEF", "TLT", "GLD"]

# Chronological splits (inclusive calendar bounds). A sample belongs to a split only if
# its decision date and the end of its holding period both fall inside the bounds.
SPLITS = {
    "train": ("2006-01-01", "2017-12-31"),
    "val": ("2018-01-01", "2020-12-31"),
    "test": ("2021-01-01", "2025-12-31"),
}

PERIODS_PER_YEAR = 52  # weekly rebalancing
COST_LEVELS_BPS = (0, 10, 25)
SELECTION_COST_BPS = 10  # validation criterion: net Sharpe at 10 bps


@dataclass
class DataConfig:
    data_path: str = "ARIN5203_Proposal_Datasets_2006_2025.zip"
    tickers: list = field(default_factory=lambda: list(PROPOSAL_TICKERS))
    lookback: int = 60  # trading days of history per input
    feature_window: int = 20  # rolling volatility / momentum window


@dataclass
class ModelConfig:
    d_model: int = 32
    n_heads: int = 4
    n_layers: int = 2
    dim_feedforward: int = 64
    dropout: float = 0.1


@dataclass
class TrainConfig:
    lambda_var: float = 0.0
    lambda_to: float = 0.0
    chunk_len: int = 26  # consecutive weeks per training sequence
    batch_size: int = 16
    lr: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 200
    patience: int = 20
    grad_clip: float = 1.0
    seed: int = 0
