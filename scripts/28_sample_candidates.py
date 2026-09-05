#!/usr/bin/env python
"""Lever 2b, step 1 — sample N candidate answers per item and label each against gold.

The self-consistency read (log/transfer/2026-09-04_self-consistency-and-seed-band.md) found
`tuned_L0` at 0.43 greedy but 0.56 any-of-8: the right answer is usually IN the sample set and
the plurality vote cannot find it. This script materialises those sample sets so a selector
can be trained and evaluated on them:

  * `--split train` / `--split val` — rows from the training pairs (data.load_pairs, the
    quarantine-checked entry point). This is the SELECTOR'S training data. It is sampled
    from the same adapter that will be reranked, so the candidate distribution matches.
  * `--split heldout` — the held-out eval items (data.load_eval_items, no H1). The
    selector is scored here and only here.

Every sample carries vLLM's cumulative log-probability so that "rerank by the generator's
own likelihood" — the zero-training selector — is available as the control the trained
verifier has to beat. A greedy completion is stored as sample_idx = -1 so greedy, vote,
any-of-N, likelihood-rerank and verifier-rerank all come from ONE parquet.

    python scripts/slurm/submit.py --partition h200 --time 02:00:00 --argv \
        scripts/28_sample_candidates.py --model codellama-7b \
        --adapter runs/adapters/codellama-7b/python/L0_r32_s17/best --tag tuned_L0 \
        --split train --n 8
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import data, scoring  # noqa: E402
from obtune.config import GLOBAL_SEED, RUNS_DIR, load_config  # noqa: E402
from obtune.eval_vllm import Engine, SystemSpec, drop_overlong, render_prompts  # noqa: E402
from obtune.paths import TRAINABLE_CONDITIONS  # noqa: E402
from obtune.schema import EvalItem  # noqa: E402

SIX = ["L0", "L1b", "L1r", "L2", "S1", "S2"]


def out_path(model: str, tag: str, split: str) -> Path:
    return RUNS_DIR / "candidates" / model / tag / f"{split}.parquet"


def load_items(split: str, conditions: list[str], language: str) -> list[EvalItem]:
    if split == "heldout":
        return data.load_eval_items(conditions, language, source="heldout",
                                    script="28_sample_candidates")
    rows = data.load_pairs(conditions, language, splits=[split])
    return [
        EvalItem(item_id=r.item_id, program_id=r.program_id, dataset="A", condition=r.condition,
                 language=r.language, code=r.code, entry_point=r.entry_point,
                 args_repr=r.args_repr, output_repr=r.output_repr)
        for r in rows
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter", default=None, help="LoRA path; omit for the untuned base")
    ap.add_argument("--tag", required=True, help="system name for the output dir, e.g. tuned_L0")
    ap.add_argument("--split", required=True, choices=["train", "val", "heldout"])
    ap.add_argument("--conditions", nargs="*", default=SIX)
    ap.add_argument("--language", default="python")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--seed", type=int, default=GLOBAL_SEED)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if "H1" in args.conditions or any(c not in TRAINABLE_CONDITIONS for c in args.conditions):
        raise SystemExit("candidates are sampled on trainable conditions only (CLAUDE.md §3.2)")

    import pandas as pd
    from vllm import SamplingParams

    mcfg = load_config("models.yaml")["models"][args.model]
    ecfg = dict(load_config("eval/_base_eval.yaml").get("engine") or {})
    ecfg.setdefault("gpu_memory_utilization", 0.85)
    items = load_items(args.split, args.conditions, args.language)
    if args.limit:
        items = items[: args.limit]
    print(f"[28] {args.split}: {len(items)} items over {args.conditions}", flush=True)

    engine = Engine(mcfg["hf_id"], ecfg)
    system = SystemSpec(name=args.tag, arch="per_type" if args.adapter else "none",
                        adapter=args.adapter)
    texts = render_prompts(items, system, engine.tokenizer)
    # Same rule as eval_vllm: one over-long prompt raises inside vLLM and kills the
    # whole job (heldout job 377858 died on an 8,193-token item). Drop and record.
    items, texts, dropped = drop_overlong(
        items, texts, engine.tokenizer,
        max_model_len=int(ecfg.get("max_model_len", 8192)), max_new_tokens=args.max_tokens)
    if dropped:
        print(f"[28] dropped {len(dropped)} over-long prompts: "
              f"{[d['item_id'] for d in dropped]}", flush=True)
    lora = engine.lora_request(args.adapter)
    stop = ["\n\n", "```"]
    t0 = time.time()
    sampled = engine.llm.generate(
        texts,
        SamplingParams(temperature=args.temperature, top_p=args.top_p, n=args.n,
                       max_tokens=args.max_tokens, stop=stop, seed=args.seed, logprobs=0),
        lora_request=lora, use_tqdm=True,
    )
    greedy = engine.llm.generate(
        texts,
        SamplingParams(temperature=0.0, n=1, max_tokens=args.max_tokens, stop=stop, logprobs=0),
        lora_request=lora, use_tqdm=True,
    )
    print(f"[28] generated in {time.time() - t0:.0f}s", flush=True)

    rows = []
    for it, so, go in zip(items, sampled, greedy):
        outs = [(-1, go.outputs[0])] + list(enumerate(so.outputs))
        for idx, c in outs:
            g = scoring.grade(c.text, it.output_repr, it.language, scoring.DEFAULT_FLOAT_TOL)
            rows.append({
                "item_id": it.item_id, "program_id": it.program_id, "condition": it.condition,
                "split": args.split, "code": it.code, "entry_point": it.entry_point,
                "args_repr": it.args_repr, "gold": it.output_repr, "sample_idx": idx,
                "text": c.text, "pred_norm": g.pred_norm, "n_tokens": len(c.token_ids),
                "cum_logprob": float(c.cumulative_logprob) if c.cumulative_logprob is not None else float("nan"),
                "correct": int(g.correct), "parse_ok": int(g.parse_ok), "format_fail": int(g.format_fail),
            })
    df = pd.DataFrame(rows)
    out = out_path(args.model, args.tag, args.split)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)

    s = df[df.sample_idx >= 0]
    per = s.groupby("item_id")["correct"]
    summary = {
        "model": args.model, "adapter": args.adapter, "split": args.split, "n_items": len(items),
        "n": args.n, "temperature": args.temperature, "seed": args.seed,
        "greedy_acc": float(df[df.sample_idx == -1]["correct"].mean()),
        "sample_acc": float(s["correct"].mean()),
        "any_of_n": float(per.max().mean()),
        "all_of_n": float(per.min().mean()),
        "pos_rate_among_samples": float(s["correct"].mean()),
        "dropped_overlong": dropped,
        "elapsed_s": round(time.time() - t0, 1),
        "out": str(out),
    }
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2))
    print("[28] " + json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
