#!/usr/bin/env python
"""Hard pilot gate: prove TRL is masking the prompt and supervising the answer.

CLAUDE.md §4.4 silent failure — a broken loss mask is invisible. If prompt tokens are
supervised the model learns to reproduce obfuscated code (loss goes *down*, accuracy
goes nowhere); if completion tokens are masked nothing is learned at all and the run
still finishes with a plausible curve. Neither shows up in the training logs. TRL's
prompt-completion handling has moved between majors, so this runs the REAL code path —
`SFTTrainer._prepare_dataset` plus the real `DataCollatorForLanguageModeling` — on real
rows, and asserts on the tensors.

CPU only, no GPU needed. It uses the true 1.5B tokenizer (the chat template is the part
that decides where the boundary falls) with a randomly-initialized *tiny* model of the
same architecture. REJECTED: loading the real 1.5B weights — ~6 GB and ~60 s on CPU for
a check that is entirely weight-independent.

    PYTHONPATH=src python scripts/inspect_batch.py [--config configs/train/pilot_qwen1.5b_l1b.yaml]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# The fixture fallback must be decided BEFORE obtune.paths computes its roots.
_REAL_PAIRS = ROOT / "data" / "train" / "pairs"
_USING_FIXTURES = False
if not os.environ.get("OBTUNE_DATA_DIR") and not any(_REAL_PAIRS.glob("*/*.jsonl")):
    os.environ["OBTUNE_DATA_DIR"] = str(ROOT / "tests" / "fixtures" / "data")
    _USING_FIXTURES = True

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")  # CPU only, and before torch

from obtune import data  # noqa: E402
from obtune.config import load_config  # noqa: E402
from obtune.train_sft import _effective_train_knobs, resolve_model_cfg  # noqa: E402

N_ROWS = 4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="train/pilot_qwen1.5b_l1b.yaml")
    ap.add_argument("--rows", type=int, default=N_ROWS)
    ap.add_argument("--show", action="store_true", help="print the decoded batch")
    args = ap.parse_args()

    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    cfg = load_config(args.config)
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    if _USING_FIXTURES:
        print(f"[inspect_batch] NOTE: real corpus absent; using {os.environ['OBTUNE_DATA_DIR']}")

    tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    bundle = data.build_sft_splits(
        {**cfg, "train": {**tcfg, "train_size": args.rows, "val_size": 0, "l0_replay_fraction": 0.0}}
    )
    ds = bundle["train"]
    assert len(ds) == args.rows, f"wanted {args.rows} rows, got {len(ds)}"
    assert set(ds.column_names) == {"prompt", "completion"}, ds.column_names

    # Tiny same-architecture model: SFTTrainer needs a model to build, but nothing
    # about the loss mask depends on the weights.
    base_cfg = AutoConfig.from_pretrained(mcfg["hf_id"])
    base_cfg.hidden_size = 64
    base_cfg.intermediate_size = 128
    base_cfg.num_hidden_layers = 2
    base_cfg.num_attention_heads = 4
    base_cfg.num_key_value_heads = 2
    base_cfg.head_dim = 16
    model = AutoModelForCausalLM.from_config(base_cfg)

    sft_args = SFTConfig(
        output_dir="/tmp/obtune_inspect_batch",
        per_device_train_batch_size=args.rows,
        max_length=int(tcfg["max_seq_len"]),
        packing=False,
        completion_only_loss=True,
        use_cpu=True,
        report_to=[],
        seed=int(tcfg.get("seed", 17)),
        dataloader_num_workers=0,
    )
    trainer = SFTTrainer(
        model=model, args=sft_args, train_dataset=ds, processing_class=tok
    )

    # --- Contract 1: TRL decided to do completion-only loss at all ------------
    assert trainer.completion_only_loss is True, (
        "SFTTrainer.completion_only_loss is False for a prompt-completion dataset — "
        "TRL API drift; the prompt would be supervised."
    )
    prepared = trainer.train_dataset
    assert "labels" in prepared.column_names, (
        f"prepared dataset has no labels column ({prepared.column_names}); the collator "
        "would default labels to input_ids and supervise the whole prompt."
    )

    # --- Contract 2: per-row boundary is exactly the rendered prompt -----------
    report = []
    for i in range(len(prepared)):
        row = prepared[i]
        ids, labels = row["input_ids"], row["labels"]
        assert len(ids) == len(labels), (len(ids), len(labels))
        sup = [j for j, v in enumerate(labels) if v != -100]
        assert sup, f"row {i}: NOTHING is supervised — the model would learn nothing"
        first, last = sup[0], sup[-1]
        assert sup == list(range(first, last + 1)), f"row {i}: supervised span is not contiguous"
        assert last == len(ids) - 1, f"row {i}: tokens after the answer are masked out"
        assert all(labels[j] == -100 for j in range(first)), f"row {i}: prompt token supervised"
        assert all(labels[j] == ids[j] for j in sup), f"row {i}: label != input_id in the answer"

        rendered = tok.apply_chat_template(
            list(ds[i]["prompt"]), tokenize=False, add_generation_prompt=True
        )
        decoded_prompt = tok.decode(ids[:first])
        assert decoded_prompt == rendered, (
            f"row {i}: the masked prefix is not the rendered prompt.\n"
            f"--- masked prefix ---\n{decoded_prompt!r}\n--- prompts.render_chat ---\n{rendered!r}"
        )
        decoded_answer = tok.decode(ids[first:])
        gold = ds[i]["completion"][0]["content"]
        assert gold in decoded_answer, (
            f"row {i}: gold {gold!r} is not inside the supervised span {decoded_answer!r}"
        )
        assert "Return value:" not in decoded_answer, f"row {i}: prompt text leaked into the answer"
        report.append(
            {
                "row": i,
                "n_tokens": len(ids),
                "n_prompt_masked": first,
                "n_supervised": len(sup),
                "gold": gold,
                "supervised_text": decoded_answer,
            }
        )

    # --- Contract 3: the real collator pads with -100 --------------------------
    collator = trainer.data_collator
    batch = collator([dict(prepared[i]) for i in range(len(prepared))])
    ids, labels = batch["input_ids"], batch["labels"]
    attn = batch["attention_mask"]
    assert ids.shape == labels.shape == attn.shape, (ids.shape, labels.shape, attn.shape)
    pad_positions = attn == 0
    assert bool((labels[pad_positions] == -100).all()), "padding positions are supervised"
    total_sup = int((labels != -100).sum())
    assert total_sup == sum(r["n_supervised"] for r in report)
    assert total_sup < int(attn.sum()), "everything is supervised — the prompt mask is gone"

    # --- Contract 4: the masked loss is finite and actually uses the mask ------
    with torch.no_grad():
        loss_masked = float(model(**batch).loss)
    unmasked = dict(batch)
    unmasked["labels"] = ids.masked_fill(pad_positions, -100)
    with torch.no_grad():
        loss_all = float(model(**unmasked).loss)
    assert loss_masked == loss_masked and loss_masked > 0, f"non-finite masked loss {loss_masked}"
    assert abs(loss_masked - loss_all) > 1e-6, (
        "masked and unmasked losses are identical — the mask is not reaching the loss"
    )

    out = {
        "ok": True,
        "config": args.config,
        "tokenizer": mcfg["hf_id"],
        "batch_shape": list(ids.shape),
        "supervised_tokens": total_sup,
        "total_tokens": int(attn.sum()),
        "loss_completion_only": round(loss_masked, 4),
        "loss_full_sequence": round(loss_all, 4),
        "rows": report,
        "data_root": os.environ.get("OBTUNE_DATA_DIR", "data/"),
    }
    if args.show:
        for i in range(len(prepared)):
            print("=" * 70)
            print(tok.decode(prepared[i]["input_ids"]))
    print(json.dumps(out, indent=2))
    print("\ninspect_batch: PASS — prompt tokens are -100, completion tokens are supervised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
