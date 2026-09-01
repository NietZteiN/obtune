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

    `_extends` merges dicts RECURSIVELY, which is what you want for settings blocks
    (`engine:`, `sampling:`, `criteria:`) — a child overriding one key keeps the rest.
    It is the wrong default for blocks that name WHAT IS EVALUATED rather than how:
    `systems:` is a set of experimental arms, and merging it means a child silently
    inherits arms it never declared.

    That is not hypothetical. Every `unlearn/negation_*` config inherited a `cft` arm
    from `cft/eval/bidir_v1.yaml` — invisible in the file, present in every result. On
    the 7B side the inherited entry still pointed at a **1.5B** adapter, so a 1.5B LoRA
    was loaded onto a 7B base and reported under a real arm's label (the 2026-08-10 run
    scored that arm 86.5 % base-identical). On the 1.5B side it was a valid adapter but
    an arm the experiment never asked for, and on 2026-08-11 it produced base-identical
    output on all 3000 trials and killed four evaluations on the §4.2 adapter guard.

    So the child declares its intent with `_replace`, listing the TOP-LEVEL keys whose
    value should replace the parent's outright::

        _extends: ../cft/eval/bidir_v1.yaml
        _replace: [systems]     # this systems block is exhaustive

    Merge stays the default because the SRH eval configs genuinely rely on it — they
    declare only their new arms and inherit `base`/`sft`/`cft` as references, and their
    published tables contain those arms. Changing the default would silently drop arms
    from every one of them.
    """
    p = Path(path)
    if not p.is_absolute():
        p = CONFIG_DIR / p
    if not p.exists():
        raise FileNotFoundError(f"config not found: {p}")
    with open(p) as f:
        cfg: dict[str, Any] = yaml.safe_load(f) or {}
    parent_rel = cfg.pop("_extends", None)
    replace = cfg.pop("_replace", None) or []
    if isinstance(replace, str):
        replace = [replace]
    replace_keys = set(replace)
    if parent_rel:
        parent = load_config((p.parent / parent_rel) if not Path(parent_rel).is_absolute() else parent_rel)
        cfg = _deep_merge(parent, cfg, replace_keys)
    elif replace_keys:
        raise ValueError(f"{p}: `_replace` is meaningless without `_extends`")
    cfg["_config_path"] = str(p)
    return cfg


def _deep_merge(base: dict[str, Any], override: dict[str, Any],
                replace: set[str] | None = None) -> dict[str, Any]:
    """Recursive dict merge, except for keys named in `replace`.

    `replace` applies only at THIS level — the level `_replace` is declared at, which is
    the top level of a config. A nested key of the same name is unaffected, so listing
    `systems` cannot reach into `engine.systems` and surprise someone.
    """
    replace = replace or set()
    out = dict(base)
    for k, v in override.items():
        if k in replace:
            out[k] = v  # exhaustive: the child's value stands alone
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def conditions() -> dict[str, Any]:
    """The condition ladder — single source of truth is configs/conditions.yaml."""
    return load_config("conditions.yaml")


DEFAULT_LAYER_FRACS = (0.14, 0.32, 0.50, 0.68, 0.82, 0.96)


def layer_indices_for(model_key: str, fracs=None) -> list[int]:
    """Probe depths as FRACTIONS of a model's depth, not absolute indices.

    `[4, 9, 14, 19, 23, 27]` is Qwen's 28 layers. Reusing those integers on CodeLlama-7b
    (32) or -13b (40) silently probes different RELATIVE depths, so RQ3, the alignment arm
    and the knockout/steering scripts would stop measuring the same thing across models
    while still producing plausible numbers. Everything that needs a layer set resolves it
    here so there is one definition rather than a copy per call site.
    """
    models = load_config("models.yaml")["models"]
    if model_key not in models:
        raise KeyError(f"unknown model key {model_key!r}")
    n = int(models[model_key]["n_layers"])
    out, seen = [], set()
    for f in (fracs or DEFAULT_LAYER_FRACS):
        i = min(n - 1, max(0, round(f * (n - 1))))
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out
