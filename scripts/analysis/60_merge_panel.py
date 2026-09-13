#!/usr/bin/env python
"""H-merge-panel — weight-space merging on the panel models (Granite, Llama-3.1-8B, StarCoder2).
    python scripts/analysis/60_merge_panel.py [model ...]
Applies the two rules pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-13 BEFORE submission, per model:
  a. "merging does not beat the clean control on seen stacks": CONFIRMED iff best-of-three merge − tuned_L0,
     pooled over the six depth-2 seen stacks, has ci_hi <= +1.0; REFUTED iff ci_lo > +1.0.
  b. "merging stays below breadth": CONFIRMED iff best merge − mono_all pooled over the same stacks has
     ci_hi < 0; REFUTED iff ci_lo > 0.
"Best of three" is chosen by point estimate on the same stacks it is tested on, which biases toward the
merge, so the CONFIRMED direction is conservative. Unseen stacks and the ladder are REPORTED only.
Merges and the untuned model come from `merge_panel`; the controls from composite_generic / f2_divergence /
panel_core on the same held-out items. Every level is read on the programs common to every cell it uses.
"""
from __future__ import annotations
import datetime as dt, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis")); sys.path.insert(0, str(ROOT / "src"))
from cellkit import load_cell  # noqa: E402
MODELS = sys.argv[1:] or ["codellama-7b", "granite31-8b", "llama31-8b", "starcoder2-15b"]
# CodeLlama-7B's merges predate merge_panel: ladder in rq2_generic, seen stacks in composite_generic,
# unseen stacks in f2_divergence (DARE-TIES only there, so its other two merges have no unseen cells).
PH_M_BY = {"codellama-7b": ["rq2_generic", "composite_generic", "f2_divergence"]}
PH_C = ["composite_generic", "f2_divergence", "panel_core"]
MERGES = ["merge_ties", "merge_dare_ties", "merge_dare_linear"]
SEEN6 = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
UNSEEN4 = ["C_L1r_X1", "C_X1_S1", "C_S2_X1", "C3_L1r_S1_X1"]
LADDER = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
N_BOOT, SEED, FMT_MAX = 2000, 17, 0.25

def _by(df, keep):
    return {p: g["correct"].to_numpy(dtype=float) for p, g in df.groupby("snippet_id") if p in keep}

