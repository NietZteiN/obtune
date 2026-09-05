"""Data-tree paths + the H1 quarantine guard (CLAUDE.md §3.1 — HARD RULE).

Every read of training data by any trainer/loader goes through
`load_training_jsonl` / `assert_trainable_path`. The guard resolves symlinks and
refuses any path outside data/train/ or inside data/quarantine/ or data/eval/.
This is quarantine layer 1 of 4 (2: tests/test_quarantine_lint.py greps for
bypasses; 3: the H1 generator write-monopoly; 4: scripts/check_manifest.py SHA +
H1-marker content scan).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

from obtune.config import DATA_DIR

TRAIN_ROOT = DATA_DIR / "train"
EVAL_ROOT = DATA_DIR / "eval"
QUARANTINE_ROOT = DATA_DIR / "quarantine"
REJECTS_ROOT = DATA_DIR / "rejects"
MANIFESTS_ROOT = DATA_DIR / "manifests"
STIMULI_ROOT = DATA_DIR / "stimuli"
HUMAN_ROOT = DATA_DIR / "human"
RAW_ROOT = DATA_DIR / "raw"
SPLITS_ROOT = DATA_DIR / "splits"

# Conditions a training job may ever see. H1 is deliberately absent.
TRAINABLE_CONDITIONS = ("L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4", "X1")
ALL_CONDITIONS = TRAINABLE_CONDITIONS + ("H1",)
LANGUAGES = ("python", "javascript")


class QuarantineViolation(RuntimeError):
    """Raised when code attempts to load quarantined/eval data for training."""


def assert_trainable_path(path: str | Path) -> Path:
    """Resolve `path` (following symlinks) and assert it is a legal training input."""
    p = Path(path).resolve()
    forbidden = (QUARANTINE_ROOT.resolve(), EVAL_ROOT.resolve())
    for root in forbidden:
        if root == p or root in p.parents:
            raise QuarantineViolation(
                f"refusing to load {p} for training: inside forbidden root {root} "
                "(H1 quarantine / eval data must never enter a training job — CLAUDE.md §3.1)"
            )
    train_root = TRAIN_ROOT.resolve()
    if train_root != p and train_root not in p.parents:
        raise QuarantineViolation(
            f"refusing to load {p} for training: not under {train_root}"
        )
    return p


def load_training_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """The ONE entry point for reading training rows. Enforces the quarantine guard
    and rejects any row labeled H1 regardless of where it was found."""
    p = assert_trainable_path(path)
    rows = list(iter_jsonl(p))
    bad = [r for r in rows if r.get("condition") == "H1"]
    if bad:
        raise QuarantineViolation(
            f"{p} contains {len(bad)} H1-labeled rows inside the training tree — quarantine breach"
        )
    return rows


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{i + 1}: invalid JSONL: {e}") from e


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return p
