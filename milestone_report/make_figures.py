"""Validation-period figures for the milestone report.

Usage: python make_figures.py <path to extracted ARIN5203-completed/results/full>
Reads only validation (2018-2020) outputs; the test period is not plotted.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

RES = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 9, "font.family": "serif", "axes.titlesize": 9,
                     "legend.fontsize": 7.5, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.3,
                     "grid.linewidth": 0.5})

metrics = pd.read_csv(RES / "metrics.csv")
val = metrics[metrics.split == "validation"]

# ---- Report Figure 2 (fig:wealth): validation net value at 10 bps -------------------------------------------
lines = [("equal_weight", "Equal weight", "#555555", (0, (4, 2))),
         ("minimum_variance", "Minimum variance", "#a08000", (0, (1, 1))),
         ("mean_variance", "Mean-variance", "#6b6b2a", (0, (5, 1, 1, 1))),
         ("lstm_full_ensemble", "LSTM, full", "#a8436e", (0, (3, 1, 1, 1))),
         ("transformer_return_ensemble", "Transformer, return", "#d9622b", (0, (6, 2))),
         ("transformer_full_ensemble", "Transformer, full", "#1f5fa8", "-")]
fig, ax = plt.subplots(figsize=(3.4, 1.8))
for key, label, color, ls in lines:
    d = pd.read_csv(RES / f"daily/validation/{key}_10bps.csv", parse_dates=["date"])
    ax.plot(d.date, d.wealth, label=label, color=color, linestyle=ls,
            linewidth=1.4 if key == "transformer_full_ensemble" else 1.0)
ax.axvspan(pd.Timestamp("2020-02-19"), pd.Timestamp("2020-03-23"), color="grey", alpha=0.15, lw=0)
ax.set_ylabel("Net value (start = 1)")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
# Legend in the empty upper-left area: every line stays below 1.1 during 2018.
ax.legend(ncol=1, fontsize=7, frameon=False, loc="upper left", handlelength=2.0,
          borderaxespad=0.1, labelspacing=0.15)
fig.tight_layout()
fig.savefig(OUT / "val_wealth.pdf")
fig.savefig(OUT / "val_wealth.png", dpi=200)
plt.close(fig)

# ---- Report Figure 1 (fig:abl): objective ablations on validation ----------------------------------------
# Labels match the variant names used in the text and Table 1.
fams = [("transformer_return", "Return", "#d9622b"), ("transformer_risk", "Risk", "#6b6b2a"),
        ("transformer_turnover", "Turnover", "#a08000"), ("transformer_full", "Full", "#1f5fa8")]
panels = [("net_sharpe", "Net excess Sharpe (10 bps)", 1),
          ("annualized_volatility", "Annualized volatility (%)", 100),
          ("annualized_turnover", "Annualized L1 turnover", 1)]
fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.0))
v10 = val[val.cost_bps == 10]
for ax, (col, title, scale) in zip(axes[:3], panels):
    for i, (fam, label, color) in enumerate(fams):
        seeds = v10[v10.strategy.str.match(fam + r"_s\d+$")][col] * scale
        ens = v10[v10.strategy == fam + "_ensemble"][col].iloc[0] * scale
        ax.scatter([i] * len(seeds), seeds, color="#8a8f98", s=10, zorder=2,
                   label="Seeds" if i == 0 else None)
        ax.scatter([i], [ens], color=color, marker="D", s=26, zorder=3,
                   label="Ensemble" if i == 0 else None)
    ax.set_xticks(range(len(fams)), [f[1] for f in fams], rotation=35, ha="right", rotation_mode="anchor")
    ax.set_title(title, fontsize=8.5)
axes[2].legend(frameon=False, loc="upper right", handletextpad=0.2, borderaxespad=0.2)
ax = axes[3]
for fam, label, color in fams:
    d = val[val.strategy == fam + "_ensemble"].sort_values("cost_bps")
    ax.plot(d.cost_bps, d.net_sharpe, marker="o", ms=3, color=color, label=label)
d = val[val.strategy == "equal_weight"].sort_values("cost_bps")
ax.plot(d.cost_bps, d.net_sharpe, marker="o", ms=3, color="#555555", ls="--", label="Equal wt.")
ax.set_xticks([0, 10, 25])
ax.set_xlabel("Cost (bps)")
ax.set_title("Ensemble Sharpe vs. cost", fontsize=8.5)
ax.set_ylim(0.7, 1.5)
ax.legend(fontsize=7, frameon=False, loc="upper center", ncol=2, columnspacing=0.6, handlelength=1.3,
          handletextpad=0.3, borderaxespad=0.2)
fig.tight_layout(w_pad=1.4)
fig.savefig(OUT / "val_ablations.pdf")
fig.savefig(OUT / "val_ablations.png", dpi=200)
plt.close(fig)
print("wrote", OUT)
