#!/usr/bin/env python
"""The backward (input-prediction) dissociation on stacked obfuscation, all eight models.

    python scripts/analysis/65_backward_stacks.py

WHY THIS EXISTS. The seven-model version of this table
(log/transfer/2026-09-14_backward-stacks-seven-models.md) was computed inline, one heredoc per
model, and its program sets were whatever each cell happened to contain. That is not reproducible
and it is not a paired comparison: the stacks containing the unseen family cover fewer programs
(X1 needs >= 3 sites), so pooling them against the seen stacks compares two different program sets
and calls the difference a drop. The numbers here SUPERSEDE that entry's; they move by a few points
and the ordering is unchanged.

WHAT THIS COMPUTES, per model and per system, on the programs common to EVERY cell of both groups:

    seen   = mean over the six depth-2 stacks built only from trained families
    unseen = mean over the three depth-2 stacks that contain X1
    drop   = 100 * (unseen - seen) / seen

and, for every system other than `base`, the DIFFERENCE of its drop against `base`'s on one
program-clustered bootstrap (2,000 resamples, seed 17), so "breadth falls further than the untuned
model" is an interval rather than two point estimates side by side.

The stack groups are exactly script 57's, so the forward and backward dissociations are read on the
same columns; the only change is the phase (inverse_generic) and the metric.

METRIC. `args_exact` -- the produced call must carry the gold arguments. The execution-graded
`correct` is reported beside it because inversion is many-to-one and a guess landing on a common
return value scores there: on CodeLlama-7B two thirds of the untuned model's backward "successes"
are of that kind, which is why the untuned model looks almost as good backwards as forwards.

FORMAT GATE. A system whose pooled format-failure rate exceeds 0.25 in either group is reported as
`gated` and excluded: its replies are mostly unparseable, so its accuracy measures the prompt
contract and not the task. The backward template was written for CodeLlama-7B.
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
SYSTEMS = ["base", "mono_all", "cons_lam3", "tuned_X1", "tuned_L0",
           "merge_dare_ties", "merge_ties"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
# Stacks only, and every stack cell was written with the one-shot inverse prompt, so this read is
# NOT affected by the zero-shot/one-shot split that contaminates the backward LADDER cells on the
# seven non-7B models (see configs/eval/inverse_ladder_1shot.yaml). inverse_1shot is listed first
# so that a future ladder variant of this script picks up the repaired cells automatically.
PHASES = ["inverse_1shot", "inverse_generic"]
FMT_GATE = 0.25
N_BOOT, SEED = 2000, 17


def read(model):
    """system -> group -> cond -> trials. A system missing any cell is dropped entirely."""
    out = {}
    for s in SYSTEMS:
        cells = {}
        ok = True
        for grp, conds in (("seen", SEEN), ("unseen", UNSEEN)):
            for c in conds:
                d = load_cell(PHASES, model, s, c)
                if d is None:
                    ok = False
                    break
                cells[(grp, c)] = d
            if not ok:
                break
        if ok:
            out[s] = cells
    return out


def common_programs(cells_by_system):
    sets = [set(d["snippet_id"]) for cells in cells_by_system.values() for d in cells.values()]
    return sorted(set.intersection(*sets)) if sets else []


def by_program(cells, progs, grp, conds, col):
    """program -> concatenated per-trial vector over the group's conditions."""
    out = {p: [] for p in progs}
    for c in conds:
        d = cells[(grp, c)]
        d = d[d["snippet_id"].isin(progs)]
        for p, g in d.groupby("snippet_id"):
            out[p].append(g[col].to_numpy(dtype=float))
    return {p: np.concatenate(v) for p, v in out.items()}


