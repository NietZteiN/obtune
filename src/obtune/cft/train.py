"""LoRA fine-tuning for the CFT replication — both arms.

    # the paper's Standard Fine-Tuning baseline (forward task only)
    python -m obtune.cft.train --config cft/train/sft_qwen1.5b_py.yaml
    # Contrastive Fine-Tuning: L_CFT = L_pos + L_neg + L_gen
    python -m obtune.cft.train --config cft/train/cft_qwen1.5b_py.yaml

The two arms differ in exactly one config key (`tasks`), which is the point: any gap
between them has to come from the extra two losses, not from a different recipe. Paper
§3.4 uses LoRA for the open-source models, so the PEFT block mirrors obtune's own
`configs/train/_base_lora.yaml` defaults.

How the three-term loss is realised
-----------------------------------
The paper writes `L_CFT = L_pos + L_neg + L_gen` (eq. 5) and describes "balanced triplet
datasets ... 10 000 each". A sum of three per-task cross-entropies over equally-sized
pools is exactly joint next-token CE over their union, which is what SFTTrainer computes
here — no custom loss is needed, and writing one would only risk diverging from the
paper's actual (dataset-level) balancing.

There is a subtlety the paper does not address, and it is large enough to report rather
than absorb: a `gen` target is an entire program (hundreds of tokens) while a `pos`/`neg`
target is the single token YES or NO. Equal *instance* counts therefore give the
generation term ~2 orders of magnitude more weight in a token-mean loss. This module
measures the realised per-task share of supervised tokens and writes it into the run
manifest as `task_token_share`, so the effective weighting is a recorded number instead
of an assumption. Measured on the Python mixture (Qwen2.5-Coder tokenizer):

    task_token_share:  gen 0.977 · pos 0.011 · neg 0.011
    mean supervised tokens/instance:  gen 196.7 · pos 3.0 · neg 3.0

So the paper's three-term objective is, at the token level, ~98 % L_gen.

`train.task_weights` upsamples a task's instances, and the replication leaves all weights
at 1 because that is what the paper describes. It is worth recording that upsampling
CANNOT fix the imbalance: with every `gen` instance kept, equal token mass would need
~484 000 instances of each classification task (86x), a ~976 000-instance mixture at
~15 200 optimizer steps per epoch — roughly fifty times the cost of the SFT arm. A
genuinely token-balanced arm therefore requires a per-task *loss* coefficient in a custom
`compute_loss`, which is a deviation from the paper's method rather than a replication of
it, and is left as a follow-up (see log/cft-replication/). A `task_weights` config that
merely upsampled to 66x was written and then retired for promising a balance it does not
deliver (it reaches gen 0.395, and starves `gen` to 612 instances under any affordable cap).

Order of operations follows `obtune.train_sft`: pin CUDA_VISIBLE_DEVICES before torch is
imported (CLAUDE.md §1), build and validate data before a GPU is warm, write the manifest
before training so a crashed run still leaves its record.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from obtune.cft import dataset as cft_data
from obtune.cft import prompts as cft_prompts
from obtune.config import GLOBAL_SEED, RUNS_DIR, load_config

SCRIPTS_FOR_PROVENANCE = [
    "src/obtune/cft/train.py",
    "src/obtune/cft/dataset.py",
    "src/obtune/cft/prompts.py",
    "src/obtune/cft/mutate.py",
    "src/obtune/paths.py",
]

#: Overlong examples are dropped rather than truncated (truncation from the right eats
#: the target program, which is the whole supervision signal for `gen`). Dropping biases
#: the pool toward shorter programs, so the rate is gated and always reported.
MAX_DROP_FRACTION = 0.25


def arm_tag(cfg: Mapping[str, Any]) -> str:
    """`sft` for the gen-only baseline, `cft` for the three-task mixture."""
    if cfg.get("arm"):
        return str(cfg["arm"])
    tasks = set(cfg["tasks"])
    if tasks == {"gen"}:
        return "sft"
    if tasks == set(cft_prompts.TASKS):
        return "cft"
    return "-".join(sorted(tasks))


def adapter_dir(cfg: Mapping[str, Any]) -> Path:
    """runs/adapters_cft/<model>/<lang>/<arm>_r<rank>_s<seed>/

    A separate root from `runs/adapters/`: these adapters are trained on a *different
    task* (emitting code) than every other adapter in the project (emitting a return
    value), and an eval config that picked one up by accident would produce numbers that
    look like obtune results and are not.
    """
    r = int(cfg["peft"]["r"])
    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    # `adapter_root` is config-driven so a follow-up experiment lands its adapters
    # somewhere an eval config cannot pick them up by accident, for the same reason
    # this root is separate from `runs/adapters/` in the first place.
    root = cfg.get("adapter_root", "adapters_cft")
    scope = cfg.get("scope")
    tag = f"{scope}_{arm_tag(cfg)}" if scope else arm_tag(cfg)
    return RUNS_DIR / root / cfg["model"] / cfg["language"] / f"{tag}_r{r}_s{seed}"


def run_id_for(cfg: Mapping[str, Any], prefix: str = "cft") -> str:
    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    scope = cfg.get("scope")
    tag = f"{scope}-{arm_tag(cfg)}" if scope else arm_tag(cfg)
    return f"{prefix}__{cfg['model']}__{cfg['language']}__{tag}__s{seed}"


def resolve_model_cfg(cfg: Mapping[str, Any]) -> dict[str, Any]:
    models = load_config("models.yaml")["models"]
    key = cfg["model"]
    if key not in models:
        raise KeyError(f"unknown model key {key!r}; known: {sorted(models)}")
    return dict(models[key])


def _effective_train_knobs(cfg: Mapping[str, Any], mcfg: Mapping[str, Any]) -> dict[str, Any]:
    t = dict(cfg.get("train", {}))
    for key in ("per_device_batch", "grad_accum", "max_seq_len"):
        if t.get(key) is None:
            t[key] = mcfg[key]
    return t


def expand_by_weight(
    rows: Sequence[cft_data.CFTInstance], weights: Mapping[str, float]
) -> list[cft_data.CFTInstance]:
    """Integer upsampling of a task's instances. Default weights are all 1 (no-op)."""
    out: list[cft_data.CFTInstance] = []
    for r in rows:
        w = int(round(float(weights.get(r.task, 1.0))))
        out.extend([r] * max(0, w))
    return out


