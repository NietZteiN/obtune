"""Geometry of LoRA task vectors — does training longer make experts interfere more?

Horoi, Wolf, Belilovsky & Dziugaite, "From Memorization to Parameter Interference: How
Overtraining Experts Harms Model Merging" (arXiv:2506.14126v2), argue that fine-tuning an
expert to its own individual optimum degrades merging, because late training is dominated by
memorization of a few hard examples, which "causes negative parameter interference".

That describes this project's checkpoint-selection procedure exactly: `eval_vllm.run_ckpt_select`
picks `best` by held-in validation accuracy — individual performance — and every merge here is
built from `best`. Two observations already on record are consistent with the mechanism and
neither was collected to test it:

  * TIES discards ~80 % of the update. Mean per-module ||dW|| is 0.362 for one expert but 0.069
    for `merge_ties`. TIES prunes that hard only when experts disagree in SIGN.
  * `ckpt_select` chose different epochs per condition (L1r, S3 at epoch 1; L2, S2, S1, S4 at
    epoch 3), so the existing merges already combine task vectors of unequal training.

This module measures the mechanism directly, on CPU, from checkpoints already on disk.

THE TRICK THAT MAKES IT CHEAP
-----------------------------
Frobenius inner products between LoRA task vectors never need dW materialized. With
dW_i = s_i * B_i @ A_i (B: [d_out, r], A: [r, d_in]):

    <dW_i, dW_j>_F = tr(dW_i^T dW_j)
                   = s_i s_j * tr(A_i^T B_i^T B_j A_j)
                   = s_i s_j * tr((B_i^T B_j) @ (A_j A_i^T))          [cyclic]

Both factors are r x r with r = 32, so a pair costs O(r^2 (d_out + d_in)) instead of
O(d_out d_in). Norms are the i == j case. Sign statistics DO need the dense matrix, so those
materialize one module at a time and free it — see `sign_conflict`.

This identity holds only for vanilla LoRA, where the scaling is the shared constant alpha/r;
`taskvec._assert_plain_lora` is reused rather than re-derived, so DoRA/rslora raise instead of
silently producing wrong geometry.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

from obtune.taskvec import TaskVector, _assert_plain_lora, load_task_vector

#: `...layers.<L>.<block>.<proj>.lora_A.weight` -> we key modules by everything before `.lora_`.
_MODULE_RE = re.compile(r"^(?P<module>.+)\.lora_(?P<which>[AB])\.weight$")


@dataclass(frozen=True)
class ModulePair:
    """The two low-rank factors of one module's update, already scaled."""

    module: str
    A: np.ndarray  # [r, d_in]
    B: np.ndarray  # [d_out, r], with alpha/r folded in


def module_factors(tv: TaskVector) -> dict[str, ModulePair]:
    """Split a task vector into per-module (A, B), folding alpha/r into B once.

    Folding into B rather than A matches `taskvec.scale`'s convention (B carries the scalar),
    so a vector produced here composes with that module without a second convention to track.
    """
    _assert_plain_lora(tv.config, f"task vector {tv.name or tv.path}")
    a: dict[str, np.ndarray] = {}
    b: dict[str, np.ndarray] = {}
    for key, t in tv.tensors.items():
        m = _MODULE_RE.match(key)
        if not m:
            continue
        arr = t.detach().to("cpu").float().numpy()
        (a if m.group("which") == "A" else b)[m.group("module")] = arr

    missing = set(a) ^ set(b)
    if missing:
        raise ValueError(f"{tv.name}: modules with only one factor: {sorted(missing)[:4]}")
    s = float(tv.scaling)
    return {mod: ModulePair(mod, a[mod], b[mod] * s) for mod in sorted(a)}


def _inner(x: ModulePair, y: ModulePair) -> float:
    """<dW_x, dW_y>_F without forming either dW. See the module docstring."""
    # tr((B_x^T B_y) @ (A_y A_x^T)) — both operands are r x r.
    left = x.B.T @ y.B          # [r, r]
    right = y.A @ x.A.T         # [r, r]
    return float(np.einsum("ij,ji->", left, right))


