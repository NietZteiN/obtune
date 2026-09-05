#!/usr/bin/env python
"""Lever 2b, step 2 — train the yes/no verifier LoRA on sampled candidates.

Reads runs/candidates/<model>/<tag>/{train,val}.parquet (scripts/28), builds
prompt-completion examples via obtune.verifier, and runs the same SFTTrainer recipe as
obtune.train_sft (LoRA r32, completion-only loss, bf16, grad ckpt). Rows are de-duplicated
on (item_id, pred_norm) — eight samples that all say `42` are one training example — and
class-balanced by downsampling the majority label so the verifier cannot win by saying
"no". The greedy completion (sample_idx == -1) is included as a candidate.

    python scripts/slurm/submit.py --partition h200 --time 04:00:00 --argv \
        scripts/29_train_verifier.py --config train/verifier_generic_py.yaml --model codellama-7b
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import verifier  # noqa: E402
from obtune.config import GLOBAL_SEED, RUNS_DIR, load_config  # noqa: E402
from obtune.train_sft import (  # noqa: E402
    SCRIPTS_FOR_PROVENANCE, _effective_train_knobs, measure_truncation, resolve_model_cfg,
)


def load_examples(pq: Path, seed: int, cap: int | None, balance: bool = True) -> tuple[list[dict], dict]:
    import pandas as pd

    df = pd.read_parquet(pq)
    df["cand"] = df["text"].fillna("").str.strip()
    df = df[df.cand != ""]
    key = df["pred_norm"].fillna(df["cand"])
    df = df.assign(_k=key).drop_duplicates(["item_id", "_k"])
    pos, neg = df[df.correct == 1], df[df.correct == 0]
    stats = {"file": str(pq), "n_rows_raw": int(len(pd.read_parquet(pq, columns=["item_id"]))),
             "n_distinct": int(len(df)), "n_pos": int(len(pos)), "n_neg": int(len(neg)),
             "n_items": int(df.item_id.nunique())}
    rng = random.Random(seed)
    if balance:
        k = min(len(pos), len(neg))
        pos = pos.sample(n=k, random_state=seed)
        neg = neg.sample(n=k, random_state=seed)
    df = pd.concat([pos, neg]).sample(frac=1.0, random_state=seed)
    if cap:
        df = df.iloc[:cap]
    stats["n_used"] = int(len(df))
    stats["pos_frac_used"] = float(df.correct.mean())
    exs = [verifier.build_verifier_example(r, r["cand"], bool(r["correct"]))
           for r in df.to_dict("records")]
    rng.shuffle(exs)
    return exs, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--candidates-tag", default=None)
    ap.add_argument("--max-steps", type=int, default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    cfg["model"] = args.model
    cfg.setdefault("train", {})
    if args.seed is not None:
        cfg["train"]["seed"] = args.seed
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    seed = int(tcfg.get("seed", GLOBAL_SEED))
    tag = args.candidates_tag or cfg["candidates_tag"]
    cand_dir = RUNS_DIR / "candidates" / args.model / tag
    out_dir = RUNS_DIR / "adapters_verifier" / args.model / cfg["language"] / f"{tag}_r{cfg['peft']['r']}_s{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"{args.model}__{cfg['language']}__{cfg['run_tag']}__{tag}__s{seed}"

    from obtune.seedutil import set_seed
    set_seed(seed)

    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig, SFTTrainer
    from obtune.provenance import RunManifest

    train_ex, train_stats = load_examples(cand_dir / "train.parquet", seed, tcfg.get("train_size"))
    val_ex, val_stats = load_examples(cand_dir / "val.parquet", seed, tcfg.get("val_size"))
    print(f"[29] train {json.dumps(train_stats)}\n[29] val {json.dumps(val_stats)}", flush=True)
    train_ds, val_ds = Dataset.from_list(train_ex), Dataset.from_list(val_ex)

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    trunc = measure_truncation(train_ds, tokenizer, int(tcfg["max_seq_len"]))
    print(f"[29] truncation: {json.dumps(trunc)}", flush=True)
    if trunc["truncation_rate"] > 0.01:
        raise SystemExit(f"truncation {trunc['truncation_rate']:.3%} > 1% — raise max_seq_len")

    gpu_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    manifest = RunManifest(
        experiment=cfg.get("phase", "main") + "/verifier_sft", run_id=run_id, seed=seed,
        config_path=str(cfg.get("_config_path", args.config)),
        config_resolved={**cfg, "train": tcfg}, model_hf_id=mcfg["hf_id"],
        adapter={"path": str(out_dir), "train_cond": f"verifier:{tag}", "rank": int(cfg["peft"]["r"]),
                 "base_model": mcfg["hf_id"]},
        gpu_visible=gpu_visible,
        extra={"verifier_version": verifier.VERIFIER_VERSION, "candidates": {"train": train_stats, "val": val_stats},
               "truncation": trunc},
    ).capture_git().hash_scripts(SCRIPTS_FOR_PROVENANCE)
    manifest.write(out_dir)

    peft_cfg = LoraConfig(r=int(cfg["peft"]["r"]), lora_alpha=int(cfg["peft"]["alpha"]),
                          lora_dropout=float(cfg["peft"]["dropout"]),
                          target_modules=list(cfg["peft"]["target_modules"]),
                          task_type="CAUSAL_LM", bias="none")
    use_cuda = torch.cuda.is_available()
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["hf_id"], dtype=torch.bfloat16 if use_cuda else torch.float32,
        attn_implementation=tcfg.get("attn_implementation", "sdpa"))
    model.config.use_cache = False
    sft_args = SFTConfig(
        output_dir=str(out_dir),
        per_device_train_batch_size=int(tcfg["per_device_batch"]),
        gradient_accumulation_steps=int(tcfg["grad_accum"]),
        num_train_epochs=float(tcfg.get("epochs", 2)),
        learning_rate=float(tcfg.get("lr", 1e-4)),
        lr_scheduler_type=tcfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=float(tcfg.get("warmup_ratio", 0.03)),
        weight_decay=float(tcfg.get("weight_decay", 0.0)),
        max_grad_norm=float(tcfg.get("max_grad_norm", 1.0)),
        max_length=int(tcfg["max_seq_len"]), packing=False, completion_only_loss=True,
        bf16=use_cuda, gradient_checkpointing=use_cuda,
        save_strategy="epoch", save_total_limit=None,
        eval_strategy="steps", eval_steps=int(tcfg.get("eval_steps", 200)),
        per_device_eval_batch_size=int(tcfg["per_device_batch"]),
        logging_steps=int(tcfg.get("logging_steps", 20)),
        seed=seed, data_seed=seed, report_to=[], use_cpu=not use_cuda,
        max_steps=args.max_steps if args.max_steps is not None else -1,
        dataloader_num_workers=2,
    )
    trainer = SFTTrainer(model=model, args=sft_args, train_dataset=train_ds, eval_dataset=val_ds,
                         processing_class=tokenizer, peft_config=peft_cfg)
    result = trainer.train()
    trainer.save_model(str(out_dir / "final"))
    tokenizer.save_pretrained(str(out_dir / "final"))
    summary = {"run_id": run_id, "finished_utc": datetime.now(timezone.utc).isoformat(),
               "train_runtime_s": result.metrics.get("train_runtime"),
               "train_loss": result.metrics.get("train_loss"), "steps": trainer.state.global_step,
               "checkpoints": sorted(str(p) for p in out_dir.glob("checkpoint-*")),
               "out": str(out_dir)}
    manifest.extra["summary"] = summary
    manifest.finalize().write(out_dir)
    (out_dir / "train_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[29] done: {json.dumps(summary)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
