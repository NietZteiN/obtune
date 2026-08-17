"""Activation-space mixture over LoRA experts — exact by construction, per token.

    h = W_base x  +  sum_e  a_e(x) * (alpha/r) * B_e A_e x

`MoLELinear` replaces one target `nn.Linear` and evaluates that sum in two dense matmuls:

    y = base(x)                                   # [*, d_out]
    z = F.linear(x, A_cat)                        # [*, E*r]   one GEMM
    z = (z.view(*, E, r) * w[..., None]).view(*, E*r)
    return y + F.linear(z, B_cat)                 # [*, d_out] one GEMM

The `[*, E, d_out]` intermediate is never formed: `a_e` is a scalar per (token, expert), so it
commutes into the rank space between the two matmuls. Peak extra activation is `[B, T, E*r]`
floats — about 4 MB at batch 8 x seq 2048 with E=8, r=32.

WHY THIS RATHER THAN MERGING
----------------------------
A merged adapter fixes ONE weight vector for the whole batch. Merging per input rebuilds ~196
tensor pairs per item ("seconds per item", the reason the old `moe_soft_generate` was
unusable), and PEFT's `linear` family is not even the mixture it claims to be — measured
2026-08-11, `dare_linear` lands at 7.175x the exact mixture's magnitude because sqrt(|w*s|)
goes on A and B separately, so the reconstruction carries cross terms `B_i A_j`. Mixing in
activation space has no cross terms, no rank growth, no rebuild, and permits real batching.

ROUTING WEIGHTS ARE SUPPLIED, NOT COMPUTED HERE
-----------------------------------------------
`MoLELinear` reads its weights from a shared `RoutingCtx` that something upstream fills — a
per-layer gate, a constant (`mole_uniform`), or a one-hot (`mole_hardrouter`, and the
exactness test). Keeping the gate out of this module is what lets the SAME code path serve the
experiment and all of its controls, so a difference between arms cannot come from a difference
in the mixing code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Optional

import torch
import torch.nn.functional as F
from torch import nn

from obtune.mole.experts import ExpertBank


@dataclass
class RoutingCtx:
    """Per-forward routing weights, shared by every `MoLELinear` in one layer.

    `weights` is `[*, E]` broadcastable against the module input's leading dims — `[B, T, E]`
    for a prefill, `[B, 1, E]` during cached decode. `None` means "no mixture this step", and
    the modules fall through to the base layer, which is what makes an unrouted forward exactly
    the base model rather than an implicit uniform mixture.
    """

    weights: Optional[torch.Tensor] = None
    #: Set by a gate that wants its weights recorded; diagnostics only, never read by forward.
    trace: dict = field(default_factory=dict)

    def clear(self) -> None:
        self.weights = None


class MoLELinear(nn.Module):
    """One target projection, with E resident experts mixed per token."""

    def __init__(self, base: nn.Linear, bank: ExpertBank, ctx: RoutingCtx) -> None:
        super().__init__()
        self.base = base
        self.ctx = ctx
        self.n_experts = bank.n_experts
        self.rank = bank.rank
        self.expert_names = bank.names
        # Buffers, not Parameters: the experts are FROZEN. Registering them as parameters
        # would put them in the optimizer and in `trainable_parameters()`, and a gate-only
        # training run would silently become a full fine-tune of the bank.
        #
        # PLACED ON THE BASE LAYER'S DEVICE. `load_bank` builds these on CPU, and under
        # `device_map="auto"` the base weights are already on a GPU by the time we attach —
        # accelerate dispatches the modules it placed, not buffers registered afterwards.
        # The result was `Expected all tensors to be on the same device, but got mat2 is on
        # cpu, different from other tensors on cuda:0` on the first real forward. It never
        # showed up in `--dry-run`, which runs `device_map=None` and is therefore CPU-only
        # on both sides. Matching dtype here too keeps the forward free of per-call casts.
        dev = base.weight.device
        dt = base.weight.dtype
        self.register_buffer("A_cat", bank.A_cat.to(device=dev, dtype=dt), persistent=False)
        self.register_buffer("B_cat", bank.B_cat.to(device=dev, dtype=dt), persistent=False)

    def extra_repr(self) -> str:
        return f"experts={self.n_experts}, rank={self.rank}"

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.base(x)
        w = self.ctx.weights
        if w is None:
            return y

        # Match x on BOTH device and dtype, here at the point of use. Doing it in the hook
        # (against the decoder layer's input) is not enough: under `device_map="auto"`
        # accelerate moves tensors to each module's device immediately before it runs, so the
        # layer's input device and the projection's device can differ. That produced
        # "found at least two devices, cuda:1 and cuda:0" on an un-pinned multi-GPU dry run.
        # A worker-run job pins CUDA_VISIBLE_DEVICES to one card and never sees it.
        if w.device != x.device:
            w = w.to(x.device)
        a = self.A_cat.to(device=x.device, dtype=x.dtype)
        b = self.B_cat.to(device=x.device, dtype=x.dtype)
        z = F.linear(x, a)                                   # [*, E*r]
        lead = z.shape[:-1]
        z = z.view(*lead, self.n_experts, self.rank)
        # Broadcast the per-expert scalar across its own rank block. `w` may carry fewer
        # leading dims than z (e.g. [B,1,E] against [B,T,E*r] is NOT valid) — callers supply
        # weights matching the current step's token count, and the reshape below fails loudly
        # rather than silently broadcasting the wrong token's routing onto another.
        w = w.to(z.dtype)
        if w.shape[:-1] != tuple(lead):
            raise ValueError(
                f"routing weights {tuple(w.shape)} do not match activation {tuple(lead)}+[E]; "
                f"a mismatch here would apply one token's routing to another")
        z = (z * w.unsqueeze(-1)).reshape(*lead, self.n_experts * self.rank)
        return y + F.linear(z, b)


def one_hot_weights(index: int, n_experts: int, shape: Iterable[int],
                    *, device=None, dtype=torch.float32) -> torch.Tensor:
    """Routing that selects a single expert — the exactness test's instrument."""
    w = torch.zeros(*shape, n_experts, device=device, dtype=dtype)
    w[..., index] = 1.0
    return w


