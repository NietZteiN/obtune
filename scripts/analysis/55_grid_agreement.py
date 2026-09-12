#!/usr/bin/env python
"""Does the uniform `panel_core` grid reproduce each incumbent's PUBLISHED R1-R3?

    python scripts/analysis/55_grid_agreement.py

WHY. The four new panel models were read through `panel_core`, a config written 2026-09-10, while
the four published models were read through `x1_generic` / `rq2_generic` / `objectives_scale`. The
09-11 four-model entry concluded that R1-R3 are MODEL-dependent. The competing explanation is that
they are GRID-dependent -- that the new config measures differently -- in which case that entry is
wrong. The incumbents settle it: their `tuned_L0`, `mono_all` and `cons_lam3` adapters are unchanged
since publication, so any difference between the two reads is the measurement, not the model.

This is the same instrument as `scripts/verify_migration.py`, which re-derived a published Grid-A
contrast to the decimal after the cluster move. Recompute a known number through a new path before
trusting the path on unknown numbers.

Run it as each incumbent's grid lands. A disagreement larger than the intervals is a FINDING, not a
formality, and blocks reading the eight models as one table.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402
from obtune.control_relative import bootstrap_delta  # noqa: E402

# Published values, from docs/RQ_SUMMARY.md and the entries it cites. Hard-coded DELIBERATELY:
# this script's whole purpose is to compare against a number fixed before the new grid existed, so
# reading it back out of a file the new grid could touch would defeat the check.
PUBLISHED = {
    "codellama-7b":  {"R1": -3.79, "R2": +4.59, "R3": -0.30},
    "codellama-13b": {"R1": -4.28, "R2": +3.95, "R3": -0.60},
    "codellama-34b": {"R1": -2.64, "R2": +3.38, "R3": +0.42},
    "llama31-8b":    {"R1": -2.88, "R2": +3.46, "R3": +0.00},
}
RULES = {
    "R1": ("mono_all", "tuned_L0", "X1"),
    "R2": ("cons_lam3", "mono_all", "X1"),
    "R3": ("cons_lam3", "tuned_L0", "L0"),
}
N_BOOT, SEED = 2000, 17


def main() -> int:
    out = {"script": "55_grid_agreement.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "phase": "panel_core", "n_resamples": N_BOOT, "seed": SEED,
           "published_source": "docs/RQ_SUMMARY.md (fixed before panel_core existed)",
           "models": {}}
    worst = 0.0
    print(f"{'model':16s} {'rule':4s} {'published':>10s} {'uniform grid':>24s} {'delta':>7s}  agree?")
    for model, pub in PUBLISHED.items():
        cells_dir = ROOT / "results/cells/panel_core" / model / "python"
        if not cells_dir.is_dir() or len(list(cells_dir.iterdir())) < 35:
            print(f"{model:16s} -- grid incomplete "
                  f"({len(list(cells_dir.iterdir())) if cells_dir.is_dir() else 0}/35), skipped")
            continue
        out["models"][model] = {}
        for rule, (treat, control, cond) in RULES.items():
            t = load_cell(["panel_core"], model, treat, cond)
            c = load_cell(["panel_core"], model, control, cond)
            if t is None or c is None:
                print(f"{model:16s} {rule:4s} MISSING CELL"); continue
            k = bootstrap_delta(t, c, f"{treat} - {control} @ {cond}",
                                n_resamples=N_BOOT, seed=SEED)
            d = abs(k.value_pts - pub[rule])
            worst = max(worst, d)
            # "Agree" means the published point lies INSIDE the new grid's interval. That is the
            # right test: it asks whether the two reads are statistically the same measurement,
            # not whether they round to the same number.
            inside = k.ci_lo <= pub[rule] <= k.ci_hi
            out["models"][model][rule] = {
                "published": pub[rule], "uniform": k.value_pts,
                "ci_lo": k.ci_lo, "ci_hi": k.ci_hi, "abs_delta": d,
                "published_inside_ci": bool(inside)}
            print(f"{model:16s} {rule:4s} {pub[rule]:+10.2f} "
                  f"{k.value_pts:+8.2f} [{k.ci_lo:+6.2f}, {k.ci_hi:+6.2f}] {d:7.2f}  "
                  f"{'yes' if inside else 'NO -- INVESTIGATE'}")
    out["max_abs_delta_pts"] = worst
    ok = all(r["published_inside_ci"] for m in out["models"].values() for r in m.values())
    out["verdict"] = ("the uniform grid reproduces every published value it was checked against"
                      if ok else
                      "AT LEAST ONE published value falls outside the uniform grid's interval")
    dst = ROOT / "results/analysis/pipeline/grid_agreement_panel_core.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(f"\nmodels checked: {len(out['models'])} of {len(PUBLISHED)}   "
          f"largest disagreement: {worst:.2f} pts")
    print(out["verdict"])
    print(f"wrote {dst.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