def measure_lengths(
    rows: Sequence[cft_data.CFTInstance],
    tokenizer: Any,
    max_seq_len: int,
    build_example: Optional[Any] = None,
) -> tuple[list[int], dict[str, Any]]:
    """Tokenize as TRL will, and report length + supervised-token stats per task.

    Returns `(keep_indices, stats)`. The completion-token count is derived as
    `len(prompt+completion) - len(prompt)`, which is what the loss mask actually
    supervises under `completion_only_loss=True`.
    """
    builder = build_example or cft_prompts.build_example
    examples = [builder(r.model_dump()) for r in rows]
    full_texts = [
        tokenizer.apply_chat_template(list(e["prompt"]) + list(e["completion"]), tokenize=False)
        for e in examples
    ]
    prompt_texts = [
        tokenizer.apply_chat_template(list(e["prompt"]), tokenize=False, add_generation_prompt=True)
        for e in examples
    ]
    full_lens = [len(x) for x in tokenizer(full_texts, add_special_tokens=False)["input_ids"]]
    prompt_lens = [len(x) for x in tokenizer(prompt_texts, add_special_tokens=False)["input_ids"]]

    keep = [i for i, n in enumerate(full_lens) if n <= max_seq_len]
    dropped_by_task = Counter(rows[i].task for i in range(len(rows)) if i not in set(keep))

    sup_by_task: dict[str, int] = defaultdict(int)
    n_by_task: dict[str, int] = defaultdict(int)
    for i in keep:
        sup_by_task[rows[i].task] += max(0, full_lens[i] - prompt_lens[i])
        n_by_task[rows[i].task] += 1
    total_sup = sum(sup_by_task.values()) or 1

    lens_sorted = sorted(full_lens)
    n = len(full_lens) or 1
    stats = {
        "n_examples": len(rows),
        "n_kept": len(keep),
        "n_dropped": len(rows) - len(keep),
        "drop_rate": (len(rows) - len(keep)) / n,
        "dropped_by_task": dict(sorted(dropped_by_task.items())),
        "max_seq_len": max_seq_len,
        "len_mean": sum(full_lens) / n,
        "len_p50": lens_sorted[n // 2],
        "len_p95": lens_sorted[min(n - 1, int(0.95 * n))],
        "len_max": max(full_lens) if full_lens else 0,
        "kept_by_task": dict(sorted(n_by_task.items())),
        "supervised_tokens_by_task": dict(sorted(sup_by_task.items())),
        # The number the paper's eq. (5) leaves implicit: what each loss term is
        # actually worth once the mixture is tokenized.
        "task_token_share": {
            k: v / total_sup for k, v in sorted(sup_by_task.items())
        },
        "mean_supervised_tokens_by_task": {
            k: sup_by_task[k] / n_by_task[k] for k in sorted(sup_by_task) if n_by_task[k]
        },
    }
    return keep, stats


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="LoRA fine-tuning for the CFT replication")
    ap.add_argument("--config", required=True, help="path under configs/ (or absolute)")
    ap.add_argument("--gpu", type=int, default=None, help="force a GPU index; default = pick an idle one")
    ap.add_argument("--out", default=None, help="override the adapter output directory")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--train-size", type=int, default=None, help="override train.train_size")
    ap.add_argument("--max-steps", type=int, default=None, help="cap optimizer steps (smoke tests)")
    ap.add_argument("--dry-run", action="store_true",
                    help="build everything, run every check, write the manifest, do NOT train")
    ap.add_argument("--cpu", action="store_true", help="force CPU (smoke tests only)")
    return ap


