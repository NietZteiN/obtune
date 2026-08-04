"""Train the RQ2 obfuscation-type router: a 2-layer MLP over frozen prompt features.

Architecture and optimizer are pinned in configs/router/router_v1.yaml:
    Linear(d, 512) -> GELU -> Dropout(0.1) -> Linear(512, 6)
    AdamW, lr 1e-3, batch 256, early stop on VAL ROUTING ACCURACY, seed 17.

Design notes
------------
* 6 classes, never 7. H1 is not a routing class — its behaviour under this router (an
  out-of-distribution prompt forced into a 6-way decision) is an RQ2 *result*, computed
  in route.py. Rows with label -1 are dropped here and their presence is asserted-away.
* The split is by `program_group_id`, never by row (CLAUDE.md §4 silent-failure #1). Six
  conditions of the same parent program are near-duplicates in feature space; splitting
  by row would put a variant of a val program in train and inflate routing accuracy by
  tens of points.
* Features are standardized with train-split statistics only, stored in the checkpoint,
  and re-applied at inference. Standardizing over the full set would leak val moments.
* Class balance: `per_class_train` caps each condition so a condition with more
  materialized pairs cannot dominate the prior; the cap is applied AFTER the split so it
  cannot move programs across splits.
* Early stopping selects on accuracy rather than loss because accuracy is the quantity
  RQ2 reports and a confident-but-wrong router is worse for the downstream system than a
  hesitant-but-right one.

CPU-runnable (tests/test_router.py trains it on synthetic features in seconds).
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np

from obtune.config import RUNS_DIR, load_config
from obtune.paths import TRAINABLE_CONDITIONS
from obtune.router.features import CONDITION_TO_LABEL, FeatureSet, load_features
from obtune.seedutil import set_seed

__all__ = ["RouterMLP", "RouterCheckpoint", "train_router", "split_by_program",
           "save_checkpoint", "load_checkpoint", "ROUTER_DIR"]

ROUTER_DIR = RUNS_DIR / "router"


def _torch():
    import torch

    return torch


class RouterMLP:
    """Constructor shim so the class can be documented without importing torch at module
    import time (features/route are used from CPU-only analysis paths)."""

    def __new__(cls, in_dim: int, hidden: int = 512, n_classes: int = 6,
                dropout: float = 0.1, activation: str = "gelu"):
        torch = _torch()
        import torch.nn as nn

        act = {"gelu": nn.GELU, "relu": nn.ReLU, "tanh": nn.Tanh}[activation]
        return nn.Sequential(
            nn.Linear(in_dim, hidden),
            act(),
            nn.Dropout(dropout),
            nn.Linear(hidden, n_classes),
        )


@dataclass
class RouterCheckpoint:
    state_dict: dict[str, Any]
    in_dim: int
    hidden: int
    n_classes: int
    dropout: float
    activation: str
    mean: np.ndarray
    std: np.ndarray
    class_order: list[str]
    seed: int
    best_epoch: int
    val_accuracy: float
    train_accuracy: float
    history: list[dict[str, float]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


def split_by_program(
    program_ids: np.ndarray, val_fraction: float = 0.1, seed: int = 17
) -> tuple[np.ndarray, np.ndarray]:
    """Boolean (train, val) masks that partition PROGRAMS, not rows."""
    rng = np.random.default_rng(seed)
    progs = np.unique(program_ids)
    rng.shuffle(progs)
    n_val = max(1, int(round(len(progs) * val_fraction)))
    val_progs = set(progs[:n_val].tolist())
    val = np.array([p in val_progs for p in program_ids])
    return ~val, val


def _cap_per_class(y: np.ndarray, mask: np.ndarray, cap: Optional[int], seed: int) -> np.ndarray:
    if not cap:
        return mask
    rng = np.random.default_rng(seed)
    out = np.zeros_like(mask)
    for c in np.unique(y[mask]):
        idx = np.flatnonzero(mask & (y == c))
        if len(idx) > cap:
            idx = rng.choice(idx, size=cap, replace=False)
        out[idx] = True
    return out


def train_router(
    fs: FeatureSet,
    *,
    hidden: int = 512,
    dropout: float = 0.1,
    activation: str = "gelu",
    lr: float = 1e-3,
    batch_size: int = 256,
    max_epochs: int = 50,
    early_stop_patience: int = 5,
    per_class_train: Optional[int] = None,
    val_fraction: float = 0.1,
    weight_decay: float = 0.01,
    seed: int = 17,
    device: str = "cpu",
    verbose: bool = True,
) -> RouterCheckpoint:
    torch = _torch()
    import torch.nn as nn

    set_seed(seed)
    keep = fs.trainable_mask()
    if not keep.all() and verbose:
        print(f"  dropping {int((~keep).sum())} non-trainable (H1) rows — H1 is never a class")
    fs = fs.subset(keep)
    n_classes = len(TRAINABLE_CONDITIONS)
    assert set(np.unique(fs.y).tolist()) <= set(range(n_classes)), "unexpected router label"

    tr_mask, va_mask = split_by_program(fs.program_ids, val_fraction=val_fraction, seed=seed)
    tr_mask = _cap_per_class(fs.y, tr_mask, per_class_train, seed)
    if va_mask.sum() == 0 or tr_mask.sum() == 0:
        raise ValueError("empty train or val split — too few distinct program_ids")

    Xtr, ytr = fs.X[tr_mask], fs.y[tr_mask].astype(np.int64)
    Xva, yva = fs.X[va_mask], fs.y[va_mask].astype(np.int64)
    mean = Xtr.mean(axis=0)
    std = Xtr.std(axis=0)
    std[std < 1e-6] = 1.0  # constant features would otherwise blow up on division
    Xtr = (Xtr - mean) / std
    Xva = (Xva - mean) / std

    dev = torch.device(device)
    model = RouterMLP(Xtr.shape[1], hidden=hidden, n_classes=n_classes,
                      dropout=dropout, activation=activation).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    lossf = nn.CrossEntropyLoss()

    Xtr_t = torch.tensor(Xtr, dtype=torch.float32, device=dev)
    ytr_t = torch.tensor(ytr, device=dev)
    Xva_t = torch.tensor(Xva, dtype=torch.float32, device=dev)
    yva_t = torch.tensor(yva, device=dev)

    g = torch.Generator().manual_seed(seed)
    best_acc, best_epoch, best_state, bad = -1.0, -1, None, 0
    history: list[dict[str, float]] = []

    for epoch in range(max_epochs):
        model.train()
        perm = torch.randperm(len(Xtr_t), generator=g).to(dev)
        tot_loss = 0.0
        for i in range(0, len(perm), batch_size):
            idx = perm[i:i + batch_size]
            opt.zero_grad(set_to_none=True)
            loss = lossf(model(Xtr_t[idx]), ytr_t[idx])
            loss.backward()
            opt.step()
            tot_loss += float(loss.detach()) * len(idx)
        model.eval()
        with torch.no_grad():
            va_acc = float((model(Xva_t).argmax(-1) == yva_t).float().mean())
            tr_acc = float((model(Xtr_t).argmax(-1) == ytr_t).float().mean())
        history.append({"epoch": epoch, "train_loss": tot_loss / len(perm),
                        "train_acc": tr_acc, "val_acc": va_acc})
        if verbose:
            print(f"  epoch {epoch:>3} loss={tot_loss/len(perm):.4f} "
                  f"train_acc={tr_acc:.4f} val_acc={va_acc:.4f}")
        if va_acc > best_acc + 1e-6:
            best_acc, best_epoch, bad = va_acc, epoch, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= early_stop_patience:
                if verbose:
                    print(f"  early stop at epoch {epoch} (best {best_epoch}, val {best_acc:.4f})")
                break

    assert best_state is not None
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        tr_acc = float((model(Xtr_t).argmax(-1) == ytr_t).float().mean())

    return RouterCheckpoint(
        state_dict={k: v.numpy() for k, v in best_state.items()},
        in_dim=int(Xtr.shape[1]), hidden=hidden, n_classes=n_classes, dropout=dropout,
        activation=activation, mean=mean, std=std,
        class_order=list(TRAINABLE_CONDITIONS), seed=seed, best_epoch=best_epoch,
        val_accuracy=best_acc, train_accuracy=tr_acc, history=history,
        meta={"n_train": int(tr_mask.sum()), "n_val": int(va_mask.sum()),
              "n_programs": int(len(np.unique(fs.program_ids))),
              "features": fs.meta, "lr": lr, "batch_size": batch_size,
              "max_epochs": max_epochs, "early_stop_patience": early_stop_patience,
              "per_class_train": per_class_train, "val_fraction": val_fraction},
    )


def save_checkpoint(ck: RouterCheckpoint, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {f"w::{k}": v for k, v in ck.state_dict.items()}
    d = asdict(ck)
    for k in ("state_dict", "mean", "std"):
        d.pop(k)
    np.savez_compressed(p, mean=ck.mean, std=ck.std,
                        meta_json=np.array(json.dumps(d), dtype=object), **payload)
    return p


def load_checkpoint(path: str | Path) -> RouterCheckpoint:
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta_json"].item()))
    sd = {k[len("w::"):]: z[k] for k in z.files if k.startswith("w::")}
    return RouterCheckpoint(state_dict=sd, mean=z["mean"], std=z["std"], **meta)


def build_model(ck: RouterCheckpoint):
    torch = _torch()

    model = RouterMLP(ck.in_dim, hidden=ck.hidden, n_classes=ck.n_classes,
                      dropout=ck.dropout, activation=ck.activation)
    model.load_state_dict({k: torch.tensor(v) for k, v in ck.state_dict.items()})
    model.eval()
    return model


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Train the RQ2 obfuscation-type router")
    ap.add_argument("--config", default="router/router_v1.yaml")
    ap.add_argument("--features", required=True, help="npz from router.features")
    ap.add_argument("--out", default=str(ROUTER_DIR / "router_v1.npz"))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--val-fraction", type=float, default=0.1)
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    fs = load_features(args.features)
    ck = train_router(
        fs,
        hidden=int(cfg["model"]["hidden"]),
        dropout=float(cfg["model"]["dropout"]),
        activation=str(cfg["model"]["activation"]),
        lr=float(cfg["train"]["lr"]),
        batch_size=int(cfg["train"]["batch_size"]),
        max_epochs=int(cfg["train"]["max_epochs"]),
        early_stop_patience=int(cfg["train"]["early_stop_patience"]),
        per_class_train=cfg["train"].get("per_class_train"),
        val_fraction=args.val_fraction,
        seed=int(cfg["train"]["seed"]),
        device=args.device,
    )
    if int(cfg["model"]["n_classes"]) != ck.n_classes:
        raise SystemExit(f"config n_classes={cfg['model']['n_classes']} != {ck.n_classes} "
                         "(the 6 trainable conditions; H1 is never a class)")
    p = save_checkpoint(ck, args.out)
    print(f"wrote {p}  val_acc={ck.val_accuracy:.4f} (epoch {ck.best_epoch}) "
          f"train_acc={ck.train_accuracy:.4f} n_train={ck.meta['n_train']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
