#!/usr/bin/env python
"""H-anchor-site — does anchoring the REPRESENTATION forward-lock less than anchoring the OUTPUT?

    python scripts/analysis/64_anchor_site.py

Applies the rule pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-14 BEFORE submission:
  a (forward-locking): CONFIRMED iff the best align_* arm's forward-collapse rate is below BOTH
     cons_lam3's and mono_all's; REFUTED iff above cons_lam3's.
  b (backward cost):   CONFIRMED iff align - base backwards (exact arguments) has ci_lo > 0 while
     cons_lam3 - base does not; REFUTED iff align - base ci_hi < 0.
  The `mismatch` arm is the control: if it behaves like the matched arm on both, the effect is not
  about aligning to the right parent and neither rule is informative.

cons_lam3's KL is over the teacher's ANSWER-TOKEN distribution (objectives.py), so it matches forward
behaviour by construction; the align_* arms constrain hidden states at six layers instead.
"""
from __future__ import annotations
import datetime as dt, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts"/"analysis")); sys.path.insert(0, str(ROOT/"src"))
from obtune.data import load_eval_items  # noqa: E402

M="codellama-7b"; CONDS=["L0","L1b","L1r","L2","S1","S2","X1"]
ALIGN=["align_lam0","align_lam0.3","align_lam1","align_lam3","align_span_lam3","align_lam1_mm"]
REF=["base","tuned_L0","mono_all","cons_lam3","tuned_X1"]
N_BOOT,SEED=2000,17

def norm(s): return str(s).strip().strip('"').strip("'").replace(" ","")
gold={}
for c in CONDS:
    for it in load_eval_items([c],"python",source="heldout"): gold[(c,it.program_id,it.item_id)]=it.output_repr

def load(sysn,c):
    p=ROOT/"results/cells/inverse_generic"/M/"python"/f"{sysn}__{c}"/"trials.parquet"
    return pd.read_parquet(p) if p.exists() else None

def collapse(sysn):
    hit=tot=0
    for c in CONDS:
        d=load(sysn,c)
        if d is None: continue
        for _,r in d.iterrows():
            tot+=1
            if norm(r["output_raw"])==norm(gold.get((c,r["snippet_id"],r["item_id"]),"\x00")): hit+=1
    return hit/tot if tot else None

def pooled(t,k):
    A={}; B={}; progs=None
    for c in CONDS:
        da,db=load(t,c),load(k,c)
        if da is None or db is None: return None
        A[c]={p:g["args_exact"].to_numpy(float) for p,g in da.groupby("snippet_id")}
        B[c]={p:g["args_exact"].to_numpy(float) for p,g in db.groupby("snippet_id")}
        s=set(A[c])&set(B[c]); progs = s if progs is None else progs&s
    P=sorted(progs); rng=np.random.default_rng(SEED); idx=np.arange(len(P))
    def d(pick):
        a=np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in CONDS])
        b=np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in CONDS])
        return (a.mean()-b.mean())*100
    draws=np.array([d(rng.choice(idx,len(P),True)) for _ in range(N_BOOT)]); pt=d(np.arange(len(P)))
    lo,hi=(float(x) for x in np.percentile(draws,[2.5,97.5]))
    return {"value_pts":float(pt),"ci_lo":lo,"ci_hi":hi,"n_programs":len(P),"excludes_zero":bool(lo>0 or hi<0)}

out={"script":"64_anchor_site.py","model":M,
     "generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
     "collapse":{}, "backward_vs_base":{}}
print("=== forward-collapse rate (share of backward replies = the gold return value) ===")
for s in REF+ALIGN:
    c=collapse(s)
    if c is None: continue
    out["collapse"][s]=c; print(f"  {s:18s} {c:.4f}")
print("\n=== backward, exact arguments, vs base (pooled over 7 conditions) ===")
for s in ["tuned_L0","mono_all","cons_lam3","tuned_X1"]+ALIGN:
    r=pooled(s,"base")
    if r is None: continue
    out["backward_vs_base"][s]=r
    print(f"  {s:18s} {r['value_pts']:+6.2f} [{r['ci_lo']:+6.2f}, {r['ci_hi']:+6.2f}]{'*' if r['excludes_zero'] else ''}")

matched=[a for a in ALIGN if not a.endswith("_mm") and a in out["collapse"]]
best=min(matched, key=lambda a: out["collapse"][a]) if matched else None
cc,mc = out["collapse"].get("cons_lam3"), out["collapse"].get("mono_all")
va = out["backward_vs_base"].get(best); vc = out["backward_vs_base"].get("cons_lam3")
a_v = ("REFUTED" if (best and out["collapse"][best] > cc) else
       "CONFIRMED" if (best and out["collapse"][best] < cc and out["collapse"][best] < mc) else "INCONCLUSIVE")
b_v = ("REFUTED" if (va and va["ci_hi"] < 0) else
       "CONFIRMED" if (va and vc and va["ci_lo"] > 0 and not (vc["ci_lo"] > 0)) else "INCONCLUSIVE")
out["hypotheses"]=[{"id":"H-anchor-site-a","best_align":best,"verdict":a_v,
                    "evidence":{"align":out["collapse"].get(best),"cons_lam3":cc,"mono_all":mc}},
                   {"id":"H-anchor-site-b","best_align":best,"verdict":b_v,
                    "evidence":{"align_vs_base":va,"cons_lam3_vs_base":vc}}]
mm=out["collapse"].get("align_lam1_mm"); m1=out["collapse"].get("align_lam1")
out["mismatch_control"]={"align_lam1":m1,"align_lam1_mm":mm,
                         "note":"if these are alike, the effect is not about aligning to the RIGHT parent"}
print(f"\nH-anchor-site-a  {a_v}   (best matched align arm: {best})")
print(f"H-anchor-site-b  {b_v}")
print(f"mismatch control: align_lam1 {m1} vs align_lam1_mm {mm}")
p=ROOT/"results/analysis/pipeline/anchor_site_codellama7b.json"; p.write_text(json.dumps(out,indent=1))
print("wrote", p.relative_to(ROOT))
