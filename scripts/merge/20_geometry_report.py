#!/usr/bin/env python
"""Task-vector geometry vs training length — does interference grow with epochs?

    python scripts/merge/20_geometry_report.py                    # 3-epoch bank
    python scripts/merge/20_geometry_report.py --root runs/adapters_overtrain --conditions L1b S1 S2

Tests the mechanism in Horoi, Wolf, Belilovsky & Dziugaite (arXiv:2506.14126v2), "From
Memorization to Parameter Interference: How Overtraining Experts Harms Model Merging": late
fine-tuning is dominated by memorization of hard examples, which causes negative parameter
interference and degrades merging.

Measured on the 3-epoch bank (2026-08-10) the mechanism is ABSENT: norms grow +24 % but mean
pairwise cosine is flat (0.584 -> 0.592), coordinate sign-conflict FALLS (0.402 -> 0.391) and
TIES retention RISES (0.854 -> 0.861). `trainer_state.json` explains why — training loss is
still falling steadily at epoch 2.5 (0.90 -> 0.31 over 219 steps), so that bank never enters
the overtraining regime and cannot test the claim. The 9-epoch probe
(`configs/train/overtrain_qwen1.5b_py_*.yaml`) is what puts it in reach; this script is the
readout for both banks, so the comparison is like-for-like.

CPU only. Zero GPU. Everything is computed from safetensors already on disk.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.merge_geometry import (  # noqa: E402
    by_projection, cosine, load_expert, norms, pooled, sign_conflict,
)

#: Layers sampled for the dense sign statistics. Sign conflict is the ONE diagnostic that
#: needs a materialized dW, so it runs on a representative slice (early/mid/late) rather than
#: all 28 layers — the trend across depth is what matters, not a fourth decimal place.
SIGN_LAYERS = (0, 7, 14, 21, 27)


def epoch_checkpoints(adapter: Path) -> dict[int, str]:
    """Map epoch index -> checkpoint dir name, by step order.

    Step counts differ per condition (S1 bails on more programs, so it has fewer steps per
    epoch), so epochs are identified by rank rather than by absolute step number.
    """
    steps = sorted(int(p.name.split("-")[1]) for p in adapter.glob("checkpoint-*"))
    return {i + 1: f"checkpoint-{s}" for i, s in enumerate(steps)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="runs/adapters",
                    help="adapter bank root (use runs/adapters_overtrain for the 9-epoch probe)")
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--conditions", nargs="*",
                    default=["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"])
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--seeds", nargs="*", type=int, default=None,
                    help="cross-seed bank: label experts <cond>@s<seed> over conditions x seeds. "
                         "Needed for the L0-seed control (L0 at s17/s42/s101), where the three "
                         "'experts' differ only in seed and --seed cannot express that.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    base = ROOT / args.root / args.model / args.language
    if args.seeds:
        # Label carries the seed so `cosine_pairs` keys stay unambiguous; the same-condition
        # pairs are the point (they measure seed-to-seed geometry, i.e. the noise floor that
        # every cross-condition cosine should be read against).
        dirs = {f"{c}@s{s}": base / f"{c}_r{args.rank}_s{s}"
                for c in args.conditions for s in args.seeds}
    else:
        dirs = {c: base / f"{c}_r{args.rank}_s{args.seed}" for c in args.conditions}
    missing = [c for c, d in dirs.items() if not d.exists()]
    if missing:
        # Not an error: the 9-epoch probe deliberately covers only 3 conditions.
        print(f"[geometry] skipping absent conditions: {missing}", flush=True)
        for c in missing:
            dirs.pop(c)
    if len(dirs) < 2:
        raise SystemExit(f"need >=2 experts under {base}; found {sorted(dirs)}")

    ckpts = {c: epoch_checkpoints(d) for c, d in dirs.items()}
    n_epochs = min(len(v) for v in ckpts.values())
    if n_epochs < 1:
        raise SystemExit(f"no checkpoint-* dirs under {base}")
    conds = sorted(dirs)
    print(f"[geometry] {args.root}: {len(conds)} experts x {n_epochs} epochs -> {conds}")

    report: dict = {
        "root": args.root, "model": args.model, "language": args.language,
        "conditions": conds, "n_epochs": n_epochs, "sign_layers": list(SIGN_LAYERS),
        "epochs": {},
    }

    for e in range(1, n_epochs + 1):
        fac = {c: load_expert(dirs[c] / ckpts[c][e], c) for c in conds}
        nrm = {c: pooled(norms(f)) for c, f in fac.items()}
        cos = {f"{i}|{j}": pooled(cosine(fac[i], fac[j]))
               for i, j in itertools.combinations(conds, 2)}
        mods = [m for m in next(iter(fac.values()))
                if any(f".layers.{l}." in m for l in SIGN_LAYERS)]
        sc = sign_conflict(fac, modules=mods)
        conflict = {m: v["conflict"] for m, v in sc.items()}
        keep = {m: v["ties_keep"] for m, v in sc.items()}

        report["epochs"][str(e)] = {
            "checkpoints": {c: ckpts[c][e] for c in conds},
            "norm_mean": float(np.mean(list(nrm.values()))),
            "norm_per_condition": nrm,
            "cosine_mean": float(np.mean(list(cos.values()))),
            "cosine_min": float(min(cos.values())),
            "cosine_max": float(max(cos.values())),
            "cosine_pairs": cos,
            "sign_conflict_mean": float(np.mean(list(conflict.values()))),
            "ties_keep_mean": float(np.mean(list(keep.values()))),
            "sign_conflict_by_projection": by_projection(conflict),
            "ties_keep_by_projection": by_projection(keep),
        }
        print(f"  epoch {e}: ||dW||={report['epochs'][str(e)]['norm_mean']:.4f} "
              f"cos={report['epochs'][str(e)]['cosine_mean']:.4f} "
              f"conflict={report['epochs'][str(e)]['sign_conflict_mean']:.4f} "
              f"ties_keep={report['epochs'][str(e)]['ties_keep_mean']:.4f}", flush=True)
        del fac

    # The claim under test, reduced to two signed numbers so a later reader does not have to
    # re-derive it: interference is said to GROW with training.
    if n_epochs >= 2:
        first, last = report["epochs"]["1"], report["epochs"][str(n_epochs)]
        d_conf = last["sign_conflict_mean"] - first["sign_conflict_mean"]
        d_cos = last["cosine_mean"] - first["cosine_mean"]
        report["verdict"] = {
            "delta_sign_conflict": d_conf,
            "delta_cosine": d_cos,
            "interference_grows": bool(d_conf > 0.01),
            "note": ("Horoi et al. predict sign conflict rises with training. "
                     "delta<=0.01 means the mechanism is not present in this bank."),
        }
        print(f"\n[geometry] epochs 1->{n_epochs}: d(sign_conflict)={d_conf:+.4f} "
              f"d(cosine)={d_cos:+.4f} -> interference_grows="
              f"{report['verdict']['interference_grows']}")

    out = Path(args.out) if args.out else (
        ROOT / "results" / "merge_geometry" / f"{Path(args.root).name}_{args.model}_{args.language}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"[geometry] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
