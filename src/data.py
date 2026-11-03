"""Load prices, build features and weekly samples.

Sample k:
  decision date d_k   = last trading day of week k (information up to d_k's close)
  execution date e_k  = next trading day after d_k (trade at its open)
  X_k                 = features over the `lookback` trading days ending at d_k,
                        shape (n_features, lookback, n_assets) -- DeepDow's layout
  r_k                 = adj_open[e_{k+1}] / adj_open[e_k] - 1, the holding-period return
"""

import zipfile
from dataclasses import dataclass

import numpy as np
import pandas as pd
from deepdow.data.augment import prepare_standard_scaler

from config import SPLITS, DataConfig

FEATURE_NAMES = ("ret", "vol20", "mom20")
DATA_DIR = "proposal_final_2006_2025"  # folder inside the dataset zip


def _read_zip_csv(zf, name):
    with zf.open(f"{DATA_DIR}/{name}") as f:
        return pd.read_csv(f)


def load_prices(path, tickers):
    """Return (adj_close, adj_open) from the team's dataset zip (2005 warm-up + 2006-2025).

    `Adjusted Open` in the dataset is Open x (Adj Close / Close), the same factor as the close.
    """
    closes, opens = {}, {}
    with zipfile.ZipFile(path) as zf:
        for t in tickers:
            df = pd.concat([_read_zip_csv(zf, f"{t}_warmup_2005.csv"), _read_zip_csv(zf, f"{t}_2006_2025.csv")])
            df = df.assign(Date=pd.to_datetime(df["Date"])).set_index("Date").sort_index()
            closes[t], opens[t] = df["Adjusted Close"], df["Adjusted Open"]
    adj_close, adj_open = pd.DataFrame(closes), pd.DataFrame(opens)
    keep = adj_close.notna().all(axis=1) & adj_open.notna().all(axis=1)
    return adj_close[keep], adj_open[keep]


def load_dtb3(path):
    """FRED DTB3 (percent, discount basis) indexed by date; official blanks dropped."""
    with zipfile.ZipFile(path) as zf:
        df = _read_zip_csv(zf, "DTB3_2006_2025.csv")
    s = pd.to_numeric(df["DTB3"], errors="coerce")
    s.index = pd.to_datetime(df["observation_date"])
    return s.dropna()


def risk_free_returns(dtb3, starts, ends):
    """Cash return over each holding period from the 3-month bill discount rate.

    Uses the latest quote strictly before the period starts (never a later value).
    P = 1 - d * 91/360, period return = P ** (-calendar_days / 91) - 1.
    Periods with no earlier quote (2005 warm-up samples, in no split) get NaN.
    """
    pos = dtb3.index.searchsorted(starts, side="left") - 1
    d = np.where(pos >= 0, dtb3.values[np.maximum(pos, 0)], np.nan) / 100
    price = 1 - d * 91 / 360
    days = (ends - starts).days.values
    return price ** (-days / 91) - 1


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
    rf: np.ndarray  # (n_samples,) risk-free return over the same holding period
    decision_dates: pd.DatetimeIndex
    exec_dates: pd.DatetimeIndex  # start of each holding period
    end_dates: pd.DatetimeIndex  # end of each holding period
    split_idx: dict  # split name -> np.ndarray of contiguous sample indices
    tickers: list
    scaler: tuple  # (means, stds) per feature, fit on training samples only

    def split(self, name):
        i = self.split_idx[name]
        return self.X[i], self.r[i], self.rf[i]


def build_weekly_data(cfg: DataConfig) -> WeeklyData:
    adj_close, adj_open = load_prices(cfg.data_path, cfg.tickers)
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
    rf = risk_free_returns(load_dtb3(cfg.data_path), exec_dates, end_dates)
    split_idx = {}
    for name, (start, stop) in SPLITS.items():
        mask = (decision_dates >= start) & (end_dates <= stop)
        split_idx[name] = np.flatnonzero(mask)
        assert not np.isnan(rf[split_idx[name]]).any(), f"missing risk-free rate in {name}"

    # Standardize per feature with statistics from the training samples only.
    means, stds = prepare_standard_scaler(X, overlap=False, indices=list(split_idx["train"]))
    X = ((X - means[None, :, None, None]) / stds[None, :, None, None]).astype(np.float32)

    return WeeklyData(
        X=X,
        r=r.astype(np.float32),
        rf=rf.astype(np.float32),
        decision_dates=decision_dates,
        exec_dates=exec_dates,
        end_dates=end_dates,
        split_idx=split_idx,
        tickers=list(cfg.tickers),
        scaler=(means, stds),
    )
