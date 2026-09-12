#!/usr/bin/env python
"""The direction ratio: how much of a forward gain survives the task being run backwards?

    python scripts/analysis/58_direction_ratio.py

WHY THIS IS THE PAPER'S SPINE (docs/PAPER_REORG.md). Adaptation to obfuscated code can raise
forward accuracy two ways: by teaching the model to READ the program better, or by teaching it the
forward task's surface -- what an answer looks like, which tokens carry a value. Only the first
should survive asking the same programs backwards (given a return value, produce a call yielding
it). No adapter is trained on the inverse task, so any inverse gain is transferred program
understanding rather than task fitting.

    DR(arm) = [inverse acc(arm) - inverse acc(base)] / [forward acc(arm) - forward acc(base)]

DR < 0 means the arm bought forward accuracy by LOSING backward competence. DR ~ 0 means the
forward gain cost nothing backwards. DR > 0 means it gained in both directions.

Both halves are on the same six seen conditions and the same programs. The ratio is descriptive and
is reported with its two components, never alone: a ratio of small differences is unstable, and the
components are what a reader should check.
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
SEEN = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
FWD_PHASES = ["rq2_generic", "x1_generic", "panel_core", "main"]
INV_PHASES = ["inverse_generic"]
ARMS = ["formatonly", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]
N_BOOT, SEED = 2000, 17


def pooled_acc(phases, system, conds, progs=None):
    """Mean accuracy over `conds`, and the per-program arrays for bootstrapping."""
    by = {}
    for c in conds:
        d = load_cell(phases, MODEL, system, c)
        if d is None:
            return None, None
        for p, g in d.groupby("snippet_id"):
            if progs is None or p in progs:
                by.setdefault(p, []).append(g["correct"].to_numpy(dtype=float))
    if not by:
        return None, None
    flat = {p: np.concatenate(v) for p, v in by.items()}
    return float(np.concatenate(list(flat.values())).mean()), flat


def main() -> int:
    # One program set for every cell in both directions, so the two halves are comparable.
    progs = None
    for phases in (FWD_PHASES, INV_PHASES):
        for s in ["base"] + ARMS:
            for c in SEEN:
                d = load_cell(phases, MODEL, s, c)
                if d is None:
                    continue
                st = set(d["snippet_id"])
                progs = st if progs is None else (progs & st)
    if not progs:
        print("no common program set", file=sys.stderr)
        return 1

    out = {"script": "58_direction_ratio.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "model": MODEL, "conditions": SEEN, "n_programs": len(progs),
           "n_resamples": N_BOOT, "seed": SEED, "arms": {}}

    fb, fbp = pooled_acc(FWD_PHASES, "base", SEEN, progs)
    ib, ibp = pooled_acc(INV_PHASES, "base", SEEN, progs)
    if fb is None or ib is None:
        print("missing base cells", file=sys.stderr)
        return 1
    P = sorted(progs)
    rng = np.random.default_rng(SEED)
    picks = [rng.choice(np.arange(len(P)), len(P), True) for _ in range(N_BOOT)]

    def boot(armp, basep):
        d = np.empty(N_BOOT)
        for i, pk in enumerate(picks):
            a = np.concatenate([armp[P[j]] for j in pk])
            b = np.concatenate([basep[P[j]] for j in pk])
            d[i] = (a.mean() - b.mean()) * 100.0
        return d

    print(f"model {MODEL}   {len(P)} programs   conditions {','.join(SEEN)}\n")
    print(f"{'arm':14s}{'forward gain':>22s}{'backward gain':>22s}{'DR':>8s}")
    for a in ARMS:
        fa, fap = pooled_acc(FWD_PHASES, a, SEEN, progs)
        ia, iap = pooled_acc(INV_PHASES, a, SEEN, progs)
        if fa is None or ia is None:
            print(f"  {a:12s} (missing cells)")
            continue
        fd, idd = boot(fap, fbp), boot(iap, ibp)
        fg, ig = (fa - fb) * 100, (ia - ib) * 100
        dr = ig / fg if abs(fg) > 1e-9 else float("nan")
        ci = lambda d: (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)))
        flo, fhi = ci(fd); ilo, ihi = ci(idd)
        out["arms"][a] = {
            "forward": {"value_pts": fg, "ci_lo": flo, "ci_hi": fhi,
                        "excludes_zero": bool(flo > 0 or fhi < 0)},
            "backward": {"value_pts": ig, "ci_lo": ilo, "ci_hi": ihi,
                         "excludes_zero": bool(ilo > 0 or ihi < 0)},
            "direction_ratio": dr}
        s = lambda v, l, h: f"{v:+6.2f} [{l:+6.2f},{h:+6.2f}]"
        print(f"  {a:12s}{s(fg,flo,fhi):>22s}{s(ig,ilo,ihi):>22s}{dr:+8.2f}")
    neg = [a for a, v in out["arms"].items() if v["direction_ratio"] < 0]
    out["reading"] = (f"{len(neg)} of {len(out['arms'])} arms have a NEGATIVE direction ratio "
                      f"({', '.join(neg)}): they bought forward accuracy by losing backward "
                      f"competence. A ratio is a ratio of small differences and is reported with "
                      f"its components, never alone.")
    print(f"\n  {out['reading']}")
    dst = ROOT / "results/analysis/pipeline/direction_ratio_codellama7b.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(f"  wrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
