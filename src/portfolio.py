"""Portfolio accounting shared by the training loss, validation and the backtester.

Everything is in torch so the same formulas are differentiable during training.
"""

import math

import torch

from config import PERIODS_PER_YEAR


def drift(w, r):
    """Holdings after one period: w * (1 + r) / (1 + w . r). Shapes (..., n_assets)."""
    grown = w * (1 + r)
    return grown / grown.sum(-1, keepdim=True)


def gross_and_turnover(w, r, w_init=None):
    """Gross returns and L1 turnover against drifted holdings for a weight sequence.

    w, r: (..., T, n_assets). Returns gross (..., T) and turnover (..., T).
    turnover[t] = |w[t] - drift(w[t-1], r[t-1])|_1. For t = 0 it is measured against
    `w_init` (e.g. zeros = starting from cash); if `w_init` is None it is set to 0, i.e.
    the first weights are taken as the starting holdings.
    """
    gross = (w * r).sum(-1)
    drifted = drift(w[..., :-1, :], r[..., :-1, :])
    to_rest = (w[..., 1:, :] - drifted).abs().sum(-1)
    if w_init is None:
        to_first = torch.zeros_like(to_rest[..., :1])
    else:
        to_first = (w[..., :1, :] - w_init).abs().sum(-1)
    return gross, torch.cat([to_first, to_rest], dim=-1)


def net_returns(gross, turnover, cost_bps):
    return gross - cost_bps * 1e-4 * turnover


def annualized_sharpe(returns, rf=None):
    """returns: (T,) per-period net returns; rf: per-period risk-free return or None."""
    excess = returns if rf is None else returns - rf
    sd = excess.std()
    return (excess.mean() / sd * math.sqrt(PERIODS_PER_YEAR)).item() if sd > 0 else float("nan")


def summary(weights, r, cost_bps, rf=None, from_cash=True):
    """Metrics for one strategy. weights, r: (T, n_assets) tensors."""
    w_init = torch.zeros_like(weights[0]) if from_cash else None
    gross, to = gross_and_turnover(weights, r, w_init)
    net = net_returns(gross, to, cost_bps)
    wealth = torch.cumprod(1 + net, 0)
    drawdown = 1 - wealth / torch.cummax(wealth, 0).values
    years = len(net) / PERIODS_PER_YEAR
    return {
        "cost_bps": cost_bps,
        "ann_return": (wealth[-1] ** (1 / years) - 1).item(),
        "ann_vol": (net.std() * math.sqrt(PERIODS_PER_YEAR)).item(),
        "sharpe": annualized_sharpe(net, rf),
        "max_drawdown": drawdown.max().item(),
        "ann_turnover": (to[1:].mean() * PERIODS_PER_YEAR).item(),
    }
