"""HuggingFace forward-pass path: attention dumps (RQ3) and the soft-mixture ablation.

vLLM drives the accuracy grid because it is an order of magnitude faster, but it does
not expose attention tensors and cannot combine adapters per example. Those two needs
are what this module exists for:

  * ``--mode attn`` — teacher-forced forward over prompt+gold with
    ``output_attentions``, saving per-item last-token attention rows for
    attention/metrics.py. Requires ``attn_implementation="eager"``; SDPA and
    flash-attn silently return ``None`` for attentions.
  * ``--mode moe-soft`` — the RQ2 soft-routing ablation: weight the per-condition
    adapters by the router softmax for each example, generate, discard.

Both import the prompt builder from prompts.py rather than re-implementing it. If
attention were measured on a differently-built prompt than accuracy, the RQ3
regression would relate two different distributions and the correlation would be
uninterpretable.

Storage: a full attention tensor is ``[layers, heads, q, k]`` — about 2 GB per item at
1k tokens on an 8B model. We keep only the **last-token query row** per (layer, head)
over the code-token span, in fp16, for a configurable layer subset. That is what the
anchoring metrics consume and it is ~4 orders of magnitude smaller.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from obtune.config import RESULTS_DIR, load_config
from obtune.paths import iter_jsonl
from obtune.prompts import build_prompt, prompt_id, render_chat, template_sha256
from obtune.provenance import RunManifest
from obtune.seedutil import set_seed

SCHEMA_DOC = """# results/attn/ — attention dump contract

One `.npz` per (system, item), written by `src/obtune/eval_hf.py --mode attn`.

| key | shape | dtype | meaning |
|---|---|---|---|
| `rows` | `[n_layers_kept, n_heads, n_keys]` | float16 | attention from the LAST prompt token to every key position |
| `layers` | `[n_layers_kept]` | int32 | which layer each row came from |
| `token_offsets` | `[n_tokens, 2]` | int32 | (start, end) char offsets of each token into `prompt_text` |
| `code_span` | `[2]` | int32 | (start, end) char offsets of the program inside `prompt_text` |
| `input_ids` | `[n_tokens]` | int32 | token ids |

Sidecar `.json` per item: `item_id`, `program_id`, `condition`, `language`, `system`,
`adapter`, `base_model`, `prompt_id`, `prompt_sha`, `prompt_text`, `entry_point`, `seed`.

