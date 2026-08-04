"""Cross-language condition purity — the invariant RQ1's family contrast rests on.

The transfer matrix compares an identifier family (L1b/L1r/L2) against a structural
family (S1/S2), in two languages. That comparison is only meaningful if a condition
means the same thing on both sides. Two ways it silently stopped meaning the same
thing during development, both caught here:

  * The JS transforms printed with Babel's raw 2-space indentation while L0
    normalization printed 4-space, so every JS identifier variant differed from its
    parent in whitespace as well as identifiers.
  * The per-condition size caps were pure ratios, but structural transforms add a
    roughly fixed amount of code, so short programs were rejected at S1/S2 and the
    structural conditions quietly selected for longer programs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from obtune.corpus.normalize import normalize
from obtune.exec import BatchItem, run_batch
from obtune.obf import builder
from obtune.schema import BaseProgram, InputCase

FIXTURES = Path(__file__).resolve().parent / "fixtures"
IDENTIFIER_CONDITIONS = ["L1b", "L1r", "L2"]
ALL_CONDITIONS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]


def _programs(language: str) -> list[BaseProgram]:
    """L0-normalize, execute to derive gold outputs, and wrap as BaseProgram."""
    rows = [json.loads(line) for line in (FIXTURES / f"programs_{language}.jsonl").read_text().splitlines() if line.strip()]
    normed = [(r, normalize(r["code"], language).code) for r in rows]
    results = run_batch(
        [BatchItem(r["program_id"], language, code, r["entry_point"], [c["args_repr"] for c in r["cases"]])
         for r, code in normed],
        timeout_s=3.0,
    )
    out = []
    for (r, code), res in zip(normed, results):
        assert res.all_ok, f"{r['program_id']} failed after normalization: {[c.status for c in res.cases]}"
        cases = [InputCase(args_repr=c["args_repr"], output_canon=cr.output or "", case_role="seed")
                 for c, cr in zip(r["cases"], res.cases)]
        out.append(BaseProgram(program_id=r["program_id"], language=language, source="fixture",
                               code=code, entry_point=r["entry_point"], cases=cases,
                               gate_inputs=[], loc=len(code.splitlines())))
    return out


@pytest.fixture(scope="module")
def build_python(tmp_path_factory):
    d = tmp_path_factory.mktemp("py")
    return builder.build_variants(_programs("python"), ALL_CONDITIONS, "python", workers=6,
                                  write=False, rejects_root=d / "r", manifests_root=d / "m")


@pytest.fixture(scope="module")
def build_javascript(tmp_path_factory):
    d = tmp_path_factory.mktemp("js")
    return builder.build_variants(_programs("javascript"), ALL_CONDITIONS, "javascript", workers=6,
                                  write=False, rejects_root=d / "r", manifests_root=d / "m")


def _coverage(report) -> dict[str, int]:
    counts: dict[str, int] = {c: 0 for c in ALL_CONDITIONS}
    for v in report.variants:
        counts[v.condition] += 1
    return counts


def test_javascript_every_condition_applies(build_javascript):
    """All six trainable conditions must apply to ordinary JS programs. A whole
    condition reading 0/N means a wiring break, not a corpus property."""
    counts = _coverage(build_javascript)
    n = len({v.program_id for v in build_javascript.variants})
    assert n >= 10
    for cond in ALL_CONDITIONS:
        assert counts[cond] == n, f"{cond} covered {counts[cond]}/{n} JS programs: {counts}"


def test_python_identifier_and_deadcode_conditions_apply(build_python):
    """S1 legitimately declines on functions too short to need a dispatch loop, so it
    is exempt; nothing else may lose a program."""
    counts = _coverage(build_python)
    n = len(_programs("python"))
    for cond in ["L0", "L1b", "L1r", "L2", "S2"]:
        assert counts[cond] == n, f"{cond} covered {counts[cond]}/{n} Python programs: {counts}"
    assert counts["S1"] >= n - 2, f"S1 declined more than the short-function cases: {counts}"


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_identifier_conditions_change_only_identifiers(language, build_python, build_javascript):
    """An identifier condition must be a pure renaming: masking every identifier
    must make the variant textually identical to its L0 parent. If formatting also
    changes, the condition confounds renaming with reformatting."""
    report = build_python if language == "python" else build_javascript
    parents = {v.program_id: v.code for v in report.variants if v.condition == "L0"}
    failures = []
    for v in report.variants:
        if v.condition not in IDENTIFIER_CONDITIONS:
            continue
        parent = parents[v.program_id]
        # rename_map keys are scope-qualified when a name binds in several scopes
        # ("x@top.outer.b"); the part before "@" is the original identifier.
        originals = {k.split("@", 1)[0] for k in v.rename_map}
        names = originals | set(v.rename_map.values()) | {v.entry_point, v.entry_point_parent}
        names = {n for n in names if n}
        pattern = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b")
        if pattern.sub("ID", parent) != pattern.sub("ID", v.code):
            failures.append(f"{language}/{v.condition}/{v.program_id}")
    assert not failures, "identifier conditions altered non-identifier text: " + ", ".join(failures)


@pytest.mark.parametrize("language", ["python", "javascript"])
def test_structural_conditions_do_not_select_for_long_programs(language, build_python, build_javascript):
    """S1/S2 must not systematically decline the shortest programs — that would make
    'structural condition' a proxy for 'longer program' in the RQ1 family contrast."""
    report = build_python if language == "python" else build_javascript
    programs = {p.program_id: len(p.code) for p in _programs(language)}
    for cond in ("S1", "S2"):
        got = {v.program_id for v in report.variants if v.condition == cond}
        missing = set(programs) - got
        if not missing:
            continue
        # Any decline must be a transform-level bail (recorded skipped_constructs),
        # never the size cap — a size-cap loss is length-correlated by construction.
        for pid in missing:
            rec = report.entries[f"{pid}::{cond}"]
            gate = rec.get("gate") or {}
            assert gate.get("checks", {}).get("size_cap") is not False, (
                f"{language}/{cond}/{pid} lost to the size cap "
                f"({programs[pid]} parent chars) — caps must have a fixed floor"
            )


def test_all_variants_are_execution_equivalent(build_python, build_javascript):
    """The gate already enforces this; asserting it here makes a regression in the
    gate itself visible rather than silently widening what counts as a variant."""
    for report in (build_python, build_javascript):
        for v in report.variants:
            checks = (v.gate or {}).get("checks", {})
            assert checks.get("exec_parity", True) is not False, f"{v.program_id}/{v.condition}"
