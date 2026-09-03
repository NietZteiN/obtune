#!/usr/bin/env python
"""Residual merge — stop diluting the part that makes a specialist a specialist. CPU only.

    python scripts/merge/25_residual_merge.py --plan
    python scripts/merge/25_residual_merge.py

WHY
---
The 2026-08-17 decomposition (docs/REPORT_2026-08-17_geometry-and-attempted-repairs.md §3.1) found
that **52-70 % of every specialist's task vector points along the clean-code direction dW_L0** — the
bulk of what fine-tuning buys is task acquisition, not transform inversion. The remainder is real
and clusters by family (residual-residual cosine 0.284 mean; within-family pairs L1b|L2 0.451 and
S2|S4 0.438 against cross-family L1r|S4 0.174), but it is a minority direction.

A uniform merge averages BOTH parts at 1/n. The shared part is agreed by every expert so it survives
intact; the residuals partially cancel. Measured: ||mean resid|| / mean||resid|| = 0.6255, i.e. a
uniform merge throws away ~37 % of each specialist-specific update by norm while keeping all of the
part `tuned_L0` already had. That is a mechanical explanation for why every merge in this project
lands near the clean-code control.

THE ARM
-------
Ask for the shared component ONCE at full strength and the residuals UNDILUTED:

    dW_target = dW_L0 + gamma * (1/n) * sum_c resid_c ,   resid_c = dW_c - s_c * dW_L0
                                                          s_c = <dW_c,dW_L0> / <dW_L0,dW_L0>

Expanding is the whole trick — it collapses to a plain LINEAR COMBINATION of the original vectors:

    w_L0 = 1 - (gamma/n) * sum_c s_c        w_c = gamma/n

so no residual is ever materialized, no new merge algorithm is needed, and the rank never grows.
`MergeSpec` already accepts explicit `weights`. This matters because exact task arithmetic cannot
be used here at all: `taskvec.combine`'s `combination_type="cat"` SUMS ranks, so two r32 experts
already hit vLLM's `max_lora_rank: 64` and eight would need r256.

`gamma = 1/0.6255 = 1.599` is chosen to restore a single specialist's residual magnitude — not
tuned, computed. With sum_c s_c = 4.181 over 7 specialists that gives w_L0 = +0.045 and w_c = +0.228
(against uniform 0.125): **up-weight every specialist ~1.8x and drop the clean-code ingredient,
because the shared direction is already supplied by the specialists themselves.**

The coefficients are RECOMPUTED here from the safetensors rather than hardcoded, so the arm cannot
silently drift from the bank it describes; the resolved values land in the run manifest.

WHAT WOULD MAKE IT A RESULT, AND WHAT WOULD NOT
----------------------------------------------
Registered before the eval runs:
  * If it beats `merge_dare_ties` (45.0 mean on the six trainable conditions, Grid B) outside the
    1.32-pt seed band, undiluted residuals are worth keeping and this is the project's first
    POSITIVE method result — one adapter, no router, closer to specialist accuracy.
  * If it is flat, the residuals do not carry recoverable per-condition value even when preserved,
    which converts §12.10's "no combination strategy helps" from an empirical sweep into a
    statement with a measured mechanism behind it.
  * It is NOT expected to fix H1/OOD. Routing is already capped by the specialists themselves
    (+3.5 pts, §5.2) and nothing in this project has moved the held-out obfuscator. The claim on
    offer is about merging without dilution — a deployment claim, not an invariance claim.

Both merge algorithms and both densities that matter are built: `ties` and `dare_ties` at d=0.5
(matching the §5.2 headline merges) and d=0.3 (the sweep winner, best on 5 of 6 conditions).

CPU only — `merge_adapters` loads the base with `device_map=None`. Zero GPU.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import RUNS_DIR, load_config  # noqa: E402
from obtune.merge_adapters import MERGE_ROOT, MergeSpec, merge_adapters  # noqa: E402
from obtune.merge_geometry import _inner, load_expert  # noqa: E402
from obtune.provenance import RunManifest  # noqa: E402

# Set from --model/--language at startup. These were module-level constants pinned to
# qwen25c-1.5b, which is the DANGEROUS form of the pin: the Qwen adapters still exist on
# disk, so this script would have silently merged THEM and written the result under the
# current panel's name -- no error, wrong ingredients. A lint that checks argparse defaults
# and HF ids cannot see a constant holding a model key.
MODEL, LANG, RANK = None, None, 32
#: The MERGE algorithm's seed — it fixes DARE's Bernoulli drop mask and must stay constant while
#: the EXPERT-BANK seed (`--seed`) varies, or a bank comparison would also change the mask and the
#: two effects could not be separated. Deliberately NOT the same knob as `--seed`.
MERGE_SEED = 17
#: `L0` FIRST — it is the shared direction every other vector is projected onto, and the weight
#: order must match this list exactly.
#: DEFAULT IS THE 6-INGREDIENT LADDER, matching `configs/merge/ties_v1.yaml`'s
#: `adapters: [L0, L1b, L1r, L2, S1, S2]`. The first build of this arm used 8 (adding S3/S4), which
#: made it ingredient-mismatched against the `merge_dare_ties` it was compared to — so a win could
#: have been the two extra experts rather than the reweighting. Match by default; `--conditions`
#: overrides so the 8-ingredient variant can still be built deliberately as its own arm.
#: The seed-42 bank has only these six (no S3/S4), which is the other reason 6 is the default:
#: it is the largest ladder that exists at BOTH seeds, hence the only one a replication can use.
CONDS_DEFAULT = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
COMBINATIONS = ["ties", "dare_ties"]
DENSITIES = [0.3, 0.5]


def adapter_paths(conds: list[str], seed: int) -> dict[str, str]:
    return {c: str(RUNS_DIR / "adapters" / MODEL / LANG / f"{c}_r{RANK}_s{seed}" / "best")
            for c in conds}


def residual_weights(paths: dict[str, str], conds: list[str]) -> tuple[list[float], dict]:
    """Recompute the linear-combination coefficients from the safetensors.

    Pooled over all 196 target modules: the per-module `s_c` differ, but the merge driver applies
    ONE scalar per ingredient, so a pooled projection is the faithful scalar approximation. The
    per-module spread is recorded in the diagnostics so a later reader can judge that choice.
    """
    fac = {c: load_expert(Path(paths[c]), c) for c in conds}
    mods = list(fac["L0"])
    L0 = fac["L0"]
    n0 = sum(_inner(L0[m], L0[m]) for m in mods)
    sp = conds[1:]
    s = {c: sum(_inner(fac[c][m], L0[m]) for m in mods) / n0 for c in sp}

    def rin(a: str, b: str) -> float:  # <resid_a, resid_b>
        return (sum(_inner(fac[a][m], fac[b][m]) for m in mods)
                - s[a] * sum(_inner(fac[b][m], L0[m]) for m in mods)
                - s[b] * sum(_inner(fac[a][m], L0[m]) for m in mods)
                + s[a] * s[b] * n0)

    n = len(sp)
    mean_r = np.sqrt(sum(rin(a, b) for a in sp for b in sp) / n**2)
    single_r = float(np.mean([np.sqrt(rin(c, c)) for c in sp]))
    ratio = mean_r / single_r          # 0.6255 measured; sqrt(n)/n = 0.378 if orthogonal
    gamma = 1.0 / ratio
    w_sp = gamma / n
    w_L0 = 1.0 - (gamma / n) * sum(s.values())
    weights = [w_L0] + [w_sp] * n
    diag = {"s_c": s, "sum_s_c": float(sum(s.values())), "n_specialists": n,
            "mean_resid_norm": float(mean_r), "single_resid_norm": single_r,
            "dilution_ratio_measured": float(ratio),
            "dilution_ratio_if_orthogonal": float(np.sqrt(n) / n),
            "gamma": float(gamma), "w_L0": float(w_L0), "w_specialist": float(w_sp),
            "note": "weights order matches the --conditions list; derivation in the module docstring",
            "conditions": list(conds)}
    return weights, diag


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="key in configs/models.yaml")
    ap.add_argument("--language", default="python")
    ap.add_argument("--plan", action="store_true", help="print weights + ingredients, build nothing")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=17, help="expert-bank seed (42 for the replication)")
    ap.add_argument("--conditions", nargs="*", default=None,
                    help="ingredient ladder; L0 FIRST. Defaults to the 6 that ties_v1.yaml merges "
                         "and that exist at both seeds.")
    ap.add_argument("--uniform", action="store_true",
                    help="use UNIFORM weights over the same ladder — the control that isolates "
                         "ingredient count from the residual reweighting")
    ap.add_argument("--tag", default=None, help="output name suffix; defaults to n<k>_s<seed>")
    args = ap.parse_args(argv)
    global MODEL, LANG, RANK
    MODEL, LANG = args.model, getattr(args, 'language', 'python')
    RANK = getattr(args, 'rank', 32)

    conds = args.conditions or list(CONDS_DEFAULT)
    if conds[0] != "L0":
        print("refusing: L0 must be first — it is the direction everything projects onto",
              file=sys.stderr)
        return 1
    paths = adapter_paths(conds, args.seed)
    missing = {c: p for c, p in paths.items() if not Path(p).exists()}
    if missing:
        print(f"refusing: {len(missing)} adapter(s) absent ({', '.join(missing)})", file=sys.stderr)
        return 1

    weights, diag = residual_weights(paths, conds)
    if args.uniform:
        weights = [1.0 / len(conds)] * len(conds)
        diag["uniform_control"] = True
    print(f"bank: {len(conds)} ingredients at seed {args.seed}"
          f"{'  [UNIFORM CONTROL]' if args.uniform else '  [residual weights]'}")
    for c, w in zip(conds, weights):
        print(f"  {c:5s} w={w:+.4f}" + ("   <- shared direction, supplied once" if c == "L0" else ""))
    print(f"\n  gamma={diag['gamma']:.3f}  measured dilution ratio={diag['dilution_ratio_measured']:.4f}"
          f"  (orthogonal bound {diag['dilution_ratio_if_orthogonal']:.4f})")
    if args.plan:
        print(f"\nwould build {len(COMBINATIONS) * len(DENSITIES)} merges: "
              f"{COMBINATIONS} x d={DENSITIES}")
        return 0

    cfg = load_config("merge/ties_v1.yaml")   # same recipe as the headline merges; only weights differ
    base_id = load_config("models.yaml")["models"][MODEL]["hf_id"]
    for comb in COMBINATIONS:
        for d in DENSITIES:
            stem = args.tag or f"n{len(conds)}_s{args.seed}" + ("_uniform" if args.uniform else "")
            tag = f"{stem}_d{str(d).replace('.', 'p')}"
            spec = MergeSpec(base_model_id=base_id, adapter_paths=paths, combination_type=comb,
                             density=d, weights=weights, seed=int(cfg.get("seed", MERGE_SEED)))
            out_dir = MERGE_ROOT / f"{MODEL}_{LANG}_residual_{comb}" / tag
            mani = RunManifest(
                experiment="residual_merge", run_id=f"residual_{comb}_{tag}",
                seed=spec.seed, config_path=str(cfg["_config_path"]),
                config_resolved={**cfg, "combination_type": comb, "density": d,
                                 "adapter_paths": paths, "weights": weights,
                                 "conditions": conds, "bank_seed": args.seed,
                                 "uniform_control": bool(args.uniform)},
                model_hf_id=base_id,
            ).hash_scripts(["src/obtune/merge_adapters.py",
                            "scripts/merge/25_residual_merge.py"]).capture_git()
            p = merge_adapters(spec, out_dir, dtype=args.dtype)
            mani.extra["merges"] = [{"density": d, "path": str(p), "combination_type": comb}]
            mani.extra["residual_decomposition"] = diag
            mani.finalize().write(out_dir)
            print(f"  {comb:10s} {tag}  -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
