"""Capture last-token attention rows from an HF model into the metrics.py npz contract.

WHY eager: `output_attentions=True` is only honoured by the eager attention path — SDPA
and flash return `None` for the probabilities (the reallocation repo's
`_forward_with_attn` raises on exactly that). Training/eval elsewhere in this project use
SDPA (configs/compute.yaml); this module overrides it *locally* and records the override
in the run manifest so the two are never confused.

Only the LAST query row is kept (metrics.py decision D1) — a [28, 12, 1500, 1500] fp32
attention tensor is ~2.4 GB per program, and there is nothing in RQ3 that reads the
earlier rows.

Requires `obtune.prompts.build_prompt(...) -> list[dict]` (chat messages). That module is
owned by a peer; ASSUMED INTERFACE:
    build_prompt(code=..., entry_point=..., args_repr=..., language=..., condition=...,
                 oracle=False) -> [{"role": "system"|"user", "content": str}, ...]
If it is missing, a minimal local prompt is used and the record's `extra` records that,
so a mismatch is visible in the parquet rather than silent.

GPU job — not runnable on the analysis box without a free device. Pin CUDA_VISIBLE_DEVICES
before invoking (CLAUDE.md: shared box, no scheduler).
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

from obtune.attention.metrics import ATTN_DIR, AttentionRecord, save_attention_npz
from obtune.attention.token_classes import classify_code
from obtune.config import load_config
from obtune.seedutil import set_seed

__all__ = ["build_prompt_text", "capture_record", "capture_many"]

_FALLBACK_PROMPT = (
    "You are given a {language} function. Compute its output for the call shown.\n"
    "Reply with only the output value.\n\n```{language}\n{code}\n```\n\n"
    "Call: {entry_point}{args_repr}\nOutput:"
)


def build_prompt_text(tokenizer, *, code: str, entry_point: str, args_repr: str,
                      language: str, condition: str) -> tuple[str, bool]:
    """Rendered prompt string + whether the project's prompts module supplied it."""
    try:
        from obtune.prompts import build_prompt  # peer-owned
    except Exception:
        text = _FALLBACK_PROMPT.format(language=language, code=code,
                                       entry_point=entry_point, args_repr=args_repr)
        return text, False
    msgs = build_prompt(code=code, entry_point=entry_point, args_repr=args_repr,
                        language=language, condition=condition, oracle=False)
    text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return text, True


def _locate_code(text: str, code: str) -> tuple[int, int]:
    """Character span of `code` inside the rendered prompt. Hard-fails if absent —
    a silently wrong offset would misclassify every token in the record."""
    i = text.find(code)
    if i >= 0:
        return i, i + len(code)
    stripped = code.strip()
    i = text.find(stripped)
    if i >= 0:
        return i, i + len(stripped)
    raise ValueError(
        "code block not found verbatim in the rendered prompt; the prompt template must "
        "insert the program unmodified or the char->token alignment is meaningless"
    )


