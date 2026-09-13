#!/usr/bin/env python
"""Validate every committed eval config against what the runner actually accepts.

    python scripts/validate_eval_configs.py            # all configs
    python scripts/validate_eval_configs.py --model codellama-7b   # also resolve adapter paths

WHY THIS EXISTS, and it is a process finding as much as a script. Three configs in one day passed
every check that existed and failed at run time, each on a DIFFERENT key:

  * `phase:` not in `TrialRow.phase`      -- caught only after a full generation pass (4 jobs, 3 days)
  * `adapter:` ending in `best/` for a MERGE, which has no checkpoints -- would have scored the BASE
    model under the merge's name, silently, with the only trace a string in metadata no analysis reads
  * `task: inverse`, the experiment's name rather than the `output|input` the runner takes -- queued
    across seven models before the first failed

Each fix afterwards was narrower than the fault class: a phase check, an adapter-existence check, a
task check. The pattern is that validation here is a pile of spot checks rather than a schema, so a
new key is validated only after it has broken something. This is the schema.

It checks CONSISTENCY, not taste: every rule below corresponds to a line in `eval_vllm.py` or
`schema.py` that raises or silently misbehaves. Unknown top-level keys are reported as warnings
rather than errors, because configs legitimately carry documentation keys the runner ignores.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import get_args

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import load_config          # noqa: E402
from obtune.schema import AnyCondition, TierICSE, TrialRow  # noqa: E402

# `arch` values the runner branches on, plus the families it matches by prefix. Anything else is
# accepted by `expand_systems` and then behaves as a plain adapter, which is usually what was meant
# -- so an unknown arch is a WARNING, while a misspelt *known* family (e.g. "moe_router") is not
# distinguishable from a new one and is left to the reader.
ARCH_EXACT = {"none", "per_type", "mono", "router", "oracle_route", "oracle_prompt",
              "mole_router", "mole_hardrouter", "mole_uniform", "mole_random",
              "invariance", "invariance_mismatch"}
ARCH_PREFIX = ("merge", "obj_")
VALID_TASKS = {"output", "input"}
PHASES = set(get_args(TrialRow.model_fields["phase"].annotation))
CONDS = set(get_args(AnyCondition.__args__[0])) | set(get_args(AnyCondition.__args__[1]))
TIERS = {f"T_{t}" for t in get_args(TierICSE)}


def check(path: Path, model: str | None) -> tuple[list[str], list[str]]:
    errs: list[str] = []
    warns: list[str] = []
    rel = path.relative_to(ROOT)
    try:
        cfg = load_config(f"eval/{path.name}")
    except Exception as e:                                    # noqa: BLE001
        return [f"{rel}: does not load: {e}"], []

    # 1. phase must be a literal TrialRow accepts, or every row fails AFTER generation.
    ph = cfg.get("phase")
    if ph is not None and ph not in PHASES:
        errs.append(f"{rel}: phase={ph!r} is not in TrialRow.phase -- rows would fail after a full "
                    f"generation pass")

    # 2. task names the prediction DIRECTION.
    tk = cfg.get("task")
    if tk is not None and tk not in VALID_TASKS:
        errs.append(f"{rel}: task={tk!r}, must be one of {sorted(VALID_TASKS)}")

    # 3. conditions must be known codes.
    for c in cfg.get("eval_conditions") or []:
        if c not in CONDS and c not in TIERS:
            errs.append(f"{rel}: eval_condition {c!r} is not a known condition code")

    # 4. H1 may never appear in an input-prediction grid, and never in a NEW grid at all
    #    (CLAUDE.md 3.2 rule 3: the budget is spent).
    if "H1" in (cfg.get("eval_conditions") or []):
        warns.append(f"{rel}: reads H1 -- its two-read budget is spent; a re-tabulation of existing "
                     f"cells is fine, a new grid is not")

    # 5. systems
    seen: set[str] = set()
    for s in cfg.get("systems") or []:
        nm = s.get("name")
        if not nm:
            errs.append(f"{rel}: a system has no name"); continue
        if nm in seen:
            errs.append(f"{rel}: duplicate system name {nm!r} -- cells key on it and would collide")
        seen.add(nm)
        arch = s.get("arch", "none")
        # A MIXTURE CONFIG MUST NOT BE RUN THROUGH vLLM. That engine has no mixture path and, until
        # 2026-09-12, accepted these arches and wrote the BASE model under the arm's name -- 40
        # cells, and an analysis that read the resulting zero-width interval as CONFIRMED.
        if arch.startswith("mole_"):
            warns.append(f"{rel}: system {nm!r} is a mixture arch ({arch}) -- this config must be "
                         f"run with `python -m obtune.mole.eval_mole`, NOT obtune.eval_vllm, which "
                         f"would silently evaluate the base model")
        if arch not in ARCH_EXACT and not arch.startswith(ARCH_PREFIX):
            warns.append(f"{rel}: system {nm!r} has arch={arch!r}, which the runner does not branch "
                         f"on -- it will behave as a plain adapter")
        a = s.get("adapter")
        if arch == "none" and a:
            warns.append(f"{rel}: system {nm!r} is arch=none but names an adapter -- it will be ignored")
        if a and arch != "none":
            # A MERGE HAS NO `best/`: no training run, no checkpoints, weights at the directory.
            leaf_is_best = a.rstrip("/").endswith("/best")
            looks_merged = "merge" in a
            if looks_merged and leaf_is_best:
                errs.append(f"{rel}: system {nm!r} points at {a!r} -- a merge has no 'best/' "
                            f"subdirectory; this resolves to nothing and would score the BASE model "
                            f"under this system's name")
            if model and "{model}" in a:
                q = ROOT / a.format(model=model, language=cfg.get("language", "python"))
                if not (q / "adapter_model.safetensors").exists() and not (q / "adapter_model.bin").exists():
                    errs.append(f"{rel}: system {nm!r} has no weights at {q.relative_to(ROOT)} "
                                f"(model={model})")
    if not seen:
        errs.append(f"{rel}: no systems")
    return errs, warns


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="also resolve {model} adapter paths against this model key")
    ap.add_argument("--quiet-warnings", action="store_true")
    a = ap.parse_args()
    E, W, n = [], [], 0
    for p in sorted((ROOT / "configs" / "eval").glob("*.yaml")):
        if p.name.startswith("_"):
            continue
        n += 1
        e, w = check(p, a.model)
        E += e; W += w
    for w in W:
        if not a.quiet_warnings:
            print(f"  warn  {w}")
    for e in E:
        print(f"  ERROR {e}", file=sys.stderr)
    print(f"\n{n} configs checked: {len(E)} error(s), {len(W)} warning(s)")
    return 1 if E else 0


if __name__ == "__main__":
    raise SystemExit(main())
