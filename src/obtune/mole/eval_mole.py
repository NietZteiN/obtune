"""Evaluate a mixture model through `eval_vllm.run_cell`, unchanged.

THE DESIGN DECISION THIS FILE EXISTS TO MAKE
--------------------------------------------
`eval_vllm`'s `render_prompts`, `drop_overlong`, `build_trial_rows`, `write_cell`, `cell_dir`
and `assert_adapter_effective` are all engine-free and importable; only `Engine.generate` is
vLLM-specific. So rather than writing a second evaluation pipeline, `HFEngine` implements the
same surface and `run_cell` works verbatim.

That is the highest-leverage choice available here. It means mixture cells are schema-valid,
graded by `scoring.grade` through the identical code path as every other arm, collatable by
`trial_table.py` with no special-casing, and `is_core`-computable — none of which the previous
HF path managed. The alternative, a bespoke loop, is exactly what `moe_soft_generate` was: it
emitted ungraded dicts that no analysis could consume, and it was deleted for it.

WHY THE MIXTURE CANNOT USE vLLM
-------------------------------
`LoRARequest` carries a single `lora_path` and the punica kernels index one `lora_int_id` per
token, so vLLM applies exactly ONE adapter per request. A per-token blend is not expressible
there at any `max_lora_rank`. Confirmed against vllm 0.26.

BATCHING IS NOT OPTIONAL
------------------------
Unbatched HF generation is ~3-5 s/item, i.e. over an hour per 1000-item cell; batched at 32
it is ~10-15 min. The old HF path looped one row at a time, which is why it was only ever
described as usable "on a stratified subset". Left-padding is required for correct generation
from a batch, and length bucketing keeps padding waste down.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import torch

from obtune.mole.model import MoLEModel


class HFEngine:
    """`eval_vllm.Engine`'s surface, backed by a mixture model.

    Contract, as `run_cell` uses it: `.tokenizer`, `.ecfg`, `.stub`,
    `.generate(texts, sampling, adapters) -> (list[str], list[int])`, `.version()`.
    """

    def __init__(
        self,
        holder: MoLEModel,
        tokenizer: Any,
        *,
        ecfg: Optional[Mapping[str, Any]] = None,
        batch_size: int = 32,
        stub: bool = False,
        label: str = "mole",
    ) -> None:
        self.holder = holder
        self.tokenizer = tokenizer
        # `run_cell` reads engine.ecfg for the drop_overlong bounds. Without it the very
        # first cell dies on AttributeError — the contract is five members, not four.
        self.ecfg = dict(ecfg or {})
        self.batch_size = int(batch_size)
        self.stub = bool(stub)
        self.label = label
        # Left padding, or a batched generate continues from pad tokens for every sequence
        # shorter than the longest — the completions would be silently mis-aligned.
        self.tokenizer.padding_side = "left"
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def version(self) -> str:
        """A STRING, matching `eval_vllm.Engine.version`.

        `run_cell` writes this straight into the cell's run manifest under `"engine"`. The
        vLLM engine returns a string there, so returning a dict would silently change the
        manifest's shape for mixture cells only — and anything that parsed it uniformly
        across cells would break on exactly the new arm. Structured detail goes to
        `version_detail()`, which callers ask for explicitly.
        """
        import transformers

        d = self.version_detail()
        return (f"hf-mole/transformers={transformers.__version__}/torch={torch.__version__}/"
                f"experts={d.get('n_experts')}/rank={d.get('total_rank')}/bs={self.batch_size}")

    def version_detail(self) -> dict[str, Any]:
        import transformers

        return {
            "engine": "hf-mole",
            "transformers": transformers.__version__,
            "torch": torch.__version__,
            "batch_size": self.batch_size,
            **{k: v for k, v in self.holder.summary.items()
               if k in ("model", "dtype", "n_experts", "experts", "rank_per_expert",
                        "total_rank", "n_attached", "gate_params")},
        }

    def generate(
        self,
        texts: Sequence[str],
        sampling: Mapping[str, Any],
        adapters: Sequence[Optional[str]],
    ) -> tuple[list[str], list[int]]:
        if self.stub:
            from obtune.provenance import sha256_text

            return [f"<stub:{sha256_text(t)[:8]}>" for t in texts], [4] * len(texts)

        # The mixture is baked into the model, so there is no per-item adapter to honour. A
        # caller passing several distinct adapters believes it is routing; say so rather than
        # silently ignoring the argument and reporting the result as routed.
        distinct = {a for a in adapters if a is not None}
        if len(distinct) > 1:
            raise ValueError(
                f"HFEngine received {len(distinct)} distinct adapters; the mixture is baked "
                f"into the model and cannot dispatch per item. Routing happens inside the "
                f"gate, not through this argument.")

        max_new = int(sampling.get("max_tokens", 64))
        temperature = float(sampling.get("temperature", 0.0))
        stop = list(sampling.get("stop", []) or [])

        # Bucket by tokenised length so each batch pads to a similar width.
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        outs: list[str] = [""] * len(texts)
        ntoks: list[int] = [0] * len(texts)
        model = self.holder.model
        model.eval()
        # Where the INPUT ids must land. `next(model.parameters())` happens to be the
        # embedding for these architectures, so it is usually right — but under
        # `device_map="auto"` accelerate sets `model.device` to the entry point of its
        # dispatch plan, and that is the value it guarantees. Prefer it; fall back only when
        # absent. This is the fourth place today where assuming a single device was wrong.
        device = getattr(model, "device", None) or next(model.parameters()).device

        for start in range(0, len(order), self.batch_size):
            idx = order[start:start + self.batch_size]
            batch = [texts[i] for i in idx]
            enc = self.tokenizer(batch, return_tensors="pt", padding=True).to(device)
            with torch.no_grad():
                gen = model.generate(
                    **enc,
                    max_new_tokens=max_new,
                    do_sample=temperature > 0.0,
                    temperature=temperature if temperature > 0.0 else None,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            new = gen[:, enc["input_ids"].shape[1]:]
            for j, i in enumerate(idx):
                text = self.tokenizer.decode(new[j], skip_special_tokens=True)
                for s in stop:
                    if s and s in text:
                        text = text.split(s)[0]
                outs[i] = text
                ntoks[i] = int((new[j] != self.tokenizer.pad_token_id).sum())
        return outs, ntoks


def routing_report(holder: MoLEModel) -> dict[str, Any]:
    """Per-layer temperature and entropy — the diagnostic that decides what may be claimed.

    If the gate collapsed to one-hot, `mole_router` is a hard router wearing a mixture's name,
    and the headline has to say so. That is a finding, so it is measured here rather than
    inferred from accuracy.
    """
    from obtune.mole.gate import RouterGate, summarise_routing

    out: dict[str, Any] = dict(holder.summary)
    cap = holder.captured()
    if cap:
        n_e = int(holder.summary.get("n_experts") or next(iter(cap.values())).shape[-1])
        out["routing"] = summarise_routing(cap, n_e)
    if isinstance(holder.gate, RouterGate):
        out["gate"] = holder.gate.report()
    return out


# --------------------------------------------------------------------------- #
# CLI. Reuses eval_vllm.run_cell verbatim — see the module docstring for why that is the
# highest-leverage decision here.


def _load_gate(holder, cfg: dict, mode: str, seed: int):
    """Install the gate this arm is defined by. The arm IS the gate; nothing else differs."""
    import torch

    from obtune.mole.gate import one_hot_gate, uniform_gate

    n_e = int(holder.summary["n_experts"])
    if mode == "mole_uniform":
        holder.gate = uniform_gate(n_e)
    elif mode == "mole_random":
        # Build a FRESH, randomly-initialised copy of the RouterGate. Two mistakes are
        # possible here and both are silent:
        #   1. re-initialising `holder.gate` in place — by the time this arm runs, a previous
        #      arm has installed a ConstantGate whose `w` is a BUFFER, so a loop over
        #      `.parameters()` matches nothing and the "random" control is byte-identical to
        #      `mole_uniform`. That is exactly what the 2026-08-13 ladder produced: the same
        #      accuracy on all eight conditions, and a control that controlled for nothing.
        #   2. re-initialising the stashed `_router_gate` — that destroys the trained weights
        #      `mole_router` needs later in the same run.
        # A deep copy avoids both.
        import copy as _copy

        _src = getattr(holder, "_router_gate", None)
        if _src is None:
            raise SystemExit("mole_random needs the RouterGate stashed by eval_mole.main")
        holder.gate = _copy.deepcopy(_src)
        # The most important negative control in the plan: the module with its gate frozen
        # at RANDOM init. If mole_router ~= mole_random, the gain came from having 8 experts
        # resident at effective rank 256, not from routing. Re-seeded explicitly so the
        # control is reproducible rather than whatever init happened to be there.
        torch.manual_seed(seed)
        for p_ in holder.gate.parameters():
            if p_.dim() > 1:
                torch.nn.init.normal_(p_, std=0.02)
    elif mode == "mole_router":
        ck = Path(cfg["gate_checkpoint"])
        if not ck.exists():
            raise SystemExit(f"mole_router needs a trained gate; {ck} does not exist")
        # Restore the ORIGINAL RouterGate first. The ladder runs arms in sequence and the
        # fixed-mixture arms REPLACE `holder.gate` with a ConstantGate — so by the time
        # `mole_router` runs, `holder.gate` is whatever the previous arm installed, and
        # loading a RouterGate checkpoint into a ConstantGate fails with "Missing key(s):
        # w / Unexpected key(s): q_proj.*". Arms must not depend on the order they run in.
        router = getattr(holder, "_router_gate", None)
        if router is None:
            raise SystemExit(
                "no RouterGate available to load into — build_mole_model must stash the "
                "gate it created as holder._router_gate before any arm replaces it")
        holder.gate = router
        state = torch.load(ck, map_location="cpu")
        holder.gate.load_state_dict(state["gate"])
    elif mode == "mole_hardrouter":
        # The TRAINED router, argmaxed. Same weights as `mole_router`; only the softmax is
        # replaced by its argmax, so the pair isolates blending from per-token selection.
        # Loads the checkpoint the same way `mole_router` does — and for the same reason:
        # a previous arm in the ladder may have replaced `holder.gate` with a ConstantGate.
        from obtune.mole.gate import HardenedGate

        ck = Path(cfg["gate_checkpoint"])
        if not ck.exists():
            raise SystemExit(f"mole_hardrouter needs a trained gate; {ck} does not exist")
        router = getattr(holder, "_router_gate", None)
        if router is None:
            raise SystemExit("mole_hardrouter needs the RouterGate stashed by eval_mole.main")
        router.load_state_dict(torch.load(ck, map_location="cpu")["gate"])
        holder.gate = HardenedGate(router)
    elif mode.startswith("mole_hardrouter:"):
        holder.gate = one_hot_gate(int(mode.split(":", 1)[1]), n_e)
    else:
        raise SystemExit(f"unknown mixture arm {mode!r}")
    # `next(model.parameters())` is NOT the gate's device under device_map="auto" — it is
    # usually the embedding. Using it here silently undid the placement build_mole_model had
    # already got right, and would fail on the first forward of the mixture ladder, AFTER
    # the ~3 GPU-h of gate training this stage depends on. One shared resolver, one answer.
    from obtune.mole.model import gate_device

    holder.gate = holder.gate.to(gate_device(holder.model))
    return holder


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    import json
    import os
    from datetime import datetime, timezone

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--language", default=None)
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--out-root", default=None)
    ap.add_argument("--eval-conditions", default=None,
                    help="comma-separated subset; the --stub smoke uses it to run before the "
                         "composite corpus exists")
    args = ap.parse_args(argv)

    # GPU pinned BEFORE torch reaches CUDA (CLAUDE.md §1).
    if args.gpu is not None:
        from obtune import gpu

        gpu.pin([args.gpu])

    from obtune import data, prompts
    from obtune.config import PROJECT_ROOT, RESULTS_DIR, load_config
    from obtune.eval_vllm import (
        SystemSpec, assert_adapter_effective, cell_dir, run_cell, validate_systems,
    )
    from obtune.mole.model import build_mole_model
    from obtune.provenance import sha256_file
    from obtune.train_sft import resolve_model_cfg

    cfg = load_config(args.config)
    model_key = args.model or (cfg.get("models") or [cfg["model"]])[0]
    language = args.language or (cfg.get("languages") or [cfg["language"]])[0]
    phase = cfg.get("phase", "main")
    eval_source = cfg.get("eval_source", data.DEFAULT_EVAL_SOURCE)  # no --source flag on this CLI
    mcfg = resolve_model_cfg({"model": model_key})
    out_root = Path(args.out_root) if args.out_root else RESULTS_DIR / "cells"
    run_ts = datetime.now(timezone.utc).isoformat()

    systems = validate_systems([SystemSpec.from_config(s) for s in cfg["systems"]])
    experts = {k: str(PROJECT_ROOT / v) for k, v in cfg["experts"].items()}

    holder = build_mole_model(
        model_key, experts,
        d_router=int((cfg.get("gate") or {}).get("d_router", 64)),
        shared_query=bool((cfg.get("gate") or {}).get("shared_query", False)),
        dtype=(cfg.get("engine") or {}).get("dtype", "bfloat16"),
        device_map=None if args.stub else "auto",
    )
    # Keep the RouterGate the builder made. Fixed-mixture arms swap `holder.gate` out, and
    # `mole_router` needs the real one back regardless of which arm ran before it.
    holder._router_gate = holder.gate

    ecfg = {"max_model_len": mcfg.get("max_seq_len", 1536) + 128, **(cfg.get("engine") or {})}
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    engine = HFEngine(holder, tokenizer, ecfg=ecfg, stub=args.stub,
                      batch_size=int(ecfg.get("batch_size", 32)))

    seed = int((cfg.get("engine") or {}).get("seed", 17))
    summary: list[dict[str, Any]] = []
    conds = list(cfg["eval_conditions"])
    if args.eval_conditions:
        want = set(args.eval_conditions.split(","))
        conds = [c for c in conds if c in want]
        if not conds:
            raise SystemExit(f"--eval-conditions {args.eval_conditions!r} selected nothing "
                             f"from {cfg['eval_conditions']}")
    for cond in conds:
        items = data.load_eval_items(
            [cond], language, h1_access_purpose=cfg.get("h1_access_purpose"),
            script="mole/eval_mole.py", source=cfg.get("eval_source", data.DEFAULT_EVAL_SOURCE))
        data.validate_eval_items(items)
        for system in systems:
            if system.arch.startswith("mole"):
                holder.bypass = False
                _load_gate(holder, cfg, cfg.get("arm_modes", {}).get(system.name, system.arch), seed)
                holder.capture_routing(True)
            else:
                # `clear_routing()` alone would be undone by the pre-hooks on the next
                # forward; `bypass` is what actually makes this the base model.
                holder.bypass = True
                holder.clear_routing()
            cell = cell_dir(out_root, phase, model_key, language, system.name, cond)
            meta_base = {
                "run_id": f"{phase}__{model_key}__{language}__{system.name}__{cond}",
                "run_ts": run_ts, "seed": seed, "phase": phase,
                # The grid this cell was evaluated on. `eval_vllm` records it; this path did
                # not, so every mixture cell written here carried no grid label and
                # `_assert_resume_same_grid` could not protect it — the guard treats a missing
                # `eval_source` as "cannot tell" and allows the resume. Same field, same
                # meaning, so the two writers now agree. See MASTER_REPORT 12.1.
                "eval_source": eval_source,
                "experiment_id": cfg.get("experiment_id", Path(args.config).stem),
                "base_model": mcfg["hf_id"], "model_family": mcfg["family"],
                "adapter_id": system.adapter, "h1_access_purpose": cfg.get("h1_access_purpose"),
                "gpu_id": os.environ.get("CUDA_VISIBLE_DEVICES"),
                "config_sha": sha256_file(cfg["_config_path"]),
                "script_sha": sha256_file(PROJECT_ROOT / "src" / "obtune" / "mole" / "eval_mole.py"),
                **prompts.provenance_block(oracle=system.prompt_oracle, one_shot=system.one_shot),
            }
            res = run_cell(engine, items, system, cell, cfg, meta_base,
                           resume=bool((cfg.get("output") or {}).get("resume", True)),
                           limit=args.limit)
            print(f"[mole.eval] {model_key}/{language} {system.name}__{cond}: "
                  f"n={res.n_items} acc={res.accuracy:.3f}", flush=True)
            summary.append({"system": system.name, "eval_cond": cond,
                            "n": res.n_items, "accuracy": res.accuracy})
            if system.arch.startswith("mole") and not res.skipped:
                (cell / "gate_report.json").write_text(
                    json.dumps(routing_report(holder), indent=2, default=str))

        # `assert_adapter_effective` runs only for `system.adapter or system.is_routed`
        # (eval_vllm.py:743), and a mixture system has NEITHER — so the check that catches
        # "the tuned system silently produced base outputs" would skip exactly the new arm.
        # Called explicitly here.
        base_sys = next((s for s in systems if s.arch == "none" and not s.prompt_oracle), None)
        if base_sys is not None and not args.stub:
            base_cell = cell_dir(out_root, phase, model_key, language, base_sys.name, cond)
            for system in systems:
                if system.arch.startswith("mole"):
                    assert_adapter_effective(
                        cell_dir(out_root, phase, model_key, language, system.name, cond),
                        base_cell)

    print(json.dumps({"n_cells": len(summary)}, indent=2))
    return 0


__all__ = ["HFEngine", "routing_report", "main"]


if __name__ == "__main__":
    import sys

    sys.exit(main())