def pooled(cells, treat, control, conds, progs):
    A = {c: _by(cells[(treat, c)], progs) for c in conds}; B = {c: _by(cells[(control, c)], progs) for c in conds}
    P = sorted(progs); rng = np.random.default_rng(SEED); idx = np.arange(len(P))
    def d(pick):
        a = np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0
    draws = np.array([d(rng.choice(idx, len(P), True)) for _ in range(N_BOOT)]); pt = d(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    return {"value_pts": float(pt), "ci_lo": lo, "ci_hi": hi, "n_programs": len(P), "excludes_zero": bool(lo > 0 or hi < 0)}

def fmt_rate(df):
    if "format_ok" in df: return float(1.0 - df["format_ok"].mean())
    if "format_fail" in df: return float(df["format_fail"].mean())
    return None

def s(c): return f"{c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{'*' if c['excludes_zero'] else ' '}"

def run(model):
    PH_M = PH_M_BY.get(model, ["merge_panel"])
    merges = [m for m in MERGES if model != "codellama-7b" or m == "merge_dare_ties"]
    LEVELS = (("seen6", SEEN6), ("unseen4", UNSEEN4), ("ladder", LADDER), ("X1", ["X1"]))
    cells, skipped = {}, {}
    for lvl, conds in LEVELS:
        missing = []
        for sysn, c, ph in ([(m, c, PH_M) for m in merges + ["base"] for c in conds]
                            + [(ctl, c, PH_C) for ctl in ("tuned_L0", "mono_all", "cons_lam3") for c in conds]):
            if (sysn, c) in cells: continue
            df = load_cell(ph, model, sysn, c)
            if df is None: missing.append(f"{sysn}__{c}")
            else: cells[(sysn, c)] = df
        if missing: skipped[lvl] = missing
    # A level with a missing cell is SKIPPED and named, not read on a partial grid. CodeLlama-7B has no
    # merge cell on single X1 (its merges predate the X1 family), so its X1 level is absent, and the
    # registered rules only need seen6.
    if "seen6" in skipped:
        print(f"{model}: seen6 incomplete -- refusing to read: {skipped['seen6'][:8]}", file=sys.stderr); return None
    LEVELS = tuple((l, c) for l, c in LEVELS if l not in skipped)
    if skipped: print(f"{model}: skipped levels {list(skipped)} (missing e.g. {[v[0] for v in skipped.values()]})")
    out = {"script": "60_merge_panel.py", "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "model": model, "n_resamples": N_BOOT, "seed": SEED, "by_level": {}, "format_fail": {}}
    for m in merges:
        out["format_fail"][m] = {c: fmt_rate(cells[(m, c)]) for c in SEEN6 + UNSEEN4 + LADDER + ["X1"] if (m, c) in cells}
    print(f"\n=== {model} ===")
    out["skipped_levels"] = skipped
    for lvl, conds in LEVELS:
        progs = None
        for key in [(sy, c) for sy in merges + ["base", "tuned_L0", "mono_all", "cons_lam3"] for c in conds]:
            ss = set(cells[key]["snippet_id"]); progs = ss if progs is None else progs & ss
        blk = {}
        for m in merges:
            blk[f"{m} - tuned_L0"] = pooled(cells, m, "tuned_L0", conds, progs)
            blk[f"{m} - mono_all"] = pooled(cells, m, "mono_all", conds, progs)
            blk[f"{m} - cons_lam3"] = pooled(cells, m, "cons_lam3", conds, progs)   # REPORTED: merge vs the anchored arm
            blk[f"{m} - base"] = pooled(cells, m, "base", conds, progs)
        blk["mono_all - tuned_L0"] = pooled(cells, "mono_all", "tuned_L0", conds, progs)
        blk["cons_lam3 - tuned_L0"] = pooled(cells, "cons_lam3", "tuned_L0", conds, progs)
        blk["_n_programs"] = len(progs); out["by_level"][lvl] = blk
        print(f"--- {lvl} ({len(progs)} programs) ---")
        for k, v in blk.items():
            if not k.startswith("_"): print(f"   {k:32s} {s(v)}")
    a = out["by_level"]["seen6"]
    best = max(merges, key=lambda m: a[f"{m} - tuned_L0"]["value_pts"])
    ra, rb = a[f"{best} - tuned_L0"], a[f"{best} - mono_all"]
    gated = [m for m in merges if any((r or 0) > FMT_MAX for r in out["format_fail"][m].values())]
    out["hypotheses"] = [
        {"id": "H-merge-panel-a", "best_merge": best,
         "rule": "CONFIRMED iff best merge - tuned_L0 pooled over the six seen stacks has ci_hi <= +1.0; REFUTED iff ci_lo > +1.0",
         "verdict": "REFUTED" if ra["ci_lo"] > 1.0 else ("CONFIRMED" if ra["ci_hi"] <= 1.0 else "INCONCLUSIVE"), "evidence": ra},
        {"id": "H-merge-panel-b", "best_merge": best,
         "rule": "CONFIRMED iff best merge - mono_all pooled over the six seen stacks has ci_hi < 0; REFUTED iff ci_lo > 0",
         "verdict": "REFUTED" if rb["ci_lo"] > 0 else ("CONFIRMED" if rb["ci_hi"] < 0 else "INCONCLUSIVE"), "evidence": rb},
    ]
    out["format_gate_note"] = (f"merges with a cell over the {FMT_MAX} format gate: {gated} (their cells are reported, not read; "
                               f"the best merge is {best})")
    for h in out["hypotheses"]: print(f"{h['id']:20s} {h['verdict']:12s} best={best}  {s(h['evidence'])}")
    print("format-gated merges:", gated)
    p = ROOT / "results/analysis/pipeline" / f"merge_panel_{model.replace('-', '')}.json"
    p.write_text(json.dumps(out, indent=1)); print("wrote", p.relative_to(ROOT)); return out

if __name__ == "__main__":
    for m in MODELS: run(m)