def norms(factors: dict[str, ModulePair]) -> dict[str, float]:
    """Per-module Frobenius norm of dW."""
    return {mod: float(np.sqrt(max(_inner(mp, mp), 0.0))) for mod, mp in factors.items()}


def cosine(x: dict[str, ModulePair], y: dict[str, ModulePair]) -> dict[str, float]:
    """Per-module cosine similarity between two experts' updates.

    Cosine rather than raw inner product because the norms themselves change with training —
    conflating "the vectors grew" with "the vectors diverged" is exactly the confound this is
    meant to separate. Norm growth is reported by `norms`.
    """
    out: dict[str, float] = {}
    for mod in x.keys() & y.keys():
        nx = np.sqrt(max(_inner(x[mod], x[mod]), 0.0))
        ny = np.sqrt(max(_inner(y[mod], y[mod]), 0.0))
        out[mod] = 0.0 if nx <= 0 or ny <= 0 else _inner(x[mod], y[mod]) / (nx * ny)
    return out


def sign_conflict(
    experts: dict[str, dict[str, ModulePair]],
    modules: Optional[Iterable[str]] = None,
) -> dict[str, dict[str, float]]:
    """Per-module sign disagreement across experts — the paper's mechanism, measured.

    This is the one statistic that needs the dense dW, so it materializes ONE module at a time
    across all experts and frees it. At 1.5B the largest is [1536, 8960] = 13.8 M floats, so
    eight of them is ~440 MB — fine on this box, and bounded regardless of expert count because
    only one module is resident.

    Returns per module:
      `conflict`  mean over coordinates of (1 - |sum_i sign| / n_experts). 0 = all experts agree
                  on every coordinate's direction, 1 = perfectly split.
      `ties_keep` fraction of total |dW| mass that survives TIES sign election, i.e. the share
                  contributed by entries agreeing with the elected (sum-of-signs) direction.
                  This is what makes the 0.19x shrinkage of `merge_ties` legible.
    """
    names = sorted(experts)
    common = set.intersection(*(set(experts[n]) for n in names))
    todo = sorted(common if modules is None else (set(modules) & common))

    out: dict[str, dict[str, float]] = {}
    for mod in todo:
        dws = [experts[n][mod].B @ experts[n][mod].A for n in names]
        stack = np.stack(dws)                       # [E, d_out, d_in]
        del dws
        sgn = np.sign(stack)
        agree = np.abs(sgn.sum(axis=0)) / len(names)
        elected = np.sign(sgn.sum(axis=0))
        mass = np.abs(stack)
        kept = np.where(sgn == elected[None, ...], mass, 0.0).sum()
        total = mass.sum()
        out[mod] = {
            "conflict": float(1.0 - agree.mean()),
            "ties_keep": float(kept / total) if total > 0 else 0.0,
        }
        del stack, sgn, mass
    return out


def pooled(per_module: dict[str, float]) -> float:
    return float(np.mean(list(per_module.values()))) if per_module else float("nan")


def by_projection(per_module: dict[str, float]) -> dict[str, float]:
    """Group per-module values by projection name (q_proj, down_proj, ...).

    Interference may be localized to particular projections; a single pooled number would hide
    that, and where it lives is itself a result.
    """
    groups: dict[str, list[float]] = defaultdict(list)
    for mod, v in per_module.items():
        groups[mod.rsplit(".", 1)[-1]].append(v)
    return {k: float(np.mean(v)) for k, v in sorted(groups.items())}


def load_expert(adapter_dir: Path | str, name: str = "") -> dict[str, ModulePair]:
    """Load one expert checkpoint and return its per-module factors."""
    return module_factors(load_task_vector(Path(adapter_dir), name=name or str(adapter_dir)))


__all__ = [
    "ModulePair", "module_factors", "norms", "cosine", "sign_conflict",
    "pooled", "by_projection", "load_expert",
]
