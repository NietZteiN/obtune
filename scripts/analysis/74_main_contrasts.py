"""Paired bootstrap CIs for every headline comparison the paper makes (user request, 2026-09-20).

The project has used a program-clustered 2,000-resample bootstrap throughout; this surfaces the
intervals in one table instead of leaving them in logs. Every contrast is paired on the programs
common to the two cells and resampled by program, because multiple input cases per program are
correlated.

  python scripts/analysis/74_main_contrasts.py            # the standard set
  python scripts/analysis/74_main_contrasts.py --ablation # adds the no-L0 / family merges
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

MODELS = ["codellama-7b","codellama-13b","codellama-34b","llama31-8b","starcoder2-15b",
          "gemma3-12b","codegemma-7b","granite31-8b"]
FWD = ["panel_core","composite_generic","composite_depth","f2_divergence","merge_panel",
       "mole_generic","rq2_generic","mergeablate_generic"]
BWD = ["inverse_1shot","inverse_generic","mergeablate_inverse"]
L0        = ["L0"]
SINGLES   = ["L1b","L1r","L2","S1","S2"]
UNSEEN    = ["X1","C_L1r_X1","C_X1_S1","C_S2_X1","C_L1r_X1m","C_S1_X1s","C3_L1r_S1_X1"]
UNSEEN_ST = ["C_L1r_X1","C_X1_S1","C_S2_X1","C_L1r_X1m","C_S1_X1s","C3_L1r_S1_X1"]
ALLBWD    = ["L0","L1b","L1r","L2","S1","S2","X1","C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4",
             "C_L1r_S3","C_S4_S3","C_L1r_X1","C_X1_S1","C_S2_X1"]

def pool(ph, m, arm, conds, gate=True):
    fr = []
    for c in conds:
        d = load_cell(ph, m, arm, c)
        if d is None: continue
        if gate and d.format_fail.mean() > 0.25: continue
        fr.append(d)
    return pd.concat(fr) if fr else None

def contrast(ph, m, a, b, conds, n=2000, seed=17):
    A, B = pool(ph, m, a, conds), pool(ph, m, b, conds)
    if A is None or B is None: return None
    ps = sorted(set(A.snippet_id) & set(B.snippet_id))
    if not ps: return None
    ga = {p: g.correct.to_numpy(float) for p, g in A.groupby("snippet_id") if p in ps}
    gb = {p: g.correct.to_numpy(float) for p, g in B.groupby("snippet_id") if p in ps}
    pt = (np.concatenate([ga[p] for p in ps]).mean() - np.concatenate([gb[p] for p in ps]).mean())*100
    rng = np.random.default_rng(seed); idx = np.arange(len(ps))
    draws = [(np.concatenate([ga[ps[j]] for j in pk]).mean()
              - np.concatenate([gb[ps[j]] for j in pk]).mean())*100
             for pk in (rng.choice(idx, len(ps), True) for _ in range(n))]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return pt, lo, hi, len(ps)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ablation", action="store_true"); a = ap.parse_args()
    C = [
        ("Merge - Base",        "merge_dare_ties", "base",            FWD, L0,        "clean L0"),
        ("Merge - Clean LoRA",  "merge_dare_ties", "tuned_L0",        FWD, L0,        "clean L0"),
        ("Breadth - Merge",     "mono_all",        "merge_dare_ties", FWD, UNSEEN,    "unseen family"),
        ("Breadth - Router",    "mono_all",        "mole_router",     FWD, UNSEEN,    "unseen family"),
        ("Router - Merge",      "mole_router",     "merge_dare_ties", FWD, UNSEEN,    "unseen family"),
        ("Router - Merge",      "mole_router",     "merge_dare_ties", FWD, UNSEEN_ST, "unseen stacks"),
        ("Router - Merge",      "mole_router",     "merge_dare_ties", BWD, ALLBWD,    "backward"),
        ("Merge - Base",        "merge_dare_ties", "base",            BWD, ALLBWD,    "backward"),
    ]
    if a.ablation:
        for arm, lbl in (("merge_ablate_nol0_dare_ties","no-L0 merge"),
                         ("merge_ablate_ident_dare_ties","identifier merge"),
                         ("merge_ablate_struct_dare_ties","structural merge")):
            C += [(f"{lbl} - Clean LoRA", arm, "tuned_L0", FWD, L0,     "clean L0"),
                  (f"{lbl} - Base",       arm, "base",     FWD, L0,     "clean L0"),
                  (f"{lbl} - Base",       arm, "base",     FWD, UNSEEN, "unseen family"),
                  (f"{lbl} - Base",       arm, "base",     BWD, ALLBWD, "backward")]
    print(f"{'contrast':30s} {'regime':15s} " + " ".join(f"{m.split('-')[0][:9]:>10s}" for m in MODELS))
    out = []
    for name, x, y, ph, conds, regime in C:
        cells, line = [], []
        for m in MODELS:
            r = contrast(ph, m, x, y, conds)
            cells.append((m, r))
            line.append("    --    " if r is None else f"{r[0]:+6.2f}{'*' if (r[1]>0)==(r[2]>0) else ' '}")
        print(f"{name:30s} {regime:15s} " + " ".join(f"{s:>10s}" for s in line))
        out.append(dict(contrast=name, regime=regime,
                        per_model={m: (None if r is None else dict(delta=round(r[0],2), lo=round(r[1],2),
                                                                   hi=round(r[2],2), n_programs=r[3]))
                                   for m, r in cells}))
    import json
    (ROOT/"results/analysis/pipeline/main_contrasts.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/analysis/pipeline/main_contrasts.json  (* = 95% CI excludes zero)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