Attention rows are stored RAW (they sum to 1 over all key positions). Restriction to
the code-token region and renormalization happen in `attention/metrics.py`, so the
normalization decision stays inspectable and revisable without re-running the dumps.
"""


@dataclass
class AttnConfig:
    model_key: str
    layers: Sequence[int] | None = None  # None => early / middle / late defaults
    max_items: int | None = None
    device: str = "cuda"
    dtype: str = "bfloat16"


def _default_layers(n_layers: int) -> list[int]:
    """Early, middle and late layers. A full dump is ~n_layers x bigger for little
    gain: the anchoring effect is reported per-layer anyway, and the layer subset is
    a config knob so it can be widened for a specific finding."""
    return sorted({3, n_layers // 4, n_layers // 2, (3 * n_layers) // 4, n_layers - 2})


def _load_model(model_key: str, adapter: str | None, dtype: str, device: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    models = load_config("models.yaml")["models"]
    spec = models[model_key]
    tok = AutoTokenizer.from_pretrained(spec["hf_id"])
    model = AutoModelForCausalLM.from_pretrained(
        spec["hf_id"],
        dtype=getattr(torch, dtype),
        # REQUIRED: sdpa/flash return None for attentions, silently producing empty dumps.
        attn_implementation="eager",
        device_map=device,
    )
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model, tok, spec


def _prompt_and_code_span(row: dict[str, Any], tokenizer: Any) -> tuple[str, tuple[int, int]]:
    """Render the eval prompt and locate the program text inside it.

    MUST match `eval_vllm.render_prompts` byte for byte. It did not: this function omitted
    `condition` and joined the message contents with newlines instead of applying the chat
    template, so every HF-path generation ran on a different prompt distribution from the
    accuracy grid. That is CLAUDE.md §4 silent-failure #3, and §1 states the requirement
    directly — both paths must import the same builder, or Δ-attention is measured on a
    different distribution than accuracy and the two cannot be compared at all.

    Nothing was lost by fixing it: `results/attn/` held only a schema and a span-validation
    file, no dumps produced under the old path.
    """
    messages = build_prompt(
        code=row["code"], entry_point=row["entry_point"],
        args_repr=row["args_repr"], language=row["language"],
        condition=row.get("condition"),
    )
    text = render_chat(messages, tokenizer)
    start = text.find(row["code"])
    if start < 0:  # the builder reformatted it; fall back to the whole user turn
        start, end = 0, len(text)
    else:
        end = start + len(row["code"])
    return text, (start, end)


def dump_attention(rows: Iterable[dict[str, Any]], cfg: AttnConfig, system: str,
                   adapter: str | None, out_root: Path, seed: int = 17) -> dict[str, Any]:
    import torch

    set_seed(seed)
    model, tok, spec = _load_model(cfg.model_key, adapter, cfg.dtype, cfg.device)
    n_layers = int(spec.get("n_layers") or model.config.num_hidden_layers)
    layers = list(cfg.layers) if cfg.layers else _default_layers(n_layers)

    out_dir = out_root / cfg.model_key / system
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_root / "SCHEMA.md").write_text(SCHEMA_DOC)

    written = 0
    for row in rows:
        if cfg.max_items is not None and written >= cfg.max_items:
            break
        text, code_span = _prompt_and_code_span(row, tok)
        enc = tok(text, return_offsets_mapping=True, return_tensors="pt")
        offsets = enc.pop("offset_mapping")[0].numpy().astype(np.int32)
        enc = {k: v.to(model.device) for k, v in enc.items()}

        with torch.no_grad():
            out = model(**enc, output_attentions=True, use_cache=False)
        if out.attentions is None:
            raise RuntimeError(
                "model returned no attentions — attn_implementation must be 'eager'"
            )

        # Last-token query row per kept layer: [n_layers_kept, n_heads, n_keys].
        rows_np = np.stack(
            [out.attentions[i][0, :, -1, :].to(torch.float16).cpu().numpy() for i in layers]
        )
        item_id = row.get("item_id") or f"{row['program_id']}::{row['condition']}"
        stem = out_dir / item_id.replace("/", "_").replace(":", "_")
        np.savez_compressed(
            stem.with_suffix(".npz"),
            rows=rows_np,
            layers=np.array(layers, dtype=np.int32),
            token_offsets=offsets,
            code_span=np.array(code_span, dtype=np.int32),
            input_ids=enc["input_ids"][0].cpu().numpy().astype(np.int32),
        )
        stem.with_suffix(".json").write_text(json.dumps({
            "item_id": item_id, "program_id": row["program_id"], "condition": row["condition"],
            "language": row["language"], "system": system, "adapter": adapter,
            "base_model": cfg.model_key, "prompt_id": prompt_id(), "prompt_sha": template_sha256(),
            "prompt_text": text, "entry_point": row["entry_point"], "seed": seed,
        }, indent=2))
        written += 1

    return {"system": system, "model": cfg.model_key, "items": written,
            "layers": layers, "out_dir": str(out_dir)}


def moe_soft_generate(*_args: Any, **_kwargs: Any) -> None:
    """REMOVED 2026-08-10. It did not compute the blend it claimed to.

    It called `add_weighted_adapter(..., combination_type="linear")`, which PEFT implements by
    putting `sqrt(|w*scaling|)` on lora_A and lora_B SEPARATELY — so the reconstruction
    `B_new @ A_new` carries cross terms `B_i A_j` for i != j and is NOT `sum_i w_i dW_i`
    (`taskvec.py:24-34`; measured on the merge arms 2026-08-10, the linear-family combination
    landed 7.175x the exact mixture's magnitude). It was also unwired, ungraded, emitted
    non-TrialRow dicts, and had no producer for its `--routing` input, so nothing depended on it.

    The replacement mixes in ACTIVATION space — h += sum_e a_e(x) * (alpha/r) * B_e A_e x — which
    is exact by construction, needs no merging, and permits batching.
    """
    raise NotImplementedError(
        "moe_soft_generate was removed: combination_type='linear' is not task arithmetic for "
        ">1 adapter. Use the activation-space mixture (src/obtune/mole/) instead.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["attn", "moe-soft"], required=True)
    ap.add_argument("--model", required=True, help="key into configs/models.yaml")
    ap.add_argument("--items", required=True, help="JSONL of eval items")
    ap.add_argument("--system", default="base", help="cell name, e.g. base | tuned_L1b")
    ap.add_argument("--adapter", default=None, help="adapter path (omit for the base model)")
    ap.add_argument("--layers", type=int, nargs="*", default=None)
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--routing", default=None, help="item_id -> {adapter: weight} JSON (moe-soft)")
    ap.add_argument("--adapters", default=None, help="{name: path} JSON (moe-soft)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()

    rows = list(iter_jsonl(args.items))
    manifest = RunManifest(
        experiment=f"eval_hf:{args.mode}", run_id=f"{args.model}:{args.system}:{args.mode}",
        seed=args.seed, config_path="configs/models.yaml", config_resolved={},
        model_hf_id=load_config("models.yaml")["models"][args.model]["hf_id"],
        adapter={"path": args.adapter} if args.adapter else None,
    ).hash_scripts(["src/obtune/eval_hf.py", "src/obtune/prompts.py"]).capture_git()

    if args.mode == "attn":
        out_root = Path(args.out) if args.out else (RESULTS_DIR / "attn")
        summary = dump_attention(
            rows,
            AttnConfig(model_key=args.model, layers=args.layers, max_items=args.max_items),
            system=args.system, adapter=args.adapter, out_root=out_root, seed=args.seed,
        )
        manifest.extra = summary
        manifest.finalize().write(out_root / args.model / args.system)
        print(json.dumps(summary, indent=2))
        return 0

    adapters = json.loads(Path(args.adapters).read_text()) if args.adapters else {}
    routing = json.loads(Path(args.routing).read_text()) if args.routing else {}
    results = moe_soft_generate(rows, args.model, adapters, routing, seed=args.seed)
    out = Path(args.out) if args.out else (RESULTS_DIR / "cells" / f"{args.model}_moe_soft.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    manifest.extra = {"items": len(results), "out": str(out)}
    manifest.finalize().write(out.parent)
    print(f"wrote {len(results)} soft-routed generations to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
