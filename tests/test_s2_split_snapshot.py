"""The S2 refactor must not have changed S2, and S3/S4 must be genuinely different.

`obf/py/deadcode.py` was refactored into `_run(ctx, mode)` so the two halves of S2 could be
emitted as their own conditions (S3 = dead helpers only, S4 = opaque predicates only). S2
itself was supposed to come out byte-identical. Nothing checked that, even though the plan
called a byte-identity snapshot "the single most important new test" — and the cost of
being wrong is unbounded: every S2 adapter, every S2 eval cell and the pilot report were
produced from the pre-refactor corpus, so a behaviour change would silently invalidate all
of them while `make check` stayed green (the manifest pins the bytes on disk, not the
bytes the code would produce today).

Verified on 2026-08-09: S2 reproduces 40/40 byte-identical. This test keeps it that way.

WHY ATTEMPT-0 RECORDS ONLY
--------------------------
The builder retries a program with a fresh seed when the gate rejects a variant, and the
gate includes execution checks (`exec_parity`, `runtime_ratio`) whose outcome can vary with
machine load — a timeout under a loaded box rejects an attempt that passes on a quiet one.
A stored record with `attempt > 0` therefore encodes a gate decision taken under conditions
we cannot reconstruct, not a property of the transform. One real instance exists
(`B:cruxeval-x-python/101` in S3, stored at attempt 1, rebuilt at attempt 0), and it is the
reason corpus regeneration is not guaranteed byte-identical even though the transforms are
deterministic. Restricting to attempt-0 records tests transform determinism, which is what
this file is about, without a fuzzy percentage tolerance that would hide a real regression.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obtune.config import PROJECT_ROOT, load_config
from obtune.obf import builder
from obtune.paths import iter_jsonl
from obtune.schema import BaseProgram

BASE_DIR = PROJECT_ROOT / "data" / "eval" / "testset" / "base"
VARIANT_DIR = PROJECT_ROOT / "data" / "eval" / "testset" / "variants"

pytestmark = pytest.mark.skipif(
    not BASE_DIR.exists() or not VARIANT_DIR.exists(),
    reason="corpus not present (fixture-only checkout)",
)


def _programs(language: str) -> list[BaseProgram]:
    out = []
    for p in sorted(BASE_DIR.glob("*.jsonl")):
        for row in iter_jsonl(p):
            bp = BaseProgram.model_validate(row)
            if bp.language == language:
                out.append(bp)
    return out


def _stored(condition: str, language: str) -> dict[str, dict]:
    f = VARIANT_DIR / condition / f"{language}.jsonl"
    if not f.exists():
        return {}
    return {r["program_id"]: r for r in map(json.loads, f.open())}


def _rebuild(conditions: list[str], language: str) -> dict[str, dict[str, str]]:
    cfg = load_config("conditions.yaml")
    progs = _programs(language)
    if not progs:
        return {}
    rep = builder.build_variants(
        progs, conditions, language, workers=4,
        seed=int(cfg.get("global_seed", 17)), cfg=cfg, write=False,
    )
    out: dict[str, dict[str, str]] = {}
    for v in rep.variants:
        out.setdefault(v.condition, {})[v.program_id] = v.code
    return out


def _assert_reproduces(condition: str, language: str) -> int:
    stored = _stored(condition, language)
    if not stored:
        pytest.skip(f"no stored {condition}/{language} corpus")
    rebuilt = _rebuild([condition], language).get(condition, {})
    assert rebuilt, f"builder produced no {condition}/{language} variants"

    checked = 0
    drift: list[str] = []
    for pid, rec in stored.items():
        if (rec.get("transform_meta") or {}).get("attempt", 0) != 0:
            continue  # gate-retry record; see the module docstring
        if pid not in rebuilt:
            drift.append(f"{pid}: no longer produced at all")
            continue
        checked += 1
        if rebuilt[pid] != rec["code"]:
            drift.append(pid)
    assert not drift, (
        f"{condition}/{language}: {len(drift)} program(s) no longer reproduce from the "
        f"on-disk corpus: {drift[:5]}. Every adapter and eval cell for this condition was "
        f"built from that corpus, so a change here invalidates them."
    )
    return checked


def test_s2_is_byte_identical_after_the_split_refactor() -> None:
    """The load-bearing one. S2 predates S3/S4 and must be untouched by their extraction."""
    n = _assert_reproduces("S2", "python")
    assert n >= 20, f"only {n} attempt-0 S2 records checked — too few to be a real guard"


def test_s3_reproduces() -> None:
    _assert_reproduces("S3", "python")


def test_s4_reproduces() -> None:
    _assert_reproduces("S4", "python")


def test_the_three_conditions_are_actually_different() -> None:
    """A split that produced identical output would be a silent no-op experiment.

    S3 and S4 exist to separate two mechanisms that S2 conflates. If any pair collided on
    real programs, the S2-split result would be uninterpretable — and nothing else in the
    suite would notice, because each condition would still pass its own purity gate.
    """
    stored = {c: _stored(c, "python") for c in ("S2", "S3", "S4")}
    common = set(stored["S2"]) & set(stored["S3"]) & set(stored["S4"])
    assert len(common) >= 20, f"only {len(common)} programs common to S2/S3/S4"
    for a, b in (("S2", "S3"), ("S2", "S4"), ("S3", "S4")):
        collisions = [p for p in common if stored[a][p]["code"] == stored[b][p]["code"]]
        assert not collisions, f"{a} and {b} produce identical code for {collisions[:5]}"


def test_s3_has_no_opaque_predicates_and_s4_has_no_dead_helpers() -> None:
    """The split is defined by mechanism, so assert the mechanism, not just difference.

    Read from the recorded transform_meta counters rather than by re-parsing: the purity
    gate already verifies these from the code itself (`purity_dead_helper_added`,
    `purity_no_opaque_guard`), so this is the cheap cross-check that the two agree.
    """
    for cond, zero_field in (("S3", "n_predicate_blocks"), ("S4", "n_dead_helpers")):
        recs = _stored(cond, "python")
        if not recs:
            pytest.skip(f"no stored {cond} corpus")
        bad = [p for p, r in recs.items()
               if (r.get("transform_meta") or {}).get(zero_field, 0) != 0]
        assert not bad, f"{cond} should have {zero_field} == 0 but {len(bad)} do not: {bad[:5]}"