def uniform_weights(n_experts: int, shape: Iterable[int],
                    *, device=None, dtype=torch.float32) -> torch.Tensor:
    """The `mole_uniform` arm: the primary fixed-mixture contrast.

    It differs from the learned gate in EXACTLY ONE way — the weights — where
    `merge_dare_ties` differs in three at once (fixed-vs-learned, weight-space-vs-activation
    space, and DARE-pruned/TIES-elected vs exact). That is why this, not the merge, is the
    comparator the experiment turns on.
    """
    return torch.full((*shape, n_experts), 1.0 / n_experts, device=device, dtype=dtype)


def attach_mixture(
    model: nn.Module,
    banks: Mapping[str, ExpertBank],
    ctx: RoutingCtx,
    *,
    strict: bool = True,
) -> list[str]:
    """Replace every `nn.Linear` named in `banks` with a `MoLELinear`.

    Bank keys are PEFT-style module paths (`base_model.model.model.layers.0.self_attn.q_proj`);
    the leading `base_model.model.` wrapper is stripped so they resolve against a plain HF
    model. Returns the paths actually replaced.

    `strict` refuses when a bank has no matching module: silently attaching to 190 of 196
    modules would produce a mixture that is *mostly* applied, which is far worse than one that
    fails — the arm would look like a weak version of itself rather than a broken one.
    """
    # TWO PASSES: resolve everything first, mutate only once every target is known good.
    # A single pass mutates as it goes, so a strict refusal leaves the model HALF ATTACHED —
    # exactly the partial-mixture state the refusal exists to prevent, and a caller that
    # catches the error and retries would then be operating on a mutated model. Caught by
    # tests/test_mole_mixture.py::test_attach_refuses_a_partial_mixture.
    resolved: list[tuple[str, nn.Module, str, nn.Linear, ExpertBank]] = []
    missing: list[str] = []
    for key, bank in banks.items():
        path = key
        for prefix in ("base_model.model.", "base_model."):
            if path.startswith(prefix):
                path = path[len(prefix):]
                break
        parts = path.split(".")
        parent = model
        try:
            for p in parts[:-1]:
                parent = getattr(parent, p) if not p.isdigit() else parent[int(p)]
            leaf = parts[-1]
            target = getattr(parent, leaf)
        except (AttributeError, IndexError, KeyError):
            missing.append(key)
            continue
        if not isinstance(target, nn.Linear):
            missing.append(key)
            continue
        resolved.append((key, parent, leaf, target, bank))

    if missing and strict:
        raise ValueError(
            f"{len(missing)} of {len(banks)} expert modules did not resolve to an nn.Linear "
            f"(e.g. {missing[:3]}). A partially attached mixture reads as a weak arm rather "
            f"than a broken one, so this refuses instead — before mutating anything.")

    replaced: list[str] = []
    for key, parent, leaf, target, bank in resolved:
        setattr(parent, leaf, MoLELinear(target, bank, ctx))
        replaced.append(key)
    return replaced


def freeze_all_but(model: nn.Module, trainable: Iterable[nn.Parameter]) -> tuple[int, int]:
    """Freeze the whole model, then re-enable exactly `trainable`. Returns (n_train, n_frozen)."""
    keep = {id(p) for p in trainable}
    n_t = n_f = 0
    for p in model.parameters():
        if id(p) in keep:
            p.requires_grad_(True)
            n_t += p.numel()
        else:
            p.requires_grad_(False)
            n_f += p.numel()
    return n_t, n_f


__all__ = [
    "RoutingCtx", "MoLELinear", "attach_mixture",
    "one_hot_weights", "uniform_weights", "freeze_all_but",
]
