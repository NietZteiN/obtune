"""Mixture assembly for the SRH arms: `rev`, MIX50, and the common program subset.

Reuses `obtune.cft.dataset` for everything on disk. The only new data is the `rev` task,
and it is an **in-memory view** of the existing `gen` pool rather than a new file — which
is precisely the claim under test ("reverse training data is free: swap the pair"). It
also means the SHA manifest, the H1-marker content scan and the quarantine lint keep
covering the same files they already cover, with nothing new to verify.

The three things this module adds
--------------------------------
`flip_to_reverse`  every `gen` row relabelled `task="rev"`. No field swap — `prompts`
                   reads `code_b` as input and `code_a` as target for `rev`.
`split_directions` the MIX50 construction: half the programs contribute forward, half
                   reverse, **partitioned by `program_id`** so no program appears in both
                   directions. Partitioning by row instead would let the model see the
                   same program from both sides, which is FLIP with extra steps and would
                   destroy the arm's whole purpose.
`common_program_subset`  programs covered by EVERY requested condition. Needed on the
                   TRAIN side, not just at eval: `S1` bails on short bodies, so its
                   programs are systematically longer (283 vs 187 mean chars on the train
                   split). A cross-transformation cell trained on S1 and tested on L1r
                   would otherwise cross transformation family *and* program-length
                   distribution at once, and nothing downstream could separate them.
"""
from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Collection, Mapping, Optional, Sequence

from obtune import paths
from obtune.cft import dataset as cft_data
from obtune.cft.dataset import CFTInstance
from obtune.config import GLOBAL_SEED
from obtune.srh import prompts as srh_prompts


def flip_to_reverse(rows: Sequence[CFTInstance]) -> list[CFTInstance]:
    """Relabel `gen` rows as `rev`. Fields are NOT swapped — see the module docstring."""
    out: list[CFTInstance] = []
    for r in rows:
        if r.task != "gen":
            continue
        out.append(
            r.model_copy(
                update={
                    "task": srh_prompts.REV_TASK,
                    "instance_id": r.instance_id.rsplit("::", 1)[0] + "::rev",
                }
            )
        )
    return out


def split_directions(
    gen_rows: Sequence[CFTInstance],
    reverse_fraction: float = 0.5,
    seed: int = GLOBAL_SEED,
    disjoint_programs: bool = True,
) -> list[CFTInstance]:
    """MIX50: replace `reverse_fraction` of the forward rows with their reverse twins.

    The result has exactly as many instances as `gen_rows`, the same sequence content and
    therefore the same FLOPs and optimizer-step count as the FWD arm — with *less*
    supervised signal, because a reverse target (the shorter original) is about half the
    length of a forward target (the inflated obfuscation). That makes it a conservative
    test: any reverse capability it shows was bought at a budget discount, not a premium.

    `disjoint_programs=False` partitions by row instead, which lets one program appear in
    both directions. Kept only so the difference can be measured; it is not the arm.
    """
    if not 0.0 <= reverse_fraction <= 1.0:
        raise ValueError(f"reverse_fraction must be in [0, 1]; got {reverse_fraction}")
    rng = random.Random(seed)

    if disjoint_programs:
        program_ids = sorted({r.program_id for r in gen_rows})
        rng.shuffle(program_ids)
        n_rev = int(round(reverse_fraction * len(program_ids)))
        reverse_programs = set(program_ids[:n_rev])
        flip_mask = [r.program_id in reverse_programs for r in gen_rows]
    else:
        idx = list(range(len(gen_rows)))
        rng.shuffle(idx)
        chosen = set(idx[: int(round(reverse_fraction * len(idx)))])
        flip_mask = [i in chosen for i in range(len(gen_rows))]

    out: list[CFTInstance] = []
    for row, flip in zip(gen_rows, flip_mask):
        out.extend(flip_to_reverse([row]) if flip else [row])
    return out


def common_program_subset(
    language: str,
    conditions: Sequence[str],
    splits: Sequence[str] = ("train", "val"),
) -> set[str]:
    """Programs with a `gen` instance under EVERY requested condition."""
    rows = cft_data.load_pool(language, "gen", splits)
    by_cond: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        by_cond[r.condition].add(r.program_id)
    missing = [c for c in conditions if c not in by_cond]
    if missing:
        raise ValueError(f"no pool rows for condition(s) {missing} in {language}")
    return set.intersection(*(by_cond[c] for c in conditions))


