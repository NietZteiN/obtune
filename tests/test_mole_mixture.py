"""The activation-space mixture must be exact, or nothing built on it is interpretable.

`MoLELinear` claims to compute `h = W x + sum_e a_e (alpha/r) B_e A_e x` without merging. If
that claim is wrong the failure is silent: the arm still produces plausible accuracies, just
not of the system it says it is. Every test here pins one clause of the claim.

The load-bearing one is `test_one_hot_reproduces_a_single_expert`. Routing all mass to expert
*i* must give exactly what running expert *i* alone gives — that is what certifies "exact by
construction, no merging", and it is the reason this mixture is preferred over
`add_weighted_adapter`, whose `linear` family was measured at 7.175x the exact mixture's
magnitude because it puts sqrt(|w*s|) on A and B separately.
"""
from __future__ import annotations

import pytest
import torch
from torch import nn

from obtune.mole.experts import ExpertBank
from obtune.mole.mixture import (
    MoLELinear, RoutingCtx, attach_mixture, freeze_all_but, one_hot_weights, uniform_weights,
)

D_IN, D_OUT, E, R, SCALE = 16, 12, 4, 3, 2.0


@pytest.fixture()
def parts():
    torch.manual_seed(17)
    base = nn.Linear(D_IN, D_OUT, bias=False)
    A = [torch.randn(R, D_IN) for _ in range(E)]
    B = [torch.randn(D_OUT, R) for _ in range(E)]
    bank = ExpertBank(names=tuple(f"e{i}" for i in range(E)), rank=R,
                      A_cat=torch.cat(A, 0), B_cat=torch.cat([b * SCALE for b in B], 1))
    ctx = RoutingCtx()
    return base, A, B, MoLELinear(base, bank, ctx), ctx, torch.randn(2, 5, D_IN)


def _delta(x, A_i, B_i):
    return (x @ A_i.T) @ (B_i * SCALE).T


def test_no_routing_is_bit_identical_to_the_base_layer(parts) -> None:
    """An unrouted forward must be the BASE model, not an implicit uniform mixture."""
    base, _, _, m, ctx, x = parts
    ctx.weights = None
    assert torch.equal(m(x), base(x))


@pytest.mark.parametrize("i", range(E))
def test_one_hot_reproduces_a_single_expert(parts, i: int) -> None:
    """THE load-bearing test. If this fails, every downstream number is wrong."""
    base, A, B, m, ctx, x = parts
    ctx.weights = one_hot_weights(i, E, (2, 5))
    assert torch.allclose(m(x), base(x) + _delta(x, A[i], B[i]), atol=1e-4)


def test_uniform_is_the_mean_of_the_single_expert_deltas(parts) -> None:
    """`mole_uniform` is the primary fixed-mixture contrast, so its semantics are pinned."""
    base, A, B, m, ctx, x = parts
    ctx.weights = uniform_weights(E, (2, 5))
    want = base(x) + sum(_delta(x, A[i], B[i]) for i in range(E)) / E
    assert torch.allclose(m(x), want, atol=1e-4)


def test_zero_weights_collapse_to_base(parts) -> None:
    """Distinct from `weights=None`: an all-zero gate must also add nothing."""
    base, _, _, m, ctx, x = parts
    ctx.weights = torch.zeros(2, 5, E)
    assert torch.allclose(m(x), base(x), atol=1e-6)


def test_routing_is_per_token_not_per_batch(parts) -> None:
    """The whole point. Two tokens with different routing must get different deltas."""
    base, A, B, m, ctx, x = parts
    w = torch.zeros(2, 5, E)
    w[:, 0, 0] = 1.0   # first token -> expert 0
    w[:, 1, 1] = 1.0   # second token -> expert 1
    ctx.weights = w
    out = m(x)
    assert torch.allclose(out[:, 0], base(x)[:, 0] + _delta(x, A[0], B[0])[:, 0], atol=1e-4)
    assert torch.allclose(out[:, 1], base(x)[:, 1] + _delta(x, A[1], B[1])[:, 1], atol=1e-4)
    assert torch.allclose(out[:, 2], base(x)[:, 2], atol=1e-6)  # unrouted token


def test_expert_permutation_invariance(parts) -> None:
    """Permuting experts AND their gate column must not change the output.

    Catches an `[E, r]` vs `[r, E]` reshape error, which would otherwise scramble which
    expert each weight addresses while still producing well-formed numbers.
    """
    base, A, B, _, _, x = parts
    perm = [2, 0, 3, 1]
    bank_p = ExpertBank(names=tuple(f"e{i}" for i in perm), rank=R,
                        A_cat=torch.cat([A[i] for i in perm], 0),
                        B_cat=torch.cat([B[i] * SCALE for i in perm], 1))
    ctx_p = RoutingCtx()
    m_p = MoLELinear(base, bank_p, ctx_p)
    for want_expert in range(E):
        ctx_p.weights = one_hot_weights(perm.index(want_expert), E, (2, 5))
        assert torch.allclose(m_p(x), base(x) + _delta(x, A[want_expert], B[want_expert]),
                              atol=1e-4)


def test_mismatched_weight_shape_raises(parts) -> None:
    """Silently broadcasting one token's routing onto another would be undetectable."""
    *_, m, ctx, x = parts
    ctx.weights = torch.full((2, 1, E), 1.0 / E)   # [B,1,E] against [B,5,...]
    with pytest.raises(ValueError, match="do not match activation"):
        m(x)


def test_experts_are_buffers_not_parameters(parts) -> None:
    """Registered as Parameters they would enter the optimizer and a gate-only run would
    silently become a full fine-tune of the bank."""
    *_, m, _, _ = parts
    names = {n for n, _ in m.named_parameters()}
    assert not any("A_cat" in n or "B_cat" in n for n in names)
    assert "A_cat" in dict(m.named_buffers()) and "B_cat" in dict(m.named_buffers())


def test_gradient_reaches_the_gate_and_not_the_bank(parts) -> None:
    base, _, _, m, ctx, x = parts
    gate = nn.Parameter(torch.zeros(2, 5, E))
    n_t, n_f = freeze_all_but(m, [gate])
    ctx.weights = torch.softmax(gate, dim=-1)
    m(x).sum().backward()
    assert gate.grad is not None and gate.grad.abs().sum() > 0
    assert all(p.grad is None for p in m.parameters())
    assert n_t == 0 and n_f > 0  # gate is external here; the bank+base are all frozen


def test_attach_refuses_a_partial_mixture() -> None:
    """A mixture attached to most modules reads as a weak arm, not a broken one."""
    model = nn.Module()
    model.good = nn.Linear(D_IN, D_OUT, bias=False)
    bank = ExpertBank(names=("a", "b"), rank=R,
                      A_cat=torch.randn(2 * R, D_IN), B_cat=torch.randn(D_OUT, 2 * R))
    with pytest.raises(ValueError, match="did not resolve"):
        attach_mixture(model, {"good": bank, "absent": bank}, RoutingCtx(), strict=True)
    replaced = attach_mixture(model, {"good": bank, "absent": bank}, RoutingCtx(), strict=False)
    assert replaced == ["good"] and isinstance(model.good, MoLELinear)