def capture_record(
    model,
    tokenizer,
    *,
    code: str,
    entry_point: str,
    args_repr: str,
    language: str,
    condition: str,
    item_id: str,
    program_id: str,
    base_model: str,
    model_state: str,
    layers: Sequence[int],
    adapter_id: Optional[str] = None,
    seed: int = 17,
    run_id: str = "",
    max_length: int = 1536,
) -> AttentionRecord:
    import torch

    text, from_prompts = build_prompt_text(
        tokenizer, code=code, entry_point=entry_point, args_repr=args_repr,
        language=language, condition=condition,
    )
    cs, ce = _locate_code(text, code)
    enc = tokenizer(text, return_offsets_mapping=True, truncation=True,
                    max_length=max_length, return_tensors="pt", add_special_tokens=False)
    offsets = enc.pop("offset_mapping")[0].numpy().astype(np.int32)
    enc = {k: v.to(model.device) for k, v in enc.items()}

    with torch.no_grad():
        out = model(**enc, use_cache=False, return_dict=True, output_attentions=True)
    if out.attentions is None:
        raise RuntimeError("model returned no attentions — load it with attn_implementation='eager'")

    # [n_layers][B,H,Q,K] -> [len(layers), H, K] on the last query row (decision D1)
    sel = [int(li) for li in layers]
    attn = torch.stack([out.attentions[li][0, :, -1, :].float().cpu() for li in sel], dim=0).numpy()

    # decode-checked span resolution, recorded at capture time (metrics.py prefers it)
    cls = classify_code(code, language, entry_point)
    from obtune.attention.metrics import resolve_spans_to_tokens

    spans = [(s.start, s.end) for s in cls.spans if s.base_cls != "other"]
    _, n_res, n_tot = resolve_spans_to_tokens(
        spans, [tuple(map(int, o)) for o in offsets.tolist()], char_base=cs,
        tokenizer=tokenizer, input_ids=enc["input_ids"][0].tolist(), code=code,
    )

    return AttentionRecord(
        attn=attn, layers=np.asarray(sel, dtype=np.int32), offsets=offsets,
        code_char_start=cs, code_char_end=ce, text=text, code=code, language=language,
        entry_point=entry_point, item_id=item_id, program_id=program_id,
        condition=condition, base_model=base_model, model_state=model_state,
        adapter_id=adapter_id, seed=seed, run_id=run_id,
        span_resolution_rate=(n_res / n_tot) if n_tot else float("nan"),
        extra={"prompt_from_prompts_module": from_prompts,
               "n_spans": n_tot, "args_repr": args_repr},
    )


def capture_many(
    items: Iterable[dict[str, Any]],
    *,
    model_key: str,
    model_state: str,
    layers: Optional[Sequence[int]] = None,
    adapter_path: Optional[str] = None,
    out_dir: str | Path = ATTN_DIR / "records",
    seed: int = 17,
    run_id: str = "",
) -> list[Path]:
    """Load the base model once (optionally + a LoRA adapter) and capture every item."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    models_cfg = load_config("models.yaml")["models"]
    mcfg = models_cfg[model_key]
    hf_id = mcfg["hf_id"]
    if layers is None:
        n = int(mcfg["n_layers"])
        # early / mid / late probes: the RQ3 claim is about *where* in depth the shift lives
        layers = sorted({n // 4, n // 2, 3 * n // 4, n - 1})

    set_seed(seed)
    tok = AutoTokenizer.from_pretrained(hf_id)
    model = AutoModelForCausalLM.from_pretrained(
        hf_id, dtype=torch.bfloat16, attn_implementation="eager",
        device_map=None,
    )
    if adapter_path:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    if torch.cuda.is_available():
        model.to("cuda")

    out_dir = Path(out_dir)
    written: list[Path] = []
    for it in items:
        rec = capture_record(
            model, tok, code=it["code"], entry_point=it["entry_point"],
            args_repr=it.get("args_repr", "()"), language=it["language"],
            condition=it["condition"], item_id=it["item_id"],
            program_id=it["program_id"], base_model=model_key,
            model_state=model_state, layers=layers, adapter_id=adapter_path,
            seed=seed, run_id=run_id,
        )
        name = f"{model_state}__{it['item_id'].replace('/', '_').replace('::', '__')}.npz"
        written.append(save_attention_npz(rec, out_dir / name))
    return written


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Capture attention records (GPU)")
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--state", required=True, help="pre | post | <adapter tag>")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--items", required=True, help="JSONL of eval items")
    ap.add_argument("--layers", default=None, help="comma-separated layer indices")
    ap.add_argument("--out-dir", default=str(ATTN_DIR / "records"))
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args(argv)

    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        print("WARNING: CUDA_VISIBLE_DEVICES is unset — pin a free GPU before running "
              "(shared box, no scheduler)")
    from obtune.paths import iter_jsonl

    items = list(iter_jsonl(args.items))
    layers = [int(x) for x in args.layers.split(",")] if args.layers else None
    paths = capture_many(items, model_key=args.model, model_state=args.state,
                         layers=layers, adapter_path=args.adapter,
                         out_dir=args.out_dir, seed=args.seed)
    print(f"wrote {len(paths)} records to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
