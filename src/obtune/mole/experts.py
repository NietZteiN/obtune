"""Load a bank of LoRA experts as stacked factors, ready for activation-space mixing.

The mixture computes, per target module,

    h = W_base x  +  sum_e  a_e(x) * (alpha/r) * B_e A_e x

and the only representation that makes that cheap is a pair of CONCATENATED factors:

    A_cat : [E*r, d_in]      the E experts' A blocks stacked
    B_cat : [d_out, E*r]     the E experts' B blocks stacked, with alpha/r folded in

With those, the forward is two dense matmuls and one broadcast multiply, and the
`[E, d_out]` intermediate is never materialized — the gate weight is a scalar per
(token, expert), so it commutes into the rank space between the two matmuls.

WHY NOT PEFT
------------
`active_adapters` sums the experts with weight 1 each and offers no per-token hook.
`add_weighted_adapter` is either inexact (`linear` puts sqrt(|w*s|) on A and B separately, so
the reconstruction carries cross terms B_i A_j — measured 2026-08-11 at 7.175x the exact
mixture's magnitude) or a full rebuild per weight vector (`cat`). Neither is needed once the
factors are stacked, and neither can vary the weights per token.

The alpha/r folding is exact ONLY for vanilla LoRA, which is why `taskvec._assert_plain_lora`
is reused rather than re-derived: under DoRA the delta decomposes into magnitude and
direction, and under rslora the scaling becomes alpha/sqrt(r), so folding a constant would
silently produce a wrong bank.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import torch

from obtune.taskvec import _assert_no_h1_path, _assert_plain_lora, load_task_vector

#: `base_model.model.model.layers.<L>.<block>.<proj>.lora_A.weight` — key modules by
#: everything before `.lora_`, which is what both PEFT and `merge_geometry` use.
_MODULE_RE = re.compile(r"^(?P<module>.+)\.lora_(?P<which>[AB])\.weight$")


@dataclass
class ExpertBank:
    """Stacked LoRA factors for one module, shared by every expert in the bank.

    `A_cat`/`B_cat` are contiguous so the two `F.linear` calls hit fast kernels. `names` fixes
    the expert order, and that order is the meaning of the gate's output dimension — permuting
    one without the other silently mislabels every routing weight, which is why
    `tests/test_mole_mixture.py` includes a permutation-invariance test.
    """

    names: tuple[str, ...]
    rank: int
    A_cat: torch.Tensor  # [E*r, d_in]
    B_cat: torch.Tensor  # [d_out, E*r], alpha/r folded in

    @property
    def n_experts(self) -> int:
        return len(self.names)

    def expert_slice(self, index: int) -> slice:
        return slice(index * self.rank, (index + 1) * self.rank)


def _factors(adapter_dir: Path, name: str) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor], float]:
    tv = load_task_vector(Path(adapter_dir), name=name)
    _assert_plain_lora(tv.config, f"expert {name} ({adapter_dir})")
    _assert_no_h1_path(str(adapter_dir))
    a: dict[str, torch.Tensor] = {}
    b: dict[str, torch.Tensor] = {}
    for key, t in tv.tensors.items():
        m = _MODULE_RE.match(key)
        if not m:
            continue
        (a if m.group("which") == "A" else b)[m.group("module")] = t.detach().float()
    missing = set(a) ^ set(b)
    if missing:
        raise ValueError(f"{name}: modules with only one factor: {sorted(missing)[:4]}")
    return a, b, float(tv.scaling)


def load_bank(
    adapters: Mapping[str, str | Path],
    *,
    dtype: torch.dtype = torch.float32,
) -> dict[str, ExpertBank]:
    """Build a per-module `ExpertBank` from `{expert_name: adapter_dir}`.

    Every expert must cover the same module set and share one rank: a mixture over ragged
    banks has no well-defined `[*, E, r]` view, and silently zero-padding would make the gate's
    weights mean different things for different experts.

    Expert order follows `adapters` iteration order and is recorded in `names`.
    """
    if len(adapters) < 2:
        raise ValueError(f"a mixture needs >=2 experts, got {list(adapters)}")

    per_expert = {name: _factors(Path(path), name) for name, path in adapters.items()}
    names = tuple(adapters)

    module_sets = {n: set(a) for n, (a, _, _) in per_expert.items()}
    common = set.intersection(*module_sets.values())
    ragged = {n: sorted(ms - common)[:3] for n, ms in module_sets.items() if ms - common}
    if ragged:
        raise ValueError(f"experts cover different modules; extras: {ragged}")

    ranks = {n: next(iter(a.values())).shape[0] for n, (a, _, _) in per_expert.items()}
    if len(set(ranks.values())) != 1:
        raise ValueError(f"experts disagree on rank: {ranks}")
    rank = int(next(iter(ranks.values())))

    banks: dict[str, ExpertBank] = {}
    for mod in sorted(common):
        a_blocks, b_blocks = [], []
        for n in names:
            a, b, scale = per_expert[n]
            a_blocks.append(a[mod])
            b_blocks.append(b[mod] * scale)  # fold alpha/r once, here
        banks[mod] = ExpertBank(
            names=names,
            rank=rank,
            A_cat=torch.cat(a_blocks, dim=0).to(dtype).contiguous(),
            B_cat=torch.cat(b_blocks, dim=1).to(dtype).contiguous(),
        )
    return banks


def bank_summary(banks: Mapping[str, ExpertBank]) -> dict[str, object]:
    """Small provenance blob for the run manifest."""
    if not banks:
        return {"n_modules": 0}
    any_bank = next(iter(banks.values()))
    n_params = sum(b.A_cat.numel() + b.B_cat.numel() for b in banks.values())
    return {
        "n_modules": len(banks),
        "n_experts": any_bank.n_experts,
        "experts": list(any_bank.names),
        "rank_per_expert": any_bank.rank,
        "total_rank": any_bank.rank * any_bank.n_experts,
        "bank_params": n_params,
    }


__all__ = ["ExpertBank", "load_bank", "bank_summary"]
