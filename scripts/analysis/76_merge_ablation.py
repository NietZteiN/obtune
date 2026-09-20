"""RQ1 merge ablation: does the clean-code gain need the L0 specialist, or diversity of view?

Four merges, identical in operator (DARE-TIES), density (0.5), weights (uniform) and rank (32),
differing only in INGREDIENTS:

  struct   S1+S2                      2 specialists, one semantic view (structure)
  ident    L1b+L1r+L2                 3 specialists, one semantic view (identifiers)
  nol0     L1b+L1r+L2+S1+S2           5 specialists, both views, no clean-code specialist
  6-way    L0+L1b+L1r+L2+S1+S2        the paper's merge

Two questions, answerable by comparing columns:
  * does removing L0 remove the clean-code gain?          nol0 vs 6-way on L0
  * does diversity of view beat number of adapters?       struct vs ident vs nol0

Everything is reported against the untuned model's L0 accuracy, as Table 4 is, and with paired
program-clustered bootstrap CIs for the two contrasts that matter.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

MODELS = ["codellama-7b","codellama-13b","llama31-8b","granite31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","codellama-13b":"CodeLlama-13B",
        "llama31-8b":"Llama-3.1-8B","granite31-8b":"Granite-3.1-8B"}
ABL  = ["mergeablate_generic"]; ABLB = ["mergeablate_inverse"]
FULL = ["panel_core","composite_generic","composite_depth","f2_divergence","merge_panel",
        "mole_generic","rq2_generic"]
BWD  = ["inverse_1shot","inverse_generic"]
ARMS = [("struct","merge_struct",ABL,"S1+S2"),("ident","merge_ident",ABL,"L1b+L1r+L2"),
        ("no-L0","merge_nol0",ABL,"5 obf."),("6-way","merge_dare_ties",FULL,"all six")]
GROUPS = [("L0", ["L0"]), ("singles", ["L1b","L1r","L2","S1","S2"]),
          ("d2 seen", ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"]),
          ("unseen", ["X1","C_L1r_X1","C_X1_S1","C_S2_X1"])]

def pool(ph, m, arm, cs):
    fr=[d for d in (load_cell(ph,m,arm,c) for c in cs) if d is not None and d.format_fail.mean()<=0.25]
    return pd.concat(fr) if fr else None

def acc(ph, m, arm, cs):
    d = pool(ph, m, arm, cs); return None if d is None else float(d.correct.mean())

def contrast(phA, phB, m, a, b, cs, n=2000):
    A, B = pool(phA,m,a,cs), pool(phB,m,b,cs)
    if A is None or B is None: return None
    ps = sorted(set(A.snippet_id) & set(B.snippet_id))
    if not ps: return None
    ga = {p:g.correct.to_numpy(float) for p,g in A.groupby("snippet_id") if p in ps}
    gb = {p:g.correct.to_numpy(float) for p,g in B.groupby("snippet_id") if p in ps}
    pt = (np.concatenate([ga[p] for p in ps]).mean()-np.concatenate([gb[p] for p in ps]).mean())*100
    rng = np.random.default_rng(17); idx = np.arange(len(ps))
    dr = [(np.concatenate([ga[ps[j]] for j in pk]).mean()-np.concatenate([gb[ps[j]] for j in pk]).mean())*100
          for pk in (rng.choice(idx,len(ps),True) for _ in range(n))]
    lo,hi = np.percentile(dr,[2.5,97.5]); return pt,lo,hi

def _completeness_guard():
    """Refuse to report on a phase whose eval is still running.

    Reading mergeablate_generic mid-write produced a 20-point spread on CodeLlama-7B's unseen-family
    row that vanished once the remaining cells landed: arms had different numbers of readable
    conditions at the moment of reading, so the group means averaged different condition sets. A
    partially written phase looks exactly like a real effect.
    """
    import subprocess
    try:
        q = subprocess.run(["squeue","-h","-u",__import__("os").environ.get("USER",""),"-o","%j"],
                           capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return
    live = [l for l in q.split("\n") if l.startswith("ev_mergeablate_")]
    if live:
        print("REFUSING: these ablation evals are still running, so the phase is incomplete:",
              file=__import__("sys").stderr)
        for l in sorted(live): print("   ", l, file=__import__("sys").stderr)
        print("    Re-run when the queue is clear, or pass --force to read anyway.",
              file=__import__("sys").stderr)
        if "--force" not in __import__("sys").argv:
            raise SystemExit(2)


def main():
    _completeness_guard()
    out = {}
    print("forward, % of the untuned model's clean-code accuracy\n")
    print(f"{'model':15s} {'group':9s} {'base':>6s} " + " ".join(f"{n:>7s}" for n,_,_,_ in ARMS))
    for m in MODELS:
        ref = acc(ABL,m,"base",["L0"]) or acc(FULL,m,"base",["L0"])
        if not ref: print(f"{m:15s} (no readable L0 reference)"); continue
        out[m] = {"ref_L0": round(ref,4), "groups": {}}
        for g,cs in GROUPS:
            row, rec = [], {}
            b = acc(ABL,m,"base",cs) or acc(FULL,m,"base",cs)
            row.append("   --  " if b is None else f"{b/ref*100:5.0f}%")
            for nm,arm,ph,_ in ARMS:
                a = acc(ph,m,arm,cs)
                rec[nm] = None if a is None else round(a/ref*100,1)
                row.append("   --  " if a is None else f"{a/ref*100:6.0f}%")
            out[m]["groups"][g] = rec
            print(f"{m:15s} {g:9s} " + " ".join(row))
        print()
    print("paired contrasts (95% CI, program-clustered, 2000 resamples)\n")
    print(f"{'model':15s} {'no-L0 - 6-way on L0':>26s} {'struct - no-L0 on L0':>26s}")
    for m in MODELS:
        c1 = contrast(ABL,FULL,m,"merge_nol0","merge_dare_ties",["L0"])
        c2 = contrast(ABL,ABL,m,"merge_struct","merge_nol0",["L0"])
        f = lambda r: "          --          " if r is None else f"{r[0]:+6.2f} [{r[1]:+5.1f},{r[2]:+5.1f}]{'*' if (r[1]>0)==(r[2]>0) else ' '}"
        out.setdefault(m,{}).setdefault("contrasts",{})
        for k,r in (("nol0_minus_6way_L0",c1),("struct_minus_nol0_L0",c2)):
            out[m]["contrasts"][k] = None if r is None else dict(delta=round(r[0],2),lo=round(r[1],2),hi=round(r[2],2))
        print(f"{m:15s} {f(c1):>26s} {f(c2):>26s}")
    (ROOT/"results/analysis/pipeline/merge_ablation.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/analysis/pipeline/merge_ablation.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
