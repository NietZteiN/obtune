"""Verify the merge-space claim on REAL adapters (user request item 8).

Section~\\ref{sec:factorspace} states that merging LoRA factors is not equivalent to merging
the assembled updates, and quantifies the gap on RANDOM factors: cosine 0.40, 39% sign
disagreement. Random factors are close to orthogonal. The specialists here are not -- they
sit at cosine 0.4-0.7 (75_specialist_geometry) -- so the real gap could be much smaller, and
the caveat in that section correspondingly weaker or stronger than it reads.

This measures it on the deployed artefacts:

  factor space   the merged adapter ALREADY ON DISK, built by PEFT's add_weighted_adapter.
                 Nothing is reimplemented; this is the thing the paper evaluates.
  update space   the SAME PEFT primitive (peft.utils.merge_utils.ties / dare_ties) applied to
                 the materialised updates Delta_c = s_c B_c A_c instead of to the factors.

Comparing those two isolates exactly one variable: what the merge operator is applied to.

TIES is reported alongside DARE-TIES because DARE draws a Bernoulli mask, so a single
DARE-TIES comparison confounds the factor/update question with one random draw. TIES is
deterministic and answers the structural question cleanly; DARE-TIES is averaged over seeds.
"""
from __future__ import annotations
import sys, json, argparse
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
STRIDE = 16          # materialise every 16th module; a 7B module is ~180 MB
DENSITY = 0.5
DARE_SEEDS = [0, 1, 2]

def load_factors(d: Path):
    """{module: (B, A, scale)} from an adapter directory."""
    from safetensors.torch import load_file
    f = d/"adapter_model.safetensors"
    if not f.exists(): return None
    sd = load_file(str(f))
    cfg = json.loads((d/"adapter_config.json").read_text())
    scale = cfg["lora_alpha"] / cfg["r"]
    out = {}
    for k in sd:
        if ".lora_A" not in k: continue
        mod = k.split(".lora_A")[0]
        b = k.replace(".lora_A", ".lora_B")
        if b in sd:
            out[mod] = (sd[b].float(), sd[k].float(), float(scale))
    return out or None

def delta(t):
    B, A, s = t
    return (B @ A) * s

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model", nargs="?", default="codellama-7b")
    a = ap.parse_args()
    from peft.utils.merge_utils import ties, dare_ties

    root = ROOT/f"runs/adapters/{a.model}/python"
    spec = {c: load_factors(root/f"{c}_r32_s17"/"best") for c in CONDS}
    missing = [c for c in CONDS if spec[c] is None]
    if missing:
        print(f"{a.model}: missing specialists {missing}"); return 1
    merged = load_factors(root/"merge_dare_ties_r32_s17")
    if merged is None:
        print(f"{a.model}: no merged adapter on disk"); return 1

    mods = sorted(set(merged) & set.intersection(*[set(spec[c]) for c in CONDS]))
    print(f"{a.model}: {len(mods)} shared modules, sampling every {STRIDE}\n")
    w = torch.ones(len(CONDS)) / len(CONDS)

    rows = {"ties": [], "dare_ties": []}
    for mi, m in enumerate(mods):
        if mi % STRIDE: continue
        dk = delta(merged[m]).flatten()                      # factor-space, as deployed
        tv = [delta(spec[c][m]).flatten() for c in CONDS]    # the six updates
        cands = {"ties": [ties(tv, w, DENSITY, "total")]}
        ds = []
        for s in DARE_SEEDS:
            torch.manual_seed(s)
            ds.append(dare_ties(tv, w, DENSITY, "total"))
        cands["dare_ties"] = ds
        for name, lst in cands.items():
            for du in lst:
                du = du.flatten()
                cos = float(torch.nn.functional.cosine_similarity(dk, du, dim=0))
                nz = (dk != 0) & (du != 0)
                sg = float((torch.sign(dk[nz]) == torch.sign(du[nz])).float().mean()) if nz.any() else float("nan")
                rows[name].append((cos, sg))
        del dk, tv, cands

    out = {}
    for name, rs in rows.items():
        if not rs: continue
        cos = sum(r[0] for r in rs)/len(rs)
        # A sampled module whose update-space merge is entirely zero -- every coordinate
        # lost the sign election -- shares no non-zero coordinate with the factor-space
        # merge and carries no sign information. Averaging its NaN propagated to the whole
        # model: Gemma-3-12B reported `sign agreement nan` off 27 good samples. Skip those
        # and say how many, rather than reporting nothing.
        good = [r[1] for r in rs if r[1] == r[1]]
        sg = sum(good)/len(good) if good else float("nan")
        skipped = len(rs) - len(good)
        out[name] = dict(cosine=round(cos, 4),
                         sign_agree=None if not good else round(sg, 4),
                         n=len(rs), n_sign=len(good), skipped_degenerate=skipped)
        note = "" if not skipped else f", {skipped} degenerate module(s) excluded from sign"
        print(f"  {name:10s} factor-space vs update-space:  cosine {cos:+.3f}   "
              f"sign agreement {sg:.3f}   ({len(rs)} samples{note})")

    f = ROOT/f"results/analysis/pipeline/merge_space_{a.model}.json"
    f.write_text(json.dumps(out, indent=2)); print(f"\nwrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