def drop(seen_map, unseen_map, progs):
    a = np.concatenate([seen_map[p] for p in progs]).mean()
    b = np.concatenate([unseen_map[p] for p in progs]).mean()
    if a <= 0:
        return None, float(a), float(b)
    return 100.0 * (b - a) / a, float(a), float(b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--metric", default="args_exact", choices=["args_exact", "correct"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    out = {"script": "65_backward_stacks.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "metric": a.metric, "n_resamples": N_BOOT, "seed": SEED, "format_gate": FMT_GATE,
           "groups": {"seen": SEEN, "unseen_containing": UNSEEN},
           "supersedes": "log/transfer/2026-09-14_backward-stacks-seven-models.md (ad-hoc, unpaired)",
           "models": {}}

    print(f"backward on stacks, metric={a.metric}: relative drop from SEEN stacks to "
          f"stacks containing the UNSEEN family\n")
    print(f"{'model':16s} {'n':>4s}  " + "  ".join(f"{s:>16s}" for s in SYSTEMS))
    rng_seed = SEED
    for m in MODELS:
        cells_by_system = read(m)
        if "base" not in cells_by_system:
            print(f"{m:16s}  (no untuned reference -- skipped)")
            continue
        progs = common_programs(cells_by_system)
        rec = {"n_programs": len(progs), "systems": {}}
        row = []
        # base first, and keep its per-program vectors for the paired bootstrap
        vecs = {}
        for s, cells in cells_by_system.items():
            fmt = max(
                float(pd.concat([cells[("seen", c)] for c in SEEN])["format_fail"].mean()),
                float(pd.concat([cells[("unseen", c)] for c in UNSEEN])["format_fail"].mean()),
            )
            sm = by_program(cells, progs, "seen", SEEN, a.metric)
            um = by_program(cells, progs, "unseen", UNSEEN, a.metric)
            d, sa, ua = drop(sm, um, progs)
            gated = fmt > FMT_GATE
            rec["systems"][s] = {"format_fail_max": round(fmt, 4), "gated": bool(gated),
                                 "seen_acc": round(sa, 4), "unseen_acc": round(ua, 4),
                                 "drop_pct": None if d is None else round(d, 2)}
            vecs[s] = (sm, um, gated, d)

        rng = np.random.default_rng(rng_seed)
        idx = np.arange(len(progs))
        picks = [rng.choice(idx, size=len(progs), replace=True) for _ in range(N_BOOT)]

        def boot_drop(sm, um, pick):
            aa = np.concatenate([sm[progs[j]] for j in pick]).mean()
            bb = np.concatenate([um[progs[j]] for j in pick]).mean()
            return np.nan if aa <= 0 else 100.0 * (bb - aa) / aa

        bsm, bum, bgated, bdrop = vecs["base"]
        base_draws = np.array([boot_drop(bsm, bum, p) for p in picks])
        # A gated untuned model is no reference at all: its drop is a drop in parse rate. The
        # other systems' levels still stand on their own, so they are printed WITHOUT a contrast.
        rec["base_gated"] = bool(bgated)
        for s in SYSTEMS:
            if s not in vecs:
                row.append(f"{'--':>16s}")
                continue
            sm, um, gated, d = vecs[s]
            if gated:
                row.append(f"{'gated':>16s}")
                continue
            if s == "base":
                row.append(f"{d:>+15.1f}%")
                continue

            if bgated:
                row.append(f"{d:>+15.1f}%")
                continue
            draws = np.array([boot_drop(sm, um, p) for p in picks]) - base_draws
            lo, hi = np.nanpercentile(draws, [2.5, 97.5])
            star = "*" if (lo > 0) == (hi > 0) else " "
            rec["systems"][s]["vs_base_pts"] = round(float(d - bdrop), 2)
            rec["systems"][s]["vs_base_ci"] = [round(float(lo), 2), round(float(hi), 2)]
            rec["systems"][s]["vs_base_sig"] = bool(star == "*")
            row.append(f"{d:>+14.1f}%{star}")
        print(f"{m:16s} {len(progs):4d}  " + "  ".join(row))
        out["models"][m] = rec

    print("\n* = the system's drop differs from the untuned model's, 95% program-clustered "
          "bootstrap on the difference.\n  `gated` = pooled format-failure rate > 0.25 in a group; "
          "`--` = a cell of the grid is missing.\n  Where the untuned model is itself gated "
          "(StarCoder2, Granite) no contrast is formed and no star can appear: the other systems' "
          "levels stand alone.")

    p = Path(a.out) if a.out else ROOT / "results/analysis/pipeline" / f"backward_stacks_{a.metric}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
