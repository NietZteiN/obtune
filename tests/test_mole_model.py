"""The gate, and the hook path that drives it, on a real Qwen2 architecture.

`tests/test_mole_mixture.py` proves the arithmetic in isolation. This file proves the parts
that only exist once the mixture is inside a transformer: that the hook reads the right tensor,
that routing survives a KV-cached decode, and that a training step moves the gate and nothing
else.

A tiny randomly-initialised Qwen2 (2 layers, hidden 64) is used rather than a checkpoint — the
questions here are structural, so they need the real module layout and none of the weights.
"""
from __future__ import annotations

import pytest
import torch
from torch import nn

from obtune.mole.experts import ExpertBank
from obtune.mole.gate import (
    GateConfig, RouterGate, gate_entropy, one_hot_gate, summarise_routing, uniform_gate,
)
from obtune.mole.model import _decoder_layers, _layer_index, attach_gate

E, R, HID = 3, 4, 64


@pytest.fixture()
def model():
    from transformers import AutoConfig, AutoModelForCausalLM

    torch.manual_seed(17)
    cfg = AutoConfig.for_model(
        "qwen2", hidden_size=HID, intermediate_size=128, num_hidden_layers=2,
        num_attention_heads=4, num_key_value_heads=2, vocab_size=128,
        max_position_embeddings=64)
    return AutoModelForCausalLM.from_config(cfg)


@pytest.fixture()
def banks(model):
    n = len(_decoder_layers(model))
    torch.manual_seed(3)
    out = {}
    for li in range(n):
        for proj, d_in, d_out in (("self_attn.q_proj", HID, HID), ("mlp.down_proj", 128, HID)):
            out[f"model.layers.{li}.{proj}"] = ExpertBank(
                names=tuple(f"e{i}" for i in range(E)), rank=R,
                A_cat=torch.randn(E * R, d_in) * 0.05,
                B_cat=torch.randn(d_out, E * R) * 0.05)
    return out


def test_layer_index_extraction() -> None:
    assert _layer_index("model.layers.7.self_attn.q_proj") == 7
    assert _layer_index("base_model.model.model.layers.13.mlp.down_proj") == 13
    assert _layer_index("model.embed_tokens") is None


def test_attach_refuses_banks_with_no_layer_index(model) -> None:
    """A module with no resolvable layer would never receive routing weights — it would sit
    inert inside a system labelled as routed."""
    bank = ExpertBank(names=("a", "b"), rank=R,
                      A_cat=torch.randn(2 * R, HID), B_cat=torch.randn(HID, 2 * R))
    with pytest.raises(ValueError, match="no resolvable layer index"):
        attach_gate(model, uniform_gate(2), {"model.embed_tokens": bank})


def test_mixture_changes_the_output(model, banks) -> None:
    ids = torch.randint(0, 128, (2, 7))
    before = model(ids).logits.clone()
    attach_gate(model, uniform_gate(E), banks)
    assert not torch.allclose(before, model(ids).logits, atol=1e-5)


def test_each_expert_gives_a_distinct_model(model, banks) -> None:
    """If one-hot routing produced identical outputs the gate would be inert."""
    ids = torch.randint(0, 128, (2, 7))
    holder = attach_gate(model, uniform_gate(E), banks)
    outs = []
    for i in range(E):
        holder.gate = one_hot_gate(i, E)
        outs.append(model(ids).logits.clone())
    for i in range(E):
        for j in range(i + 1, E):
            assert (outs[i] - outs[j]).abs().max() > 1e-4, f"experts {i},{j} indistinguishable"


def test_kv_cache_decode_matches_uncached(model, banks) -> None:
    """THE decode hazard. At generation T==1 and the hook fires per step; the gate is a pure
    function of the current hidden state, so cached and uncached must agree exactly."""
    model.eval()
    attach_gate(model, RouterGate(GateConfig(E, HID, len(_decoder_layers(model)), d_router=8)),
                banks)
    ids = torch.randint(0, 128, (2, 6))
    with torch.no_grad():
        cached = model.generate(ids, max_new_tokens=8, do_sample=False, use_cache=True)
        uncached = model.generate(ids, max_new_tokens=8, do_sample=False, use_cache=False)
    assert torch.equal(cached, uncached)


