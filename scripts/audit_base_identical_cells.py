#!/usr/bin/env python
"""Find cells that are the BASE MODEL wearing another system's name.

    python scripts/audit_base_identical_cells.py

WHY. On 2026-09-12 forty cells labelled as four routing arms turned out to contain the untuned
model: `eval_vllm` has no mixture path, applied no adapter, and wrote them anyway. The failure was
invisible in every summary and obvious in one place -- the per-item correctness vector was
*identical* to the base cell's, which showed up downstream as a confidence interval of exactly zero
width. That is a signature, and it is cheap to look for everywhere.

THE TEST. For each (phase, model, language, condition) that has a `base` cell, compare every other
system's per-item correctness against it. Two different systems agreeing on every one of ~1,200
items is not a coincidence; it means no adapter was applied.

A near-identical cell is reported separately and is NOT an error: `formatonly` and some ICL arms are
*supposed* to sit close to base. Only exact identity over the whole vector is flagged.

KNOWN-BENIGN IDENTITY, and the reason this script reports rather than fails on principle. The three
`norm_*` arms (symbolic normalisation, `arch: none`) are identical to base on `L2` and ONLY on `L2`
-- 0.89 and 0.84 agreement on `L0` and `L1b`, exactly 1.00 on `L2`. That is correct behaviour: `L2`
is sequential minification, so a prompt-side normaliser has nothing left to rename and emits the
input unchanged. Identity that appears on ONE condition and not its siblings is a property of the
stimulus; identity across EVERY condition of an arm is a missing adapter. The routing failure was
the second kind.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT / "results" / "cells"


def vec(p: Path):
    try:
        df = pd.read_parquet(p, columns=["item_id", "correct"])
    except Exception:
        return None
    return df.sort_values("item_id")["correct"].to_numpy()


def main() -> int:
    groups: dict[tuple, dict[str, Path]] = {}
    for p in CELLS.rglob("trials.parquet"):
        rel = p.relative_to(CELLS).parts
        if len(rel) < 4:
            continue
        phase, model, lang, cell = rel[0], rel[1], rel[2], rel[3]
        system, _, cond = cell.rpartition("__")
        if not cond:
            continue
        groups.setdefault((phase, model, lang, cond), {})[system] = p

    flagged, near, checked = [], [], 0
    for key, sysmap in sorted(groups.items()):
        if "base" not in sysmap or len(sysmap) < 2:
            continue
        b = vec(sysmap["base"])
        if b is None:
            continue
        for s, p in sysmap.items():
            if s == "base":
                continue
            v = vec(p)
            if v is None or v.shape != b.shape:
                continue
            checked += 1
            agree = float((v == b).mean())
            if agree == 1.0:
                flagged.append((*key, s, len(b)))
            elif agree > 0.995:
                near.append((*key, s, agree))

    for phase, model, lang, cond, s, n in flagged:
        print(f"  IDENTICAL TO BASE  {phase}/{model}/{lang}  {s}__{cond}  ({n} items)")
    for phase, model, lang, cond, s, a in near:
        print(f"  near-identical ({a:.4f})  {phase}/{model}/{lang}  {s}__{cond}", file=sys.stderr)
    print(f"\n  {checked} non-base cells compared against their own base cell")
    print(f"  {len(flagged)} identical to base (an adapter was not applied)")
    print(f"  {len(near)} within 0.5% of base -- reported, not flagged; some arms belong there")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
