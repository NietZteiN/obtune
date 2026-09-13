#!/usr/bin/env python
"""H-F2-route — inference-time ROUTING on stacks that contain an UNSEEN family (CodeLlama-7B).
    python scripts/analysis/61_f2_route.py
Applies the rule pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-13 BEFORE submission, restated verbatim:
  On the four fully-unseen-containing stacks (C_L1r_X1, C_X1_S1, C_S2_X1, C3_L1r_S1_X1), pooled:
  - CONFIRMED ("routing inherits breadth's unseen failure") iff mole_router - mono_all is TOST-equivalent at
    +/-1.5 pts AND mole_router - tuned_L0 ci_hi < 0.
  - REFUTED ("routing composes where breadth does not") iff mole_router - tuned_L0 ci_lo > 0.
  - otherwise INCONCLUSIVE. mole_router - mole_random, mole_router - cons_lam3 and the two half-unseen stacks
    are REPORTED.
Routing arms come from mole_generic (obtune.mole.eval_mole); the controls from f2_divergence on the same items.
"""
from __future__ import annotations
import datetime as dt, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis")); sys.path.insert(0, str(ROOT / "src"))
from cellkit import load_cell  # noqa: E402
MODEL = "codellama-7b"; PH_R = ["mole_generic"]; PH_C = ["f2_divergence"]
UNSEEN4 = ["C_L1r_X1", "C_X1_S1", "C_S2_X1", "C3_L1r_S1_X1"]; HALVES = ["C_L1r_X1m", "C_S1_X1s"]
ROUTE = ["mole_router", "mole_hardrouter", "mole_uniform", "mole_random"]
N_BOOT, SEED, EQ = 2000, 17, 1.5

def _by(df, keep):
    return {p: g["correct"].to_numpy(dtype=float) for p, g in df.groupby("snippet_id") if p in keep}

def pooled(cells, treat, control, conds, progs, eq=None):
    A = {c: _by(cells[(treat, c)], progs) for c in conds}; B = {c: _by(cells[(control, c)], progs) for c in conds}
    P = sorted(progs); rng = np.random.default_rng(SEED); idx = np.arange(len(P))
    def d(pick):
        a = np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0
    draws = np.array([d(rng.choice(idx, len(P), True)) for _ in range(N_BOOT)]); pt = d(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    out = {"value_pts": float(pt), "ci_lo": lo, "ci_hi": hi, "n_programs": len(P), "excludes_zero": bool(lo > 0 or hi < 0)}
    if eq is not None:
        elo, ehi = (float(x) for x in np.percentile(draws, [5.0, 95.0]))
        out["equivalent"] = bool(elo > -eq and ehi < eq); out["eq_margin_pts"] = eq
    return out

def s(c): return f"{c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{'*' if c['excludes_zero'] else ' '}"

def main():
    cells, missing = {}, []
    for c in UNSEEN4 + HALVES:
        for sy, ph in [(r, PH_R) for r in ROUTE + ["base"]] + [(k, PH_C) for k in ("tuned_L0", "mono_all", "cons_lam3")]:
            df = load_cell(ph, MODEL, sy, c)
            if df is None: missing.append(f"{sy}__{c}")
            else: cells[(sy, c)] = df
    if missing:
        print(f"grid incomplete -- {len(missing)} cell(s) missing, refusing to read: {missing[:8]}", file=sys.stderr); return 1
    out = {"script": "61_f2_route.py", "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "model": MODEL, "n_resamples": N_BOOT, "seed": SEED, "by_level": {}}
    CON = [("mole_router - mono_all", "mole_router", "mono_all"), ("mole_router - tuned_L0", "mole_router", "tuned_L0"),
           ("mole_router - mole_random", "mole_router", "mole_random"), ("mole_router - mole_uniform", "mole_router", "mole_uniform"),
           ("mole_hardrouter - mole_router", "mole_hardrouter", "mole_router"), ("mole_router - cons_lam3", "mole_router", "cons_lam3"),
           ("mole_uniform - base", "mole_uniform", "base"), ("mono_all - tuned_L0", "mono_all", "tuned_L0"), ("cons_lam3 - tuned_L0", "cons_lam3", "tuned_L0")]
    for lvl, conds in (("unseen4", UNSEEN4), ("halves", HALVES)):
        progs = None
        for key in [(sy, c) for sy in ROUTE + ["base", "tuned_L0", "mono_all", "cons_lam3"] for c in conds]:
            ss = set(cells[key]["snippet_id"]); progs = ss if progs is None else progs & ss
        blk = {lab: pooled(cells, t, k, conds, progs, eq=EQ if lab == "mole_router - mono_all" else None) for lab, t, k in CON}
        blk["_n_programs"] = len(progs); out["by_level"][lvl] = blk
        print(f"--- {lvl} ({len(progs)} programs) ---")
        for k, v in blk.items():
            if not k.startswith("_"): print(f"   {k:32s} {s(v)}" + ("  [TOST equiv]" if v.get("equivalent") else ""))
    a = out["by_level"]["unseen4"]; rm, rt = a["mole_router - mono_all"], a["mole_router - tuned_L0"]
    verdict = ("REFUTED" if rt["ci_lo"] > 0 else "CONFIRMED" if (rm.get("equivalent") and rt["ci_hi"] < 0) else "INCONCLUSIVE")
    out["hypotheses"] = [{"id": "H-F2-route",
        "rule": "CONFIRMED iff mole_router - mono_all TOST-equivalent at +/-1.5 AND mole_router - tuned_L0 ci_hi < 0 on the four "
                "unseen-containing stacks pooled; REFUTED iff mole_router - tuned_L0 ci_lo > 0; else INCONCLUSIVE",
        "verdict": verdict, "evidence": {"mole_router - mono_all": rm, "mole_router - tuned_L0": rt}}]
    print(f"H-F2-route  {verdict}")
    p = ROOT / "results/analysis/pipeline/f2_route_codellama7b.json"; p.write_text(json.dumps(out, indent=1)); print("wrote", p.relative_to(ROOT)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
