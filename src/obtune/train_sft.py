"""LoRA SFT over output prediction on still-obfuscated code (TRL SFTTrainer).

    python -m obtune.train_sft --config configs/train/pilot_qwen1.5b_l1b.yaml

Positioning (CLAUDE.md §3): the target is the *return value*, never the deobfuscated
source. Training and evaluation both happen on obfuscated code; nothing in this file
ever sees an L0 parent unless L0 is an explicit train condition or replay source.

Order of operations matters and is enforced here:
  1. Pin CUDA_VISIBLE_DEVICES **before** torch is imported (CLAUDE.md §1). Every torch/
     transformers/trl/peft import in this module is therefore inside `main`.
  2. Build the dataset through `data.build_sft_splits`, which runs the split-partition
     and gold-round-trip checks — a corpus defect must fail before a GPU is warm.
  3. Measure the truncation rate at `max_seq_len` and abort above 1 %. S1/S2 inflate
     code length by up to 6x (configs/conditions.yaml size_cap); silent truncation
     would present as a structural-condition effect and there is no way to detect it
     downstream (CLAUDE.md §4.8).
  4. Dump a RunManifest before training starts, and finalize it after, so a crashed
     run still leaves the record of what it was.

TRL 1.x contract: the dataset is conversational prompt-completion, so SFTTrainer sets
`completion_only_loss=True` and masks prompt tokens to -100 itself. We pass it
explicitly anyway and `scripts/inspect_batch.py` asserts the masking on real rows —
that assertion, not this comment, is the guarantee (CLAUDE.md §4.4).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from obtune import data, prompts
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RUNS_DIR, load_config

SCRIPTS_FOR_PROVENANCE = [
    "src/obtune/train_sft.py",
    "src/obtune/data.py",
    "src/obtune/prompts.py",
    "src/obtune/schema.py",
    "src/obtune/paths.py",
]

MAX_TRUNCATION_RATE = 0.01


def cond_tag(train_conditions) -> str:
    """Adapter directory tag. Single condition -> `L1b`; multi -> `L0-L1b-S1` (sorted
    by the ladder order so the same set always yields the same directory)."""
    from obtune.paths import TRAINABLE_CONDITIONS

    order = {c: i for i, c in enumerate(TRAINABLE_CONDITIONS)}
    conds = sorted(train_conditions, key=lambda c: order.get(c, 99))
    return "-".join(conds)


def adapter_dir(cfg: Mapping[str, Any]) -> Path:
    """runs/adapters/<model>/<lang>/<cond_tag>_r<rank>_s<seed>/ — the path the eval
    configs hardcode (see configs/eval/pilot_w1.yaml). Keep the two in sync."""
    tag = cond_tag(cfg["train_conditions"])
    r = int(cfg["peft"]["r"])
    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    return RUNS_DIR / "adapters" / cfg["model"] / cfg["language"] / f"{tag}_r{r}_s{seed}"


def run_id_for(cfg: Mapping[str, Any]) -> str:
    tag = cfg.get("run_tag") or cond_tag(cfg["train_conditions"])
    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    return f"{cfg['model']}__{cfg['language']}__{tag}__s{seed}"


def resolve_model_cfg(cfg: Mapping[str, Any]) -> dict[str, Any]:
    models = load_config("models.yaml")["models"]
    key = cfg["model"]
    if key not in models:
        raise KeyError(f"unknown model key {key!r}; known: {sorted(models)}")
    return dict(models[key])


def _effective_train_knobs(cfg: Mapping[str, Any], mcfg: Mapping[str, Any]) -> dict[str, Any]:
    """`null` in configs/train/_base_lora.yaml means "take it from configs/models.yaml"."""
    t = dict(cfg.get("train", {}))
    if t.get("per_device_batch") is None:
        t["per_device_batch"] = mcfg["per_device_batch"]
    if t.get("grad_accum") is None:
        t["grad_accum"] = mcfg["grad_accum"]
    if t.get("max_seq_len") is None:
        t["max_seq_len"] = mcfg["max_seq_len"]
    return t


def measure_truncation(dataset, tokenizer, max_seq_len: int, sample: Optional[int] = None) -> dict:
    """Fraction of examples whose tokenized prompt+completion exceeds `max_seq_len`.

    Tokenized the same way TRL will: chat template over prompt, then over
    prompt+completion. We measure the full sequence because TRL truncates from the
    right by default, which eats the *answer* — the most damaging possible truncation.
    """
    n = len(dataset) if sample is None else min(sample, len(dataset))
    texts, prompt_texts = [], []
    for i in range(n):
        ex = dataset[i]
        full = list(ex["prompt"]) + list(ex["completion"])
        texts.append(tokenizer.apply_chat_template(full, tokenize=False))
        prompt_texts.append(
            tokenizer.apply_chat_template(list(ex["prompt"]), tokenize=False, add_generation_prompt=True)
        )
    lens = [len(x) for x in tokenizer(texts, add_special_tokens=False)["input_ids"]]
    plens = [len(x) for x in tokenizer(prompt_texts, add_special_tokens=False)["input_ids"]]
    over = sum(1 for x in lens if x > max_seq_len)
    lens_sorted = sorted(lens)
    return {
        "n_checked": n,
        "max_seq_len": max_seq_len,
        "truncation_rate": over / n if n else 0.0,
        "n_truncated": over,
        "len_mean": sum(lens) / n if n else 0.0,
        "len_p50": lens_sorted[n // 2] if n else 0,
        "len_p95": lens_sorted[min(n - 1, int(0.95 * n))] if n else 0,
        "len_max": max(lens) if lens else 0,
        "prompt_len_mean": sum(plens) / n if n else 0.0,
    }


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="LoRA SFT for obtune")
    ap.add_argument("--config", required=True, help="path under configs/ (or absolute)")
    ap.add_argument("--gpu", type=int, default=None, help="force a GPU index; default = pick an idle one")
    ap.add_argument("--out", default=None, help="override the adapter output directory")
    ap.add_argument("--seed", type=int, default=None, help="override train.seed (seed-variance runs)")
    ap.add_argument("--train-size", type=int, default=None, help="override train.train_size (scaling arm)")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="build dataset + trainer, run every check, write the manifest, do NOT train",
    )
    ap.add_argument("--max-steps", type=int, default=None, help="cap optimizer steps (smoke tests)")
    ap.add_argument("--cpu", action="store_true", help="force CPU (smoke tests only)")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    cfg = load_config(args.config)
    cfg.setdefault("train", {})
    if args.seed is not None:
        cfg["train"]["seed"] = args.seed
    if args.train_size is not None:
        cfg["train"]["train_size"] = args.train_size
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    seed = int(tcfg.get("seed", GLOBAL_SEED))

    # ---- GPU pinning BEFORE torch (CLAUDE.md §1) -------------------------------
    if args.cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    elif args.gpu is not None:
        from obtune import gpu

        gpu.pin([args.gpu])
    elif not os.environ.get("CUDA_VISIBLE_DEVICES"):
        from obtune import gpu

        gpu.pin(gpu.pick_free_gpus(1))
    gpu_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")

    from obtune.seedutil import set_seed

    set_seed(seed)

    import torch  # noqa: E402  (must follow the pin)
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    from obtune.provenance import RunManifest, sha256_dir

    out_dir = Path(args.out) if args.out else adapter_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id_for(cfg)

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bundle = data.build_sft_splits({**cfg, "train": tcfg})
    train_ds, val_ds = bundle["train"], bundle["val"]

    trunc = measure_truncation(train_ds, tokenizer, int(tcfg["max_seq_len"]))
    print(f"[train_sft] truncation: {json.dumps(trunc)}", flush=True)

    manifest = (
        RunManifest(
            experiment=cfg.get("phase", "main") + "/sft",
            run_id=run_id,
            seed=seed,
            config_path=str(cfg.get("_config_path", args.config)),
            config_resolved={**cfg, "train": tcfg},
            model_hf_id=mcfg["hf_id"],
            adapter={
                "path": str(out_dir),
                "train_cond": cond_tag(cfg["train_conditions"]),
                "rank": int(cfg["peft"]["r"]),
                "base_model": mcfg["hf_id"],
            },
            gpu_visible=gpu_visible,
            extra={
                "dataset": bundle["meta"],
                "truncation": trunc,
                **prompts.provenance_block(
                    oracle=bool((cfg.get("prompt") or {}).get("oracle", False)),
                    one_shot=bool((cfg.get("prompt") or {}).get("one_shot", False)),
                ),
            },
        )
        .capture_git()
        .hash_scripts(SCRIPTS_FOR_PROVENANCE)
    )
    manifest.write(out_dir)

    if trunc["truncation_rate"] > MAX_TRUNCATION_RATE:
        raise SystemExit(
            f"truncation rate {trunc['truncation_rate']:.3%} exceeds "
            f"{MAX_TRUNCATION_RATE:.0%} at max_seq_len={tcfg['max_seq_len']} "
            f"(p95={trunc['len_p95']}, max={trunc['len_max']}). Raise max_seq_len or "
            "drop the oversized programs — silent truncation eats the gold answer and "
            "would masquerade as a structural-condition effect (CLAUDE.md §4.8)."
        )

    peft_cfg = LoraConfig(
        r=int(cfg["peft"]["r"]),
        lora_alpha=int(cfg["peft"]["alpha"]),
        lora_dropout=float(cfg["peft"]["dropout"]),
        target_modules=list(cfg["peft"]["target_modules"]),
        task_type=cfg["peft"].get("task_type", "CAUSAL_LM"),
        bias="none",
    )

    use_cuda = bool(gpu_visible) and torch.cuda.is_available()
    dtype = torch.bfloat16 if tcfg.get("dtype", "bfloat16") == "bfloat16" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["hf_id"],
        dtype=dtype if use_cuda else torch.float32,
        attn_implementation=tcfg.get("attn_implementation", "sdpa"),
        device_map=None,
    )
    model.config.use_cache = False

    sft_args = SFTConfig(
        output_dir=str(out_dir),
        per_device_train_batch_size=int(tcfg["per_device_batch"]),
        gradient_accumulation_steps=int(tcfg["grad_accum"]),
        num_train_epochs=float(tcfg.get("epochs", 3)),
        learning_rate=float(tcfg.get("lr", 1e-4)),
        lr_scheduler_type=tcfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=float(tcfg.get("warmup_ratio", 0.03)),
        weight_decay=float(tcfg.get("weight_decay", 0.0)),
        max_grad_norm=float(tcfg.get("max_grad_norm", 1.0)),
        max_length=int(tcfg["max_seq_len"]),
        packing=False,  # packing would cross example boundaries and blur the loss mask
        completion_only_loss=True,
        bf16=use_cuda and dtype is torch.bfloat16,
        gradient_checkpointing=bool(tcfg.get("gradient_checkpointing", True)) and use_cuda,
        save_strategy=tcfg.get("save_strategy", "epoch"),
        save_total_limit=None,  # every epoch checkpoint is a ckpt-select candidate
        eval_strategy="steps" if val_ds is not None else "no",
        eval_steps=int(tcfg.get("eval_steps", 200)),
        per_device_eval_batch_size=int(tcfg["per_device_batch"]),
        logging_steps=int(tcfg.get("logging_steps", 20)),
        seed=seed,
        data_seed=seed,
        report_to=[],
        use_cpu=not use_cuda,
        max_steps=args.max_steps if args.max_steps is not None else -1,
        dataloader_num_workers=2,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        peft_config=peft_cfg,
    )

    if args.dry_run:
        batch = next(iter(trainer.get_train_dataloader()))
        supervised = int((batch["labels"] != -100).sum())
        print(
            "[train_sft] DRY RUN — no optimizer step taken. "
            f"batch keys={sorted(batch)} shape={tuple(batch['input_ids'].shape)} "
            f"supervised_tokens={supervised}",
            flush=True,
        )
        manifest.extra["dry_run"] = True
        manifest.finalize().write(out_dir)
        return 0

    result = trainer.train()
    trainer.save_model(str(out_dir / "final"))
    tokenizer.save_pretrained(str(out_dir / "final"))

    summary = {
        "run_id": run_id,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "train_runtime_s": result.metrics.get("train_runtime"),
        "train_loss": result.metrics.get("train_loss"),
        "tokens_per_sec": result.metrics.get("train_tokens_per_second"),
        "steps": result.global_step,
        "truncation": trunc,
        "n_train": len(train_ds),
        "n_val": len(val_ds) if val_ds is not None else 0,
        "checkpoints": sorted(p.name for p in out_dir.glob("checkpoint-*")),
    }
    (out_dir / "training_summary.json").write_text(json.dumps(summary, indent=2))

    manifest.extra["training_summary"] = summary
    manifest.adapter["sha256"] = sha256_dir(out_dir / "final")
    manifest.finalize().write(out_dir)
    print(f"[train_sft] done: {json.dumps(summary)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
