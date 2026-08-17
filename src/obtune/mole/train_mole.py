"""Train the RouterLoRA gate. Base and experts stay frozen.

    python -m obtune.mole.train_mole --config mole/routerlora_v1.yaml --dry-run
    python -m obtune.mole.train_mole --config mole/routerlora_v1.yaml

WHAT IS TRAINABLE
-----------------
The gate, and nothing else — 2.77 M parameters against a 295 M expert bank and a 1.5 B base.
`attach_gate` freezes by allow-list rather than by name pattern, because a pattern that missed
would silently produce a full fine-tune that still yields plausible losses and would be
attributed to "the mixture". `--dry-run` prints the trainable/frozen split so that is visible
before any GPU time is spent.

WHY NOT TRL
-----------
`SFTTrainer` wants a `peft_config` or a plain model and owns the parameterisation; here the
parameterisation is a hook-driven mixture that PEFT knows nothing about. The loop below is
deliberately small — completion-only cross-entropy over prompt-masked labels — and reuses the
project's existing pieces for everything that is not the loop itself:

  * `obtune.gpu.pin` BEFORE importing torch (CLAUDE.md §1);
  * `obtune.data.to_sft_records` / `srh.dataset.load_mixture` for the mixture, so the training
    distribution is identical to every other arm's;
  * `obtune.prompts` via those builders, so train and eval prompts match (§4 silent-failure #3);
  * `obtune.train_sft.measure_truncation` as a HARD gate at 1 % (§4 silent-failure #8);
  * `obtune.provenance.RunManifest` so the run is reproducible.

LOSS-MASK CHECK IS NOT OPTIONAL. §4 silent-failure #4: prompt tokens must be -100. `--dry-run`
decodes a real batch and asserts it, because TRL-style masking bugs produce a model that
trains on its own prompt and looks fine on the loss curve.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Optional

from obtune.config import PROJECT_ROOT, RUNS_DIR, load_config


def _mask_prompt(tokenizer, prompt: str, full: str, max_len: int) -> tuple[list[int], list[int]]:
    """Tokenise `full`, masking the `prompt` prefix to -100."""
    enc = tokenizer(full, truncation=True, max_length=max_len)
    ids = enc["input_ids"]
    n_prompt = len(tokenizer(prompt, truncation=True, max_length=max_len)["input_ids"])
    labels = [-100] * min(n_prompt, len(ids)) + ids[min(n_prompt, len(ids)):]
    return ids, labels


def render_pair(tokenizer, record) -> tuple[str, str]:
    """(prompt_text, prompt+completion_text) for one record, via the chat template."""
    prompt = tokenizer.apply_chat_template(record["prompt"], tokenize=False,
                                           add_generation_prompt=True)
    full = tokenizer.apply_chat_template(list(record["prompt"]) + list(record["completion"]),
                                         tokenize=False)
    return prompt, full


def make_collate(tokenizer, max_len: int):
    """Batch collator: right-pad ids, pad labels with -100, build the attention mask.

    Module-level and returned as a closure rather than defined inside `main`, because as a
    local it was unreachable from tests — and it is the only place the loss mask, the
    padding and the attention mask meet. Those ~10 lines run for ~3 GPU-h; a label padded
    with the pad TOKEN instead of -100 would train the gate to predict padding and still
    produce a falling loss curve.
    """
    import torch

    pad = tokenizer.pad_token_id
    if pad is None:
        pad = tokenizer.eos_token_id

    def collate(batch):
        enc = [_mask_prompt(tokenizer, *render_pair(tokenizer, b), max_len) for b in batch]
        width = max(len(i) for i, _ in enc)
        ids = torch.tensor([i + [pad] * (width - len(i)) for i, _ in enc])
        lab = torch.tensor([l + [-100] * (width - len(l)) for _, l in enc])
        att = torch.tensor([[1] * len(i) + [0] * (width - len(i)) for i, _ in enc])
        return {"input_ids": ids, "labels": lab, "attention_mask": att}

    return collate



def load_balance_term(contexts, device=None):
    """Switch-style load-balancing loss over the routing of the forward just run.

    `E * sum_i(f_i * P_i)` averaged over layers, where `f_i` is the fraction of tokens whose
    argmax is expert `i` and `P_i` the mean gate probability for `i`. Minimised when every
    expert receives an equal share and grows as mass concentrates, so it penalises exactly
    the pattern §12.8 measured: three of eight experts at ~.003 regardless of input.

    `f` is DETACHED on purpose. It comes from an argmax and carries no usable gradient; the
    learning signal flows through `P`. This is the Switch Transformer formulation, not an
    approximation of it.

    Module-level rather than a closure in `main` for the reason `make_collate` already is:
    as a local it was unreachable from tests, and this is ~10 lines that will run for GPU
    hours and whose failure mode is a silently mis-scaled loss.
    """
    import torch

    total = torch.zeros((), device=device)
    n = 0
    for ctx in contexts.values():
        w = getattr(ctx, "weights", None)
        if w is None:
            continue
        flat = w.reshape(-1, w.shape[-1]).float()
        P = flat.mean(dim=0)
        f = torch.zeros_like(P).scatter_add_(
            0, flat.argmax(dim=-1), torch.ones(flat.shape[0], device=flat.device)
        ) / flat.shape[0]
        total = total + flat.shape[-1] * (f.detach() * P).sum()
        n += 1
    return total / max(n, 1)


def build_records(cfg: dict):
    """Output-prediction prompt/completion pairs — THE SAME TASK THE GATE IS SCORED ON.

    THE BUG THIS REPLACED (found 2026-08-11, before any GPU time was spent).
    ------------------------------------------------------------------------
    This used `cft.prompts.build_gen_messages`, which builds a source-to-source
    transformation prompt: *"Obfuscate the following Python code by random variable
    renaming"*, with the obfuscated program as the target. But `eval_mole` scores through
    `eval_vllm.run_cell`, whose prompt is *"You are a deterministic code execution engine
    ... Return value:"* with the RETURN VALUE as the target.

    Those are different tasks, not different templates. The gate would have been trained to
    route for code rewriting and evaluated on output prediction — and it would have trained
    cleanly, converged, and produced a plausible accuracy that answered no question at all.
    CLAUDE.md §4 silent-failure #3, in its most severe form.

    `data.build_sft_splits` is the path `train_sft.py` uses, so the gate is now trained on
    exactly the task, prompt builder and data the eight experts were themselves trained on.
    It returns TRL conversational prompt-completion records — `{"prompt": [...],
    "completion": [{"role": "assistant", ...}]}` — which is the shape `measure_truncation`
    and the collate function below both require.
    """
    from obtune import data

    tcfg = dict(cfg.get("train") or {})
    bundle = data.build_sft_splits({**cfg, "train": tcfg})
    return bundle["train"], bundle["val"]


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--gpu", default=None, help="physical GPU index; pinned before torch")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the trainable split, the mixture and the loss mask; no training")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    seed = int(args.seed if args.seed is not None else cfg.get("train", {}).get("seed", 17))

    # GPU pinned BEFORE torch is imported anywhere (CLAUDE.md §1). The scheduler already sets
    # CUDA_VISIBLE_DEVICES for queued jobs, so --gpu is for hand runs only.
    if args.gpu is not None:
        from obtune import gpu

        gpu.pin(int(args.gpu))

    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    from obtune.mole.model import build_mole_model
    from obtune.seedutil import set_seed
    from obtune.train_sft import measure_truncation

    set_seed(seed)

    experts = {k: str(PROJECT_ROOT / v) for k, v in cfg["experts"].items()}
    missing = {k: v for k, v in experts.items() if not Path(v).exists()}
    if missing:
        raise SystemExit(f"missing expert adapter(s): {missing}")

    tcfg = cfg.get("train", {})
    max_len = int(tcfg.get("max_seq_len", 2048))
    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)[cfg["model"]]["hf_id"]
    tokenizer = AutoTokenizer.from_pretrained(hf_id)

    records, val_records = build_records(cfg)
    print(f"[mole.train] {len(records)} train / {len(val_records)} val instances, "
          f"{len(experts)} experts, seed {seed}")

    # §4 silent-failure #8 — S1/S2 inflate code length, and silent truncation reads as a
    # structural-condition effect. Hard gate, never bypassed.
    trunc = measure_truncation(records, tokenizer, max_len, sample=2000)
    rate = float(trunc.get("rate", trunc.get("truncated_fraction", 0.0)))
    print(f"[mole.train] truncation at max_seq_len={max_len}: {rate:.3%}")
    if rate > 0.01:
        raise SystemExit(
            f"truncation {rate:.2%} exceeds the 1% gate; raise max_seq_len or shorten the "
            f"mixture. Truncated targets would be scored as generation failures.")

    # GPU when we can get one, CPU when we cannot. Preferring "auto" is what makes the dry
    # run exercise real device placement (see the note below), but the pipeline invokes it as
    # a GATE — often while the previous stage's job still occupies the card — and a dry run
    # that hard-fails on a busy GPU turns a structural check into a false negative that skips
    # the stage. Degrade to CPU with a loud note instead: the mask, freeze and gradient
    # checks all still run, only the placement check is lost.
    def _build(dev_map):
        return build_mole_model(
            cfg["model"], experts,
            d_router=int(cfg.get("gate", {}).get("d_router", 64)),
            shared_query=bool(cfg.get("gate", {}).get("shared_query", False)),
            dtype=tcfg.get("dtype", "bfloat16"),
            device_map=dev_map,
            gradient_checkpointing=bool(tcfg.get("gradient_checkpointing", True)),
        )

    if args.dry_run:
        try:
            holder = _build("auto" if torch.cuda.is_available() else None)
        except Exception as exc:  # noqa: BLE001
            print(f"[mole.train] could not place on GPU ({type(exc).__name__}: {exc}); "
                  f"falling back to CPU — the DEVICE check is skipped this run", flush=True)
            holder = _build(None)
    else:
        holder = _build("auto")

    n_gate = sum(p.numel() for p in holder.gate.parameters())
    n_bank = int(holder.summary.get("bank_params", 0))
    print(f"[mole.train] trainable gate params {n_gate:,} | frozen bank {n_bank:,} "
          f"| ratio {n_gate / max(n_bank, 1):.4f}")

    if args.dry_run:
        # §4 silent-failure #4: prompt tokens MUST be -100, or the model trains on its own
        # prompt and the loss curve looks entirely healthy.
        r = records[0]
        p_text = tokenizer.apply_chat_template(r["prompt"], tokenize=False,
                                               add_generation_prompt=True)
        _, full = render_pair(tokenizer, r)
        ids, labels = _mask_prompt(tokenizer, p_text, full, max_len)
        n_masked = sum(1 for x in labels if x == -100)
        print(f"[mole.train] loss mask: {n_masked}/{len(labels)} prompt tokens are -100")
        assert n_masked > 0 and n_masked < len(labels), "loss mask is degenerate"
        assert all(p.requires_grad for p in holder.gate.parameters())
        assert not any(p.requires_grad for p in holder.model.parameters())

        # ONE REAL STEP. Everything above inspects the setup; none of it executes the
        # model. On 2026-08-12 this dry run passed and the queued job then died on the very
        # first forward with `expected mat1 and mat2 to have the same dtype` — the base runs
        # bf16, the gate is fp32, and nothing had ever put a tensor through the hooks. A gate
        # that "validates" without running the thing it validates is not a gate.
        #
        # Kept to two examples so it stays seconds on CPU, and it is the FULL path: collate,
        # forward through the mixture hooks, loss, backward, and a check that gradient
        # actually reached the gate.
        # `records` is a datasets.Dataset: slicing it returns a DICT OF COLUMNS, not rows,
        # and the collator would then iterate the column names as if they were examples
        # ("string indices must be integers"). Index row-wise instead — which is also what
        # DataLoader does, so this exercises the same access pattern training will use.
        batch = make_collate(tokenizer, max_len)([records[i] for i in range(2)])
        device = next(holder.model.parameters()).device
        batch = {k: v.to(device) for k, v in batch.items()}
        out = holder.model(**batch)
        assert torch.isfinite(out.loss), f"non-finite loss on the first batch: {out.loss}"
        out.loss.backward()
        n_grad = sum(1 for p in holder.gate.parameters()
                     if p.grad is not None and p.grad.abs().sum() > 0)
        assert n_grad > 0, "backward produced no gradient on the gate — it would not train"
        holder.model.zero_grad(set_to_none=True)
        print(f"[mole.train] forward+backward OK: loss {out.loss.item():.4f}, "
              f"{n_grad} gate tensor(s) received gradient")
        print("[mole.train] --dry-run OK: gate trainable, base+bank frozen, mask asserted, "
              "one real step executed")
        return 0

    collate = make_collate(tokenizer, max_len)

    bs = int(tcfg.get("per_device_batch", 8))
    accum = int(tcfg.get("grad_accum", 8))
    epochs = int(tcfg.get("epochs", 2))
    loader = DataLoader(records, batch_size=bs, shuffle=True, collate_fn=collate)
    opt = torch.optim.AdamW(holder.trainable_parameters(),
                            lr=float(tcfg.get("lr", 1e-3)),
                            weight_decay=float(tcfg.get("weight_decay", 0.0)))
    device = next(holder.model.parameters()).device
    holder.model.train()

    # --- routing regularisation -------------------------------------------------------- #
    # WHY THIS EXISTS. The first gate was trained on the task loss ALONE, and the result was
    # a gate that ignores its input: one fixed blend (~.38 L2, ~.24 S2/S4) on every
    # condition, with L1r/S1/S3/L0 at ~.003, and composites showing 13-60x BELOW-chance mass
    # on the experts whose transforms are actually present (MASTER_REPORT §12.8).
    #
    # That is the EXPECTED optimum of the objective we wrote, not a bug in it: a constant
    # blend minimises average loss and nothing rewards varying with the input. Switch
    # Transformer and GShard both add an auxiliary load-balancing term for exactly this
    # reason, and neither this file nor configs/mole/ had one.
    #
    # `aux_load_balance` is the Switch-style term E * sum_i(f_i * P_i), where f_i is the
    # fraction of tokens routed to expert i (argmax) and P_i the mean gate probability. It is
    # minimised at a uniform assignment and grows when mass concentrates, so it penalises
    # exactly the dead-expert pattern observed. Default 0.0 => OFF, so every existing config
    # reproduces bit-for-bit; the fixed arm opts in.
    aux_coef = float(tcfg.get("aux_load_balance", 0.0))
    if aux_coef and not hasattr(holder.gate, "keys"):
        raise ValueError("aux_load_balance is only meaningful for a trainable RouterGate")

    step = 0
    for epoch in range(epochs):
        for i, batch in enumerate(loader):
            batch = {k: v.to(device) for k, v in batch.items()}
            task = holder.model(**batch).loss
            aux = (load_balance_term(holder.contexts, device) if aux_coef
                   else torch.zeros((), device=device))
            loss = (task + aux_coef * aux) / accum
            loss.backward()
            if (i + 1) % accum == 0:
                torch.nn.utils.clip_grad_norm_(holder.trainable_parameters(),
                                               float(tcfg.get("max_grad_norm", 1.0)))
                opt.step()
                opt.zero_grad(set_to_none=True)
                # Temperature floor. The first run learned tau down to .39-.51 uniformly
                # across all 28 layers from an init of 1.0 — the gate became MORE confident
                # about a preference that does not depend on its input. Clamping stops it
                # sharpening before it can discriminate; it cannot help a gate that has
                # already collapsed, so it is a training-time guard, not a fix on its own.
                tau_min = float(tcfg.get("min_temperature", 0.0))
                if tau_min > 0 and hasattr(holder.gate, "log_tau"):
                    with torch.no_grad():
                        holder.gate.log_tau.clamp_(min=math.log(tau_min))
                step += 1
                if step % 10 == 0:
                    print(f"[mole.train] epoch {epoch} step {step} "
                          f"loss {task.item():.4f}"
                          + (f" aux {aux.item():.4f}" if aux_coef else ""), flush=True)

    out_dir = Path(cfg.get("out_dir") or (RUNS_DIR / "mole" / cfg["model"] / cfg["language"]
                                          / f"{cfg.get('run_tag', 'routerlora')}_s{seed}"))
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"gate": holder.gate.state_dict(), "summary": holder.summary}, out_dir / "gate.pt")
    (out_dir / "summary.json").write_text(json.dumps(holder.summary, indent=2))

    from obtune.provenance import RunManifest

    RunManifest(
        experiment=str(cfg.get("experiment", "mole/routerlora")),
        run_id=f"mole__{cfg['model']}__{cfg['language']}__s{seed}",
        seed=seed,
        config_path=str(args.config),
        config_resolved=dict(cfg),
        model_hf_id=hf_id,
        extra={"summary": holder.summary, "steps": step},
    ).write(out_dir)
    print(f"[mole.train] wrote {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
