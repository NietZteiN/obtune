#!/usr/bin/env python
"""F1 — does inference-time ROUTING or weight MERGING compose on STACKED inputs?

    python scripts/analysis/56_f1_routing_merging.py

Applies the five rules pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-12, BEFORE the two eval
jobs were submitted. The rules are restated here verbatim and are not re-derived from the numbers.

WHY THE EXPERIMENT EXISTS. RQ1 claims routing and merging fail to compose. On this panel both were
measured on SINGLE transforms only, where the router is saturated -- 100 % route accuracy, gate
entropy ~1e-6 -- and beats a RANDOM gate by exactly +0.0000. A stacked input genuinely contains two
mechanisms, so a hard router must pick one and be wrong while a soft mixture can blend. That is the
condition the hypothesis predicts and it had never been evaluated.

GRID. Both configs set `eval_source: heldout` explicitly. The published single-transform routing
numbers sit on the 145-176-program `testset` grid, because `_base_eval.yaml` leaves the key unset
and the default is `testset` -- so any comparison against those numbers is ACROSS GRIDS and the
report says so rather than quietly lining them up.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402

MODEL = "codellama-7b"
PHASES = ["mole_generic", "composite_generic", "composite_depth"]
D2 = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
D34 = ["C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4"]
ALL = D2 + D34
N_BOOT, SEED, EQ = 2000, 17, 1.0

CONTRASTS = [
    ("mole_router - mole_random", "mole_router", "mole_random"),
    ("mole_router - mono_all", "mole_router", "mono_all"),
    ("mole_router - mole_uniform", "mole_router", "mole_uniform"),
    ("mole_uniform - base", "mole_uniform", "base"),
    ("mole_hardrouter - mole_router", "mole_hardrouter", "mole_router"),
    ("merge_ties - tuned_L0", "merge_ties", "tuned_L0"),
    ("merge_dare_ties - tuned_L0", "merge_dare_ties", "tuned_L0"),
    ("merge_dare_linear - tuned_L0", "merge_dare_linear", "tuned_L0"),
    ("l0merge_ties - tuned_L0", "l0merge_ties", "tuned_L0"),
    ("l0merge_dare_ties - tuned_L0", "l0merge_dare_ties", "tuned_L0"),
    ("mono_all - tuned_L0", "mono_all", "tuned_L0"),
]


def _by(df, keep):
    return {p: g["correct"].to_numpy(dtype=float)
            for p, g in df.groupby("snippet_id") if p in keep}


def pooled(cells, treat, control, conds, progs, eq=None):
    """acc(treat) - acc(control), pooled over `conds`, resampling PROGRAMS once across the level."""
    A = {c: _by(cells[(treat, c)], progs) for c in conds}
    B = {c: _by(cells[(control, c)], progs) for c in conds}
    P = sorted(progs)
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(P))

    def d(pick):
        a = np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0

    draws = np.array([d(rng.choice(idx, len(P), True)) for _ in range(N_BOOT)])
    pt = d(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    out = {"value_pts": pt, "ci_lo": lo, "ci_hi": hi, "n_programs": len(P),
           "excludes_zero": bool(lo > 0 or hi < 0)}
    if eq is not None:
        elo, ehi = (float(x) for x in np.percentile(draws, [5.0, 95.0]))
        out["equivalent"] = bool(elo > -eq and ehi < eq)
        out["eq_margin_pts"] = eq
    return out


def main() -> int:
    systems = sorted({s for _, t, c in CONTRASTS for s in (t, c)} | {"tuned_S1"})
    cells, missing = {}, []
    for cond in ALL:
        for s in systems:
            df = load_cell(PHASES, MODEL, s, cond)
            if df is None:
                missing.append(f"{s}__{cond}")
            else:
                cells[(s, cond)] = df
    if missing:
        print(f"grid incomplete -- {len(missing)} cell(s) missing, refusing to read:", file=sys.stderr)
        for m in missing[:12]:
            print("   ", m, file=sys.stderr)
        return 1

    progs = None
    for df in cells.values():
        s = set(df["snippet_id"])
        progs = s if progs is None else (progs & s)
    progs = sorted(progs)

    out = {"script": "56_f1_routing_merging.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "model": MODEL, "n_programs_common": len(progs), "n_resamples": N_BOOT, "seed": SEED,
           "grid": "heldout (NOT the testset grid the published single-transform routing numbers "
                   "sit on -- any comparison to those is across grids)",
           "by_level": {}}
    for lvl, cs in (("all_ten", ALL), ("depth2", D2), ("depth34", D34)):
        out["by_level"][lvl] = {
            lab: pooled(cells, t, c, cs, progs,
                        eq=EQ if lab == "mole_router - mole_random" else None)
            for lab, t, c in CONTRASTS}

    # H-F3-order: does stacking DESTROY a structural specialist's surface cue? `C_S1_L1r` renames
    # the `_st_` state variables S1 emits; `C_L1r_S1` leaves them intact. Paired by program.
    A = _by(cells[("tuned_S1", "C_L1r_S1")], progs); Ac = _by(cells[("tuned_L0", "C_L1r_S1")], progs)
    B = _by(cells[("tuned_S1", "C_S1_L1r")], progs); Bc = _by(cells[("tuned_L0", "C_S1_L1r")], progs)
    P = sorted(set(A) & set(Ac) & set(B) & set(Bc))
    rng = np.random.default_rng(SEED)

    def dd(pick):
        f = lambda X, Y: (np.concatenate([X[P[j]] for j in pick]).mean()
                          - np.concatenate([Y[P[j]] for j in pick]).mean()) * 100.0
        return f(A, Ac) - f(B, Bc)

    draws = np.array([dd(rng.choice(np.arange(len(P)), len(P), True)) for _ in range(N_BOOT)])
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    order = {"label": "tuned_S1 gain: cue-intact (C_L1r_S1) - cue-destroyed (C_S1_L1r)",
             "value_pts": dd(np.arange(len(P))), "ci_lo": lo, "ci_hi": hi,
             "n_programs": len(P), "excludes_zero": bool(lo > 0 or hi < 0)}
    out["order_test"] = order

    a = out["by_level"]["all_ten"]
    out["hypotheses"] = [
        {"id": "H-F1-route",
         "rule": "CONFIRMED iff mole_router - mole_random is TOST-equivalent at +/-1.0 pooled over "
                 "the ten composites; REFUTED iff ci_lo > +1.0",
         "verdict": ("REFUTED" if a["mole_router - mole_random"]["ci_lo"] > 1.0 else
                     "CONFIRMED" if a["mole_router - mole_random"].get("equivalent") else
                     "INCONCLUSIVE"),
         "evidence": a["mole_router - mole_random"]},
        {"id": "H-F1-route-vs-breadth",
         "rule": "CONFIRMED iff mole_router - mono_all pooled ci_hi < 0",
         "verdict": ("CONFIRMED" if a["mole_router - mono_all"]["ci_hi"] < 0 else
                     "REFUTED" if a["mole_router - mono_all"]["ci_lo"] > 0 else "INCONCLUSIVE"),
         "evidence": a["mole_router - mono_all"]},
        {"id": "H-F1-merge",
         "rule": "CONFIRMED iff merge_dare_ties - tuned_L0 pooled ci_hi <= 0",
         "verdict": ("CONFIRMED" if a["merge_dare_ties - tuned_L0"]["ci_hi"] <= 0 else
                     "REFUTED" if a["merge_dare_ties - tuned_L0"]["ci_lo"] > 0 else "INCONCLUSIVE"),
         "evidence": {k: a[k] for k in a if "merge" in k}},
        {"id": "H-F1-mixture", "rule": "descriptive: mole_uniform - base pooled",
         "verdict": "REPORTED", "evidence": a["mole_uniform - base"]},
        {"id": "H-F3-order",
         "rule": "CONFIRMED iff [tuned_S1 - tuned_L0 on C_L1r_S1] - [same on C_S1_L1r] ci_lo > 0",
         "verdict": ("CONFIRMED" if order["ci_lo"] > 0 else
                     "REFUTED" if order["ci_hi"] < 0 else "INCONCLUSIVE"),
         "evidence": order},
    ]

    dst = ROOT / "results/analysis/pipeline/f1_routing_merging_codellama7b.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))

    print(f"model {MODEL}   common subset {len(progs)} programs   grid: heldout\n")
    for lvl in ("all_ten", "depth2", "depth34"):
        print(f"--- {lvl} ---")
        for lab, _, _ in CONTRASTS:
            c = out["by_level"][lvl][lab]
            mark = "*" if c["excludes_zero"] else ("=" if c.get("equivalent") else " ")
            print(f"   {lab:32s} {c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{mark}")
        print()
    print(f"--- order test ---\n   {order['label']}\n   {order['value_pts']:+6.2f} "
          f"[{order['ci_lo']:+6.2f}, {order['ci_hi']:+6.2f}]"
          f"{'*' if order['excludes_zero'] else ''}  (n={order['n_programs']})\n")
    for h in out["hypotheses"]:
        print(f"{h['id']:24s} {h['verdict']}")
    print(f"\nwrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
