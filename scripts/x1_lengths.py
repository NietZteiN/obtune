#!/usr/bin/env python
"""Token-length audit for a pair bank against a model's max_seq_len (silent-failure check §4.8).

    python scripts/slurm/submit.py --partition dev --gres none --cpus 4 --mem 16G --time 00:20:00 \
        --argv scripts/x1_lengths.py --conditions X1 --model codellama-7b
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from obtune.config import load_config
from obtune import data, paths
from obtune.prompts import build_example


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", nargs="+", default=["X1"])
    ap.add_argument("--model", default="codellama-7b")
    ap.add_argument("--aug-tag", default=None)
    args = ap.parse_args()
    from transformers import AutoTokenizer
    mcfg = load_config("models.yaml")["models"][args.model]
    tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    cap = int(mcfg["max_seq_len"])
    for cond in args.conditions:
        rows = data.load_pairs([cond], "python", splits=["train"],
                               augment_tags=[args.aug_tag] if args.aug_tag else None)
        texts = []
        for r in rows:
            ex = build_example(r.model_dump())
            texts.append(tok.apply_chat_template(list(ex["prompt"]) + list(ex["completion"]), tokenize=False))
        lens = sorted(len(x) for x in tok(texts, add_special_tokens=False)["input_ids"])
        n = len(lens); over = sum(l > cap for l in lens)
        print(json.dumps({"condition": cond, "model": args.model, "n": n, "p50": lens[n // 2],
                          "p95": lens[int(0.95 * n)], "max": lens[-1], "max_seq_len": cap,
                          "n_over": over, "truncation_rate": round(over / n, 4)}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
