"""Assemble a mixture model: frozen base + frozen expert bank + one trainable gate.

Each decoder layer gets a `forward_pre_hook` that reads the layer's INPUT hidden state, asks
the gate for `[B, T, E]` routing weights, and writes them into that layer's `RoutingCtx`. Every
`MoLELinear` inside the layer then reads the same weights, so one gate evaluation serves all
seven target projections.

THREE HAZARDS, each handled explicitly:

* **Decode with a KV cache.** At generation time `T == 1` and the hook fires per layer per
  step. The gate is a pure function of the CURRENT hidden state — it is attention over
  EXPERTS, not over positions — so nothing needs caching, and a cached decode must produce the
  same tokens as an uncached one. `tests/test_mole_model.py` asserts that equivalence rather
  than assuming it.

* **Gradient checkpointing.** HF wraps `decoder_layer.__call__`, and pre-hooks run inside
  `Module._call_impl`, so the gate is inside the checkpointed region and is recomputed on the
  backward pass. That requires `use_reentrant=False`; reentrant checkpointing mishandles
  tensors created inside a hook. `build_mole_model` sets it and says so rather than leaving it
  to the caller.

* **Argument form.** transformers may pass `hidden_states` positionally or by keyword
  depending on version and call site, so the hook accepts both. Reading the wrong one would
  route on `position_ids`.

Rejected alternatives, recorded per CLAUDE.md §5:
  - gate inside each `MoLELinear` from its own input — `down_proj` would route on the 8960-d
    SwiGLU activation and `q_proj` on the 1536-d residual: different quantities, no shared
    meaning;
  - attach the gate to `q_proj` and rely on intra-layer call order — works for Qwen2 and is
    silently architecture-dependent;
  - wrap the decoder layer in a new `nn.Module` — breaks HF internals that reach for
    `layer.self_attn`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional

import torch
from torch import nn

from obtune.mole.experts import ExpertBank, bank_summary, load_bank
from obtune.mole.gate import ConstantGate, GateConfig, RouterGate
from obtune.mole.mixture import RoutingCtx, attach_mixture, freeze_all_but


@dataclass
class MoLEModel:
    """A model with the mixture attached, plus everything needed to drive and inspect it."""

    model: nn.Module
    gate: nn.Module
    contexts: dict[int, RoutingCtx]
    handles: list[Any] = field(default_factory=list)
    attached: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    #: When True the hooks clear routing instead of filling it, so the model is the BARE
    #: base. `clear_routing()` alone is NOT enough: the pre-hooks refill every context on
    #: the next forward, so a caller evaluating a `base` row would silently be evaluating
    #: whatever gate happened to be installed — and every delta would be measured against
    #: a mixture rather than against base.
    bypass: bool = False
    #: Filled only while capturing; see `capture_routing`.
    _captured: dict[int, Any] = field(default_factory=dict)  # int -> gate.RoutingStats
    _capturing: bool = False

    def trainable_parameters(self) -> list[nn.Parameter]:
        return [p for p in self.gate.parameters() if p.requires_grad]

    def clear_routing(self) -> None:
        for ctx in self.contexts.values():
            ctx.clear()

    def capture_routing(self, on: bool = True) -> None:
        """Record per-layer routing on the next forward, for `gate_report.json`."""
        self._capturing = on
        if on:
            self._captured.clear()

    def captured(self) -> dict[int, Any]:
        return dict(self._captured)

    def remove(self) -> None:
        for h in self.handles:
            h.remove()
        self.handles.clear()


def _decoder_layers(model: nn.Module) -> list[nn.Module]:
    """The decoder layer list, across the shapes HF actually uses."""
    for path in ("model.layers", "model.model.layers", "transformer.h", "model.decoder.layers"):
        obj: Any = model
        try:
            for part in path.split("."):
                obj = getattr(obj, part)
        except AttributeError:
            continue
        if isinstance(obj, (nn.ModuleList, list)) and len(obj):
            return list(obj)
    raise ValueError("could not locate the decoder layer list on this model")


def attach_gate(
    model: nn.Module,
    gate: nn.Module,
    banks: Mapping[str, ExpertBank],
    *,
    strict: bool = True,
    freeze_base: bool = True,
) -> MoLEModel:
    """Attach the mixture to `model` and drive it from `gate`.

    `freeze_base` defaults to TRUE, and that default is a safety property rather than a
    convenience. The gate is 2.77 M parameters against a 295 M expert bank and a 1.5 B base;
    a caller who attaches and then trains without freezing gets a silent full fine-tune that
    still produces plausible losses and would be attributed to "the mixture". Opting out has
    to be deliberate.
    """
    layers = _decoder_layers(model)
    contexts: dict[int, RoutingCtx] = {i: RoutingCtx() for i in range(len(layers))}

    # Route each bank key to the RoutingCtx of the layer it belongs to, so one gate call per
    # layer serves every projection in it.
    per_layer_banks: dict[int, dict[str, ExpertBank]] = {i: {} for i in range(len(layers))}
    unassigned: list[str] = []
    for key, bank in banks.items():
        idx = _layer_index(key)
        if idx is None or idx not in per_layer_banks:
            unassigned.append(key)
            continue
        per_layer_banks[idx][key] = bank
    if unassigned and strict:
        raise ValueError(
            f"{len(unassigned)} expert module(s) carry no resolvable layer index "
            f"(e.g. {unassigned[:3]}); they would never receive routing weights.")

    attached: list[str] = []
    for i, sub in per_layer_banks.items():
        if sub:
            attached += attach_mixture(model, sub, contexts[i], strict=strict)

    holder = MoLEModel(model=model, gate=gate, contexts=contexts,
                       attached=attached, summary=dict(bank_summary(banks)))

    for i, layer in enumerate(layers):
        layer.register_forward_pre_hook(_make_hook(holder, i), with_kwargs=True)
        holder.handles.append(layer._forward_pre_hooks)  # kept for symmetry; see remove()

    if freeze_base:
        n_train, n_frozen = freeze_all_but(model, [])
        for p in gate.parameters():
            p.requires_grad_(True)
        holder.summary["frozen_params"] = n_frozen

    holder.summary["n_layers"] = len(layers)
    holder.summary["n_attached"] = len(attached)
    holder.summary["gate_params"] = sum(p.numel() for p in gate.parameters())
    return holder


def gate_device(model: nn.Module) -> torch.device:
    """Where the gate must live: the device of the FIRST decoder layer.

    Under `device_map="auto"` a model's parameters can be spread across devices, and
    `next(model.parameters())` returns whichever happened to be registered first — often the
    embedding, not the layer whose hook calls the gate. Getting this wrong produces
    `Expected all tensors to be on the same device` on the first forward, which is how the
    expert buffers failed on 2026-08-13. Both `build_mole_model` and `eval_mole._load_gate`
    resolve it here so they cannot disagree.
    """
    layers = _decoder_layers(model)
    src = layers[0] if layers else model
    try:
        return next(src.parameters()).device
    except StopIteration:
        return next(model.parameters()).device


def _layer_index(module_key: str) -> Optional[int]:
    for part in module_key.split("."):
        if part.isdigit():
            return int(part)
    return None


def _make_hook(holder: MoLEModel, layer: int) -> Callable:
    def hook(module: nn.Module, args: tuple, kwargs: dict):
        if holder.bypass:
            holder.contexts[layer].clear()
            return None
        # transformers passes hidden_states positionally or by keyword depending on version
        # and call site; reading the wrong one would route on position_ids.
        hidden = kwargs.get("hidden_states")
        if hidden is None and args:
            hidden = args[0]
        if not isinstance(hidden, torch.Tensor) or hidden.dim() != 3:
            holder.contexts[layer].clear()
            return None
        w = holder.gate(hidden, layer)
        # The gate is ONE module serving every layer, but `device_map="auto"` can shard the
        # model across cards — so a layer's hidden state may live on cuda:1 while the gate
        # sits on cuda:0, and the mixture then dies with "found at least two devices". A
        # worker-run job never sees this (it pins CUDA_VISIBLE_DEVICES to one card and the
        # model cannot shard); the pipeline's un-pinned dry run did. Move the weights to the
        # hidden state's device so routing is correct under any placement.
        if w.device != hidden.device:
            w = w.to(hidden.device)
        holder.contexts[layer].weights = w
        if holder._capturing:
            # ACCUMULATE, do not overwrite. This used to assign, so `gate_report.json`
            # described only the LAST batch of a cell — the limitation that bounded the
            # routing analysis in MASTER_REPORT §12.8. `RoutingStats` keeps sufficient
            # statistics (summed mass, summed per-token entropy, token count), so the
            # report now covers every item in the cell at O(n_experts) memory per layer
            # instead of O(tokens).
            from obtune.mole.gate import RoutingStats

            wd = w.detach().float().cpu()
            st = holder._captured.get(layer)
            if st is None:
                st = RoutingStats(mass_sum=torch.zeros(wd.shape[-1]))
                holder._captured[layer] = st
            st.update(wd)
        return None

    return hook


def build_mole_model(
    model_key: str,
    expert_paths: Mapping[str, str],
    *,
    gate: Optional[nn.Module] = None,
    d_router: int = 64,
    shared_query: bool = False,
    dtype: str = "bfloat16",
    device_map: Optional[str] = None,
    gradient_checkpointing: bool = False,
) -> MoLEModel:
    """Load the base model, attach the expert bank, and freeze everything but the gate."""
    from transformers import AutoModelForCausalLM

    from obtune.config import load_config

    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)[model_key]["hf_id"]
    torch_dtype = getattr(torch, dtype)

    base = AutoModelForCausalLM.from_pretrained(hf_id, dtype=torch_dtype, device_map=device_map)
    banks = load_bank(expert_paths, dtype=torch_dtype)

    if gate is None:
        any_bank = next(iter(banks.values()))
        cfg = GateConfig(
            n_experts=any_bank.n_experts,
            hidden_size=int(base.config.hidden_size),
            n_layers=len(_decoder_layers(base)),
            d_router=d_router,
            shared_query=shared_query,
        )
        gate = RouterGate(cfg)
    gate = gate.to(device=gate_device(base))

    # attach_gate freezes the base and re-enables the gate; the gate is the ONLY trainable
    # component, established by explicit allow-list rather than a name pattern (a pattern that
    # missed would silently train the 295 M-parameter bank).
    holder = attach_gate(base, gate, banks)
    holder.summary.update({"model": model_key, "dtype": dtype})

    if gradient_checkpointing:
        # use_reentrant=False is REQUIRED: the gate's weights are created inside a
        # forward_pre_hook, and reentrant checkpointing mishandles tensors made in hooks.
        base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        base.enable_input_require_grads()

    return holder


__all__ = ["MoLEModel", "attach_gate", "build_mole_model"]
