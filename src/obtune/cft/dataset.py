"""Build the three CFT instance pools (L_gen, L_pos, L_neg) from the obtune corpus.

Paper §5.0.2: "CFT uses balanced triplet datasets across transformation types. For
open-source models, we construct 30 000 instances (10 000 each for positive
classification, negative classification, and obfuscation task generation)."

Pool construction on our corpus
-------------------------------
Let `A` be an L0 parent program and `obf_c(A)` its gate-validated variant under
condition `c`.

    gen  : prompt = A,  target = obf_c(A)             — the forward task
    pos  : (A, obf_c(A))                    -> YES    — semantics preserved
    neg  : (A, mutate(obf_c(A)))            -> NO     — semantics altered

The negative's second program is the *obfuscated variant with one token changed*, so
positives and negatives are equally obfuscated and "does B look obfuscated?" carries
zero information about the label. The paper's own construction (§5.0.2: positives pair
non-obfuscated with obfuscated code, negatives pair non-obfuscated with non-obfuscated
code) leaves that shortcut open; `negative_style="clean_mutant"` reproduces it exactly
so the difference can be measured instead of asserted.

Mutating the *variant* rather than obfuscating a *mutant* also avoids re-running the
obfuscation pipeline on code that never passed the semantic gate — the mutant is by
construction not semantics-preserving, so the gate would reject it and there would be no
way to tell a gate bail from a mutation that broke the program.

Everything is read through `paths.load_training_jsonl` (quarantine layer 1) and written
under `data/train/cft/`, which `scripts/check_manifest.py` then scans for H1 markers
like any other training file.
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Collection, Iterable, Mapping, Optional, Sequence

from pydantic import BaseModel, Field, field_validator

from obtune import paths
from obtune.cft import mutate, prompts
from obtune.config import GLOBAL_SEED

CFT_SUBDIR = "cft"
NEGATIVE_STYLES = ("obfuscated_mutant", "clean_mutant")


class CFTInstance(BaseModel):
    """One CFT training instance (data/train/cft/<lang>/<task>.jsonl)."""

    instance_id: str  # f"{program_id}::{condition}::{task}"
    task: str  # gen | pos | neg
    program_id: str
    program_group_id: str  # = program_id; the split unit, never split by row
    condition: str  # trainable conditions only
    language: str
    code_a: str  # the L0 parent
    code_b: str  # obfuscated variant (gen/pos) or semantics-altered program (neg)
    label: Optional[str] = None  # YES | NO for pos/neg; None for gen
    split: str
    negative_style: Optional[str] = None
    mutation: Optional[dict[str, Any]] = None
    provenance: str = "cft_v1"

    @field_validator("condition")
    @classmethod
    def _no_h1(cls, v: str) -> str:
        if v not in paths.TRAINABLE_CONDITIONS:
            raise ValueError(
                f"condition {v!r} is not trainable; CFT instances may never carry H1 "
                "(CLAUDE.md §3.2)"
            )
        return v


class PoolReport(BaseModel):
    language: str
    negative_style: str
    seed: int
    by_task: dict[str, int] = Field(default_factory=dict)
    by_task_condition: dict[str, dict[str, int]] = Field(default_factory=dict)
    by_task_split: dict[str, dict[str, int]] = Field(default_factory=dict)
    n_programs: dict[str, int] = Field(default_factory=dict)
    mutation_stats: dict[str, Any] = Field(default_factory=dict)
    coverage: dict[str, int] = Field(default_factory=dict)
    prompt_provenance: dict[str, str] = Field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Paths and loading

def cft_dir(language: str, variant: Optional[str] = None) -> Path:
    """Pool directory. `variant` writes to a SIBLING dir, never over the default.

    Added 2026-08-17 so the paper-literal `clean_mutant` negatives could be built without
    destroying `data/train/cft/<lang>/`, which is the pool every published number in
    paper_bidirectional was trained on. There is no versioning under `data/train/` and the
    build script overwrites in place, so a `--negative-style clean_mutant` run without this
    would have silently replaced the corpus behind Table 2, Table 3 and the whole 2x2 with
    no way back short of a 40-minute rebuild.
    """
    leaf = language if not variant else f"{language}__{variant}"
    return paths.TRAIN_ROOT / CFT_SUBDIR / leaf


def pool_path(language: str, task: str, variant: Optional[str] = None) -> Path:
    return cft_dir(language, variant) / f"{task}.jsonl"


def report_path(language: str, variant: Optional[str] = None) -> Path:
    return cft_dir(language, variant) / "pool_report.json"


def load_splits(language: str) -> dict[str, str]:
    """program_id -> train|val|test, from the corpus split file.

    Read directly (not via `load_training_jsonl`) because data/splits/ holds no code —
    it is an assignment map, and the loader guard is scoped to files that carry program
    text. The guard still covers every file this module reads code from.
    """
    p = paths.SPLITS_ROOT / f"{language}.json"
    if not p.exists():
        raise FileNotFoundError(f"missing split file: {p}")
    with p.open() as f:
        spec = json.load(f)
    return {str(k): str(v) for k, v in spec["assignment"].items()}


def load_base_programs(language: str) -> dict[str, dict[str, Any]]:
    rows = paths.load_training_jsonl(paths.TRAIN_ROOT / "base" / f"{language}.jsonl")
    return {r["program_id"]: r for r in rows}


def load_variants(condition: str, language: str) -> dict[str, dict[str, Any]]:
    p = paths.TRAIN_ROOT / "variants" / condition / f"{language}.jsonl"
    if not p.exists():
        raise FileNotFoundError(f"missing variants for {condition}/{language}: {p}")
    return {r["program_id"]: r for r in paths.load_training_jsonl(p)}


# --------------------------------------------------------------------------- #
# Pool construction

def _balanced_take(rows: Sequence[CFTInstance], n: int, seed: int) -> list[CFTInstance]:
    """Take `n` instances round-robin across conditions (mirrors `data._balanced_take`).

    S1 bails on some programs by design (CLAUDE.md §4 coverage honesty), so a straight
    concatenation would under-represent the structural conditions in every capped pool.
    """
    rng = random.Random(seed)
    if n <= 0 or n >= len(rows):
        out = list(rows)
        rng.shuffle(out)
        return out
    by_cond: dict[str, list[CFTInstance]] = defaultdict(list)
    for r in rows:
        by_cond[r.condition].append(r)
    for v in by_cond.values():
        rng.shuffle(v)
    conds = sorted(by_cond)
    idx = {c: 0 for c in conds}
    out: list[CFTInstance] = []
    while len(out) < n:
        progressed = False
        for c in conds:
            if len(out) >= n:
                break
            i = idx[c]
            if i < len(by_cond[c]):
                out.append(by_cond[c][i])
                idx[c] = i + 1
                progressed = True
        if not progressed:
            break
    rng.shuffle(out)
    return out


def build_pools(
    language: str,
    conditions: Sequence[str],
    splits: Sequence[str] = ("train", "val"),
    negative_style: str = "obfuscated_mutant",
    n_per_task: Optional[int] = None,
    seed: int = GLOBAL_SEED,
    mutants_per_program: int = 6,
    keep_mutants_per_program: int = 1,
    min_ok_fraction: float = 0.5,
    max_cases: int = 12,
    exec_timeout_s: float = 2.0,
    exec_workers: int = 32,
    program_limit: Optional[int] = None,
) -> tuple[dict[str, list[CFTInstance]], PoolReport]:
    """Materialize the gen/pos/neg pools for one language.

    `n_per_task` caps each pool (the paper's 10 000); `None` means "everything the
    corpus supports", which is what a smaller corpus than CodeNet's 10 000 Java
    programs actually allows.
    """
    if negative_style not in NEGATIVE_STYLES:
        raise ValueError(f"negative_style must be one of {NEGATIVE_STYLES}")
    bad = [c for c in conditions if c not in paths.TRAINABLE_CONDITIONS]
    if bad:
        raise paths.QuarantineViolation(f"conditions {bad} are not trainable")

    split_of = load_splits(language)
    base = load_base_programs(language)
    keep_splits = set(splits)

    program_ids = sorted(pid for pid in base if split_of.get(pid) in keep_splits)
    if program_limit:
        program_ids = program_ids[:program_limit]
    base = {pid: base[pid] for pid in program_ids}

    variants: dict[str, dict[str, dict[str, Any]]] = {
        c: load_variants(c, language) for c in conditions
    }

    gen: list[CFTInstance] = []
    pos: list[CFTInstance] = []
    coverage: Counter[str] = Counter()

    for cond in conditions:
        vmap = variants[cond]
        for pid in program_ids:
            v = vmap.get(pid)
            if v is None:
                continue  # the transform bailed on this program (coverage honesty)
            coverage[cond] += 1
            parent = base[pid]
            common = dict(
                program_id=pid,
                program_group_id=pid,
                condition=cond,
                language=language,
                code_a=parent["code"],
                code_b=v["code"],
                split=split_of[pid],
            )
            gen.append(CFTInstance(instance_id=f"{pid}::{cond}::gen", task="gen", **common))
            pos.append(
                CFTInstance(
                    instance_id=f"{pid}::{cond}::pos",
                    task="pos",
                    label=prompts.EQUIV_YES,
                    **common,
                )
            )

    # ---- negatives: one execution-verified mutation per (program, condition) ------
    # The mutation target depends on `negative_style`; both go through the same
    # verifier, so a "different semantics" label is always an executed fact.
    neg: list[CFTInstance] = []
    mutation_stats: dict[str, Any] = {}

    if negative_style == "clean_mutant":
        # Mutate the L0 parent once per program and reuse it under every condition:
        # the parent does not depend on the condition, and re-verifying the same
        # mutation six times would only burn CPU.
        progs = mutate.iter_programs(base[pid] for pid in program_ids)
        kept, stats = mutate.verify(
            progs,
            n_per_program=mutants_per_program,
            seed=seed,
            max_cases=max_cases,
            min_ok_fraction=min_ok_fraction,
            timeout_s=exec_timeout_s,
            workers=exec_workers,
            keep_per_program=keep_mutants_per_program,
        )
        mutation_stats["clean"] = stats.as_dict()
        by_pid: dict[str, list[mutate.Mutant]] = defaultdict(list)
        for m in kept:
            by_pid[m.program_id].append(m)
        for cond in conditions:
            vmap = variants[cond]
            for pid in program_ids:
                if pid not in vmap or pid not in by_pid:
                    continue
                m = by_pid[pid][0]
                neg.append(
                    CFTInstance(
                        instance_id=f"{pid}::{cond}::neg",
                        task="neg",
                        program_id=pid,
                        program_group_id=pid,
                        condition=cond,
                        language=language,
                        code_a=base[pid]["code"],
                        code_b=m.code,
                        label=prompts.EQUIV_NO,
                        split=split_of[pid],
                        negative_style=negative_style,
                        mutation=m.as_meta(),
                    )
                )
    else:
        # Mutate each obfuscated variant. Verification executes the mutated variant
        # against the *variant* (not the parent) so that a transform-introduced
        # behavioural quirk cannot be misread as the mutation's effect — the gate
        # already established variant == parent.
        for cond in conditions:
            vmap = variants[cond]
            targets = []
            for pid in program_ids:
                v = vmap.get(pid)
                if v is None:
                    continue
                targets.append(
                    {
                        "program_id": pid,
                        "language": language,
                        "code": v["code"],
                        "entry_point": v["entry_point"],
                        "cases": base[pid].get("cases", []),
                        "gate_inputs": base[pid].get("gate_inputs", []),
                    }
                )
            kept, stats = mutate.verify(
                targets,
                n_per_program=mutants_per_program,
                seed=seed,
                max_cases=max_cases,
                min_ok_fraction=min_ok_fraction,
                timeout_s=exec_timeout_s,
                workers=exec_workers,
                keep_per_program=keep_mutants_per_program,
            )
            mutation_stats[cond] = stats.as_dict()
            for m in kept:
                pid = m.program_id
                neg.append(
                    CFTInstance(
                        instance_id=f"{pid}::{cond}::neg",
                        task="neg",
                        program_id=pid,
                        program_group_id=pid,
                        condition=cond,
                        language=language,
                        code_a=base[pid]["code"],
                        code_b=m.code,
                        label=prompts.EQUIV_NO,
                        split=split_of[pid],
                        negative_style=negative_style,
                        mutation=m.as_meta(),
                    )
                )

    pools = {"gen": gen, "pos": pos, "neg": neg}
    if n_per_task:
        pools = {k: _balanced_take(v, n_per_task, seed + i) for i, (k, v) in enumerate(sorted(pools.items()))}
    else:
        pools = {k: _balanced_take(v, 0, seed + i) for i, (k, v) in enumerate(sorted(pools.items()))}

    validate_pools(pools, split_of)

    report = PoolReport(
        language=language,
        negative_style=negative_style,
        seed=seed,
        by_task={k: len(v) for k, v in sorted(pools.items())},
        by_task_condition={
            k: dict(sorted(Counter(r.condition for r in v).items())) for k, v in sorted(pools.items())
        },
        by_task_split={
            k: dict(sorted(Counter(r.split for r in v).items())) for k, v in sorted(pools.items())
        },
        n_programs={k: len({r.program_id for r in v}) for k, v in sorted(pools.items())},
        mutation_stats=mutation_stats,
        coverage=dict(sorted(coverage.items())),
        prompt_provenance=prompts.provenance_block(),
    )
    return pools, report


# --------------------------------------------------------------------------- #
# Validation

class CFTDataError(RuntimeError):
    """A CFT pool violates the dataset contract."""


def validate_pools(
    pools: Mapping[str, Sequence[CFTInstance]], split_of: Mapping[str, str]
) -> None:
    """The three checks that would silently invalidate a CFT comparison.

    1. Split leakage — a program in two splits (CLAUDE.md §4.1).
    2. Test-split contamination — CFT training data must never contain an eval program.
    3. Degenerate instances — `code_a == code_b` in a pos/neg pair, or an unchanged
       "obfuscated" target in gen. An identity pair labelled NO would teach the model
       that identical programs are inequivalent.
    """
    seen_split: dict[str, set[str]] = defaultdict(set)
    degenerate: list[str] = []
    for task, rows in pools.items():
        ids = [r.instance_id for r in rows]
        dupes = [k for k, v in Counter(ids).items() if v > 1]
        if dupes:
            raise CFTDataError(f"duplicate instance_id in pool {task!r}: {dupes[:5]}")
        for r in rows:
            seen_split[r.program_id].add(r.split)
            if r.split == "test":
                raise CFTDataError(
                    f"{r.instance_id}: test-split program in a CFT training pool — "
                    "this contaminates the bidirectional evaluation"
                )
            if r.code_a.strip() == r.code_b.strip():
                degenerate.append(r.instance_id)
    leaked = sorted(pid for pid, s in seen_split.items() if len(s) > 1)
    if leaked:
        raise CFTDataError(
            f"{len(leaked)} program_id(s) in more than one split (e.g. {leaked[:5]})"
        )
    if degenerate:
        raise CFTDataError(
            f"{len(degenerate)} instance(s) whose two programs are identical "
            f"(e.g. {degenerate[:5]})"
        )


# --------------------------------------------------------------------------- #
# Persistence

def write_pools(
    language: str,
    pools: Mapping[str, Sequence[CFTInstance]],
    report: PoolReport,
    variant: Optional[str] = None,
) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for task, rows in sorted(pools.items()):
        p = pool_path(language, task, variant)
        paths.write_jsonl(p, [r.model_dump() for r in rows])
        out[task] = p
    rp = report_path(language, variant)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report.model_dump(), indent=2, sort_keys=True) + "\n")
    out["report"] = rp
    return out


def load_pool(language: str, task: str, splits: Optional[Sequence[str]] = None,
              variant: Optional[str] = None) -> list[CFTInstance]:
    p = pool_path(language, task, variant)
    if not p.exists():
        raise FileNotFoundError(
            f"missing CFT pool {task}/{language}: {p}. Run scripts/cft/10_build_cft_data.py first."
        )
    rows = [CFTInstance(**r) for r in paths.load_training_jsonl(p)]
    if splits is not None:
        keep = set(splits)
        rows = [r for r in rows if r.split in keep]
    return rows


def pair_pos_neg(rows: Sequence[CFTInstance]) -> list[CFTInstance]:
    """Keep only the (program_id, condition) keys that have BOTH a YES and a NO.

    Why this is not optional. Mutation coverage is not uniform across conditions: `S2`
    yields far fewer verified negatives than the others, because most of what `S2`
    inserts is dead code and opaque predicates and a mutation landing there changes
    nothing observable (measured on the Python corpus: 6 070 rejected as equivalent
    mutants under `S2`, against ~430 under each identifier condition). Left alone, that
    gives P(YES | S2) = 0.65 against 0.55 elsewhere — and the condition is plainly
    visible in the code, so a model can beat chance on L_pos/L_neg by recognising the
    obfuscation style instead of comparing semantics.

    Pairing removes the shortcut completely rather than shrinking it: after it, every
    program-condition key contributes exactly one YES and one NO built from the SAME
    `code_a`, so nothing observable about the pair predicts the label except the
    semantic difference itself. It is also the natural reading of the paper's "balanced
    triplet datasets" (§5.0.2).

    Applied at mixture-assembly time, not at pool-build time: the pools on disk stay the
    complete raw material (and `pool_report.json` keeps showing the real imbalance),
    while the experimental design lives with the run that uses it.
    """
    keyed: dict[tuple[str, str], dict[str, list[CFTInstance]]] = defaultdict(
        lambda: defaultdict(list)
    )
    other: list[CFTInstance] = []
    for r in rows:
        if r.task in ("pos", "neg"):
            keyed[(r.program_id, r.condition)][r.task].append(r)
        else:
            other.append(r)
    out = list(other)
    for key in sorted(keyed):
        bucket = keyed[key]
        if bucket.get("pos") and bucket.get("neg"):
            out.extend(bucket["pos"])
            out.extend(bucket["neg"])
    return out


def load_mixture(
    language: str,
    tasks: Sequence[str],
    splits: Sequence[str] = ("train",),
    paired: bool = True,
    variant: Optional[str] = None,
) -> list[CFTInstance]:
    """The training mixture. `tasks=["gen"]` is the paper's SFT baseline;
    `tasks=["gen","pos","neg"]` is CFT (L_CFT = L_pos + L_neg + L_gen, §5.0.2).

    `paired=False` reproduces the unbalanced mixture so the shortcut described in
    `pair_pos_neg` can be measured rather than only asserted.
    """
    bad = [t for t in tasks if t not in prompts.TASKS]
    if bad:
        raise ValueError(f"unknown task(s) {bad}; trainable tasks are {list(prompts.TASKS)}")
    rows: list[CFTInstance] = []
    for t in tasks:
        rows.extend(load_pool(language, t, splits, variant=variant))
    if paired:
        rows = pair_pos_neg(rows)
    return rows


def label_balance(rows: Sequence[CFTInstance]) -> dict[str, Any]:
    """P(YES) overall and per condition — recorded in every run manifest.

    A shortcut that is measured every run cannot quietly come back.
    """
    per: dict[str, dict[str, int]] = defaultdict(lambda: {"pos": 0, "neg": 0})
    for r in rows:
        if r.task in ("pos", "neg"):
            per[r.condition][r.task] += 1
    out: dict[str, Any] = {}
    tot_p = tot_n = 0
    for cond, c in sorted(per.items()):
        tot_p += c["pos"]
        tot_n += c["neg"]
        total = c["pos"] + c["neg"]
        out[cond] = {**c, "p_yes": c["pos"] / total if total else None}
    out["ALL"] = {
        "pos": tot_p,
        "neg": tot_n,
        "p_yes": tot_p / (tot_p + tot_n) if (tot_p + tot_n) else None,
    }
    return out


def to_sft_records(
    rows: Iterable[CFTInstance],
    build_example: Optional[Callable[[Mapping[str, Any]], dict[str, Any]]] = None,
) -> list[dict[str, Any]]:
    """`build_example` is injectable so a follow-up experiment can add a task format
    without touching this module's frozen prompt contract (the replication's reverse
    direction must stay unsupervised — see `prompts.completion_for`). Defaults to the
    replication's own builder, so existing callers are unaffected."""
    builder = build_example or prompts.build_example
    return [builder(r.model_dump()) for r in rows]