def main(
    argv: Optional[list[str]] = None,
    *,
    load_mixture: Optional[Any] = None,
    build_example: Optional[Any] = None,
    run_id_prefix: str = "cft",
) -> int:
    """Train one arm.

    The three keyword-only hooks let a follow-up experiment reuse this trainer instead
    of forking it. They default to the replication's own loader and prompt builder, so
    every existing caller is unaffected — and the replication's guarantee that its
    reverse direction is never supervised stays enforced by `cft.prompts.completion_for`,
    which is untouched.
    """
    args = build_parser().parse_args(argv)
    mixture = load_mixture or cft_data.load_mixture

    cfg = load_config(args.config)
    cfg.setdefault("train", {})
    if args.seed is not None:
        cfg["train"]["seed"] = args.seed
    if args.train_size is not None:
        cfg["train"]["train_size"] = args.train_size
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    seed = int(tcfg.get("seed", GLOBAL_SEED))
    language = cfg["language"]
    tasks = list(cfg["tasks"])

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
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer

    from obtune.provenance import RunManifest, sha256_dir

    out_dir = Path(args.out) if args.out else adapter_dir(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id_for(cfg, run_id_prefix)

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ---- data -------------------------------------------------------------------
    import random

    paired = bool((cfg.get("train", {}) or {}).get("pair_pos_neg", True))
    mix_kw = dict(cfg.get("train", {}).get("mixture_kwargs", {}) or {})
    train_rows = mixture(language, tasks, splits=("train",), paired=paired, **mix_kw)
    val_rows = mixture(language, tasks, splits=("val",), paired=paired, **mix_kw)
    weights = dict((cfg.get("train", {}) or {}).get("task_weights", {}) or {})
    if weights:
        train_rows = expand_by_weight(train_rows, weights)

    rng = random.Random(seed)
    rng.shuffle(train_rows)
    rng.shuffle(val_rows)
    if tcfg.get("train_size"):
        train_rows = train_rows[: int(tcfg["train_size"])]
    if tcfg.get("val_size"):
        val_rows = val_rows[: int(tcfg["val_size"])]

    keep, length_stats = measure_lengths(
        train_rows, tokenizer, int(tcfg["max_seq_len"]), build_example
    )
    print(f"[cft.train] lengths: {json.dumps(length_stats)}", flush=True)
    train_rows = [train_rows[i] for i in keep]

    val_keep, val_length_stats = measure_lengths(
        val_rows, tokenizer, int(tcfg["max_seq_len"]), build_example
    )
    val_rows = [val_rows[i] for i in val_keep]

    train_ds = Dataset.from_list(cft_data.to_sft_records(train_rows, build_example))
    val_ds = (
        Dataset.from_list(cft_data.to_sft_records(val_rows, build_example)) if val_rows else None
    )

    dataset_meta = {
        "language": language,
        "tasks": tasks,
        "arm": arm_tag(cfg),
        "task_weights": weights or {t: 1 for t in tasks},
        "n_train": len(train_rows),
        "n_val": len(val_rows),
        "n_train_programs": len({r.program_id for r in train_rows}),
        "train_by_task": dict(sorted(Counter(r.task for r in train_rows).items())),
        "train_by_condition": dict(sorted(Counter(r.condition for r in train_rows).items())),
        "negative_style": next((r.negative_style for r in train_rows if r.negative_style), None),
        "pair_pos_neg": paired,
        # Recorded every run so the per-condition label shortcut (see
        # dataset.pair_pos_neg) cannot quietly reappear in a later mixture.
        "label_balance": cft_data.label_balance(train_rows),
        "lengths": length_stats,
        "val_lengths": val_length_stats,
        **cft_prompts.provenance_block(),
    }

    manifest = (
        RunManifest(
            experiment=cfg.get("experiment", "cft/replication"),
            run_id=run_id,
            seed=seed,
            config_path=str(cfg.get("_config_path", args.config)),
            config_resolved={**cfg, "train": tcfg},
            model_hf_id=mcfg["hf_id"],
            adapter={
                "path": str(out_dir),
                "train_cond": "cft:" + "+".join(sorted(tasks)),
                "rank": int(cfg["peft"]["r"]),
                "base_model": mcfg["hf_id"],
            },
            gpu_visible=gpu_visible,
            extra={"dataset": dataset_meta},
        )
        .capture_git()
        .hash_scripts(SCRIPTS_FOR_PROVENANCE)
    )
    manifest.write(out_dir)

    if length_stats["drop_rate"] > MAX_DROP_FRACTION:
        raise SystemExit(
            f"dropped {length_stats['drop_rate']:.1%} of instances at "
            f"max_seq_len={tcfg['max_seq_len']} (p95={length_stats['len_p95']}, "
            f"max={length_stats['len_max']}, by task {length_stats['dropped_by_task']}). "
            "Raise max_seq_len — above this rate the surviving pool is a short-program "
            "corpus and the arms are no longer comparable to the paper's."
        )
    if not train_rows:
        raise SystemExit("no training instances survived length filtering")

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
        save_total_limit=None,
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
            "[cft.train] DRY RUN — no optimizer step taken. "
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
        "arm": arm_tag(cfg),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "train_runtime_s": result.metrics.get("train_runtime"),
        "train_loss": result.metrics.get("train_loss"),
        "steps": result.global_step,
        "n_train": len(train_rows),
        "n_val": len(val_rows),
        "lengths": length_stats,
        "checkpoints": sorted(p.name for p in out_dir.glob("checkpoint-*")),
    }
    (out_dir / "training_summary.json").write_text(json.dumps(summary, indent=2))
    manifest.extra["training_summary"] = summary
    manifest.adapter["sha256"] = sha256_dir(out_dir / "final")
    manifest.finalize().write(out_dir)
    print(f"[cft.train] done: {json.dumps(summary)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
