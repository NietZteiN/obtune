#!/usr/bin/env python
"""Approximate unlearning of the forward direction, by task-vector negation (Part IV, Stage 1).

    python scripts/unlearn/20_negation_sweep.py --dry-run
    python scripts/unlearn/20_negation_sweep.py --enqueue

WHY APPROXIMATE AND NOT EXACT
-----------------------------
Exact unlearning is DEFINED as retraining on the retained data only. For "FLIP minus the
forward examples" that is training on reverse alone — which is the REV arm, whose reverse
performance is therefore guaranteed to survive. Exact deletion can never collapse reverse, so
it cannot test whether the two directions share representation. The signature relocates to:
**approximate unlearning over-removes relative to exact**, and the size of the over-removal
measures entanglement.

    U(lambda) = FLIP - lambda * FWD

`taskvec` makes this EXACT weight-space arithmetic rather than an approximation of one:
dW = (alpha/r) B@A with use_dora/use_rslora false, so scaling lora_B by a scalar scales the
whole delta (`taskvec.py:4-14`). `_assert_plain_lora` refuses if that ever stops holding.
`combination_type="cat"` avoids the cross-term trap that `linear` falls into. Two r=32
ingredients concatenate to rank 64, exactly the default `max_lora_rank`.

THE STATISTIC
-------------
    Over-removal = Rev(REV) - Rev(FLIP->U)

interpretable ONLY at an operating point where both preconditions hold, and both are reported
beside it:

  1. Forward removal reached gold: Fwd(U(lambda*)) ~= Fwd(base). If forward was not actually
     removed, nothing about reverse is informative.
  2. No collateral collapse: HumanEval+ and L0 intact. Otherwise the model is merely damaged
     and "reverse fell" says nothing about shared structure. This is now checkable: the
     HumanEval+ scorer was repaired on 2026-08-10 (it had been silently reporting 0.0 for
     every arm), and it already shows these arms losing up to 34 points of general code
     ability — so collateral damage is a live risk, not a formality.

THE ASSET
---------
Forget and retain sets are CONTENT-IDENTICAL — the same programs, the same variants, differing
only in which side is the question. Every "the forget set was just harder/rarer" confound is
eliminated by construction, which no capability-unlearning benchmark can currently claim.

Note the wording: REV is exact unlearning of the DIRECTION, not of the DATA — a `rev` row
contains the same two programs as its `gen` twin. Do not write "data deletion".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import CONFIG_DIR, RUNS_DIR, load_config  # noqa: E402
from obtune.taskvec import TASKVEC_ROOT, combine  # noqa: E402

#: lambda=0 must reproduce FLIP exactly — it is the built-in correctness check on the whole
#: construction, and is evaluated rather than assumed.
DEFAULT_LAMBDAS = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5)

ARMS = {
    "flip": "runs/adapters_srh/{model}/{lang}/all5_flip_r32_s17/final",
    "sft": "runs/adapters_cft/{model}/{lang}/sft_r32_s17/final",
    "rev": "runs/adapters_srh/{model}/{lang}/all5_rev_r32_s17/final",
    "mix50": "runs/adapters_srh/{model}/{lang}/all5_mix50_r32_s17/final",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--lambdas", nargs="*", type=float, default=list(DEFAULT_LAMBDAS))
    ap.add_argument("--target", default="flip",
                    help="arm to unlearn FROM (flip primary; fwd2x/mix50 are controls)")
    ap.add_argument("--subtract", default="sft", help="arm to unlearn (the forward direction)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--enqueue", action="store_true")
    args = ap.parse_args()

    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)[args.model]["hf_id"]
    resolved = {k: ROOT / v.format(model=args.model, lang=args.language)
                for k, v in ARMS.items()}
    missing = {k: str(p) for k, p in resolved.items() if not p.exists()}
    if missing:
        raise SystemExit(f"missing arm(s): {missing}")

    tgt, sub = resolved[args.target], resolved[args.subtract]
    out_root = TASKVEC_ROOT / "unlearn" / args.model / args.language
    plan = [{"lam": lam,
             "out": str(out_root / f"{args.target}_minus_{args.subtract}_lam{lam:g}".replace(".", "p"))}
            for lam in args.lambdas]

    print(f"[unlearn] U(lambda) = {args.target} - lambda * {args.subtract}")
    print(f"[unlearn] {len(plan)} point(s): {[p['lam'] for p in plan]}")
    for p in plan:
        print(f"    lambda={p['lam']:<5g} -> {Path(p['out']).name}")
    if args.dry_run:
        print("[unlearn] --dry-run: nothing written")
        return 0

    built = []
    for p in plan:
        out = Path(p["out"])
        if (out / "adapter_model.safetensors").exists():
            print(f"[unlearn] exists, skipping: {out.name}")
            built.append(p)
            continue
        # A zero coefficient would still concatenate a rank-32 block of zeros, doubling the
        # rank for no effect; drop it so lambda=0 is literally FLIP re-emitted.
        ingredients = {str(tgt): 1.0}
        if p["lam"] != 0.0:
            ingredients[str(sub)] = -float(p["lam"])
        combine(hf_id, ingredients, out, max_lora_rank=64)
        print(f"[unlearn] built {out.name}  ingredients={ {Path(k).parent.name: v for k, v in ingredients.items()} }")
        built.append(p)

    # Scored by the SAME bidirectional harness as Experiment 1, so forward and reverse numbers
    # are directly comparable to the arms already reported rather than to a private scale.
    systems = {"base": None,
               "rev": str(resolved["rev"].relative_to(ROOT)),
               "flip": str(tgt.relative_to(ROOT)),
               "sft": str(sub.relative_to(ROOT))}
    for p in built:
        systems[f"u_lam{p['lam']:g}".replace(".", "p")] = str(Path(p["out"]).relative_to(ROOT))

    cfg_path = (CONFIG_DIR / "unlearn" /
                f"negation_{args.target}_minus_{args.subtract}_{args.model}_{args.language}.yaml")
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    body = [
        "# Generated by scripts/unlearn/20_negation_sweep.py — do not hand-edit.",
        "#",
        "# Approximate unlearning of the forward direction from FLIP, by exact task-vector",
        "# negation. `rev` is the exact-unlearning gold reference; `flip` and `sft` are the",
        "# endpoints. u_lam0 MUST reproduce flip — that is the built-in correctness check.",
        "#",
        "# No H1: this is entirely within trainable conditions and CLAUDE.md 3.2 grants H1",
        "# only two evaluation passes, both already spent.",
        "#",
        "# `_replace: [systems]` is load-bearing, not tidiness. Without it the parent's",
        "# `systems:` block MERGES into this one and the run silently gains a `cft` arm the",
        "# unlearning experiment never asked for. At 7B the inherited entry still pointed at",
        "# a 1.5B adapter, so a 1.5B LoRA was loaded onto a 7B base and reported under a real",
        "# arm's label — the 2026-08-10 run scored it 86.5% base-identical. At 1.5B the arm",
        "# was valid but spurious, and on 2026-08-11 it produced base-identical output on all",
        "# 3000 trials and killed four evaluations on the §4.2 adapter guard. The 7B configs",
        "# had been patched BY HAND to override `cft:`, in a file this generator overwrites.",
        "_extends: ../cft/eval/bidir_v1.yaml",
        "_replace: [systems]",
        "",
        f"model: {args.model}",
        f"run_tag: unlearn_{args.target}_minus_{args.subtract}_{args.language}",
        "",
        "systems:",
    ]
    for name, path in systems.items():
        body.append(f"  {name}: {'null' if path is None else path}")
    body += [
        "",
        "reverse_strategies: [simple]",
        "",
        "engine:",
        "  dtype: bfloat16",
        "  max_model_len: 4096",
        "  # rank 64: every U(lambda) is a `cat` of two r=32 ingredients.",
        "  max_lora_rank: 64",
        # Resident GPU slots, NOT total adapters: excess ones swap in from `max_cpu_loras`.
        # Capped at 8 because that is what the completed 7B evaluation used at this
        # gpu_memory_utilization; 11 rank-64 adapters resident beside a 7B base is a needless
        # OOM risk for a throughput gain we do not need.
        f"  max_loras: {min(8, len(systems))}",
        f"  max_cpu_loras: {max(16, len(systems) * 2)}",
        "  gpu_memory_utilization: 0.80",
        "  seed: 17",
        "",
    ]
    cfg_path.write_text("\n".join(body))
    print(f"[unlearn] wrote {cfg_path.relative_to(ROOT)} ({len(systems)} systems)")

    if args.enqueue:
        qdir = RUNS_DIR / "manifest" / "queued"
        qdir.mkdir(parents=True, exist_ok=True)
        jid = f"evalunlearn_{args.target}m{args.subtract}__{args.model}_{args.language}"
        (qdir / f"057_{jid}.json").write_text(json.dumps({
            "job_id": jid, "kind": "eval-cell",
            "argv": ["-m", "obtune.cft.evaluate", "--config",
                     f"unlearn/{cfg_path.name}"],
            "raw": False, "est_gpu_h": 1.5, "priority": 57,
            "meta": {"experiment": "srh/exp3-unlearning", "language": args.language,
                     "note": "approximate unlearning by exact task-vector negation"},
        }, indent=2))
        print(f"[unlearn] queued {jid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