def test_attach_freezes_the_base_by_default(model, banks) -> None:
    """Without this a caller who attaches and trains gets a silent FULL fine-tune that still
    produces plausible losses and would be attributed to the mixture."""
    gate = RouterGate(GateConfig(E, HID, len(_decoder_layers(model)), d_router=8))
    attach_gate(model, gate, banks)
    assert [n for n, p in model.named_parameters() if p.requires_grad] == []
    assert all(p.requires_grad for p in gate.parameters())


def test_training_step_moves_the_gate_and_only_the_gate(model, banks) -> None:
    gate = RouterGate(GateConfig(E, HID, len(_decoder_layers(model)), d_router=8))
    attach_gate(model, gate, banks)
    ids = torch.randint(0, 128, (2, 6))
    model(ids, labels=ids).loss.backward()
    assert all(p.grad is not None and p.grad.abs().sum() > 0 for p in gate.parameters())
    assert all(p.grad is None for _, p in model.named_parameters())


def test_routing_capture_accumulates_and_normalises(model, banks) -> None:
    """Capture keeps whole-cell sufficient statistics, not the last batch's tensor.

    It used to overwrite `_captured[layer]` on every forward, so `gate_report.json`
    described only the final batch — the limitation that bounded the routing analysis in
    MASTER_REPORT §12.8. Two forwards must therefore accumulate rather than replace, and the
    mean routing weights must still be a distribution.
    """
    n = len(_decoder_layers(model))
    holder = attach_gate(model, RouterGate(GateConfig(E, HID, n, d_router=8)), banks)
    holder.capture_routing(True)
    model(torch.randint(0, 128, (2, 7)))
    after_one = {k: v.n_tokens for k, v in holder.captured().items()}
    model(torch.randint(0, 128, (3, 5)))
    cap = holder.captured()

    assert sorted(cap) == list(range(n))
    for layer, st in cap.items():
        assert after_one[layer] == 2 * 7, "first forward should contribute B*T tokens"
        assert st.n_tokens == 2 * 7 + 3 * 5, "second forward must ACCUMULATE, not overwrite"
        assert st.mass_sum.shape == (E,)
        mean = st.mass_sum / st.n_tokens
        assert torch.allclose(mean.sum(), torch.tensor(1.0), atol=1e-5)

    # And the summary built from those statistics is a valid distribution per layer.
    rep = summarise_routing(cap, E)
    assert rep["n_tokens_total"] == n * (2 * 7 + 3 * 5)
    for lay in rep["layers"].values():
        assert abs(sum(lay["expert_mass"]) - 1.0) < 1e-5
        assert 0.0 <= lay["entropy_norm"] <= 1.0 + 1e-6


def test_clear_routing_restores_the_base_model(model, banks) -> None:
    """`weights=None` must mean the BASE model, not an implicit uniform mixture."""
    ids = torch.randint(0, 128, (2, 7))
    before = model(ids).logits.clone()
    holder = attach_gate(model, uniform_gate(E), banks)
    # Remove the hooks so nothing refills the contexts, then clear.
    for layer in _decoder_layers(model):
        layer._forward_pre_hooks.clear()
    holder.clear_routing()
    assert torch.allclose(before, model(ids).logits, atol=1e-6)


# --------------------------------------------------------------------------- #
# gate diagnostics — the collapse question is a finding, so it must be measurable


def test_entropy_bounds() -> None:
    uni = torch.full((2, 3, 8), 1.0 / 8)
    assert torch.allclose(gate_entropy(uni), torch.full((2, 3), torch.tensor(8.0).log()), atol=1e-5)
    hot = torch.zeros(2, 3, 8)
    hot[..., 0] = 1.0
    assert torch.allclose(gate_entropy(hot), torch.zeros(2, 3), atol=1e-5)


def test_summarise_flags_collapse() -> None:
    """A mixture that is secretly a hard router is a finding, not a bug — so it is detected."""
    n_layers, E8 = 6, 8
    hot = torch.zeros(2, 4, E8)
    hot[..., 1] = 1.0
    assert summarise_routing({i: hot for i in range(n_layers)}, E8)["collapsed"] is True
    uni = torch.full((2, 4, E8), 1.0 / E8)
    assert summarise_routing({i: uni for i in range(n_layers)}, E8)["collapsed"] is False


