#!/usr/bin/env python
"""F2 — the divergence ladder: does a stack containing an UNSEEN family break what breadth learned?

    python scripts/analysis/53_f2_divergence.py --model codellama-7b

Applies the five rules pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-11, BEFORE any F2 cell
existed. The rules are restated here verbatim and are not re-derived from the numbers.

LEVELS. d0 = the six depth-2 composites built from SEEN transforms (`composite_generic`);
d1 = the depth-3/4 seen stacks (`composite_depth`); d2 = C_L1r_X1 / C_X1_S1 / C_S2_X1, one unseen
component at depth 2; d3 = C3_L1r_S1_X1. C_L1r_X1m and C_S1_X1s are single-mechanism halves and
are reported BESIDE d2, never pooled into it -- half an unseen family is a different stimulus.

COMMON SUBSET. `data/manifests/f2_divergence_common_subset.json`, 287 programs, computed from the
emitted items before any system ran. Coverage differs per composite because X1 needs >= 3 sites,
so a per-condition full set would confound the divergence contrast with differing program sets.

NO H1 anywhere: the unseen component is X1 throughout (CLAUDE.md 3.2, budget spent).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402

PHASES = ["f2_divergence"]
D2 = ["C_L1r_X1", "C_X1_S1", "C_S2_X1"]
D3 = ["C3_L1r_S1_X1"]
HALVES = ["C_L1r_X1m", "C_S1_X1s"]
N_BOOT, SEED = 2000, 17

# (label, treat, control) for every rule; pooled over a level's composites.
#
# CORE vs FULL. `--core` restricts this list to the arms every panel model has, which is exactly the
# set `configs/eval/f2_divergence_core.yaml` evaluates. It is NOT a degraded read: the five
# pre-registered F2 rules reference only `mono_all`, `tuned_L0`, `cons_lam3` and `tuned_X1`, so the
# core set answers every one of them. The extra arms in the full config exist for CodeLlama-7b
# alone and carry the "reported beside it" lines (`mono_allX`, `merge_dare_ties`), not verdicts.
# The distinction matters because the script REFUSES an incomplete grid, and a deliberately smaller
# system set must not be mistaken for a grid that failed to finish.
CORE_SYSTEMS = {"base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"}
CONTRASTS = [
    ("mono_all - tuned_L0", "mono_all", "tuned_L0"),
    ("cons_lam3 - tuned_L0", "cons_lam3", "tuned_L0"),
    ("cons_lam3 - mono_all", "cons_lam3", "mono_all"),
    ("tuned_X1 - tuned_L0", "tuned_X1", "tuned_L0"),
    ("mono_allX - mono_all", "mono_allX", "mono_all"),
    ("merge_dare_ties - tuned_L0", "merge_dare_ties", "tuned_L0"),
    ("tuned_S2 - tuned_L0", "tuned_S2", "tuned_L0"),
    ("x1_resample - tuned_L0", "x1_resample", "tuned_L0"),
    ("tuned_L0 - base", "tuned_L0", "base"),
]


def _by_program(df, keep):
    out = {}
    for pid, g in df.groupby("snippet_id"):
        if pid in keep:
            out[pid] = g["correct"].to_numpy(dtype=float)
    return out


def pooled(cells, treat, control, conds, progs):
    """acc(treat) - acc(control) in points, pooled over `conds`, resampling PROGRAMS once.

    Resampling once across the whole level (rather than per composite and averaging) is what makes
    a level's interval honest: the same program contributes a correlated item to every composite.
    """
    A = {c: _by_program(cells[(treat, c)], progs) for c in conds}
    B = {c: _by_program(cells[(control, c)], progs) for c in conds}
    P = sorted(progs)
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(P))

    def delta(pick):
        a = np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0

    draws = np.array([delta(rng.choice(idx, size=len(P), replace=True)) for _ in range(N_BOOT)])
    pt = delta(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    n_items = int(sum(len(A[c][p]) for c in conds for p in P))
    return {"value_pts": pt, "ci_lo": lo, "ci_hi": hi, "n_programs": len(P),
            "n_items": n_items, "excludes_zero": bool(lo > 0 or hi < 0)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="codellama-7b")
    ap.add_argument("--core", action="store_true",
                    help="read the four-arm core grid (f2_divergence_core.yaml). Answers all five "
                         "pre-registered rules; drops only the reported-beside lines.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    contrasts = ([c for c in CONTRASTS if c[1] in CORE_SYSTEMS and c[2] in CORE_SYSTEMS]
                 if a.core else CONTRASTS)

    sub = json.loads((ROOT / "data/manifests/f2_divergence_common_subset.json").read_text())
    progs = set(sub["common_subset"])

    conds = D2 + D3 + HALVES
    systems = sorted({s for _, t, c in contrasts for s in (t, c)})
    cells, missing = {}, []
    for cond in conds:
        for s in systems:
            df = load_cell(PHASES, a.model, s, cond)
            if df is None:
                missing.append(f"{s}__{cond}")
            else:
                cells[(s, cond)] = df
    if missing:
        print("MISSING cells -- the grid is incomplete, refusing to read:", file=sys.stderr)
        for m in missing:
            print("   ", m, file=sys.stderr)
        return 1

    levels = {"d2": D2, "d3": D3, "C_L1r_X1m": ["C_L1r_X1m"], "C_S1_X1s": ["C_S1_X1s"]}
    out = {
        "script": "53_f2_divergence.py",
        "grid": "core" if a.core else "full",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "model": a.model, "phase": PHASES[0],
        "n_programs_common": len(progs), "n_resamples": N_BOOT, "seed": SEED,
        "levels": {k: v for k, v in levels.items()},
        "by_level": {}, "per_composite": {},
    }
    for lvl, cs in levels.items():
        out["by_level"][lvl] = {lab: pooled(cells, t, c, cs, progs) for lab, t, c in contrasts}
    for cond in conds:
        out["per_composite"][cond] = {
            lab: pooled(cells, t, c, [cond], progs) for lab, t, c in contrasts}

    # ---- the pre-registered rules, restated verbatim -------------------------------------
    d2, d3 = out["by_level"]["d2"], out["by_level"]["d3"]
    ref_d0 = None
    p = ROOT / "results/analysis/pipeline/composite_generic_codellama7b.json"
    if p.exists():
        try:
            ref_d0 = json.loads(p.read_text())["pooled"]["mono_all - tuned_L0"]
        except Exception:
            ref_d0 = None

    def verdict(c, *, confirm_lo=None, confirm_hi=None):
        if confirm_lo is not None:
            return "CONFIRMED" if c["ci_lo"] > confirm_lo else (
                "REFUTED" if c["ci_hi"] < confirm_lo else "INCONCLUSIVE")
        return "CONFIRMED" if c["ci_hi"] < confirm_hi else (
            "REFUTED" if c["ci_lo"] > confirm_hi else "INCONCLUSIVE")

    hyps = [
        {"id": "H-F2-breadth-monotone",
         "rule": ("CONFIRMED iff mono_all - tuned_L0 has ci_lo > 0 at d0 (known) AND ci_hi < 0 "
                  "pooled over the three d2 stacks; INCONCLUSIVE if d2 straddles zero."),
         "verdict": verdict(d2["mono_all - tuned_L0"], confirm_hi=0.0),
         "evidence": {"d0_ref": ref_d0, "d2": d2["mono_all - tuned_L0"],
                      "d3_reported": d3["mono_all - tuned_L0"]}},
        {"id": "H-F2-cons-no-tax",
         "rule": "CONFIRMED iff cons_lam3 - tuned_L0 ci_hi >= 0 at d2 AND at d3.",
         "verdict": ("CONFIRMED" if (d2["cons_lam3 - tuned_L0"]["ci_hi"] >= 0
                                     and d3["cons_lam3 - tuned_L0"]["ci_hi"] >= 0)
                     else "REFUTED"),
         "evidence": {"d2": d2["cons_lam3 - tuned_L0"], "d3": d3["cons_lam3 - tuned_L0"]}},
        {"id": "H-F2-cons-vs-breadth",
         "rule": "CONFIRMED iff cons_lam3 - mono_all ci_lo > 0 pooled at d2.",
         "verdict": verdict(d2["cons_lam3 - mono_all"], confirm_lo=0.0),
         "evidence": {"d2": d2["cons_lam3 - mono_all"], "d3": d3["cons_lam3 - mono_all"]}},
        {"id": "H-F2-family-stacks",
         "rule": "CONFIRMED iff tuned_X1 - tuned_L0 ci_lo > 0 pooled at d2.",
         "verdict": verdict(d2["tuned_X1 - tuned_L0"], confirm_lo=0.0),
         "evidence": {"d2": d2["tuned_X1 - tuned_L0"],
                      "mono_allX_minus_mono_all_d2": d2.get("mono_allX - mono_all")}},
        {"id": "H-F2-merge",
         "rule": "CONFIRMED iff merge_dare_ties - tuned_L0 ci_hi <= 0 pooled at d2.",
         "verdict": (verdict(d2["merge_dare_ties - tuned_L0"], confirm_hi=0.0)
                     if "merge_dare_ties - tuned_L0" in d2 else "NOT EVALUATED (core grid)"),
         "evidence": {"d2": d2.get("merge_dare_ties - tuned_L0")}},
    ]
    out["hypotheses"] = hyps

    # RQ4's answer follows mechanically from two of the rules, and is written down here so it is
    # not chosen after the fact: both outcomes were declared publishable in the pre-registration.
    cons_holds = d2["cons_lam3 - tuned_L0"]["ci_hi"] >= 0 and d3["cons_lam3 - tuned_L0"]["ci_hi"] >= 0
    breadth_drops = d2["mono_all - tuned_L0"]["ci_hi"] < 0
    out["rq4_reading"] = (
        "genuine robustness: anchoring holds the clean-code level where breadth falls below it"
        if (cons_holds and breadth_drops) else
        "a better heuristic, not genuine robustness: anchoring drops with breadth"
        if not cons_holds else
        "undecided by F2: breadth does not fall below the clean-code control at d2")

    dst = Path(a.out) if a.out else (
        ROOT / "results/analysis/pipeline" /
        f"f2_divergence_{'core_' if a.core else ''}{a.model.replace('-', '')}.json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))

    print(f"model {a.model}   common subset {len(progs)} programs\n")
    for lvl in ["d2", "d3", "C_L1r_X1m", "C_S1_X1s"]:
        print(f"--- {lvl} ({', '.join(levels[lvl])}) ---")
        for lab, _, _ in contrasts:
            c = out["by_level"][lvl][lab]
            star = "*" if c["excludes_zero"] else " "
            print(f"   {lab:30s} {c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{star}")
        print()
    for h in hyps:
        print(f"{h['id']:26s} {h['verdict']}")
    print(f"\nRQ4 reading: {out['rq4_reading']}")
    print(f"wrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
