"""Geometry of the specialist updates (user request item 10, 2026-09-20).

Accuracy shows that composing specialists beats pooling their data. It does not show whether the
specialists occupy related directions. This measures that directly on the adapter weights, with no
GPU and no evaluation:

  cosine      pairwise cosine similarity between task vectors Delta = s * B A, per target module,
              averaged over modules. Within-family pairs (identifier x identifier, structural x
              structural) are separated from across-family pairs.
  overlap     fraction of coordinates retained by TIES magnitude-trimming that two specialists share,
              at the density the paper uses. This is the quantity the sign election operates on.
  sign agree  fraction of jointly-retained coordinates on which two specialists agree in sign, which
              is what the disjoint merge keeps.

Reads adapters directly; nothing here touches results/cells.
"""
from __future__ import annotations
import sys, json, itertools
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[2]
FAM = {"L1b":"identifier","L1r":"identifier","L2":"identifier","S1":"structural","S2":"structural","L0":"clean"}
CONDS = ["L0","L1b","L1r","L2","S1","S2"]
DENSITY = 0.5
OVERLAP_STRIDE = 16   # materialise every 16th module for the trim-overlap statistics
# RUN THIS AS A JOB, NOT ON THE LOGIN NODE. One materialised module of a 7B is ~180 MB and the
# login node refuses it; the cosine path needs no materialisation but the overlap path does.
#   python scripts/slurm/submit.py --partition normal --mem 64G --argv -m ... (see log entry)

def load(model, cond):
    """Return the FACTORS, not the product. Materialising B A for every module of a 7B exhausted the
    login node (180 MB per module, hundreds of modules). Every quantity below is computable from the
    factors: see `cos_factored`."""
    from safetensors.torch import load_file
    d = ROOT/f"runs/adapters/{model}/python/{cond}_r32_s17/best"
    f = d/"adapter_model.safetensors"
    if not f.exists(): return None
    sd = load_file(str(f))
    import json as J
    cfg = J.loads((d/"adapter_config.json").read_text())
    scale = cfg.get("lora_alpha", 32) / cfg.get("r", 32)
    out = {}
    for k in sd:
        if "lora_A" not in k: continue
        kb = k.replace("lora_A", "lora_B")
        if kb not in sd: continue
        out[k.split(".lora_A")[0]] = (sd[kb].float(), sd[k].float(), scale)
    return out


def cos_factored(f1, f2):
    """cos(vec(s1 B1 A1), vec(s2 B2 A2)) without forming either product.

    <B1A1, B2A2>_F = tr(A1^T B1^T B2 A2) = tr((B1^T B2)(A2 A1^T)), a product of two r x r matrices.
    The scalars s cancel from the cosine, so they are omitted."""
    B1, A1, _ = f1; B2, A2, _ = f2
    num = torch.trace((B1.T @ B2) @ (A2 @ A1.T))
    n1 = torch.sqrt(torch.trace((B1.T @ B1) @ (A1 @ A1.T)))
    n2 = torch.sqrt(torch.trace((B2.T @ B2) @ (A2 @ A2.T)))
    return float(num / (n1 * n2 + 1e-12))

def trim_mask(t, density):
    k = max(1, int(density * t.numel()))
    thr = t.abs().flatten().topk(k).values[-1]
    return t.abs() >= thr

def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "codellama-7b"
    vecs = {c: load(model, c) for c in CONDS}
    have = [c for c in CONDS if vecs[c]]
    if len(have) < 2:
        print(f"{model}: fewer than two specialists on disk"); return 1
    mods = sorted(set.intersection(*[set(vecs[c]) for c in have]))
    print(f"{model}: {len(have)} specialists, {len(mods)} shared target modules\n")
    rows = []
    for a, b in itertools.combinations(have, 2):
        cs, ov, sg = [], [], []
        for mi, m in enumerate(mods):
            cs.append(cos_factored(vecs[a][m], vecs[b][m]))
            # Overlap and sign agreement need the materialised update. Do it for a subsample of
            # modules only, one at a time, and free immediately: the full set does not fit in memory.
            if mi % OVERLAP_STRIDE: continue
            B1, A1, s1 = vecs[a][m]; B2, A2, s2 = vecs[b][m]
            x = ((B1 @ A1) * s1).flatten(); y = ((B2 @ A2) * s2).flatten()
            mx, my = trim_mask(x, DENSITY), trim_mask(y, DENSITY)
            both = mx & my
            ov.append(float(both.sum()) / float(mx.sum()))
            if both.any():
                sg.append(float((torch.sign(x[both]) == torch.sign(y[both])).float().mean()))
            del x, y, mx, my, both
        pair = f"{a}-{b}"
        kind = "within" if FAM[a] == FAM[b] else ("clean" if "clean" in (FAM[a], FAM[b]) else "across")
        rows.append(dict(pair=pair, kind=kind, cosine=sum(cs)/len(cs),
                         overlap=sum(ov)/len(ov), sign_agree=sum(sg)/len(sg) if sg else None))
    rows.sort(key=lambda r: -r["cosine"])
    print(f"{'pair':12s} {'kind':8s} {'cosine':>8s} {'overlap':>8s} {'sign-agree':>11s}")
    for r in rows:
        print(f"{r['pair']:12s} {r['kind']:8s} {r['cosine']:+8.3f} {r['overlap']:8.3f} "
              f"{(f'{r[chr(115)+chr(105)+chr(103)+chr(110)+chr(95)+chr(97)+chr(103)+chr(114)+chr(101)+chr(101)]:.3f}' if r['sign_agree'] is not None else '--'):>11s}")
    for kind in ("within","across","clean"):
        sel = [r for r in rows if r["kind"] == kind]
        if sel:
            print(f"\n  {kind:7s} n={len(sel):2d}  mean cosine {sum(r['cosine'] for r in sel)/len(sel):+.3f}"
                  f"  mean overlap {sum(r['overlap'] for r in sel)/len(sel):.3f}"
                  f"  mean sign-agree {sum(r['sign_agree'] for r in sel)/len(sel):.3f}")
    (ROOT/f"results/analysis/pipeline/specialist_geometry_{model}.json").write_text(json.dumps(rows, indent=2))
    print(f"\nwrote results/analysis/pipeline/specialist_geometry_{model}.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
