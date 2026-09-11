#!/usr/bin/env python
"""Clean-code baseline per model, and every arm expressed as a percentage of it.

    python scripts/analysis/50_baseline_relative.py [--language python] [--json OUT]

WHY THIS VIEW. Accuracy deltas in points answer "did this arm beat that arm"; they do not answer
"how much of what obfuscation destroyed did we get back". The natural reference is the UNTUNED
model on UNOBFUSCATED code -- `base` @ `L0` -- because that is the model's own competence on the
task before either obfuscation or any intervention. Every other cell is then readable as a share
of it: 100 % means obfuscation has cost nothing relative to the untouched model, above 100 % means
the arm has surpassed what the model could do on clean code to begin with.

TWO REFERENCES ARE REPORTED, because they answer different questions and conflating them flatters
the method:
  * `base@L0`       -- the untouched model on clean code. The honest denominator for "how much did
                       we get back", since it involves no training at all.
  * `tuned_L0@L0`   -- a model tuned on clean code, read on clean code. The ceiling a
                       clean-code-only intervention reaches, and the control every obfuscation arm
                       in this project is measured against elsewhere.

A percentage is NOT a substitute for the paired contrast with its interval. Ratios of two noisy
means have wide and asymmetric error, and this script prints no interval on them; they are a
readability aid for the paper's narrative, and the verdicts stay with the bootstraps in
`RQ_SUMMARY.md`. That is why the raw accuracies are printed alongside.

Models are never compared across rows: a 7B and a 34B differ on everything, and the point of the
normalisation is to make each model's own recovery legible.
"""
from __future__ import annotations

import argparse, glob, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

LADDER = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
HELDOUT = "X1"


def load_cells(model: str, language: str, task: str = "forward") -> dict:
    """(system, condition) -> (n, accuracy) for ONE task direction.

    THE KEY MUST INCLUDE THE TASK. The inverse-task cells (`inverse_generic`, RQ5') carry the
    same (system, condition) names as the forward ones -- 56 such collisions exist for
    codellama-7b alone -- so a dict keyed on (system, condition) silently keeps whichever phase
    sorted last. The forward numbers happened to survive because `rq2_generic` sorts after
    `inverse_generic`, which is luck, not correctness: any system whose only forward cells live
    in a phase sorting earlier (`grid_rq1_7b`, `h1_codellama`, `basecheck`) would have had an
    inverse accuracy reported as a forward one.

    The direction is read from `prompt_id`, which the prompt builder stamps into every row
    (`inverse_*` for the value->call task), not from the phase name -- a phase is a batch label
    and a future config could mix.
    """
    import pandas as pd
    out = {}
    for p in sorted(glob.glob(f"results/cells/*/{model}/{language}/*/trials.parquet")):
        phase = p.split("/")[2]
        if phase.startswith("_"):          # quarantined cells are never read
            continue
        s, _, c = os.path.basename(os.path.dirname(p)).partition("__")
        df = pd.read_parquet(p, columns=["correct", "prompt_id"])
        if df.empty:
            continue
        is_inv = str(df["prompt_id"].iloc[0]).startswith("inverse")
        if (task == "inverse") != is_inv:
            continue
        out[(s, c)] = (len(df), float(df["correct"].mean()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--language", default="python")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--task", choices=["forward", "inverse"], default="forward",
                    help="which direction to report; the inverse task is RQ5', "
                         "program+value -> a call, graded by execution")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    models = a.models or sorted({p.split("/")[3] for p in glob.glob(f"results/cells/*/*/{a.language}/*/trials.parquet")})
    report = {}
    for m in models:
        cells = load_cells(m, a.language, a.task)
        base = cells.get(("base", "L0"))
        if not base:
            continue
        if base[1] <= 0:
            # A zero clean-code baseline makes every ratio undefined, and that is informative
            # rather than a nuisance: starcoder2-15b reads 0.0000 untuned because its chat
            # template asserts its own assistant persona and our instruction, demoted into the
            # user turn by `merged` rendering, loses. "% of baseline" cannot be computed for a
            # model whose baseline is the measurement failing, and printing inf would hide that.
            print(f"\n=== {m} ===")
            print(f"  NO USABLE CLEAN-CODE BASELINE: base@L0 = {base[1]:.4f} (n={base[0]}).")
            t = cells.get(("tuned_L0", "L0"))
            if t:
                print(f"  tuned_L0@L0 = {t[1]:.4f} — the model is capable; the UNTUNED read is what failed.")
            print("  Ratios are omitted. See docs/MODEL_AND_DATA_SELECTION.md §5b.")
            report[m] = {"base_L0": base[1], "n_base_L0": base[0],
                         "usable_baseline": False,
                         "tuned_L0_L0": cells.get(("tuned_L0", "L0"), (None, None))[1]}
            continue
        tuned = cells.get(("tuned_L0", "L0"))
        systems = sorted({s for s, _ in cells})
        conds = [c for c in LADDER + [HELDOUT] if any((s, c) in cells for s in systems)]
        report[m] = {"base_L0": base[1], "tuned_L0_L0": tuned[1] if tuned else None,
                     "n_base_L0": base[0], "usable_baseline": True, "cells": {}}
        print(f"\n=== {m} ===")
        print(f"  clean-code baseline  base@L0     = {base[1]:.4f}  (n={base[0]})")
        if tuned:
            print(f"  clean-code ceiling   tuned_L0@L0 = {tuned[1]:.4f}"
                  f"   ({tuned[1]/base[1]*100:6.1f} % of baseline)")
        hdr = "  " + f"{'system':14s}" + "".join(f"{c:>14s}" for c in conds)
        print(hdr); print("  " + "-" * (len(hdr) - 2))
        for s in systems:
            row = f"  {s:14s}"
            for c in conds:
                v = cells.get((s, c))
                row += f"{'':>14s}" if not v else f"{v[1]:6.4f} {v[1]/base[1]*100:5.1f}% "
                report[m]["cells"][f"{s}__{c}"] = None if not v else {
                    "acc": v[1], "n": v[0], "pct_of_base_L0": v[1] / base[1] * 100,
                    "pct_of_tuned_L0_L0": (v[1] / tuned[1] * 100) if tuned else None}
            print(row)
        print("  (each cell: accuracy, then % of that model's own base@L0)")

        # The headline: how far each arm claws back what obfuscation costs, in one number per arm.
        # Mean over the five OBFUSCATED ladder conditions -- L0 is excluded because it is the
        # reference, and including it would flatter every arm by folding the easy column in.
        obf = [c for c in LADDER if c != "L0"]
        print("\n  recovery, mean over the five obfuscated conditions (L0 excluded: it is the reference)")
        for s_ in systems:
            vals = [cells[(s_, c)][1] for c in obf if (s_, c) in cells]
            if len(vals) < len(obf):
                continue
            mean = sum(vals) / len(vals)
            x1 = cells.get((s_, HELDOUT))
            x1s = f"   X1 {x1[1]/base[1]*100:6.1f}%" if x1 else ""
            print(f"    {s_:16s} {mean:.4f}  {mean/base[1]*100:6.1f}% of clean-code baseline{x1s}")
            report[m]["cells"][f"{s_}__MEAN_OBF"] = {
                "acc": mean, "pct_of_base_L0": mean / base[1] * 100,
                "pct_of_tuned_L0_L0": (mean / tuned[1] * 100) if tuned else None}

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(report, indent=2))
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
