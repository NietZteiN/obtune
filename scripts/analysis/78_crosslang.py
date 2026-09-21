"""Cross-language transfer: Python-trained adapters evaluated on JavaScript (user item 9).

Forward only. JavaScript backward grading executes the predicted input through
obtune.exec.pool, which needs `node`; juno has none. Forward grading is a JSON parse
against the precomputed output_repr, so it needs no interpreter. See
configs/eval/crosslang_fwd.yaml.

Reports each arm as a percentage of the UNTUNED model's accuracy on clean JavaScript,
the same reference the Python tables use, so the recovery claim can be compared across
languages directly. Paired program-clustered bootstrap for the contrasts.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/analysis"))
from cellkit import load_cell

JS, PY = "javascript", "python"
XPH = ["crosslang_generic"]
PYPH = ["panel_core","composite_generic","composite_depth","f2_divergence","merge_panel",
        "mole_generic","rq2_generic"]
MODELS = ["codellama-7b","llama31-8b"]
NICE = {"codellama-7b":"CodeLlama-7B","llama31-8b":"Llama-3.1-8B"}
ARMS = [("base","base"),("tuned_L0","clean"),("mono_all","breadth"),("merge_dare_ties","merge")]
GROUPS = [("L0", ["L0"]),
          ("singles", ["L1b","L1r","L2","S1","S2"]),
          ("d2 seen", ["C_L1b_S1","C_L1r_S1","C_S1_L1r","C_L2_S4","C_L1r_S3","C_S4_S3"])]

def pool(ph, m, arm, cs, lang):
    fr = [d for d in (load_cell(ph, m, arm, c, language=lang) for c in cs)
          if d is not None and d.format_fail.mean() <= 0.25]
    return pd.concat(fr) if fr else None

def acc(ph, m, arm, cs, lang):
    d = pool(ph, m, arm, cs, lang); return None if d is None else float(d.correct.mean())

def contrast(m, a, b, cs, lang, ph, n=2000):
    A, B = pool(ph, m, a, cs, lang), pool(ph, m, b, cs, lang)
    if A is None or B is None: return None
    ps = sorted(set(A.snippet_id) & set(B.snippet_id))
    if not ps: return None
    ga = {p: g.correct.to_numpy(float) for p, g in A.groupby("snippet_id") if p in ps}
    gb = {p: g.correct.to_numpy(float) for p, g in B.groupby("snippet_id") if p in ps}
    pt = (np.concatenate([ga[p] for p in ps]).mean() - np.concatenate([gb[p] for p in ps]).mean())*100
    rng = np.random.default_rng(17); idx = np.arange(len(ps))
    dr = [(np.concatenate([ga[ps[j]] for j in pk]).mean() - np.concatenate([gb[ps[j]] for j in pk]).mean())*100
          for pk in (rng.choice(idx, len(ps), True) for _ in range(n))]
    lo, hi = np.percentile(dr, [2.5, 97.5]); return pt, lo, hi

def main() -> int:
    out = {}
    for m in MODELS:
        ref_js = acc(XPH, m, "base", ["L0"], JS)
        if ref_js is None:
            print(f"{NICE[m]}: no JavaScript cells yet\n"); continue
        ref_py = acc(PYPH, m, "base", ["L0"], PY)
        print(f"=== {NICE[m]} ===")
        print(f"untuned clean-code accuracy: JavaScript {ref_js:.3f}"
              + (f", Python {ref_py:.3f}" if ref_py else ", Python --"))
        print("\n% of the untuned model's clean-JavaScript accuracy "
              "(Python-trained adapters, JavaScript items)\n")
        print(f"{'group':10s} " + " ".join(f"{n:>9s}" for _, n in ARMS))
        rec = {}
        for g, cs in GROUPS:
            row, gr = [], {}
            for a, n in ARMS:
                v = acc(XPH, m, a, cs, JS)
                gr[n] = None if v is None else round(v/ref_js*100, 2)
                row.append("       --" if v is None else f"{v/ref_js*100:8.0f}%")
            rec[g] = gr
            print(f"{g:10s} " + " ".join(row))
        out[NICE[m]] = {"ref_js": round(ref_js, 4),
                        "ref_py": None if ref_py is None else round(ref_py, 4), "groups": rec}
        print("\npaired contrasts on JavaScript (95% CI, program-clustered, 2000 resamples)\n")
        cons = [("breadth - base", "mono_all", "base"),
                ("merge - base", "merge_dare_ties", "base"),
                ("clean - base", "tuned_L0", "base"),
                ("breadth - merge", "mono_all", "merge_dare_ties")]
        cr = {}
        for lab, a, b in cons:
            r = contrast(m, a, b, [c for _, cs in GROUPS for c in cs], JS, XPH)
            cr[lab] = None if r is None else dict(delta=round(r[0],2), lo=round(r[1],2), hi=round(r[2],2))
            f = "      --      " if r is None else \
                f"{r[0]:+6.2f} [{r[1]:+5.1f},{r[2]:+5.1f}]{'*' if (r[1]>0)==(r[2]>0) else ' '}"
            print(f"  {lab:18s} {f}")
        out[NICE[m]]["contrasts"] = cr
        print()
    f = ROOT/"results/analysis/pipeline/crosslang.json"
    f.write_text(json.dumps(out, indent=2)); print(f"wrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
