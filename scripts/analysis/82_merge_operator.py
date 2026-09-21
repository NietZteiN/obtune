#!/usr/bin/env python
"""A5: does the merge OPERATOR matter, or would averaging do?

    python scripts/analysis/82_merge_operator.py

Ingredients, weights, rank and seed are identical across the three merges; only the operator
differs. `linear` is plain uniform averaging -- no sparsification, no sign election -- and is
the control the paper never ran, which is why DARE-TIES looked arbitrary.

Backward is read on two models only: the other two backward runs were cancelled to stay inside
a 15-GPU cap, and the forward answer was already unambiguous on four.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

FWD, BWD = ["mergeop_generic"], ["mergeop_inverse"]
MODELS = ["codellama-7b", "codellama-13b", "llama31-8b", "granite31-8b"]
NICE = {"codellama-7b": "CodeLlama-7B", "codellama-13b": "CodeLlama-13B",
        "llama31-8b": "Llama-3.1-8B", "granite31-8b": "Granite-3.1-8B"}
ARMS = [("base", "base"), ("merge_linear", "linear"),
        ("merge_ties", "TIES"), ("merge_dare_ties", "DARE-TIES")]
GROUPS = [("L0", ["L0"]), ("singles", ["L1b", "L1r", "L2", "S1", "S2"]),
          ("unseen", ["X1", "C_L1r_X1", "C_X1_S1", "C_S2_X1"])]

def pool(ph, m, arm, cs, gate=True):
    fr = [d for d in (load_cell(ph, m, arm, c) for c in cs)
          if d is not None and (not gate or d.format_fail.mean() <= 0.25)]
    return pd.concat(fr) if fr else None

def lock_rate(m, arm):
    """Fraction of BACKWARD replies equal to the gold FORWARD answer."""
    from obtune.data import load_eval_items
    b = pool(BWD, m, arm, ["L0"], gate=False)
    if b is None: return None
    idx = {it.item_id: str(it.output_repr) for it in
           load_eval_items(["L0"], "python", script=__file__, source="heldout")}
    g = b.item_id.map(idx)
    return float((b.output_raw.str.strip() == g.astype(str).str.strip()).mean())

def main() -> int:
    sys.path.insert(0, str(ROOT/"src"))
    out = {}
    for tag, ph in (("forward", FWD), ("backward", BWD)):
        print(f"\n{tag}: % of the untuned model's clean-code accuracy\n")
        print(f"{'model':16s} {'group':9s} " + " ".join(f"{n:>10s}" for _, n in ARMS))
        for m in MODELS:
            ref_d = pool(ph, m, "base", ["L0"])
            if ref_d is None: continue
            ref = ref_d.correct.mean()
            for g, cs in GROUPS:
                row, rec = [], {}
                for arm, n in ARMS:
                    d = pool(ph, m, arm, cs)
                    rec[n] = None if d is None else round(d.correct.mean()/ref*100, 1)
                    row.append("     gated" if d is None else f"{d.correct.mean()/ref*100:9.0f}%")
                out.setdefault(NICE[m], {}).setdefault(tag, {})[g] = rec
                print(f"{m:16s} {g:9s} " + " ".join(row))
            print()
    print("\ndirection lock on backward L0 (fraction of backward replies "
          "equal to the gold FORWARD answer)\n")
    print(f"{'model':16s} " + " ".join(f"{n:>11s}" for _, n in ARMS))
    for m in MODELS:
        if pool(BWD, m, "base", ["L0"], gate=False) is None: continue
        vals = []
        for arm, n in ARMS:
            v = lock_rate(m, arm)
            vals.append("         --" if v is None else f"{v:11.3f}")
            out.setdefault(NICE[m], {}).setdefault("lock", {})[n] = v
        print(f"{m:16s} " + " ".join(vals))
    f = ROOT/"results/analysis/pipeline/merge_operator.json"
    f.write_text(json.dumps(out, indent=2)); print(f"\nwrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
