"""Weight-space invariance: L = L_task(x_obf) + lambda * L_align  (Phase 2).

THE IDEA. Every repair attempted so far optimized task accuracy and hoped invariance
would follow; all five were null. This arm optimizes invariance as an OBJECTIVE. The
student does output prediction on obfuscated code as usual, and is additionally pulled
to represent that code the way a frozen teacher represents the CLEAN original:

    "Do the task on the obfuscated code, and while you're at it, think about it the
     way you think about the clean code."

L_task is the ordinary answer loss, identical to the vanilla SFT arm. It is what stops
the student satisfying L_align by collapsing to a degenerate representation.

WHY A FROZEN CLEAN-CODE TEACHER, NOT A SECOND OBFUSCATED VIEW. The earlier sketch
(master report §9 Stage 3) used a symmetric consistency loss between two obfuscated
views, which can be minimized by both views drifting to a shared degenerate point.
Anchoring asymmetrically to a frozen teacher cannot drift: the target is fixed.

WHY tuned_L0 AND NOT base. `base` scores 21.7 on L0; aligning to it teaches the student
to be as weak as an untuned model. `tuned_L0` scores 44.7 and is the project's control
anyway, so the arm's ceiling is legible: on H1 that is 24.5 -> 44.7 of headroom.

THE n != m PROBLEM, AND WHY IT DOES NOT ARISE. Teacher states on clean x are [n, d] and
student states on obfuscated x_obf are [m, d] with n != m, because obfuscated code
tokenizes differently. We compare only at the ANSWER POSITION: prompts.py is frozen and
its template sha is pinned in every run manifest, so the prompt SUFFIX tokenizes
identically across conditions. The last k prompt tokens are therefore the same k tokens
in both sequences, and the mismatch never arises. `resolve_answer_positions` derives
those positions from the loss mask rather than from string lengths, so it cannot drift
out of sync with whatever TRL actually built.

COST. The plan budgeted ~2x vanilla SFT for a no-grad teacher forward every step. That
is avoidable: the teacher is FROZEN, so its states are constant and can be computed once
and cached (`build_cache`). Training is then ~1.0x vanilla, and -- the part that matters
more -- the mismatched-teacher control becomes a permutation of a cache index, i.e. free.
That control was budgeted as first-class precisely because this project has three times
been burned by an arm that turned out to be a regularizer (`mole_random`, the `l0merge`
control, the oracle-of-k headroom). Making it cost nothing is the best way to guarantee
it actually gets run.

    python -m obtune.align cache --config train/align_qwen1.5b_py_S2.yaml
    python -m obtune.align train --config train/align_qwen1.5b_py_S2.yaml
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import numpy as np

from obtune import data, prompts
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RUNS_DIR, load_config

# Layers RQ3 already sweeps. Chosen because the condition is linearly decodable at 99.4 %
# by layer 4, so if "read past the surface" happens anywhere, it has to happen by then.
# (DEFAULT_LAYERS removed: superseded by resolve_align_layers(), which turns depth
# fractions into indices per model. A literal set here meant Qwen's 28 layers.)
DEFAULT_K = 4
CACHE_ROOT = RUNS_DIR / "align_cache"


def case_key(item_id: str) -> str:
    """`program_id::condition::case_idx` -> `program_id::case_idx`.

    The join key between an obfuscated row and its clean L0 parent. Pairing is free by
    construction: every condition is a single transform from an L0 parent (CLAUDE.md
    §3.1), so the corpus already contains the pair -- there is nothing to generate.
    """
    parts = item_id.split("::")
    if len(parts) != 3:
        raise ValueError(f"unexpected item_id shape: {item_id!r}")
    return f"{parts[0]}::{parts[2]}"


def resolve_answer_positions(labels: "Any", k: int) -> tuple["Any", "Any"]:
    """Positions of the k hidden states that predict the first k answer tokens.

    HF computes causal LM loss as logits[:, :-1] against labels[:, 1:], so hidden[j] is
    the state that predicts token j+1. If p is the first index with labels != -100 (the
    first completion token), hidden[p-1] is the state that predicts it, and the k states
    ending there are hidden[p-k : p].

    Returns (index tensor [B, k], valid mask [B]) -- a row whose prompt is shorter than k
    is dropped from the alignment term rather than silently clamped, because a clamped
    row would align a DIFFERENT token position in student and teacher, which is exactly
    the correspondence failure this whole design exists to avoid.
    """
    import torch

    supervised = labels != -100
    has_any = supervised.any(dim=1)
    p = supervised.float().argmax(dim=1)  # first supervised index
    valid = has_any & (p >= k)
    offsets = torch.arange(-k, 0, device=labels.device).unsqueeze(0)  # [1, k]
    idx = p.unsqueeze(1) + offsets  # [B, k]
    return idx.clamp(min=0), valid


def gather_states(hidden_states: Sequence["Any"], layers: Sequence[int], idx: "Any") -> "Any":
    """[B, len(layers), k, d] from a tuple of per-layer [B, T, d] tensors.

    `hidden_states[L]` is the OUTPUT of layer L (index 0 is the embedding table), which
    is the same indexing src/obtune/attention/ uses, so a layer number means the same
    thing here as it does in the RQ3 sweep.
    """
    import torch

    out = []
    for layer in layers:
        h = hidden_states[layer]                                  # [B, T, d]
        gather_idx = idx.unsqueeze(-1).expand(-1, -1, h.size(-1))  # [B, k, d]
        out.append(torch.gather(h, 1, gather_idx))
    return torch.stack(out, dim=1)



CODE_OPEN = "Program:\n"
CODE_CLOSE = "\n\nCall:"


def resolve_span_mask(input_ids: "Any", tokenizer: Any) -> "Any":
    """[B, T] float mask over the CODE-SPAN tokens of each prompt (lever 3b, `mode: span`).

    The answer-position mode (W5) compares only the k states that predict the answer and
    found the teacher does not matter. This mode aligns the representation of the CODE
    itself -- the user's literal request, "make the hidden states match the unobfuscated
    code" -- which n != m forbids token-by-token, so each side is MEAN-POOLED over its
    own code span per layer. The span is recovered from the token ids by re-assembling
    the sentencepiece pieces (`▁` -> space, `<0x0A>` -> newline) and locating the frozen
    prompt markers `Program:\n` … `\n\nCall:` from prompts.USER_TEMPLATE, so it needs no
    offsets from TRL's tokenization and cannot drift from what the batch really holds.
    A row with no recoverable span gets an all-zero mask (dropped from the term).
    """
    import torch

    mask = torch.zeros(input_ids.shape, dtype=torch.float32, device=input_ids.device)
    for b in range(input_ids.size(0)):
        ids = input_ids[b].tolist()
        pieces = []
        for t in tokenizer.convert_ids_to_tokens(ids):
            if t is None:
                pieces.append("")
            elif t == "<0x0A>":
                pieces.append("\n")
            elif t.startswith("<0x") and t.endswith(">") and len(t) == 6:
                pieces.append("?")
            elif t.startswith("<") and t.endswith(">"):  # special tokens
                pieces.append("")
            else:
                pieces.append(t.replace("\u2581", " "))
        text = "".join(pieces)
        s = text.find(CODE_OPEN)
        e = text.rfind(CODE_CLOSE)
        if s < 0 or e < 0 or e <= s:
            continue
        s += len(CODE_OPEN)
        pos = 0
        for j, piece in enumerate(pieces):
            a, z = pos, pos + len(piece)
            pos = z
            if z > s and a < e and piece:
                mask[b, j] = 1.0
    return mask


def pool_states(hidden_states: Sequence["Any"], layers: Sequence[int], mask: "Any") -> tuple["Any", "Any"]:
    """Mean over masked positions per layer: ([B, len(layers), d], valid [B])."""
    import torch

    cnt = mask.sum(dim=1)                                   # [B]
    valid = cnt > 0
    denom = cnt.clamp(min=1.0).unsqueeze(-1)
    out = []
    for layer in layers:
        h = hidden_states[layer]                            # [B, T, d]
        out.append((h.float() * mask.unsqueeze(-1)).sum(dim=1) / denom)
    return torch.stack(out, dim=1), valid


def resolve_align_layers(acfg, mcfg) -> list[int]:
    """Layer indices for L_align, model-agnostically.

    `layer_fracs` (fractions of depth) is the model-agnostic form and wins when present:
    [4,9,14,19,23,27] was Qwen's 28 layers, and reusing those integers on CodeLlama-7b (32)
    or -13b (40) would silently probe different RELATIVE depths, so the arm would stop
    measuring the same thing across models. `layers` is still honoured for reproducing an
    existing Qwen run exactly.
    """
    if acfg.get("layers"):
        return list(acfg["layers"])
    n = int(mcfg["n_layers"])
    fracs = acfg.get("layer_fracs") or [0.14, 0.32, 0.50, 0.68, 0.82, 0.96]
    # round to distinct in-range indices, preserving order
    out, seen = [], set()
    for f in fracs:
        i = min(n - 1, max(0, round(f * (n - 1))))
        if i not in seen:
            seen.add(i); out.append(i)
    return out

# --------------------------------------------------------------------------- #
# Teacher cache
# --------------------------------------------------------------------------- #

def cache_path(cfg: Mapping[str, Any]) -> Path:
    acfg = cfg.get("align", {}) or {}
    teacher = Path(acfg["teacher_adapter"]).name or "teacher"
    conds = "-".join(cfg["train_conditions"])
    seed = int(cfg.get("train", {}).get("seed", GLOBAL_SEED))
    mode = str(acfg.get("mode", "answer"))
    suffix = "" if mode == "answer" else f"__{mode}"
    return CACHE_ROOT / cfg["model"] / cfg["language"] / f"{conds}_s{seed}__{teacher}{suffix}.npz"


def build_cache(cfg: Mapping[str, Any], out: Optional[Path] = None, batch_size: int = 16) -> Path:
    """Run the frozen teacher over the CLEAN parents once; store answer-position states."""
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from obtune.train_sft import resolve_model_cfg, _effective_train_knobs

    acfg = cfg.get("align", {}) or {}
    layers = resolve_align_layers(acfg, resolve_model_cfg(cfg))
    k = int(acfg.get("k", DEFAULT_K))
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)

    bundle = data.build_sft_splits({**cfg, "train": tcfg})
    # TRAIN **AND** VAL. The Trainer runs compute_loss on the eval split too, so a
    # val row with no cached teacher entry raises KeyError at the first evaluation --
    # or, worse, would have to be silently skipped, which would make eval_loss and
    # train_loss incomparable (one carrying the alignment term and one not).
    student_rows = list(bundle["train_rows"]) + list(bundle["val_rows"] or [])

    # The clean parents, indexed by the join key. load_pairs is the ONLY read path, so
    # the quarantine guard in paths.load_training_jsonl still applies to this arm.
    l0_by_key = {
        case_key(r.item_id): r
        for r in data.load_pairs(["L0"], cfg["language"])
    }
    missing = [r.item_id for r in student_rows if case_key(r.item_id) not in l0_by_key]
    if missing:
        raise SystemExit(
            f"{len(missing)} of {len(student_rows)} rows have no L0 parent "
            f"(e.g. {missing[:3]}). Alignment needs the pair; refusing to train on a "
            "silently reduced set."
        )

    # One cache entry per DISTINCT clean parent, not per student row: several conditions
    # share a parent and the teacher's states do not depend on the student's condition.
    keys = sorted({case_key(r.item_id) for r in student_rows})
    records = [prompts.build_example(l0_by_key[key].model_dump()) for key in keys]

    tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["hf_id"], dtype=torch.bfloat16, attn_implementation="sdpa"
    )
    model = PeftModel.from_pretrained(model, acfg["teacher_adapter"])
    model.eval()
    if torch.cuda.is_available():
        model.cuda()

    d = int(mcfg["hidden_size"])
    mode = str(acfg.get("mode", "answer"))
    if mode == "span":
        states = np.zeros((len(records), len(layers), d), dtype=np.float16)
    else:
        states = np.zeros((len(records), len(layers), k, d), dtype=np.float16)
    kept = np.zeros(len(records), dtype=bool)

    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]
        texts, prompt_lens = [], []
        for rec in chunk:
            p_text = tok.apply_chat_template(rec["prompt"], tokenize=False, add_generation_prompt=True)
            full = p_text + rec["completion"][0]["content"]
            texts.append(full)
            prompt_lens.append(len(tok(p_text, add_special_tokens=False)["input_ids"]))
        enc = tok(texts, return_tensors="pt", padding=True, truncation=True,
                  max_length=int(tcfg["max_seq_len"]), add_special_tokens=False)
        # Build a loss mask with the same meaning TRL's completion_only_loss gives, so
        # resolve_answer_positions means the same thing in the cache and in training.
        labels = enc["input_ids"].clone()
        for i, plen in enumerate(prompt_lens):
            labels[i, :plen] = -100
        labels[enc["attention_mask"] == 0] = -100
        if torch.cuda.is_available():
            enc = {kk: v.cuda() for kk, v in enc.items()}
            labels = labels.cuda()
        with torch.no_grad():
            out_hs = model(**enc, output_hidden_states=True).hidden_states
        if mode == "span":
            span = resolve_span_mask(enc["input_ids"], tok)
            pooled, valid = pool_states(out_hs, layers, span)
            got = pooled.float().cpu().numpy()
            if start == 0:
                n_span = int(span[0].sum())
                shown = tok.decode([i for i, m in zip(enc["input_ids"][0].tolist(), span[0].tolist()) if m > 0])
                print(f"[align.cache] span check row0: {n_span} tokens -> {shown[:160]!r}", flush=True)
        else:
            idx, valid = resolve_answer_positions(labels, k)
            got = gather_states(out_hs, layers, idx).float().cpu().numpy()
        sl = slice(start, start + len(chunk))
        states[sl] = got.astype(np.float16)
        kept[sl] = valid.cpu().numpy()
        print(f"[align.cache] {start + len(chunk)}/{len(records)}", flush=True)

    dest = Path(out) if out else cache_path(cfg)
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        dest, states=states, keys=np.array(keys), valid=kept,
        layers=np.array(layers), k=k, mode=mode, teacher=str(acfg["teacher_adapter"]),
        hf_id=mcfg["hf_id"], prompt_sha=prompts.provenance_block()["prompt_template_sha256"],
    )
    print(f"[align.cache] wrote {dest}  states={states.shape}  valid={int(kept.sum())}/{len(kept)}")
    return dest


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #

class AlignCollator:
    """Wraps TRL's collator and carries one integer per row: the teacher cache index.

    The index has to survive shuffling, so it cannot be recovered from batch order --
    it travels WITH the example. `remove_unused_columns=False` is what keeps the column
    alive that far; this collator strips the remaining non-tensor columns before handing
    the batch to TRL, which would otherwise try to pad a list of chat messages.
    """

    def __init__(self, inner, passthrough: str = "align_idx"):
        self.inner = inner
        self.passthrough = passthrough

    def __call__(self, features):
        import torch

        idx = [f.pop(self.passthrough) for f in features]
        cleaned = [
            {kk: v for kk, v in f.items() if kk not in ("prompt", "completion")}
            for f in features
        ]
        batch = self.inner(cleaned)
        batch[self.passthrough] = torch.tensor(idx, dtype=torch.long)
        return batch


def make_trainer_class():
    """Built lazily so importing this module does not import torch/trl."""
    import torch
    import torch.nn.functional as F
    from trl import SFTTrainer

    class AlignTrainer(SFTTrainer):
        def __init__(self, *a, teacher_states=None, teacher_valid=None, layers=(), k=4,
                     lam=0.0, mode="answer", **kw):
            super().__init__(*a, **kw)
            self.align_mode = mode
            self.teacher_states = teacher_states   # [N, L, k, d] float32 on device
            self.teacher_valid = teacher_valid     # [N] bool
            self.align_layers = list(layers)
            self.align_k = int(k)
            self.lam = float(lam)
            self._align_running = 0.0
            self._align_steps = 0
            # GRADIENT-ACCUMULATION SCALING (found 2026-09-04 on the CodeLlama-7b W5 arms).
            # transformers' training_step only divides the loss by the accumulation count
            # when the model does NOT accept loss kwargs; otherwise it trusts compute_loss
            # to have passed `num_items_in_batch` through so the model returns a loss
            # already normalized over the whole accumulated batch. This override computes
            # per-microbatch means and never forwards that kwarg, so every arm trained
            # before this line -- the 2026-08-30 Qwen sweep and W5 -- ran on gradients
            # grad_accum (4x) too large. Adam absorbs a constant scale, but max_grad_norm
            # 1.0 then clips almost every step (grad_norm ~4.6 vs ~1.0 on mono_all), so
            # lambda = 0 was a near-twin of the vanilla arm, not the exact twin the design
            # promises. Declaring the truth here makes training_step apply the /accum to
            # task and alignment terms alike. Residual difference from vanilla: mean of
            # per-microbatch means instead of one mean over all supervised tokens.
            self.model_accepts_loss_kwargs = False

        def compute_loss(self, model, inputs, return_outputs=False, **kw):
            align_idx = inputs.pop("align_idx", None)
            labels = inputs["labels"]

            outputs = model(**inputs, output_hidden_states=self.lam > 0.0)
            task_loss = outputs.loss

            # lambda = 0 must reproduce the vanilla specialist EXACTLY -- it is the
            # plumbing check that tells a null objective apart from a broken harness.
            # So the alignment path is skipped entirely, not multiplied by zero.
            if self.lam <= 0.0 or align_idx is None:
                return (task_loss, outputs) if return_outputs else task_loss

            if self.align_mode == "span":
                span = resolve_span_mask(inputs["input_ids"], self.processing_class)
                student, valid = pool_states(outputs.hidden_states, self.align_layers, span)  # [B,L,d]
            else:
                idx, valid = resolve_answer_positions(labels, self.align_k)
                student = gather_states(outputs.hidden_states, self.align_layers, idx)  # [B,L,k,d]
            teacher = self.teacher_states[align_idx].to(student.dtype)
            valid = valid & self.teacher_valid[align_idx]

            if valid.any():
                diff = (student[valid] - teacher[valid]).float()
                align_loss = diff.pow(2).mean()
            else:
                align_loss = task_loss.new_zeros(())

            self._align_running += float(align_loss.detach())
            self._align_steps += 1
            loss = task_loss + self.lam * align_loss
            return (loss, outputs) if return_outputs else loss

        def log(self, logs, *a, **kw):
            # Surface L_align separately. A run where total loss falls while L_align is
            # flat is the objective failing to bite, and would be invisible in the sum.
            if self._align_steps:
                logs["align_loss"] = self._align_running / self._align_steps
                self._align_running, self._align_steps = 0.0, 0
            return super().log(logs, *a, **kw)

    return AlignTrainer


def _mismatch_permutation(keys: Sequence[str], seed: int) -> np.ndarray:
    """Map each cache row to a DIFFERENT program's cache row.

    THE CONTROL THAT DECIDES WHETHER A POSITIVE RESULT MEANS ANYTHING. If aligning to an
    unrelated program's clean states works as well as aligning to the matched one, then
    L_align is a regularizer and the semantic reading collapses. Permuting by PROGRAM
    (not by row) matters: a row-level shuffle would sometimes land on another case of the
    same program, which is still the matched program and would weaken the control.
    """
    rng = np.random.default_rng(seed)
    programs = np.array([kk.split("::")[0] for kk in keys])
    uniq = np.unique(programs)
    if uniq.size < 2:
        raise SystemExit("mismatch control needs >= 2 distinct programs")
    # A CYCLIC SHIFT OF a random permutation, which is a guaranteed derangement. The
    # obvious `zip(uniq, np.roll(permutation(uniq), 1))` is NOT: it pairs the sorted
    # order against a rolled random order, so a program can be handed its own states.
    # A control with fixed points is partly not a control, and the failure is invisible
    # -- it just makes the mismatch arm look a little more like the matched one.
    order = rng.permutation(uniq)
    shifted = {order[i]: order[(i + 1) % order.size] for i in range(order.size)}
    by_program: dict[str, list[int]] = {}
    for i, p in enumerate(programs):
        by_program.setdefault(p, []).append(i)
    out = np.empty(len(keys), dtype=np.int64)
    for i, p in enumerate(programs):
        pool = by_program[shifted[p]]
        out[i] = pool[i % len(pool)]
    return out


def train(cfg: Mapping[str, Any], args: argparse.Namespace) -> int:
    """Train one invariance arm. Mirrors train_sft.main; only the loss differs."""
    import torch
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTConfig

    from obtune.provenance import RunManifest, sha256_dir
    from obtune.seedutil import set_seed
    from obtune.train_sft import (
        MAX_TRUNCATION_RATE, SCRIPTS_FOR_PROVENANCE, _effective_train_knobs,
        cond_tag, measure_truncation, resolve_model_cfg,
    )

    acfg = dict(cfg.get("align", {}) or {})
    if args.lam is not None:
        acfg["lam"] = args.lam
    lam = float(acfg.get("lam", 1.0))
    layers = resolve_align_layers(acfg, resolve_model_cfg(cfg))
    k = int(acfg.get("k", DEFAULT_K))
    mismatch = bool(args.mismatch or acfg.get("mismatch", False))
    mode = str(acfg.get("mode", "answer"))

    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    seed = int(tcfg.get("seed", GLOBAL_SEED))
    set_seed(seed)

    bundle = data.build_sft_splits({**cfg, "train": tcfg})
    train_rows, val_rows = bundle["train_rows"], bundle["val_rows"]

    blob = np.load(args.cache or cache_path(cfg), allow_pickle=False)
    keys = [str(x) for x in blob["keys"]]
    if str(blob["prompt_sha"]) != prompts.provenance_block()["prompt_template_sha256"]:
        raise SystemExit(
            "teacher cache was built under a DIFFERENT prompt template. The whole "
            "answer-position correspondence rests on the suffix tokenizing identically; "
            "rebuild the cache."
        )
    cache_mode = str(blob["mode"]) if "mode" in blob.files else "answer"
    if cache_mode != mode:
        raise SystemExit(f"teacher cache is mode={cache_mode!r} but config asks for {mode!r}")
    key_to_row = {kk: i for i, kk in enumerate(keys)}
    if mismatch:
        perm = _mismatch_permutation(keys, seed + 991)
        key_to_row = {kk: int(perm[i]) for i, kk in enumerate(keys)}

    def idx_for(rows):
        return [key_to_row[case_key(r.item_id)] for r in rows]

    from datasets import Dataset
    train_ds = Dataset.from_list([
        {**rec, "align_idx": i}
        for rec, i in zip(data.to_sft_records(train_rows), idx_for(train_rows))
    ])
    val_ds = Dataset.from_list([
        {**rec, "align_idx": i}
        for rec, i in zip(data.to_sft_records(val_rows), idx_for(val_rows))
    ]) if val_rows else None

    out_dir = Path(args.out) if args.out else (
        RUNS_DIR / "adapters_align" / cfg["model"] / cfg["language"] /
        f"{cond_tag(cfg['train_conditions'])}_r{int(cfg['peft']['r'])}"
        f"_lam{lam:g}_{'span' if mode == 'span' else f'k{k}'}_L{'-'.join(map(str, layers))}"
        f"{'_mismatch' if mismatch else ''}_s{seed}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    trunc = measure_truncation(train_ds, tokenizer, int(tcfg["max_seq_len"]))
    if trunc["truncation_rate"] > MAX_TRUNCATION_RATE:
        raise SystemExit(f"truncation rate {trunc['truncation_rate']:.3%} exceeds guard")

    use_cuda = torch.cuda.is_available()
    model = AutoModelForCausalLM.from_pretrained(
        mcfg["hf_id"], dtype=torch.bfloat16 if use_cuda else torch.float32,
        attn_implementation=tcfg.get("attn_implementation", "sdpa"),
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
        max_grad_norm=float(tcfg.get("max_grad_norm", 1.0)),
        max_length=int(tcfg["max_seq_len"]),
        packing=False,
        completion_only_loss=True,
        bf16=use_cuda,
        gradient_checkpointing=bool(tcfg.get("gradient_checkpointing", True)) and use_cuda,
        save_strategy=tcfg.get("save_strategy", "epoch"),
        eval_strategy="steps" if val_ds is not None else "no",
        eval_steps=int(tcfg.get("eval_steps", 200)),
        per_device_eval_batch_size=int(tcfg["per_device_batch"]),
        logging_steps=int(tcfg.get("logging_steps", 20)),
        seed=seed, data_seed=seed, report_to=[], use_cpu=not use_cuda,
        max_steps=args.max_steps if args.max_steps is not None else -1,
        dataloader_num_workers=2,
        # Keeps `align_idx` alive as far as the collator. Without it the Trainer drops
        # every column the model's forward signature does not name.
        remove_unused_columns=False,
    )

    peft_cfg = LoraConfig(
        r=int(cfg["peft"]["r"]), lora_alpha=int(cfg["peft"]["alpha"]),
        lora_dropout=float(cfg["peft"]["dropout"]),
        target_modules=list(cfg["peft"]["target_modules"]),
        task_type=cfg["peft"].get("task_type", "CAUSAL_LM"), bias="none",
    )

    dev = "cuda" if use_cuda else "cpu"
    teacher_states = torch.from_numpy(blob["states"]).to(dev).float()
    teacher_valid = torch.from_numpy(blob["valid"]).to(dev)

    AlignTrainer = make_trainer_class()
    trainer = AlignTrainer(
        model=model, args=sft_args, train_dataset=train_ds, eval_dataset=val_ds,
        processing_class=tokenizer, peft_config=peft_cfg,
        teacher_states=teacher_states, teacher_valid=teacher_valid,
        layers=layers, k=k, lam=lam, mode=mode,
    )
    trainer.data_collator = AlignCollator(trainer.data_collator)

    manifest = RunManifest(
        experiment=cfg.get("phase", "main") + "/align",
        run_id=f"{cfg['model']}__{cfg['language']}__{cfg.get('run_tag','align')}__s{seed}",
        seed=seed, config_path=str(args.config), config_resolved={**cfg, "train": tcfg},
        model_hf_id=mcfg["hf_id"],
        adapter={"path": str(out_dir), "train_cond": cond_tag(cfg["train_conditions"]),
                 "rank": int(cfg["peft"]["r"]), "base_model": mcfg["hf_id"],
                 "arch": "invariance_mismatch" if mismatch else "invariance"},
        gpu_visible=os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        extra={"dataset": bundle["meta"], "truncation": trunc,
               "align": {"lam": lam, "layers": layers, "k": k, "mode": mode, "mismatch": mismatch,
                         "teacher_adapter": acfg.get("teacher_adapter"),
                         "cache": str(args.cache or cache_path(cfg)),
                         "n_teacher_rows": len(keys),
                         "teacher_valid": int(blob["valid"].sum())},
               **prompts.provenance_block()},
    ).capture_git().hash_scripts(SCRIPTS_FOR_PROVENANCE)
    manifest.write(out_dir)

    if args.dry_run:
        batch = next(iter(trainer.get_train_dataloader()))
        print(f"[align] DRY RUN keys={sorted(batch)} shape={tuple(batch['input_ids'].shape)} "
              f"supervised={int((batch['labels'] != -100).sum())} "
              f"align_idx={batch['align_idx'][:4].tolist()}", flush=True)
        if mode == "span":
            span = resolve_span_mask(batch["input_ids"], tokenizer)
            for b in range(min(2, span.size(0))):
                ids = [i for i, m in zip(batch["input_ids"][b].tolist(), span[b].tolist()) if m > 0]
                print(f"[align] span row{b}: {len(ids)} tokens; head={tokenizer.decode(ids[:40])!r} "
                      f"tail={tokenizer.decode(ids[-20:])!r}", flush=True)
            print(f"[align] span counts: {span.sum(dim=1).tolist()}", flush=True)
        return 0

    result = trainer.train()
    trainer.save_model(str(out_dir / "final"))
    tokenizer.save_pretrained(str(out_dir / "final"))
    summary = {"train_runtime_s": result.metrics.get("train_runtime"),
               "train_loss": result.metrics.get("train_loss"), "steps": result.global_step,
               "lam": lam, "layers": layers, "k": k, "mode": mode, "mismatch": mismatch}
    (out_dir / "training_summary.json").write_text(json.dumps(summary, indent=2))
    manifest.extra["training_summary"] = summary
    manifest.adapter["sha256"] = sha256_dir(out_dir / "final")
    manifest.finalize().write(out_dir)
    print(f"[align] done: {json.dumps(summary)}", flush=True)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cache", help="build the frozen teacher's answer-position states")
    c.add_argument("--config", required=True)
    c.add_argument("--out", default=None)
    c.add_argument("--batch-size", type=int, default=16)
    t = sub.add_parser("train", help="train one invariance arm")
    t.add_argument("--config", required=True)
    t.add_argument("--out", default=None)
    t.add_argument("--cache", default=None)
    t.add_argument("--lam", type=float, default=None, help="override align.lam (sweep)")
    t.add_argument("--seed", type=int, default=None)
    t.add_argument("--mismatch", action="store_true",
                   help="THE CONTROL: align to a different program's clean states")
    t.add_argument("--max-steps", type=int, default=None)
    t.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    cfg = load_config(a.config)
    cfg.setdefault("train", {})
    if getattr(a, "seed", None) is not None:
        cfg["train"]["seed"] = a.seed

    if a.cmd == "cache":
        if not os.environ.get("CUDA_VISIBLE_DEVICES"):
            from obtune import gpu
            gpu.pin(gpu.pick_free_gpus(1))
        build_cache(cfg, Path(a.out) if a.out else None, a.batch_size)
        return 0
    if not os.environ.get("CUDA_VISIBLE_DEVICES"):
        from obtune import gpu
        gpu.pin(gpu.pick_free_gpus(1))
    return train(cfg, a)


if __name__ == "__main__":
    sys.exit(main())
