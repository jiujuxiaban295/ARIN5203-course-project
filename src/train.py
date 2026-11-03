"""Train the Transformer, select penalty strengths on validation, save val/test weights.

Examples (run from the repo root):
  python src/train.py --variant both
  python src/train.py --variant none --tickers SPY,QQQ,IWM,TLT,GLD

Variants (the proposal's ablations):
  none  lambda_var = lambda_to = 0
  var   variance penalty only
  to    turnover penalty only
  both  both penalties
"""

import argparse
import itertools
import json
import warnings
from dataclasses import asdict, replace
from pathlib import Path

import lightning as L
import pandas as pd
import torch
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger

from config import COST_LEVELS_BPS, DataConfig, ModelConfig, TrainConfig
from data import FEATURE_NAMES, build_weekly_data
from lit import LitPortfolio, make_loaders
from portfolio import summary

warnings.filterwarnings("ignore", ".*does not have many workers.*")
warnings.filterwarnings("ignore", ".*GPU available but not used.*")

# lambda_to is a per-unit-turnover charge: 0.001 equals a 10 bps cost.
LAMBDA_VAR_GRID = [1.0, 5.0, 10.0]
LAMBDA_TO_GRID = [0.001, 0.0025, 0.005]
VARIANTS = {
    "none": [(0.0, 0.0)],
    "var": [(lv, 0.0) for lv in LAMBDA_VAR_GRID],
    "to": [(0.0, lt) for lt in LAMBDA_TO_GRID],
    "both": list(itertools.product(LAMBDA_VAR_GRID, LAMBDA_TO_GRID)),
}


def fit_one(data, model_cfg, train_cfg, out_dir):
    L.seed_everything(train_cfg.seed, workers=True, verbose=False)
    train_loader, val_loader = make_loaders(data, train_cfg)
    lit = LitPortfolio(len(FEATURE_NAMES), len(data.tickers), data.X.shape[2], asdict(model_cfg), asdict(train_cfg))
    ckpt = ModelCheckpoint(dirpath=out_dir, monitor="val_sharpe", mode="max", save_top_k=1)
    trainer = L.Trainer(
        accelerator="cpu",
        devices=1,
        max_epochs=train_cfg.max_epochs,
        gradient_clip_val=train_cfg.grad_clip,
        callbacks=[EarlyStopping(monitor="val_sharpe", mode="max", patience=train_cfg.patience), ckpt],
        logger=CSVLogger(out_dir, name="", version=""),
        deterministic=True,
        num_sanity_val_steps=0,
        log_every_n_steps=10,
        enable_progress_bar=False,
        enable_model_summary=False,
    )
    trainer.fit(lit, train_loader, val_loader)
    return ckpt.best_model_score.item(), ckpt.best_model_path, trainer.current_epoch


@torch.no_grad()
def predict(lit, data, split):
    X, r = data.split(split)
    lit.eval()
    w = lit(torch.as_tensor(X)[None])[0]
    dates = data.exec_dates[data.split_idx[split]]
    return pd.DataFrame(w.numpy(), index=dates, columns=data.tickers), torch.as_tensor(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--variant", choices=VARIANTS, default="both")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--tickers", help="comma-separated; default is the proposal's six ETFs")
    p.add_argument("--raw-path", default="yahoo_raw.csv")
    p.add_argument("--max-epochs", type=int, default=TrainConfig.max_epochs)
    p.add_argument("--out", default="results")
    args = p.parse_args()

    torch.set_num_threads(4)
    data_cfg = DataConfig(raw_path=args.raw_path)
    if args.tickers:
        data_cfg.tickers = args.tickers.split(",")
    data = build_weekly_data(data_cfg)
    print({k: len(v) for k, v in data.split_idx.items()}, "weekly samples;", data.tickers)

    model_cfg = ModelConfig()
    base = TrainConfig(seed=args.seed, max_epochs=args.max_epochs)
    run_dir = Path(args.out) / f"transformer_{args.variant}_seed{args.seed}"

    grid = []
    for lv, lt in VARIANTS[args.variant]:
        cfg = replace(base, lambda_var=lv, lambda_to=lt)
        score, path, epochs = fit_one(data, model_cfg, cfg, run_dir / f"lv{lv}_lt{lt}")
        grid.append({"lambda_var": lv, "lambda_to": lt, "val_sharpe_10bps": score, "epochs": epochs, "ckpt": path})
        print(grid[-1])
    grid = pd.DataFrame(grid)
    grid.to_csv(run_dir / "grid.csv", index=False)

    best = grid.loc[grid["val_sharpe_10bps"].idxmax()]
    lit = LitPortfolio.load_from_checkpoint(best["ckpt"])
    metrics = []
    for split in ("val", "test"):
        weights, r = predict(lit, data, split)
        weights.to_csv(run_dir / f"weights_{split}.csv")
        w = torch.tensor(weights.values)
        metrics += [{"split": split, **summary(w, r, c)} for c in COST_LEVELS_BPS]
    metrics = pd.DataFrame(metrics)
    metrics.to_csv(run_dir / "metrics.csv", index=False)

    (run_dir / "best.json").write_text(json.dumps({
        "variant": args.variant,
        "seed": args.seed,
        "tickers": data.tickers,
        "selected": best.drop("ckpt").to_dict(),
        "model": asdict(model_cfg),
        "train": asdict(replace(base, lambda_var=best["lambda_var"], lambda_to=best["lambda_to"])),
        "note": "Sharpe uses rf = 0 until DTB3 is added",
    }, indent=2, default=float))
    print(metrics.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
