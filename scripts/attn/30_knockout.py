#!/usr/bin/env python
"""RQ3 causal step: is the S2 adapter's re-anchoring load-bearing, or incidental?

    python scripts/attn/30_knockout.py --system tuned_S2_s17 --condition S2 \
        --adapter runs/adapters/qwen25c-1.5b/python/S2_r32_s17/best

WHY
---
The 2026-08-18 sweep found that `tuned_S2_s17` moves attention off identifiers and onto
control/dataflow on the `S2` condition by +0.111 [+0.093, +0.131] — 2.6x the clean-code
control and 3.7x the `L1b` specialist, and specific to `S2`. That is a CORRELATION. CLAUDE.md
§3 is explicit that RQ3's causal claims wait for the knockout intervention.

THE INTERVENTION. `attention_knockout` adds a large negative bias to attention logits at
identifier KEY positions in the chosen layers, and each item is decoded twice: once clean,
once knocked out. If a model's accuracy depends on reading identifiers, suppressing them
costs accuracy; if it has learned to ignore them, it costs less.

PRE-REGISTERED PREDICTIONS, fixed before this ran:
  * ON `S2` (where the inert material lives): knockout damage (clean - knockout) should be
    SMALLER for `tuned_S2_s17` than for `base`. The adapter already attends less to those
    identifiers, so removing them takes away less that it was using. This is the directional
    claim the mechanism story rests on.
  * ON `L1r` (a renaming condition, the CONTRAST): every adapter shifted attention TOWARD
    identifiers there (sweep: `tuned_S2` -0.044, `tuned_L0` -0.031), because under renaming
    the identifiers are what changed. So knockout damage should be LARGER for the adapters
    than for `base` — the opposite sign from `S2`. A mechanism that only ever predicted "less
    damage" would be unfalsifiable; this is the cell that can embarrass it.
  * If damage is identical across systems on both conditions, the re-anchoring is incidental
    and the correlation carries no mechanism.

NOT a claim about `H1`. No quarantined item is read here. The link from "ignores inert
material on S2" to "transfers to H1" stays inferential until either an H1 attention read is
paid for or this knockout is repeated there.
"""
from __future__ import annotations
import argparse, json, sys
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
    # MANIPULATION CHECK. The identifier knockout produced ~0 damage for EVERY system including
    # `base` (-0.7 to +2.7 across 8 cells, all inside the 3.61-pt seed band). A manipulation that
    # moves no one's accuracy has not been shown to be a manipulation, so the null is uninformative
    # rather than evidence against the mechanism. Suppressing a class the task PROVABLY needs must
    # produce damage; if it does not, the intervention is broken and no knockout result can be read.
    # `--tag` keeps each variant in its own file so the identifier run is not overwritten.
    ap.add_argument("--classes", nargs="*", default=["identifier"])
    ap.add_argument("--tag", default=None)
    # `score` = teacher-forced log P(gold) under clean vs knocked attention. Use it, not
    # `generate`: the 2026-08-26 manipulation check showed exact-match accuracy has no headroom
    # at base's ~22% on obfuscated S2, so a working intervention (68% of outputs change) reads
    # as a null. Log-prob has no floor and is defined on items the model gets wrong.
    ap.add_argument("--mode", choices=["generate", "score"], default="score")
    ap.add_argument("--out", default="results/attn/knockout")
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args(argv)

    from obtune.attention.knockout import (KnockoutSpec, evaluate_with_knockout,
                                           score_with_knockout)
    from obtune.config import load_config
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

    model, tok, _ = _load_model(args.model, args.adapter, "bfloat16", "cuda")
    spec = KnockoutSpec(layers=tuple(args.layers), classes=tuple(args.classes)).validate()
    if args.mode == "score":
        rows = score_with_knockout(model, tok, items, spec)
        n = len(rows)
        import statistics as st
        dl = [r["delta_logp"] for r in rows]
        dlt = [r["delta_logp_per_token"] for r in rows]
        summary = {
            "system": args.system, "condition": args.condition, "model": args.model,
            "mode": "score", "classes": list(args.classes), "adapter": args.adapter,
            "n_items": n, "layers": args.layers,
            "mean_logp_clean": st.mean(r["logp_clean"] for r in rows) if n else 0.0,
            "mean_logp_knockout": st.mean(r["logp_knockout"] for r in rows) if n else 0.0,
            # NEGATIVE = the knockout hurt. This is the quantity the mechanism predicts.
            "mean_delta_logp": st.mean(dl) if n else 0.0,
            "median_delta_logp": st.median(dl) if n else 0.0,
            "mean_delta_logp_per_token": st.mean(dlt) if n else 0.0,
            "mean_keys_knocked": st.mean(r["n_knocked_keys"] for r in rows) if n else 0.0,
        }
        out = Path(args.out) / args.model / args.condition
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.system}{('__' + args.tag) if args.tag else ''}.json").write_text(
            json.dumps({"summary": summary, "rows": rows}, indent=1))
        RunManifest(
            experiment="rq3/knockout-score", run_id=f"{args.system}:{args.condition}",
            seed=args.seed, config_path="configs/models.yaml",
            config_resolved={"spec": vars(args)},
            model_hf_id=load_config("models.yaml")["models"][args.model]["hf_id"],
            adapter={"path": args.adapter} if args.adapter else None,
        ).hash_scripts(["src/obtune/attention/knockout.py",
                        "scripts/attn/30_knockout.py"]).capture_git().finalize().write(out)
        print(json.dumps(summary, indent=2))
        return 0

    rows = evaluate_with_knockout(model, tok, items, spec)

    n = len(rows)
    cc = sum(r["correct_clean"] for r in rows)
    ck = sum(r["correct_knockout"] for r in rows)
    summary = {
        "system": args.system, "condition": args.condition, "model": args.model,
        "classes": list(args.classes),
        "adapter": args.adapter, "n_items": n, "layers": args.layers,
        "acc_clean": cc / n if n else 0.0,
        "acc_knockout": ck / n if n else 0.0,
        # The quantity the predictions are about: accuracy LOST when identifier keys are
        # suppressed.
        "knockout_damage": (cc - ck) / n if n else 0.0,
        "mean_keys_knocked": sum(r["n_knocked_keys"] for r in rows) / n if n else 0.0,
    }
    out = Path(args.out) / args.model / args.condition
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.system}{('__' + args.tag) if args.tag else ''}.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
    RunManifest(
        experiment="rq3/knockout", run_id=f"{args.system}:{args.condition}", seed=args.seed,
        config_path="configs/models.yaml", config_resolved={"spec": vars(args)},
        model_hf_id=load_config("models.yaml")["models"][args.model]["hf_id"],
        adapter={"path": args.adapter} if args.adapter else None,
    ).hash_scripts(["src/obtune/attention/knockout.py",
                    "scripts/attn/30_knockout.py"]).capture_git().finalize().write(out)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
