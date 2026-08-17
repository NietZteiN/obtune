"""The RouterLoRA gate — attention over experts, computed per token and per layer.

    q   = W_q^l · LayerNorm(h)          [B, T, d_r]
    s_e = (q · k_e^l) / (sqrt(d_r) · tau_l)
    a   = softmax_e(s)                  [B, T, E]

`h` is the decoder layer's INPUT hidden state, so one gate serves every target projection in
that layer. The alternative — computing the gate inside each `MoLELinear` from its own input —
would have `down_proj` routing on the 8960-d SwiGLU activation while `q_proj` routes on the
1536-d residual, i.e. a different quantity per module with no shared meaning.

WHY A LEARNED KEY PER EXPERT rather than deriving it from the expert's own `A` factor: a free
key has exactly the capacity a derived one would, and keeps the gate's parameters independent
of the bank, so swapping an expert does not silently redefine the routing geometry.

TAU IS A REPORTED RESULT, NOT A KNOB. Large `tau` means the gate learned to be one-hot — a
mixture that is secretly a hard router — and small `tau` means genuine blending. Given the
existing router is saturated on single conditions (100 % route accuracy, entropy ~1e-6), gate
collapse is the most likely outcome, and it is a finding rather than a bug. `gate_report`
exists so that outcome is measured instead of inferred.

PARAMETER COUNT at 1.5B (28 layers, hidden 1536, d_r 64, E 8): 28 x (1536x64 + 8x64 + 1) =
2.77 M, which is 0.94 % of the 8-expert bank and 7.5 % of ONE expert. Worth stating explicitly,
because `router/features.py` argues the RQ2 router must be a frozen-feature MLP so parameter
budgets stay comparable to one monolithic adapter — this gate trains THROUGH the frozen base
and so breaks that argument. Still defensible at 2.77 M against 295 M of experts, but the
design doc should say it rather than let a reviewer find it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import torch
from torch import nn


@dataclass
class GateConfig:
    n_experts: int
    hidden_size: int
    n_layers: int
    d_router: int = 64
    #: Per-layer queries by default. `shared_query` is the ablation that asks whether the
    #: routing decision is layer-specific at all; it costs 28x fewer query parameters.
    shared_query: bool = False
    #: Learned per layer, initialised at 1.0. Reported, never tuned.
    learn_temperature: bool = True
    init_temperature: float = 1.0


class RouterGate(nn.Module):
    """Attention over experts. The ONLY trainable component of the mixture."""

    def __init__(self, cfg: GateConfig) -> None:
        super().__init__()
        self.cfg = cfg
        n_q = 1 if cfg.shared_query else cfg.n_layers
        # affine=False: the gate must not be able to rescale the residual stream it reads,
        # only to compare directions within it.
        self.norm = nn.LayerNorm(cfg.hidden_size, elementwise_affine=False)
        self.q_proj = nn.ModuleList(
            [nn.Linear(cfg.hidden_size, cfg.d_router, bias=False) for _ in range(n_q)]
        )
        self.keys = nn.Parameter(torch.empty(cfg.n_layers, cfg.n_experts, cfg.d_router))
        nn.init.normal_(self.keys, std=cfg.d_router ** -0.5)
        if cfg.learn_temperature:
            self.log_tau = nn.Parameter(
                torch.full((cfg.n_layers,), math.log(cfg.init_temperature)))
        else:
            self.register_buffer(
                "log_tau", torch.full((cfg.n_layers,), math.log(cfg.init_temperature)))

    def temperature(self) -> torch.Tensor:
        return self.log_tau.exp()

    def forward(self, hidden: torch.Tensor, layer: int) -> torch.Tensor:
        """Routing weights `[B, T, E]` for one layer's input hidden state.

        DTYPE. The base model runs in bf16 while the gate is kept in fp32, and mixing them
        is a hard error: `expected mat1 and mat2 to have the same dtype, but got
        c10::BFloat16 != float`. That is exactly how the first real training run died on
        2026-08-12, after `--dry-run` had passed — the dry run never executed a forward.

        The gate stays fp32 on purpose. It is 2.77 M parameters against a 295 M frozen bank,
        a softmax over a temperature-scaled dot product is precisely where bf16's 8-bit
        mantissa hurts, and casting the *weights* down would make routing decisions noisy for
        no memory saving worth having. So the input is promoted for the computation and the
        result is cast back to the hidden state's dtype, which is what `MoLELinear` then
        multiplies against. This makes the gate work under any autocast or model dtype
        without the caller having to match it.
        """
        # Match the gate's own weights on BOTH axes. dtype because the base runs bf16 while
        # the gate is fp32; device because `device_map="auto"` can shard the model, leaving
        # the gate on one card and a layer's hidden state on another. The result is returned
        # on the input's device and dtype so the caller is unaffected either way.
        w = self.q_proj[0 if self.cfg.shared_query else layer].weight
        h = hidden.to(device=w.device, dtype=w.dtype)
        q = self.q_proj[0 if self.cfg.shared_query else layer](self.norm(h))
        k = self.keys[layer].to(q.dtype)                      # [E, d_r]
        scale = math.sqrt(self.cfg.d_router) * self.log_tau[layer].exp().to(q.dtype)
        out = torch.softmax(q @ k.t() / scale, dim=-1)        # [B, T, E]
        return out.to(device=hidden.device, dtype=hidden.dtype)

    @torch.no_grad()
    def report(self) -> dict[str, list[float]]:
        """Per-layer temperature — the diagnostic that says whether the gate blends at all."""
        return {"temperature": [float(t) for t in self.temperature().detach().cpu()]}


class ConstantGate(nn.Module):
    """A fixed routing vector, for the control arms.

    `mole_uniform` (1/E everywhere) is the PRIMARY fixed-mixture contrast: it differs from the
    learned gate in exactly one respect, the weights, running the identical code path with
    identical numerics. `merge_dare_ties` differs in three respects at once, which is why it is
    the reference rather than the comparator.

    `mole_random` — a RouterGate frozen at init — is the control that decides what the headline
    may claim. If the learned gate does not beat it, the gain came from having E experts
    resident at effective rank E*r, not from routing, and the honest headline says so.
    """

    def __init__(self, weights: torch.Tensor) -> None:
        super().__init__()
        self.register_buffer("w", weights)      # [E]

    def forward(self, hidden: torch.Tensor, layer: int) -> torch.Tensor:
        b, t, _ = hidden.shape
        return self.w.to(hidden.dtype).view(1, 1, -1).expand(b, t, -1)


def uniform_gate(n_experts: int) -> ConstantGate:
    return ConstantGate(torch.full((n_experts,), 1.0 / n_experts))


def one_hot_gate(index: int, n_experts: int) -> ConstantGate:
    w = torch.zeros(n_experts)
    w[index] = 1.0
    return ConstantGate(w)


class HardenedGate(nn.Module):
    """The trained `RouterGate`, argmaxed to one-hot at every token and layer.

    This is the `mole_hardrouter` arm from the Part III ladder, and it isolates ONE thing:
    whether the mixture's gain comes from BLENDING experts or merely from PICKING the right
    one per token/layer. `mole_router` and this differ in exactly that — same weights, same
    module, same forward path; only the softmax is replaced by its argmax.

    It is the arm that decides how the headline may be phrased. If hardening costs nothing,
    "attention-weighted mixture" is an overclaim and the honest description is a fine-grained
    hard router. The existing `mole_hardrouter:<i>` mode is a different control (it pins ONE
    expert for the whole run) and cannot answer this.

    Straight-through is deliberately absent: nothing is trained here, so the argmax needs no
    gradient path, and adding one would only invite someone to fine-tune through it later.
    """

    def __init__(self, router: nn.Module) -> None:
        super().__init__()
        self.router = router

    @torch.no_grad()
    def forward(self, hidden: torch.Tensor, layer: int) -> torch.Tensor:
        w = self.router(hidden, layer)
        hard = torch.zeros_like(w)
        # scatter, not one_hot: keeps device/dtype and works for any trailing expert dim.
        hard.scatter_(-1, w.argmax(dim=-1, keepdim=True), 1.0)
        return hard


@torch.no_grad()
def gate_entropy(weights: torch.Tensor) -> torch.Tensor:
    """Shannon entropy of the routing distribution, in nats, per token.

    Compared against `log E`: at the maximum the gate is uniform, at zero it is one-hot. The
    pre-registered read is the MEAN over the middle third of layers, because the max over 28
    layers is a forking path.
    """
    p = weights.clamp_min(1e-12)
    return -(p * p.log()).sum(dim=-1)


@dataclass
class RoutingStats:
    """Running routing totals for one layer, accumulated across every forward in a cell.

    WHY SUMS AND NOT THE TENSORS
    ----------------------------
    `MoLEModel`'s capture used to OVERWRITE `_captured[layer]` on each forward, so every
    `gate_report.json` described the final batch of a cell rather than all of its items —
    which bounded the 2026-08-14 routing analysis (MASTER_REPORT §12.8) to a sample it never
    declared. Concatenating the tensors instead would be exact but unbounded: 28 layers x
    all tokens x 8 experts for a 1,670-item cell is not a reporting artifact, it is a
    memory leak.

    Sufficient statistics give the exact same answer in O(n_experts) per layer. `mass_sum`
    is summed over tokens, so `mass_sum / n_tokens` is identical to the mean over a
    concatenated tensor; `ent_sum` is summed per-token entropy, so `ent_sum / n_tokens` is
    the mean per-token entropy — NOT the entropy of the mean, which is a different and much
    less informative quantity.
    """

    mass_sum: torch.Tensor          # [E], summed over every token seen
    ent_sum: float = 0.0            # sum of per-token entropy, in nats
    n_tokens: int = 0

    def update(self, w: torch.Tensor) -> "RoutingStats":
        w = w.detach().float()
        flat = w.reshape(-1, w.shape[-1])
        self.mass_sum = self.mass_sum.to(flat.device) + flat.sum(dim=0)
        self.ent_sum += float(gate_entropy(flat).sum())
        self.n_tokens += int(flat.shape[0])
        return self


def summarise_routing(
    per_layer: dict[int, "torch.Tensor | RoutingStats"], n_experts: int
) -> dict[str, object]:
    """Turn captured routing into the numbers `gate_report.json` needs.

    Accepts either accumulated `RoutingStats` (what the capture now produces, covering every
    item in the cell) or a raw weight tensor (a single forward — still used by tests and by
    any caller holding one batch). Both paths compute the same quantities.
    """
    max_ent = math.log(n_experts)
    out: dict[str, object] = {"n_experts": n_experts, "max_entropy": max_ent, "layers": {}}
    ents: list[float] = []
    n_tok_total = 0
    for layer, cap in sorted(per_layer.items()):
        if isinstance(cap, RoutingStats):
            n = max(cap.n_tokens, 1)
            e = cap.ent_sum / n
            mass = (cap.mass_sum / n).tolist()
            n_tok_total += cap.n_tokens
        else:
            # DETACH. This is a reporting function, and it is called with whatever tensors
            # the capture produced — which during a training-time diagnostic still carry
            # requires_grad. Converting those to Python floats warns, and keeping them alive
            # pins the autograd graph for every layer while the report is built.
            w = cap.detach()
            e = float(gate_entropy(w).mean())
            mass = [float(v) for v in w.mean(dim=tuple(range(w.dim() - 1)))]
        out["layers"][str(layer)] = {
            "entropy_mean": e,
            "entropy_norm": e / max_ent if max_ent else float("nan"),
            "expert_mass": [float(v) for v in mass],
        }
        ents.append(e)
    if n_tok_total:
        # Declared so a reader can tell a whole-cell report from a single-batch one.
        out["n_tokens_total"] = n_tok_total
    if ents:
        lo, hi = len(ents) // 3, 2 * len(ents) // 3
        mid = ents[lo:hi] or ents
        out["entropy_mean_all"] = sum(ents) / len(ents)
        out["entropy_mean_mid_third"] = sum(mid) / len(mid)
        out["collapsed"] = bool(out["entropy_mean_mid_third"] < 0.9 * max_ent)
    return out


__all__ = [
    "GateConfig", "RouterGate", "ConstantGate",
    "uniform_gate", "one_hot_gate", "gate_entropy", "summarise_routing",
]
