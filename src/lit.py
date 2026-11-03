"""Lightning wiring: sequential chunk dataset, risk-and-turnover loss, validation metric."""

import lightning as L
import torch
from torch.utils.data import DataLoader, Dataset

from config import SELECTION_COST_BPS, ModelConfig, TrainConfig
from model import PortfolioTransformer
from portfolio import annualized_sharpe, gross_and_turnover, net_returns


class ChunkDataset(Dataset):
    """Every run of `chunk_len` consecutive weeks inside one split.

    Turnover depends on last week's weights, so samples cannot be shuffled one by one
    (as DeepDow's per-sample losses assume); chunks are shuffled, weeks inside stay ordered.
    """

    def __init__(self, X, r, chunk_len):
        self.X, self.r, self.len = torch.as_tensor(X), torch.as_tensor(r), chunk_len

    def __len__(self):
        return len(self.X) - self.len + 1

    def __getitem__(self, i):
        return self.X[i : i + self.len], self.r[i : i + self.len]


class FullSequence(Dataset):
    """The whole split as a single ordered sequence (for validation)."""

    def __init__(self, X, r):
        self.X, self.r = torch.as_tensor(X), torch.as_tensor(r)

    def __len__(self):
        return 1

    def __getitem__(self, i):
        return self.X, self.r


def risk_turnover_loss(w, r, lambda_var, lambda_to):
    """-mean(R) + lambda_var * Var(R) + lambda_to * mean(TO) over each chunk, averaged over chunks.

    w, r: (B, T, n_assets). The first week of a chunk only sets the starting holdings,
    so turnover is averaged from the second week on.
    """
    gross, to = gross_and_turnover(w, r)
    mean_ret = gross.mean(1)
    var = gross.var(1)
    mean_to = to[:, 1:].mean(1)
    loss = -mean_ret + lambda_var * var + lambda_to * mean_to
    return loss.mean(), {"mean_ret": mean_ret.mean(), "var": var.mean(), "turnover": mean_to.mean()}


class LitPortfolio(L.LightningModule):
    def __init__(self, n_features, n_assets, lookback, model_cfg: dict, train_cfg: dict):
        """Configs are plain dicts so checkpoints stay loadable with torch.load(weights_only=True)."""
        super().__init__()
        self.save_hyperparameters()
        self.model = PortfolioTransformer(n_features, n_assets, lookback, ModelConfig(**model_cfg))
        self.cfg = TrainConfig(**train_cfg)

    def forward(self, x):
        """x: (B, T, n_features, lookback, n_assets) -> (B, T, n_assets)."""
        b, t = x.shape[:2]
        return self.model(x.flatten(0, 1)).view(b, t, -1)

    def training_step(self, batch, _):
        x, r = batch
        loss, parts = risk_turnover_loss(self(x), r, self.cfg.lambda_var, self.cfg.lambda_to)
        self.log("train_loss", loss, prog_bar=True)
        self.log_dict({f"train_{k}": v for k, v in parts.items()})
        return loss

    def validation_step(self, batch, _):
        x, r = batch
        w = self(x)[0]
        gross, to = gross_and_turnover(w, r[0], torch.zeros_like(w[0]))
        net = net_returns(gross, to, SELECTION_COST_BPS)
        self.log("val_sharpe", annualized_sharpe(net), prog_bar=True)
        self.log("val_turnover", to[1:].mean())

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.cfg.lr, weight_decay=self.cfg.weight_decay)


def make_loaders(data, cfg: TrainConfig):
    X_tr, r_tr = data.split("train")
    X_va, r_va = data.split("val")
    train = DataLoader(ChunkDataset(X_tr, r_tr, cfg.chunk_len), batch_size=cfg.batch_size, shuffle=True)
    val = DataLoader(FullSequence(X_va, r_va), batch_size=1)
    return train, val
