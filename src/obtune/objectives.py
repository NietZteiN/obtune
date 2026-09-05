"""Alternative fine-tuning OBJECTIVES for output prediction on obfuscated code.

    python -m obtune.objectives train --config train/obj_cons_codellama7b_py.yaml [--lam 1]
    python -m obtune.objectives train --config train/obj_neg_codellama7b_py.yaml [--no-ul]
    python -m obtune.objectives train --config train/obj_curr_codellama7b_py.yaml --objective consistency

WHY THIS MODULE EXISTS. Every arm of the 2026-08/09 campaign -- ~60 systems across per-condition
specialists, monolithic mixes, merges, routers, ICL, trace SFT, reranking, rank, data and scale --
optimised the SAME objective: next-token cross-entropy on the answer span. The only exception
(align.py) added a hidden-state MSE and was marginal. The user's question ("have you tried
different fine-tuning objectives?") is therefore fair, and this module is the answer: three
objectives that change the LOSS, not the data mix or the model, plus the curriculum variant that
changes the order.

  consistency   L = CE(y | x_obf) + lam * KL( p_T(. | x_parent) || p_S(. | x_obf) )
                at the answer tokens. T is the FROZEN tuned_L0 adapter on the CLEAN L0 parent of
                the same program and case (the pair exists by construction, CLAUDE.md §3.1).
                The student is told, token by token, "predict what the clean-code model predicts".
                This is the output-space version of align.py's representation-space pull, and
                unlike a symmetric consistency loss it cannot be satisfied by collapse: the
                target is a fixed distribution. `teacher_view: same` is the CONTROL -- the
                teacher sees the obfuscated input itself, i.e. plain knowledge distillation from a
                stronger model, with no cross-surface pairing. If matched == same, the objective
                is distillation, not invariance.

  negatives     rows carry a `kind`: 0 = ordinary CE row (original rows AND verified mutants with
                their TRUE output); 1 = NEGATIVE row (mutant code, ORIGINAL output), whose loss is
                unlikelihood -log(1 - p(y_orig[t*])) at the FIRST token t* where y_orig diverges
                from y_mut. Only that token: the shared prefix is correct under y_mut and is being
                pushed UP by the positive twin, so penalising it would fight the task term.
                The negatives are single-operator mutants executed against their own parent
                (cft/mutate.py), so "different" is verified, never assumed. `--no-ul` keeps the
                mutant positives and drops the negative rows: the data-only control.

  curriculum    not a loss but an initialisation: `init_adapter` loads an existing LoRA
                (tuned_L0/best) as the trainable adapter instead of a fresh one, and training
                continues on the five transformed conditions with either objective above or
                plain CE (`--objective sft`). tuned_L0 is the strongest single arm on the
                held-out family; this asks whether that advantage survives a SHORT exposure to
                transforms once the task is already learned.

Everything else -- data loading through `data.build_sft_splits` / `paths.load_training_jsonl`,
truncation guard, run manifest, epoch checkpoints for ckpt-select -- is inherited from
train_sft.py so that the vanilla arms stay the exact control.

GRADIENT-ACCUMULATION NOTE (inherited from align.py, found 2026-09-04): `model_accepts_loss_kwargs`
is set False so transformers divides our per-microbatch loss by the accumulation count itself.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from obtune import data, paths, prompts
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RUNS_DIR, load_config
from obtune.schema import TrainPair

NEGATIVES_SUBDIR = "negatives"


# --------------------------------------------------------------------------- #
# Shared tokenization (mirrors TRL 1.x prompt-completion: chat template over the prompt
# with add_generation_prompt, then over prompt+completion; completion = the suffix).
# --------------------------------------------------------------------------- #

def _ids(tok, msgs, **kw) -> list[int]:
    out = tok.apply_chat_template(msgs, tokenize=True, **kw)
    if isinstance(out, dict) or hasattr(out, "keys"):
        out = out["input_ids"]
    return list(out)


def tokenize_pc(tok, prompt: Sequence[Mapping[str, str]], completion: str) -> tuple[list[int], int]:
    """(prompt+completion ids, n_completion_tokens) exactly as TRL will build them."""
    p_ids = _ids(tok, list(prompt), add_generation_prompt=True)
    f_ids = _ids(tok, list(prompt) + [{"role": "assistant", "content": completion}])
    if f_ids[: len(p_ids)] != p_ids:
        raise ValueError("prompt is not a prefix of prompt+completion under this template")
    return f_ids, len(f_ids) - len(p_ids)


def first_divergence(a: Sequence[int], b: Sequence[int]) -> int:
    """Index of the first position where two completion token lists differ."""
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n  # one is a strict prefix of the other: the divergence is the next token


def case_key(item_id: str) -> str:
    parts = item_id.split("::")
    if len(parts) < 3:
        raise ValueError(f"unexpected item_id shape: {item_id!r}")
    return f"{parts[0]}::{parts[2]}"


# --------------------------------------------------------------------------- #
# Negatives corpus (data/train/negatives/<cond>/<lang>.jsonl; built by scripts/32_build_negatives.py)
# --------------------------------------------------------------------------- #

class NegativePair(TrainPair):
    """A verified semantic mutant of a training row.

    `code` is the MUTANT, `output_repr` its TRUE output on `args_repr`, and `orig_output_repr`
    the parent row's gold -- the answer the mutant must NOT give. Inherits TrainPair's H1
    validator, and is read only through `paths.load_training_jsonl`, so all four quarantine
    layers apply unchanged.
    """

    parent_item_id: str
    orig_output_repr: str
    mutation: dict[str, Any]


def negatives_path(condition: str, language: str) -> Path:
    return paths.TRAIN_ROOT / NEGATIVES_SUBDIR / condition / f"{language}.jsonl"


def load_negatives(conditions: Sequence[str], language: str, splits=("train",)) -> list[NegativePair]:
    rows: list[NegativePair] = []
    for cond in conditions:
        p = negatives_path(cond, language)
        if not p.exists():
            raise FileNotFoundError(f"no negatives for {cond}/{language}: {p} (run scripts/32_build_negatives.py)")
        for raw in paths.load_training_jsonl(p):
            r = NegativePair(**raw)
            if r.split in splits and r.output_repr != r.orig_output_repr:
                rows.append(r)
    return rows


# --------------------------------------------------------------------------- #
# Dataset builders
# --------------------------------------------------------------------------- #

def build_consistency_records(rows: Sequence[TrainPair], tok, language: str, view: str) -> tuple[list[dict], dict]:
    """SFT records + the teacher's input ids for each row.

    view = "parent": teacher input is the L0 parent of the same program/case.
    view = "same":   teacher input is the student's own (obfuscated) example -- the control.
    """
    meta = {"view": view, "n": len(rows), "n_missing_parent": 0}
    parents: dict[str, TrainPair] = {}
    if view == "parent":
        parents = {case_key(r.item_id): r for r in data.load_pairs(["L0"], language)}
    recs = []
    for r in rows:
        ex = prompts.build_example(r.model_dump())
        if view == "parent":
            par = parents.get(case_key(r.item_id))
            if par is None:
                meta["n_missing_parent"] += 1
                continue
            if par.output_repr != r.output_repr:
                raise data.DataContractError(
                    f"{r.item_id}: parent gold {par.output_repr!r} != row gold {r.output_repr!r}")
            t_ex = prompts.build_example(par.model_dump())
        else:
            t_ex = ex
        t_ids, t_clen = tokenize_pc(tok, t_ex["prompt"], t_ex["completion"][0]["content"])
        recs.append({**ex, "t_ids": t_ids, "t_clen": t_clen})
    if meta["n_missing_parent"]:
        raise data.DataContractError(
            f"{meta['n_missing_parent']} rows have no L0 parent; refusing a silently reduced set")
    return recs, meta


def build_negative_records(rows: Sequence[TrainPair], negs: Sequence[NegativePair], tok,
                           use_ul: bool, seed: int) -> tuple[list[dict], dict]:
    """kind 0 rows: originals + mutant positives. kind 1 rows: mutant with ORIGINAL gold."""
    import random

    recs = [{**prompts.build_example(r.model_dump()), "kind": 0, "ul_index": -1} for r in rows]
    n_pos = n_neg = 0
    for n in negs:
        base = n.model_dump()
        pos = prompts.build_example(base)
        recs.append({**pos, "kind": 0, "ul_index": -1})
        n_pos += 1
        if not use_ul:
            continue
        neg = prompts.build_example({**base, "output_repr": n.orig_output_repr})
        f_orig, c_orig = tokenize_pc(tok, neg["prompt"], n.orig_output_repr)
        f_mut, c_mut = tokenize_pc(tok, pos["prompt"], n.output_repr)
        div = first_divergence(f_orig[len(f_orig) - c_orig:], f_mut[len(f_mut) - c_mut:])
        if div >= c_orig:
            continue  # y_orig is a strict prefix of y_mut: nothing in y_orig is wrong yet
        recs.append({**neg, "kind": 1, "ul_index": int(div)})
        n_neg += 1
    random.Random(seed).shuffle(recs)
    return recs, {"n_orig": len(rows), "n_mutant_pos": n_pos, "n_neg": n_neg, "use_ul": use_ul}


# --------------------------------------------------------------------------- #
# Collator + trainer
# --------------------------------------------------------------------------- #

class PassthroughCollator:
    """Carries the objective's extra columns through TRL's collator as tensors."""

    def __init__(self, inner, pad_id: int, mode: str):
        self.inner, self.pad_id, self.mode = inner, pad_id, mode

    def __call__(self, features):
        import torch

        extra = {}
        if self.mode == "consistency":
            t_ids = [f.pop("t_ids") for f in features]
            t_clen = [f.pop("t_clen") for f in features]
            T = max(len(x) for x in t_ids)
            ids = torch.full((len(t_ids), T), self.pad_id, dtype=torch.long)
            att = torch.zeros((len(t_ids), T), dtype=torch.long)
            for i, x in enumerate(t_ids):
                ids[i, : len(x)] = torch.tensor(x); att[i, : len(x)] = 1
            extra = {"t_ids": ids, "t_att": att, "t_clen": torch.tensor(t_clen, dtype=torch.long)}
        elif self.mode == "negatives":
            extra = {"kind": torch.tensor([f.pop("kind") for f in features], dtype=torch.long),
                     "ul_index": torch.tensor([f.pop("ul_index") for f in features], dtype=torch.long)}
        cleaned = [{k: v for k, v in f.items() if k not in ("prompt", "completion")} for f in features]
        batch = self.inner(cleaned)
        batch.update(extra)
        return batch


def make_trainer_class():
    import torch
    import torch.nn.functional as F
    from trl import SFTTrainer

    class ObjectiveTrainer(SFTTrainer):
        def __init__(self, *a, mode="sft", lam=1.0, teacher=None, **kw):
            super().__init__(*a, **kw)
            self.mode, self.lam, self.teacher = mode, float(lam), teacher
            self._acc: dict[str, float] = {}
            self._n = 0
            self.model_accepts_loss_kwargs = False

        def _tick(self, **vals):
            for k, v in vals.items():
                self._acc[k] = self._acc.get(k, 0.0) + float(v)
            self._n += 1

        # -- consistency ---------------------------------------------------
        def _consistency(self, model, inputs):
            t_ids, t_att, t_clen = inputs.pop("t_ids"), inputs.pop("t_att"), inputs.pop("t_clen")
            labels = inputs["labels"]
            outputs = model(**inputs)
            task = outputs.loss
            if self.lam <= 0.0:
                return task, outputs
            with torch.no_grad():
                t_logits = self.teacher(input_ids=t_ids.to(labels.device),
                                        attention_mask=t_att.to(labels.device)).logits
            s_logits = outputs.logits
            kls, n_ok, n_bad = [], 0, 0
            for b in range(labels.size(0)):
                s_pos = (labels[b] != -100).nonzero(as_tuple=True)[0]
                L = int(t_att[b].sum()); c = int(t_clen[b])
                t_pos = torch.arange(L - c, L, device=labels.device)
                if s_pos.numel() != c or s_pos.numel() == 0 or int(s_pos[0]) == 0:
                    n_bad += 1; continue
                # The targets must be the SAME tokens on both sides -- the correspondence check.
                if not torch.equal(labels[b, s_pos], t_ids[b].to(labels.device)[t_pos]):
                    n_bad += 1; continue
                sl = F.log_softmax(s_logits[b, s_pos - 1].float(), dim=-1)
                tl = F.log_softmax(t_logits[b, t_pos - 1].float(), dim=-1)
                kls.append((tl.exp() * (tl - sl)).sum(-1).mean())
                n_ok += 1
            kl = torch.stack(kls).mean() if kls else task.new_zeros(())
            self._tick(task_loss=task.detach(), kl_loss=kl.detach(), kl_rows_ok=n_ok, kl_rows_bad=n_bad)
            return task + self.lam * kl, outputs

        # -- negatives -----------------------------------------------------
        def _negatives(self, model, inputs):
            kind, ul_index = inputs.pop("kind"), inputs.pop("ul_index")
            labels = inputs["labels"]
            neg = kind == 1
            pos_labels = labels.clone()
            pos_labels[neg] = -100
            if not (pos_labels != -100).any():
                pos_labels = labels  # degenerate all-negative microbatch: keep CE defined
            outputs = model(**{**inputs, "labels": pos_labels})
            task = outputs.loss
            uls, n_bad = [], 0
            for b in neg.nonzero(as_tuple=True)[0].tolist():
                s_pos = (labels[b] != -100).nonzero(as_tuple=True)[0]
                j = int(ul_index[b])
                if j < 0 or j >= s_pos.numel() or int(s_pos[j]) == 0:
                    n_bad += 1; continue
                p = int(s_pos[j])
                logp = F.log_softmax(outputs.logits[b, p - 1].float(), dim=-1)[labels[b, p]]
                uls.append(-torch.log1p(-logp.exp().clamp(max=1 - 1e-6)))
            ul = torch.stack(uls).mean() if uls else task.new_zeros(())
            self._tick(task_loss=task.detach(), ul_loss=ul.detach(), n_neg=len(uls), n_neg_bad=n_bad)
            return task + self.lam * ul, outputs

        def compute_loss(self, model, inputs, return_outputs=False, **kw):
            if self.mode == "consistency":
                loss, outputs = self._consistency(model, inputs)
            elif self.mode == "negatives":
                loss, outputs = self._negatives(model, inputs)
            else:
                outputs = model(**inputs); loss = outputs.loss
            return (loss, outputs) if return_outputs else loss

        def log(self, logs, *a, **kw):
            if self._n:
                for k, v in self._acc.items():
                    logs[k] = v / self._n
                self._acc, self._n = {}, 0
            return super().log(logs, *a, **kw)

    return ObjectiveTrainer


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def out_dir_for(cfg: Mapping[str, Any], tag: str) -> Path:
    from obtune.train_sft import cond_tag

    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    root = PROJECT_ROOT / cfg.get("adapter_root", "runs/adapters_objectives")
    return root / cfg["model"] / cfg["language"] / f"{cond_tag(cfg['train_conditions'])}_r{int(cfg['peft']['r'])}_{tag}_s{seed}"


def train(cfg: Mapping[str, Any], args: argparse.Namespace) -> int:
    import torch
    from datasets import Dataset
    from peft import LoraConfig, PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig

    from obtune.provenance import RunManifest, sha256_dir
    from obtune.seedutil import set_seed
    from obtune.train_sft import (MAX_TRUNCATION_RATE, SCRIPTS_FOR_PROVENANCE, _effective_train_knobs,
                                  cond_tag, measure_truncation, resolve_model_cfg)

    ocfg = dict(cfg.get("objective", {}) or {})
    mode = args.objective or ocfg.get("mode", "sft")
    lam = float(args.lam if args.lam is not None else ocfg.get("lam", 1.0))
    view = args.teacher_view or ocfg.get("teacher_view", "parent")
    use_ul = not args.no_ul and bool(ocfg.get("use_ul", True))
    init_adapter = ocfg.get("init_adapter")

    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    seed = int(tcfg.get("seed", GLOBAL_SEED))
    set_seed(seed)

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bundle = data.build_sft_splits({**cfg, "train": tcfg})
    train_rows, val_rows = bundle["train_rows"], bundle["val_rows"]

    obj_meta: dict[str, Any] = {"mode": mode, "lam": lam, "init_adapter": init_adapter}
    if mode == "consistency":
        tr, m1 = build_consistency_records(train_rows, tokenizer, cfg["language"], view)
        va, _ = build_consistency_records(val_rows, tokenizer, cfg["language"], view) if val_rows else ([], {})
        obj_meta.update(m1)
        tag = f"cons_{view}_lam{lam:g}"
    elif mode == "negatives":
        negs = load_negatives(cfg["train_conditions"], cfg["language"])
        tr, m1 = build_negative_records(train_rows, negs, tokenizer, use_ul, seed)
        va = [{**r, "kind": 0, "ul_index": -1} for r in data.to_sft_records(val_rows)] if val_rows else []
        obj_meta.update(m1)
        tag = f"neg_{'ul' if use_ul else 'data'}_lam{lam:g}"
    else:
        tr = data.to_sft_records(train_rows)
        va = data.to_sft_records(val_rows) if val_rows else []
        tag = "sft"
    if init_adapter:
        tag = f"curr_{tag}"
    train_ds = Dataset.from_list(tr)
    val_ds = Dataset.from_list(va) if va else None

    out_dir = Path(args.out) if args.out else out_dir_for(cfg, tag)
    out_dir.mkdir(parents=True, exist_ok=True)

    trunc = measure_truncation(train_ds, tokenizer, int(tcfg["max_seq_len"]))
    print(f"[objectives] truncation: {json.dumps(trunc)}", flush=True)
    if trunc["truncation_rate"] > MAX_TRUNCATION_RATE:
        raise SystemExit(f"truncation rate {trunc['truncation_rate']:.3%} exceeds guard")

    use_cuda = torch.cuda.is_available()
    dtype = torch.bfloat16 if use_cuda else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["hf_id"], dtype=dtype, attn_implementation=tcfg.get("attn_implementation", "sdpa"))
    model.config.use_cache = False

    peft_cfg = None
    if init_adapter:
        # Curriculum: the trainable adapter IS the existing tuned_L0 LoRA, continued.
        model = PeftModel.from_pretrained(model, str(PROJECT_ROOT / init_adapter), is_trainable=True)
        n_tr = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"[objectives] init from {init_adapter}: {n_tr:,} trainable params", flush=True)
        if n_tr == 0:
            raise SystemExit("init_adapter loaded with no trainable parameters")
    else:
        peft_cfg = LoraConfig(
            r=int(cfg["peft"]["r"]), lora_alpha=int(cfg["peft"]["alpha"]),
            lora_dropout=float(cfg["peft"]["dropout"]), target_modules=list(cfg["peft"]["target_modules"]),
            task_type=cfg["peft"].get("task_type", "CAUSAL_LM"), bias="none")

    teacher = None
    if mode == "consistency" and lam > 0:
        # A SEPARATE frozen copy rather than a second adapter on the student: 13.5 GB more on a
        # 141 GB card buys a forward path that cannot interact with PEFT's active-adapter state
        # or gradient checkpointing.
        t_base = AutoModelForCausalLM.from_pretrained(mcfg["hf_id"], dtype=dtype, attn_implementation="sdpa")
        teacher = PeftModel.from_pretrained(t_base, str(PROJECT_ROOT / ocfg["teacher_adapter"]))
        teacher.eval()
        for p in teacher.parameters():
            p.requires_grad_(False)
        if use_cuda:
            teacher.cuda()
        obj_meta["teacher_adapter"] = ocfg["teacher_adapter"]
        obj_meta["teacher_view"] = view

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
        packing=False, completion_only_loss=True,
        bf16=use_cuda and dtype is torch.bfloat16,
        gradient_checkpointing=bool(tcfg.get("gradient_checkpointing", True)) and use_cuda,
        save_strategy=tcfg.get("save_strategy", "epoch"),
        save_steps=int(tcfg.get("save_steps", 500)),
        save_total_limit=None,
        eval_strategy="steps" if val_ds is not None else "no",
        eval_steps=int(tcfg.get("eval_steps", 200)),
        per_device_eval_batch_size=int(tcfg["per_device_batch"]),
        logging_steps=int(tcfg.get("logging_steps", 20)),
        seed=seed, data_seed=seed, report_to=[], use_cpu=not use_cuda,
        max_steps=args.max_steps if args.max_steps is not None else -1,
        dataloader_num_workers=2,
        remove_unused_columns=False,
    )

    Trainer = make_trainer_class()
    trainer = Trainer(model=model, args=sft_args, train_dataset=train_ds, eval_dataset=val_ds,
                      processing_class=tokenizer, peft_config=peft_cfg,
                      mode=mode, lam=lam, teacher=teacher)
    trainer.data_collator = PassthroughCollator(trainer.data_collator, tokenizer.pad_token_id, mode)

    manifest = RunManifest(
        experiment=cfg.get("phase", "main") + "/objectives",
        run_id=f"{cfg['model']}__{cfg['language']}__{cfg.get('run_tag', 'obj')}__{tag}__s{seed}",
        seed=seed, config_path=str(args.config), config_resolved={**cfg, "train": tcfg},
        model_hf_id=mcfg["hf_id"],
        adapter={"path": str(out_dir), "train_cond": cond_tag(cfg["train_conditions"]),
                 "rank": int(cfg["peft"]["r"]), "base_model": mcfg["hf_id"], "arch": f"objective_{mode}"},
        gpu_visible=os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        extra={"dataset": bundle["meta"], "truncation": trunc, "objective": obj_meta,
               "n_train_records": len(train_ds), **prompts.provenance_block()},
    ).capture_git().hash_scripts(SCRIPTS_FOR_PROVENANCE + ["src/obtune/objectives.py"])
    manifest.write(out_dir)

    if args.dry_run:
        batch = next(iter(trainer.get_train_dataloader()))
        print(f"[objectives] DRY RUN keys={sorted(batch)} shape={tuple(batch['input_ids'].shape)} "
              f"supervised={int((batch['labels'] != -100).sum())}", flush=True)
        if mode == "consistency":
            ok = 0
            for b in range(batch["labels"].size(0)):
                s_pos = (batch["labels"][b] != -100).nonzero(as_tuple=True)[0]
                L = int(batch["t_att"][b].sum()); c = int(batch["t_clen"][b])
                ok += int(s_pos.numel() == c and torch.equal(batch["labels"][b, s_pos], batch["t_ids"][b, L - c:L]))
            print(f"[objectives] answer-token correspondence: {ok}/{batch['labels'].size(0)} rows", flush=True)
        if mode == "negatives":
            print(f"[objectives] kinds={batch['kind'].tolist()} ul_index={batch['ul_index'].tolist()}", flush=True)
        return 0

    result = trainer.train()
    trainer.save_model(str(out_dir / "final"))
    tokenizer.save_pretrained(str(out_dir / "final"))
    summary = {"train_runtime_s": result.metrics.get("train_runtime"),
               "train_loss": result.metrics.get("train_loss"), "steps": result.global_step,
               "objective": obj_meta, "n_train_records": len(train_ds),
               "checkpoints": sorted(p.name for p in out_dir.glob("checkpoint-*"))}
    (out_dir / "training_summary.json").write_text(json.dumps(summary, indent=2))
    manifest.extra["training_summary"] = summary
    manifest.adapter["sha256"] = sha256_dir(out_dir / "final")
    manifest.finalize().write(out_dir)
    print(f"[objectives] done: {json.dumps(summary)}", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="alternative fine-tuning objectives")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--config", required=True)
    t.add_argument("--model", default=None)
    t.add_argument("--objective", choices=["sft", "consistency", "negatives"], default=None)
    t.add_argument("--lam", type=float, default=None)
    t.add_argument("--teacher-view", choices=["parent", "same"], default=None)
    t.add_argument("--no-ul", action="store_true", help="negatives: drop the negative rows (data-only control)")
    t.add_argument("--out", default=None)
    t.add_argument("--seed", type=int, default=None)
    t.add_argument("--max-steps", type=int, default=None)
    t.add_argument("--dry-run", action="store_true")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)
    cfg.setdefault("train", {})
    if args.model:
        cfg["model"] = args.model
    if args.seed is not None:
        cfg["train"]["seed"] = args.seed
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        from obtune import gpu
        gpu.pin(gpu.pick_free_gpus(1))
    return train(cfg, args)


if __name__ == "__main__":
    sys.exit(main())
