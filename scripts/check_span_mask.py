#!/usr/bin/env python
"""Gate for lever 3b: does align.resolve_span_mask recover exactly the code span?

Renders real train rows through prompts.build_example + the chat template (what TRL
builds), tokenizes, applies the mask, and compares the decoded masked tokens to the
row's `code` after whitespace normalisation. Prints per-condition recall/precision on
characters; fails if any condition drops below 0.98 recall."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import data, prompts  # noqa: E402
from obtune.align import resolve_span_mask  # noqa: E402
from obtune.config import load_config  # noqa: E402


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    import torch
    from transformers import AutoTokenizer

    model = sys.argv[1] if len(sys.argv) > 1 else "codellama-7b"
    hf_id = load_config("models.yaml")["models"][model]["hf_id"]
    tok = AutoTokenizer.from_pretrained(hf_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    ok = True
    for cond in ["L0", "L1b", "L1r", "L2", "S1", "S2"]:
        rows = data.load_pairs([cond], "python", splits=["train"])[:40]
        texts = []
        for r in rows:
            ex = prompts.build_example(r.model_dump())
            texts.append(tok.apply_chat_template(ex["prompt"], tokenize=False, add_generation_prompt=True)
                         + ex["completion"][0]["content"])
        enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False)
        mask = resolve_span_mask(enc["input_ids"], tok)
        rec, prec, n_tok = [], [], []
        for i, r in enumerate(rows):
            ids = [t for t, m in zip(enc["input_ids"][i].tolist(), mask[i].tolist()) if m > 0]
            got, want = norm(tok.decode(ids)), norm(r.code)
            # char-level containment: the decoded span may carry a leading/trailing
            # newline from a neighbouring token; anything more is a real miss.
            common = len(want) if want in got else max(
                len(want[j:]) for j in range(len(want)) if want[j:] in got) if want else 0
            rec.append(common / max(1, len(want))); prec.append(common / max(1, len(got))); n_tok.append(len(ids))
        s = {"cond": cond, "n": len(rows), "recall": round(sum(rec) / len(rec), 4),
             "precision": round(sum(prec) / len(prec), 4), "tok_mean": round(sum(n_tok) / len(n_tok), 1),
             "min_recall": round(min(rec), 4)}
        print(json.dumps(s), flush=True)
        if s["recall"] < 0.98 or s["precision"] < 0.95:
            ok = False
            print(f"  FAIL example: got={tok.decode([t for t, m in zip(enc['input_ids'][0].tolist(), mask[0].tolist()) if m > 0])[:300]!r}")
    print("SPAN MASK OK" if ok else "SPAN MASK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
