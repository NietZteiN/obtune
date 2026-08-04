"""Every Python transform must change the source and survive the semantic gate.

The fixtures deliberately span the constructs that break naive obfuscators: recursion,
closures over an enclosing local, comprehensions (inlined in 3.12) next to a generator
expression (still its own scope), shadowing of a module-level name, dict string keys
that look like identifiers, `except ... as`, early returns from inside nested loops,
default arguments, type annotations, and a program whose *output* is a string
containing the names of its own variables — the case that kills regex renaming.

Gold outputs are not hand-written: each fixture's cases are executed through
`exec.pool` once and the canonical outputs recorded, exactly as corpus/inputs.py will
do. That keeps the reference honest (a fixture whose expected output we typed wrong
would otherwise make the gate vacuously pass).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import conditions as load_conditions  # noqa: E402
from obtune.exec.pool import BatchItem, run_batch  # noqa: E402
from obtune.obf.base import make_ctx  # noqa: E402
from obtune.obf.builder import _params_for, build_variants, load_transform  # noqa: E402
from obtune.obf.py.rename import canonical_text  # noqa: E402
from obtune.obf.validate import gate  # noqa: E402
from obtune.schema import BaseProgram, InputCase, Variant  # noqa: E402

CFG = load_conditions()
TRANSFORM_CONDITIONS = ["L1b", "L1r", "L2", "S1", "S2"]

# (program_id, entry_point, source, [args_repr, ...])
FIXTURES: list[tuple[str, str, str, list[str]]] = [
    (
        "fx_recursion",
        "fibfib",
        '''def fibfib(n):
    if n < 3:
        return [0, 0, 1][n]
    return fibfib(n - 1) + fibfib(n - 2) + fibfib(n - 3)
''',
        ["(3,)", "(7,)", "(0,)", "(10,)"],
    ),
    (
        "fx_while_loop",
        "collatz_len",
        '''def collatz_len(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps
''',
        ["(6,)", "(27,)", "(1,)", "(97,)"],
    ),
    (
        "fx_comprehensions",
        "summarize",
        '''def summarize(xs):
    squares = [x * x for x in xs if x % 2 == 0]
    lookup = {k: k * 2 for k in xs}
    gen = (y - 1 for y in squares)
    return [sum(gen), sorted(lookup.values()), squares]
''',
        ["([1, 2, 3, 4],)", "([],)", "([5, 5, 6],)", "([0, 1, 2, 3, 4, 5, 6],)"],
    ),
    (
        "fx_dict_keys",
        "tally",
        '''def tally(words):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    counts["total"] = len(words)
    return counts
''',
        ['(["a", "b", "a"],)', "([],)", '(["total"],)', '(["x", "x", "x", "y"],)'],
    ),
    (
        "fx_self_naming_strings",
        "describe",
        '''def describe(counts):
    label = "counts"
    parts = []
    for name in ["counts", "label", "parts"]:
        parts.append(name + "=" + str(counts))
    return label + ":" + "|".join(parts)
''',
        ["(1,)", "(0,)", "(42,)", "(-3,)"],
    ),
    (
        "fx_nested_function",
        "apply_twice",
        '''def apply_twice(n, bump=1):
    offset = bump * 2

    def inner(v):
        return v + offset

    scale = lambda z: z * 3
    return scale(inner(inner(n)))
''',
        ["(1,)", "(0, 5)", "(-4, 2)", "(10, 0)"],
    ),
    (
        "fx_early_return",
        "first_pair",
        '''def first_pair(grid, target):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == target:
                return [i, j]
            if grid[i][j] < 0:
                break
    return [-1, -1]
''',
        [
            "([[1, 2], [3, 4]], 4)",
            "([[1, 2], [3, 4]], 9)",
            "([[-1, 2], [3, 4]], 2)",
            "([], 1)",
        ],
    ),
    (
        "fx_annotations",
        "weighted",
        '''from typing import List

def weighted(values: List[int], factor: int = 2) -> int:
    total: int = 0
    for v in values:
        total += v * factor
    return total
''',
        ["([1, 2, 3],)", "([], 5)", "([4], 0)", "([-1, 1], 3)"],
    ),
    (
        "fx_shadowing",
        "shadow",
        '''LIMIT = 10

def helper(x):
    LIMIT = 3
    return x + LIMIT

def shadow(n):
    total = helper(n)
    for LIMIT in range(2):
        total += LIMIT
    return total + LIMIT
''',
        ["(1,)", "(0,)", "(-5,)", "(100,)"],
    ),
    (
        "fx_exception",
        "safe_div",
        '''def safe_div(a, b):
    try:
        return a // b
    except ZeroDivisionError as err:
        return str(type(err).__name__)
''',
        ["(6, 3)", "(1, 0)", "(-7, 2)", "(0, 4)"],
    ),
    (
        "fx_string_build",
        "rle",
        '''def rle(s):
    if not s:
        return ""
    out = ""
    run = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            run += 1
        else:
            out += s[i - 1] + str(run)
            run = 1
    out += s[-1] + str(run)
    return out
''',
        ['("aaabbc",)', '("",)', '("z",)', '("abcabc",)'],
    ),
    (
        "fx_max_prime",
        "find_max_prime",
        '''def find_max_prime(numbers):
    best = -1
    for n in numbers:
        if n < 2:
            continue
        prime = True
        d = 2
        while d * d <= n:
            if n % d == 0:
                prime = False
                break
            d += 1
        if prime and n > best:
            best = n
    return best
''',
        ["([3, 4, 5, 6],)", "([1, 0],)", "([97, 91],)", "([2],)"],
    ),
]


def _record_outputs(program_id: str, entry: str, code: str, args: list[str]) -> list[InputCase]:
    """Execute the L0 parent once and keep whatever it canonically produced."""
    res = run_batch(
        [BatchItem(program_id=program_id, language="python", code=code, entry_point=entry, args_reprs=args)],
        timeout_s=5.0,
    )[0]
    assert res.child_status == "ok", f"{program_id}: parent failed to run: {res.stderr[:400]}"
    cases: list[InputCase] = []
    for arg, case in zip(args, res.cases):
        assert case.status in ("ok", "raised"), f"{program_id}: unusable case {arg}: {case}"
        cases.append(
            InputCase(args_repr=arg, output_canon=case.output or "", case_role="seed")
        )
    return cases


@pytest.fixture(scope="module")
def programs() -> dict[str, BaseProgram]:
    out: dict[str, BaseProgram] = {}
    for pid, entry, code, args in FIXTURES:
        cases = _record_outputs(pid, entry, code, args)
        out[pid] = BaseProgram(
            program_id=pid,
            language="python",
            source="fixture",
            code=code,
            entry_point=entry,
            cases=cases[:2],
            gate_inputs=cases[2:],
            loc=code.count("\n"),
        )
    return out


def _run_transform(program: BaseProgram, condition: str):
    spec = CFG["conditions"][condition]
    fn = load_transform("python", condition)
    assert fn is not None, f"no transform registered for {condition}"
    ctx = make_ctx(
        "python", program.program_id, condition, program.code, program.entry_point,
        params=_params_for(spec),
    )
    return fn(ctx)


@pytest.mark.parametrize("condition", TRANSFORM_CONDITIONS)
@pytest.mark.parametrize("pid", [f[0] for f in FIXTURES])
def test_transform_changes_source_and_passes_gate(programs, pid, condition):
    program = programs[pid]
    result = _run_transform(program, condition)
    if not result.applied:
        # Declining is legal (S1 bails on `try`), but only for the structural family,
        # and it must say why.
        assert CFG["conditions"][condition]["family"] == "structural", (
            f"{pid}/{condition}: identifier transforms must always apply"
        )
        assert result.skipped_constructs, f"{pid}/{condition}: declined without a reason"
        return

    assert result.src_out != program.code, f"{pid}/{condition}: output identical to input"

    variant = Variant(
        program_id=pid,
        condition=condition,
        language="python",
        code=result.src_out,
        entry_point=result.entry_point_out or program.entry_point,
        entry_point_parent=program.entry_point,
        rename_map=dict(result.rename_map),
    )
    verdict = gate(program, variant, CFG)
    assert verdict.ok, (
        f"{pid}/{condition} failed the gate: "
        f"{[k for k, v in verdict.checks.items() if not v]} {verdict.mismatch_details}\n"
        f"{result.src_out}"
    )


@pytest.mark.parametrize("pid", [f[0] for f in FIXTURES])
def test_l1_conditions_rename_the_entry_point(programs, pid):
    program = programs[pid]
    for condition in ("L1b", "L1r", "L2"):
        result = _run_transform(program, condition)
        assert result.applied
        assert result.entry_point_out and result.entry_point_out != program.entry_point
        assert program.entry_point in result.rename_map


def test_l1r_names_are_hex():
    program_id, entry, code, _ = FIXTURES[0]
    result = _run_transform(
        BaseProgram(
            program_id=program_id, language="python", source="fixture", code=code,
            entry_point=entry, cases=[InputCase(args_repr="(3,)", output_canon="1")],
        ),
        "L1r",
    )
    assert result.applied
    for new in result.rename_map.values():
        assert re.fullmatch(r"[vf]_[0-9a-f]{4}", new), new


def test_l1b_records_misdirection_strength(programs):
    result = _run_transform(programs["fx_max_prime"], "L1b")
    assert result.applied
    strengths = result.extra["misdirection_strength"]
    # The entry name carries an invertible concept, so it must get the strongest kind.
    assert result.extra["entry_misdirection_strength"] == 3
    assert strengths["find_max_prime"] == 3
    assert result.entry_point_out != "find_max_prime"
    assert result.extra["mean_misdirection_strength"] > 0


def test_s1_produces_a_dispatch_loop(programs):
    result = _run_transform(programs["fx_while_loop"], "S1")
    assert result.applied
    assert result.extra["n_states"] >= 3
    assert re.search(r"while _st_[0-9a-f]{4} != -1:", result.src_out), result.src_out
    assert "raise RuntimeError" in result.src_out


def test_s1_declines_on_try_except(programs):
    result = _run_transform(programs["fx_exception"], "S1")
    assert not result.applied
    assert "try" in result.skipped_constructs


def test_s2_adds_dead_helpers_and_predicates(programs):
    result = _run_transform(programs["fx_while_loop"], "S2")
    assert result.applied
    assert result.extra["n_predicate_blocks"] >= 1
    assert result.extra["n_dead_helpers"] >= 1
    assert result.src_out.count("\n") > programs["fx_while_loop"].code.count("\n")


# --------------------------------------------------------------------------- #
# L2 as the alpha-equivalence canonicalizer (corpus/dedup.py contract)

ALPHA_A = '''def total_sum(values, start=0):
    acc = start
    for item in values:
        acc += item
    return acc
'''
ALPHA_B = '''def add_everything(numbers, seed=0):
    running = seed
    for element in numbers:
        running += element
    return running
'''
ALPHA_C_DIFFERENT_FORMATTING = '''def add_everything(numbers,seed=0):
    running=seed
    for element in numbers:
        running+=element
    return running
'''
ALPHA_D_DIFFERENT_STRUCTURE = '''def add_everything(numbers, seed=0):
    running = seed
    for element in numbers:
        running -= element
    return running
'''


def _l2_text(code: str, entry: str) -> str:
    ctx = make_ctx("python", "alpha", "L2", code, entry, params=_params_for(CFG["conditions"]["L2"]))
    result = load_transform("python", "L2")(ctx)
    assert result.applied
    return result.src_out


def test_l2_maps_alpha_equivalent_programs_to_identical_text():
    a = _l2_text(ALPHA_A, "total_sum")
    b = _l2_text(ALPHA_B, "add_everything")
    assert a == b, f"L2 is not a canonicalizer:\n{a}\n---\n{b}"


def test_canonical_text_absorbs_formatting_differences():
    assert canonical_text(ALPHA_B) == canonical_text(ALPHA_C_DIFFERENT_FORMATTING)
    assert canonical_text(ALPHA_A) == canonical_text(ALPHA_B)


def test_canonical_text_separates_different_programs():
    assert canonical_text(ALPHA_B) != canonical_text(ALPHA_D_DIFFERENT_STRUCTURE)


def test_l2_strips_annotations(programs):
    result = _run_transform(programs["fx_annotations"], "L2")
    assert result.applied
    assert "-> int" not in result.src_out
    assert "List[int]" not in result.src_out


# --------------------------------------------------------------------------- #
# Quarantine: the H1-marker scan must reject a planted marker


def _poison(program: BaseProgram, marker: str):
    """An otherwise-valid L1r variant with `marker` planted as a trailing comment.

    The marker has to ride along without changing the line count or the runtime
    behaviour, or an earlier gate check would short-circuit and the H1 scan would never
    be exercised — which is precisely the bug this test exists to rule out.
    """
    result = _run_transform(program, "L1r")
    assert result.applied
    poisoned = result.src_out.rstrip("\n") + f"  # {marker}\n"
    assert marker in poisoned
    return result, Variant(
        program_id=program.program_id, condition="L1r", language="python", code=poisoned,
        entry_point=result.entry_point_out, entry_point_parent=program.entry_point,
        rename_map=dict(result.rename_map),
    )


def test_gate_rejects_planted_h1_marker(programs):
    """A trainable-condition variant carrying an H1 marker must never pass the gate.

    This is quarantine layer 4 acting *before* the corpus is written; without it a
    string-array or MBA feature could enter a trainable condition and quietly destroy
    the held-out claim.
    """
    program = programs["fx_while_loop"]
    _, variant = _poison(program, "_0xdeadbeef")
    verdict = gate(program, variant, CFG)
    assert not verdict.ok
    assert verdict.checks.get("h1_markers_absent") is False
    assert any("_0x" in d for d in verdict.mismatch_details)


def test_clean_variant_passes_the_same_path(programs):
    """Control for the poisoning test: the un-poisoned variant must pass."""
    program = programs["fx_while_loop"]
    result = _run_transform(program, "L1r")
    variant = Variant(
        program_id=program.program_id, condition="L1r", language="python", code=result.src_out,
        entry_point=result.entry_point_out, entry_point_parent=program.entry_point,
        rename_map=dict(result.rename_map),
    )
    assert gate(program, variant, CFG).ok


@pytest.mark.parametrize(
    "marker",
    ["atob(", "atob (", "fromCharCode", "b64decode", "base64", "_0xabcd", "__mba_",
     "_mba_add", "_mba_xor", "stringArray", "rc4"],
)
def test_every_h1_pattern_is_detected(programs, marker):
    program = programs["fx_while_loop"]
    _, variant = _poison(program, marker)
    verdict = gate(program, variant, CFG)
    assert not verdict.ok
    assert verdict.checks.get("h1_markers_absent") is False, verdict.checks


# --------------------------------------------------------------------------- #
# Gate negatives: a transform that changes behaviour must be caught


def test_gate_catches_a_semantics_breaking_variant(programs):
    program = programs["fx_while_loop"]
    broken = program.code.replace("steps += 1", "steps += 2")
    variant = Variant(
        program_id=program.program_id, condition="S2", language="python", code=broken + "\n_x = 1\n",
        entry_point=program.entry_point, entry_point_parent=program.entry_point,
    )
    verdict = gate(program, variant, CFG)
    assert not verdict.ok
    assert verdict.checks.get("exec_parity") is False


def test_gate_accepts_l0_identity(programs):
    program = programs["fx_recursion"]
    variant = Variant(
        program_id=program.program_id, condition="L0", language="python", code=program.code,
        entry_point=program.entry_point, entry_point_parent=program.entry_point,
    )
    verdict = gate(program, variant, CFG)
    assert verdict.ok, verdict.mismatch_details


# --------------------------------------------------------------------------- #
# Builder end-to-end


def test_builder_end_to_end(programs, tmp_path):
    report = build_variants(
        list(programs.values()),
        ["L0"] + TRANSFORM_CONDITIONS,
        "python",
        workers=4,
        cfg=CFG,
        rejects_root=tmp_path / "rejects",
        manifests_root=tmp_path / "manifests",
    )
    summary = report.summary()
    assert summary["L0"]["ok"] == len(FIXTURES)
    for cond in ("L1b", "L1r", "L2"):
        assert summary[cond]["ok"] == len(FIXTURES), (cond, summary[cond], report.rejects[:1])
    # S1 legitimately declines on the try/except fixture; nothing may hard-fail.
    for cond in TRANSFORM_CONDITIONS:
        assert summary[cond]["failed"] == 0, (cond, summary[cond], report.rejects[:2])
        assert summary[cond]["ok"] >= len(FIXTURES) - 2, (cond, summary[cond])

    manifest_path = tmp_path / "manifests" / "coverage_matrix.json"
    assert manifest_path.exists()
    assert report.manifest["summary"] == summary
    assert set(report.manifest["common_subset"]) <= {p[0] for p in FIXTURES}

    # Every emitted variant must be reproducible from its recorded seed.
    for variant in report.variants:
        if variant.condition == "L0":
            continue
        spec = CFG["conditions"][variant.condition]
        ctx = make_ctx(
            "python", variant.program_id, variant.condition,
            programs[variant.program_id].code, variant.entry_point_parent,
            attempt=variant.transform_meta["attempt"],
            seed=variant.transform_meta["seed"],
            params=_params_for(spec),
        )
        again = load_transform("python", variant.condition)(ctx)
        assert again.src_out == variant.code, f"{variant.program_id}/{variant.condition} not reproducible"
