"""Project-root anchoring and YAML config loading (CLAUDE.md §5: configs own all knobs).

Every entrypoint loads its knobs from a YAML under configs/ via `load_config`;
resolved configs are dumped into the run's provenance manifest so a result can
be reproduced without guessing.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# src/obtune/config.py -> obtune/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
DATA_DIR = Path(os.environ.get("OBTUNE_DATA_DIR", PROJECT_ROOT / "data"))
RUNS_DIR = PROJECT_ROOT / "runs"
RESULTS_DIR = PROJECT_ROOT / "results"

GLOBAL_SEED = 17  # project-wide default; per-run seeds live in configs and manifests


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config. Relative paths are anchored at configs/.

    Supports a single level of `_extends: <relative path>` so condition/eval
    configs can layer over a `_base_*.yaml` without a templating dependency.
    """
    p = Path(path)
    if not p.is_absolute():
        p = CONFIG_DIR / p
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    with open(p) as f:
        cfg: dict[str, Any] = yaml.safe_load(f) or {}
    parent_rel = cfg.pop("_extends", None)
    if parent_rel:
        parent = load_config((p.parent / parent_rel) if not Path(parent_rel).is_absolute() else parent_rel)
        cfg = _deep_merge(parent, cfg)
    cfg["_config_path"] = str(p)
    return cfg


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def conditions() -> dict[str, Any]:
    """The condition ladder — single source of truth is configs/conditions.yaml."""
    return load_config("conditions.yaml")
