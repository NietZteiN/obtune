#!/usr/bin/env python
"""The paper's three main methods side by side, one table, both directions.

    python scripts/analysis/66_three_methods.py [--metric correct|args_exact]

WHY. The paper introduces and compares three ways of adapting a model to obfuscated code -- a
BREADTH-trained LoRA, a MERGE of per-type adapters, and a learned ROUTER over the same adapters --
and its argument is that an adaptation has to be tested in both directions. Those three have never
appeared in one table. RQ1's brittleness read covers breadth (script 57), the merge has its own
script (60, 62), and the router's numbers live in the mole grids; the backward half was breadth and
merge only until today. A reader deciding whether the three are the same finding or three different
findings cannot do it from four scripts with four program sets.

WHAT IS COMPUTED, per model and per method, on the programs common to EVERY cell of both groups and
of every method (so the four columns are paired, not merely adjacent):

    drop = 100 * (unseen_containing - seen) / seen

over the six depth-2 stacks built only from trained families against the three that contain X1 --
script 57's groups, so this is the same comparison the forward dissociation already reports, widened
from one method to three and from one direction to two. Every method's drop also gets a
program-clustered bootstrap (2,000 resamples, seed 17) on its DIFFERENCE from the untuned model's,
because the quantity the paper argues about is "does this method fall further than doing nothing",
and that is a difference of two small differences.

FORWARD and BACKWARD are separate reads of separate phases and are printed as two blocks. The
format gate (0.25) applies to both; a gated cell is not a competence number. Where the untuned model
is itself gated no contrast is formed at all -- a gated baseline is a parse rate, not a reference.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from cellkit import load_cell  # noqa: E402

SEEN = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
UNSEEN = ["C_L1r_X1", "C_X1_S1", "C_S2_X1"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]

# (column label, cell system name, forward phases). Backward is always inverse_generic.
METHODS = [
    ("base",    "base",            ["composite_generic", "f2_divergence", "panel_core"]),
    ("breadth", "mono_all",        ["composite_generic", "f2_divergence"]),
    ("merge",   "merge_dare_ties", ["merge_panel", "rq2_generic", "composite_generic", "f2_divergence"]),
    ("router",  "mole_router",     ["mole_generic"]),
]
FMT_GATE = 0.25
N_BOOT, SEED = 2000, 17


def read(model, direction):
    out = {}
    for label, sysn, fwd_phases in METHODS:
        phases = ["inverse_generic"] if direction == "backward" else fwd_phases
        cells, ok = {}, True
        for grp, conds in (("seen", SEEN), ("unseen", UNSEEN)):
            for c in conds:
                d = load_cell(phases, model, sysn, c)
                if d is None:
                    ok = False
                    break
                cells[(grp, c)] = d
            if not ok:
                break
        if ok:
            out[label] = cells
    return out


def vectors(cells, progs, grp, conds, col):
    acc = {p: [] for p in progs}
    for c in conds:
        d = cells[(grp, c)]
        d = d[d["snippet_id"].isin(progs)]
        for p, g in d.groupby("snippet_id"):
            acc[p].append(g[col].to_numpy(dtype=float))
    return {p: np.concatenate(v) for p, v in acc.items()}


def block(model, direction, metric, out):
    cells_by = read(model, direction)
    if "base" not in cells_by:
        return f"{model:16s}  (no untuned reference in {direction})"
    sets = [set(d["snippet_id"]) for cells in cells_by.values() for d in cells.values()]
    progs = sorted(set.intersection(*sets))
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(progs))
    picks = [rng.choice(idx, size=len(progs), replace=True) for _ in range(N_BOOT)]

    def drop_draws(sm, um):
        def one(pick):
            a = np.concatenate([sm[progs[j]] for j in pick]).mean()
            b = np.concatenate([um[progs[j]] for j in pick]).mean()
            return np.nan if a <= 0 else 100.0 * (b - a) / a
        return np.array([one(p) for p in picks])

    info, cols = {}, []
    for label, _, _ in METHODS:
        if label not in cells_by:
            info[label] = None
            continue
        cells = cells_by[label]
        fmt = max(float(pd.concat([cells[("seen", c)] for c in SEEN])["format_fail"].mean()),
                  float(pd.concat([cells[("unseen", c)] for c in UNSEEN])["format_fail"].mean()))
        sm = vectors(cells, progs, "seen", SEEN, metric)
        um = vectors(cells, progs, "unseen", UNSEEN, metric)
        a = np.concatenate([sm[p] for p in progs]).mean()
        b = np.concatenate([um[p] for p in progs]).mean()
        d = None if a <= 0 else 100.0 * (b - a) / a
        info[label] = {"gated": fmt > FMT_GATE, "fmt": round(fmt, 4), "seen": round(float(a), 4),
                       "unseen": round(float(b), 4), "drop": None if d is None else round(d, 2),
                       "_sm": sm, "_um": um}

    bi = info["base"]
    base_draws = None if bi is None or bi["gated"] else drop_draws(bi["_sm"], bi["_um"])
    for label, _, _ in METHODS:
        r = info[label]
        if r is None:
            cols.append(f"{'--':>15s}")
            continue
        if r["gated"]:
            cols.append(f"{'gated':>15s}")
            continue
        if label == "base" or base_draws is None:
            cols.append(f"{r['drop']:>+14.1f}%")
            continue
        dd = drop_draws(r["_sm"], r["_um"]) - base_draws
        lo, hi = np.nanpercentile(dd, [2.5, 97.5])
        star = "*" if (lo > 0) == (hi > 0) else " "
        r["vs_base_pts"] = round(float(r["drop"] - bi["drop"]), 2)
        r["vs_base_ci"] = [round(float(lo), 2), round(float(hi), 2)]
        r["vs_base_sig"] = star == "*"
        cols.append(f"{r['drop']:>+13.1f}%{star}")
    for r in info.values():
        if r:
            r.pop("_sm", None); r.pop("_um", None)
    out.setdefault(model, {})[direction] = {"n_programs": len(progs), "methods": info}
    return f"{model:16s} {len(progs):4d}  " + "  ".join(cols)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metric", default=None,
                    help="forward is always `correct`; backward defaults to args_exact. "
                         "Pass a name to force both.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    res = {"script": "66_three_methods.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "n_resamples": N_BOOT, "seed": SEED, "format_gate": FMT_GATE,
           "groups": {"seen": SEEN, "unseen_containing": UNSEEN},
           "methods": [m[0] for m in METHODS], "models": {}}
    hdr = f"{'model':16s} {'n':>4s}  " + "  ".join(f"{m[0]:>15s}" for m in METHODS)
    for direction, default_metric in (("forward", "correct"), ("backward", "args_exact")):
        metric = a.metric or default_metric
        print(f"\n=== {direction.upper()} ({metric}) — relative drop, SEEN stacks → "
              f"stacks containing the UNSEEN family ===\n")
        print(hdr)
        for m in MODELS:
            print(block(m, direction, metric, res["models"]))
    print("\n* = differs from the untuned model's drop, 95% program-clustered bootstrap on the "
          "difference.\n  `gated` = format-failure rate > 0.25; `--` = the method has no cells "
          "for this model and direction.")
    p = Path(a.out) if a.out else ROOT / "results/analysis/pipeline/three_methods.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=2) + "\n")
    print(f"  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