def load_mixture(
    language: str,
    tasks: Sequence[str],
    splits: Sequence[str] = ("train",),
    paired: bool = True,
    conditions: Optional[Sequence[str]] = None,
    program_ids: Optional[Collection[str]] = None,
    program_subset: Optional[str] = None,
    direction_mix: Optional[Mapping[str, Any]] = None,
) -> list[CFTInstance]:
    """The SRH training mixture. Signature-compatible with `cft.dataset.load_mixture`
    so `cft.train.main` can take it as a drop-in via its `load_mixture=` hook.

    `direction_mix` (MIX50) is mutually exclusive with putting `rev` in `tasks`: the
    first replaces forward rows, the second adds reverse rows alongside them, and doing
    both would silently produce an arm that is neither.
    """
    srh_prompts.assert_tasks_known(tasks)
    srh_prompts.assert_replication_untouched()

    conds = list(conditions) if conditions else None
    if program_subset == "common":
        if not conds:
            raise ValueError("program_subset='common' requires an explicit condition list")
        common = common_program_subset(language, conds, splits=("train", "val"))
        program_ids = common if program_ids is None else (set(program_ids) & common)
    elif program_subset not in (None, "all"):
        raise ValueError(f"program_subset must be None|'all'|'common'; got {program_subset!r}")

    wants_rev = srh_prompts.REV_TASK in tasks
    if direction_mix and wants_rev:
        raise ValueError(
            "direction_mix (MIX50) replaces forward rows with reverse ones, while "
            "tasks=[... 'rev'] adds them alongside. Pick one; together they build an arm "
            "that is neither FLIP nor MIX50."
        )

    base_tasks = [t for t in tasks if t != srh_prompts.REV_TASK]
    rows: list[CFTInstance] = []
    if base_tasks:
        rows.extend(cft_data.load_mixture(language, base_tasks, splits, paired=paired))
    if wants_rev:
        rows.extend(flip_to_reverse(cft_data.load_pool(language, "gen", splits)))

    if direction_mix:
        gen_rows = [r for r in rows if r.task == "gen"]
        other = [r for r in rows if r.task != "gen"]
        rows = other + split_directions(
            gen_rows,
            reverse_fraction=float(direction_mix.get("reverse_fraction", 0.5)),
            seed=int(direction_mix.get("seed", GLOBAL_SEED)),
            disjoint_programs=bool(direction_mix.get("disjoint_programs", True)),
        )

    if conds:
        keep = set(conds)
        rows = [r for r in rows if r.condition in keep]
    if program_ids is not None:
        keep_p = set(program_ids)
        rows = [r for r in rows if r.program_id in keep_p]

    if direction_mix and direction_mix.get("disjoint_programs", True):
        assert_direction_disjoint(rows)
    return rows


def assert_direction_disjoint(rows: Sequence[CFTInstance]) -> None:
    """Under MIX50 no program may contribute both directions — see `split_directions`."""
    seen: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        if r.task in ("gen", srh_prompts.REV_TASK):
            seen[r.program_id].add(r.task)
    both = sorted(p for p, t in seen.items() if len(t) > 1)
    if both:
        raise cft_data.CFTDataError(
            f"{len(both)} program(s) appear in BOTH directions under a disjoint MIX50 "
            f"(e.g. {both[:5]}) — the arm is no longer budget-matched to FWD"
        )


def direction_balance(rows: Sequence[CFTInstance]) -> dict[str, Any]:
    """Instance counts per direction and per condition — recorded in every run manifest
    so an arm's realised composition is a number rather than an assumption."""
    per: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        per[r.condition][r.task] += 1
    out: dict[str, Any] = {c: dict(sorted(v.items())) for c, v in sorted(per.items())}
    totals: dict[str, int] = defaultdict(int)
    for v in per.values():
        for task, n in v.items():
            totals[task] += n
    out["ALL"] = dict(sorted(totals.items()))
    n_fwd, n_rev = totals.get("gen", 0), totals.get(srh_prompts.REV_TASK, 0)
    out["reverse_share"] = n_rev / (n_fwd + n_rev) if (n_fwd + n_rev) else None
    return out


def assert_no_h1(rows: Sequence[CFTInstance]) -> None:
    """Belt and braces on top of `CFTInstance`'s validator (CLAUDE.md §3.2)."""
    bad = sorted({r.condition for r in rows} - set(paths.TRAINABLE_CONDITIONS))
    if bad:
        raise paths.QuarantineViolation(f"non-trainable condition(s) in an SRH mixture: {bad}")
