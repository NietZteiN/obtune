#!/usr/bin/env python
"""Training-free attention steering: is the benefit of removing inert code about ATTENTION?

    python scripts/attn/31_steer.py --system base --condition S2

WHY THIS EXISTS
---------------
Deleting provably-inert code helps, and the effect is large and well-powered: symbolic dead-code
elimination is worth **+4.74 pts** to `base` on `S2` [+3.12, +6.24], n=1667. But DELETION changes
two things at once:

  (a) the distracting tokens are gone, so no attention can land on them; and
  (b) the sequence is SHORTER, so every surviving token sits closer to the answer position and the
      softmax has fewer competitors to spread mass over.

Every normalization result in this project — and, as far as we can tell, the deobfuscation
literature's normalization baselines generally — confounds those two. Masking separates them. The
model is shown the byte-identical original program; every token keeps its position and its
neighbours; the only thing that changes is that attention to the inert KEY positions is
suppressed. The spans are the same ones `normalize.inert` deletes, so the two arms differ in
exactly one respect by construction.

PRE-REGISTERED PREDICTIONS, fixed before this ran
-------------------------------------------------
Note the sign is the OPPOSITE of the 2026-08-26 identifier knockout. There, the suppressed tokens
were ones the answer depends on, and suppressing them HURT `base` (delta_logp −0.089
[−0.158, −0.023]). Here the suppressed tokens are provably irrelevant, so:

  * **`base` on `S2`/`S4`: delta_logp > 0.** If the model is being distracted by inert material,
    refusing to let it look there should HELP. This is the claim; a null or a negative refutes it.
  * **`tuned_S2` on `S2`: delta_logp ≈ 0.** It has already learned to ignore this material
    (2026-08-26 knockout; and adding symbolic DCE to it is worth +0.06 [−0.96, +1.08]), so
    forbidding what it already declines to do should change nothing. This is the cell that makes
    the prediction falsifiable rather than a one-way bet.
  * **`L0` (no inert material, so an empty mask): delta_logp == 0 exactly**, for every system. A
    non-zero value here would mean the mask is firing on live code and the whole arm is void.

The readout is teacher-forced log P(gold), not exact-match accuracy — the 2026-08-26 lesson, where
a 12-cell accuracy sweep was null purely because `base` sits near the floor at ~22 % and binary
hit/miss has no headroom to register the manipulation. `--mode generate` is available for a
confirmatory accuracy read once the sign is known.

NO H1 IS READ HERE.
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--system", required=True)
    ap.add_argument("--condition", required=True)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--max-items", type=int, default=150)
    ap.add_argument("--layers", type=int, nargs="*", default=[4, 9, 14, 19, 23, 27])
    ap.add_argument("--classes", nargs="*", default=["inert"])
    ap.add_argument("--mode", choices=["score", "generate"], default="score")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--out", default="results/attn/steer")
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args(argv)

    from obtune.attention.knockout import (KnockoutSpec, evaluate_with_knockout,
                                           inert_key_mask, score_with_knockout)
    from obtune.eval_hf import _load_model
    from obtune.provenance import RunManifest
    from obtune.seedutil import set_seed

    set_seed(args.seed)

    items = []
    with open(f"data/eval/heldout/items/{args.condition}/{args.language}.jsonl") as f:
        for line in f:
            items.append(json.loads(line))
            if len(items) >= args.max_items:
                break

    # COVERAGE FIRST, before a GPU is touched. A mask that fires on nothing would produce a
    # perfect null that looks like a scientific result but is an empty intervention, and the
    # `L0` control cell is EXPECTED to be empty — so the two have to be distinguishable in the
    # output rather than inferred later.
    from obtune.normalize.inert import inert_spans
    n_with_dead = sum(1 for it in items if inert_spans(it["code"], it.get("entry_point") or ""))
    frac_dead = st.mean([
        sum(b - a for a, b in inert_spans(it["code"], it.get("entry_point") or ""))
        / max(1, len(it["code"])) for it in items])
    print(f"[steer] {args.system}/{args.condition}: {n_with_dead}/{len(items)} items carry "
          f"provably-inert code, mean {100 * frac_dead:.1f}% of characters")

    model, tok, _ = _load_model(args.model, args.adapter, "bfloat16", "cuda")
    spec = KnockoutSpec(layers=tuple(args.layers), classes=tuple(args.classes)).validate()

    tag = args.tag or "_".join(args.classes)
    outdir = ROOT / args.out
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.model}__{args.language}__{args.system}__{args.condition}__{tag}__{args.mode}"

    if args.mode == "score":
        rows = score_with_knockout(model, tok, items, spec)
        n = len(rows)
        dl = [r["delta_logp"] for r in rows]
        dlt = [r["delta_logp_per_token"] for r in rows]
        summary = {
            "system": args.system, "condition": args.condition, "model": args.model,
            "mode": "score", "classes": list(args.classes), "adapter": args.adapter,
            "layers": args.layers, "n_items": n, "seed": args.seed,
            "n_items_with_inert_code": n_with_dead,
            "mean_frac_chars_inert": frac_dead,
            "mean_logp_clean": st.mean(r["logp_clean"] for r in rows) if n else 0.0,
            "mean_logp_steered": st.mean(r["logp_knockout"] for r in rows) if n else 0.0,
            # POSITIVE = suppressing attention to inert code HELPED. Opposite sign convention to
            # the identifier knockout, and deliberately so: see the module docstring.
            "mean_delta_logp": st.mean(dl) if n else 0.0,
            "mean_delta_logp_per_token": st.mean(dlt) if n else 0.0,
            "n_improved": sum(1 for d in dl if d > 0),
            "n_worsened": sum(1 for d in dl if d < 0),
            "n_unchanged": sum(1 for d in dl if d == 0),
        }
    else:
        rows = evaluate_with_knockout(model, tok, items, spec)
        n = len(rows)
        acc_c = st.mean(1.0 if r.get("correct_clean") else 0.0 for r in rows) if n else 0.0
        acc_k = st.mean(1.0 if r.get("correct_knockout") else 0.0 for r in rows) if n else 0.0
        summary = {
            "system": args.system, "condition": args.condition, "model": args.model,
            "mode": "generate", "classes": list(args.classes), "adapter": args.adapter,
            "layers": args.layers, "n_items": n, "seed": args.seed,
            "n_items_with_inert_code": n_with_dead,
            "acc_clean": acc_c, "acc_steered": acc_k, "delta_acc": acc_k - acc_c,
        }

    (outdir / f"{stem}.rows.json").write_text(json.dumps(rows, indent=2))
    (outdir / f"{stem}.json").write_text(json.dumps(summary, indent=2))
    from obtune.config import load_config
    RunManifest(
        experiment="rq3/steer", run_id=f"{args.system}:{args.condition}:{tag}",
        seed=args.seed, config_path="configs/models.yaml",
        config_resolved={"spec": vars(args)},
        model_hf_id=load_config("models.yaml")["models"][args.model]["hf_id"],
        adapter={"path": args.adapter} if args.adapter else None,
    ).hash_scripts(["src/obtune/attention/knockout.py",
                    "src/obtune/normalize/inert.py",
                    "scripts/attn/31_steer.py"]).capture_git().finalize().write(
        outdir / f"{stem}.manifest.json")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
