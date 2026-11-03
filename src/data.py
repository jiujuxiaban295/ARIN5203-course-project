"""Load prices, build features and weekly samples.

Sample k:
  decision date d_k   = last trading day of week k (information up to d_k's close)
  execution date e_k  = next trading day after d_k (trade at its open)
  X_k                 = features over the `lookback` trading days ending at d_k,
                        shape (n_features, lookback, n_assets) -- DeepDow's layout
  r_k                 = adj_open[e_{k+1}] / adj_open[e_k] - 1, the holding-period return
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from deepdow.data.augment import prepare_standard_scaler

from config import SPLITS, DataConfig

FEATURE_NAMES = ("ret", "vol20", "mom20")


def load_prices(path, tickers):
    """Return (adj_close, adj_open) DataFrames from a yfinance download (auto_adjust=False)."""
    raw = pd.read_csv(path, header=[0, 1], index_col=0, skiprows=[2])
    raw.index = pd.to_datetime(raw.index)
    missing = [t for t in tickers if t not in raw["Adj Close"].columns]
    if missing:
        raise ValueError(f"{path} has no data for {missing}; columns: {list(raw['Adj Close'].columns)}")
    adj_close = raw["Adj Close"][tickers]
    # Yahoo does not provide an adjusted open; scale the raw open by the close's adjustment factor.
    adj_open = raw["Open"][tickers] * adj_close / raw["Close"][tickers]
    keep = adj_close.notna().all(axis=1) & adj_open.notna().all(axis=1)
    return adj_close[keep], adj_open[keep]


def build_features(adj_close, window):
    """Daily return, rolling volatility and momentum; each uses data up to that day's close."""
    ret = adj_close.pct_change()
    vol = ret.rolling(window).std()
    mom = adj_close / adj_close.shift(window) - 1
    return np.stack([ret.values, vol.values, mom.values])  # (n_features, n_days, n_assets)


@dataclass
class WeeklyData:
    X: np.ndarray  # (n_samples, n_features, lookback, n_assets), standardized
    r: np.ndarray  # (n_samples, n_assets) holding-period simple returns
    decision_dates: pd.DatetimeIndex
    exec_dates: pd.DatetimeIndex  # start of each holding period
    end_dates: pd.DatetimeIndex  # end of each holding period
    split_idx: dict  # split name -> np.ndarray of contiguous sample indices
    tickers: list
    scaler: tuple  # (means, stds) per feature, fit on training samples only

    def split(self, name):
        i = self.split_idx[name]
        return self.X[i], self.r[i]


def build_weekly_data(cfg: DataConfig) -> WeeklyData:
    adj_close, adj_open = load_prices(cfg.raw_path, cfg.tickers)
    feats = build_features(adj_close, cfg.feature_window)
    days = adj_close.index

    # Last trading day of each calendar week.
    week = days.to_period("W-FRI")
    decision_pos = np.flatnonzero(week[1:] != week[:-1])  # position of each week's last day
    # Execution is the next session; the holding period ends at the following execution.
    exec_pos = decision_pos + 1
    valid = np.arange(len(decision_pos) - 1)
    first_ok = cfg.lookback + cfg.feature_window  # warm-up for rolling features
    valid = valid[decision_pos[valid] >= first_ok]

    d_pos, e_pos, end_pos = decision_pos[valid], exec_pos[valid], exec_pos[valid + 1]
    X = np.stack([feats[:, p - cfg.lookback + 1 : p + 1, :] for p in d_pos])
    opens = adj_open.values
    r = opens[end_pos] / opens[e_pos] - 1
    assert not np.isnan(X).any() and not np.isnan(r).any()

    decision_dates, exec_dates, end_dates = days[d_pos], days[e_pos], days[end_pos]
    split_idx = {}
    for name, (start, stop) in SPLITS.items():
        mask = (decision_dates >= start) & (end_dates <= stop)
        split_idx[name] = np.flatnonzero(mask)

    # Standardize per feature with statistics from the training samples only.
    means, stds = prepare_standard_scaler(X, overlap=False, indices=list(split_idx["train"]))
    X = ((X - means[None, :, None, None]) / stds[None, :, None, None]).astype(np.float32)

    return WeeklyData(
        X=X,
        r=r.astype(np.float32),
        decision_dates=decision_dates,
        exec_dates=exec_dates,
        end_dates=end_dates,
        split_idx=split_idx,
        tickers=list(cfg.tickers),
        scaler=(means, stds),
    )