def test_shared_query_ablation_has_far_fewer_params() -> None:
    n_layers = 28
    per = RouterGate(GateConfig(8, 1536, n_layers, d_router=64, shared_query=False))
    shared = RouterGate(GateConfig(8, 1536, n_layers, d_router=64, shared_query=True))
    n_per = sum(p.numel() for p in per.parameters())
    n_shared = sum(p.numel() for p in shared.parameters())
    assert n_shared < n_per / 10, f"shared-query ablation is not cheaper: {n_shared} vs {n_per}"
    # The number quoted in the design docs, so a change is visible rather than silent.
    assert 2.7e6 < n_per < 2.9e6, f"per-layer gate is {n_per} params, docs claim ~2.77 M"


def test_bypass_makes_the_model_bare_base(model, banks) -> None:
    """The `base` row must be BASE. `clear_routing()` alone does not achieve that — the
    pre-hooks refill every context on the next forward, so a base cell evaluated through
    this engine would silently be a mixture and every delta would be measured against the
    wrong reference."""
    ids = torch.randint(0, 128, (2, 7))
    before = model(ids).logits.clone()
    holder = attach_gate(model, uniform_gate(E), banks)
    mixed = model(ids).logits.clone()
    assert not torch.allclose(before, mixed, atol=1e-5), "mixture is inert; test proves nothing"

    holder.clear_routing()
    assert not torch.allclose(before, model(ids).logits, atol=1e-6), (
        "clear_routing() alone appears to survive a forward — the hook no longer refills")

    holder.bypass = True
    assert torch.allclose(before, model(ids).logits, atol=1e-6)
    holder.bypass = False
    assert torch.allclose(mixed, model(ids).logits, atol=1e-6), "bypass must be reversible"


# --------------------------------------------------------------------------- #
# Routing regularisation (MASTER_REPORT §12.8/§12.9). The v1 gate was trained on the task
# loss alone and collapsed to an input-independent blend with three of eight experts dead.
# These assert the balancing term actually distinguishes those cases — a term that returned
# a constant would train for GPU-hours and change nothing.

class _Ctx:
    def __init__(self, w):
        self.weights = w


def test_load_balance_term_is_minimal_at_uniform_and_maximal_at_collapse() -> None:
    from obtune.mole.train_mole import load_balance_term

    n_tok, E8 = 64, 8
    uniform = torch.full((1, n_tok, E8), 1.0 / E8)
    collapsed = torch.zeros(1, n_tok, E8)
    collapsed[..., 3] = 1.0

    lb_uniform = float(load_balance_term({0: _Ctx(uniform)}))
    lb_collapsed = float(load_balance_term({0: _Ctx(collapsed)}))

    # Switch-style E*sum(f_i*P_i): 1.0 at a perfectly balanced assignment, E when all tokens
    # land on one expert. The ORDERING is what the loss relies on.
    assert lb_collapsed > lb_uniform, "balancing term must punish collapse"
    assert abs(lb_uniform - 1.0) < 1e-4
    assert abs(lb_collapsed - E8) < 1e-4


def test_load_balance_term_gradient_reaches_the_gate_probabilities() -> None:
    """`f` is detached by design; the signal must still flow through `P`."""
    from obtune.mole.train_mole import load_balance_term

    logits = torch.zeros(1, 16, 8, requires_grad=True)
    w = torch.softmax(logits, dim=-1)
    load_balance_term({0: _Ctx(w)}).backward()
    assert logits.grad is not None and logits.grad.abs().sum() > 0


def test_load_balance_term_ignores_layers_with_no_routing() -> None:
    """Bypassed layers carry `weights=None`; they must not contribute or divide by zero."""
    from obtune.mole.train_mole import load_balance_term

    w = torch.full((1, 8, 8), 1.0 / 8)
    only = float(load_balance_term({0: _Ctx(w)}))
    with_empty = float(load_balance_term({0: _Ctx(w), 1: _Ctx(None)}))
    assert abs(only - with_empty) < 1e-6
    assert float(load_balance_term({0: _Ctx(None)})) == 0.0
