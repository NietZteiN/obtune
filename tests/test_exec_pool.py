"""The sandboxed executor is the ground truth for every gold label in the project.

If it mislabels a hung program as a crash, or lets a program's exception message
leak into the comparison, the semantic gate stops being a gate. These tests pin
the status taxonomy and the isolation guarantees in both languages.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from obtune.exec import BatchItem, CaseResult, run_batch, run_one

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _fixture_items(name: str) -> list[BatchItem]:
    rows = [json.loads(line) for line in (FIXTURES / name).read_text().splitlines() if line.strip()]
    return [
        BatchItem(r["program_id"], r["language"], r["code"], r["entry_point"],
                  [c["args_repr"] for c in r["cases"]])
        for r in rows
    ]


@pytest.mark.parametrize("fixture", ["programs_python.jsonl", "programs_javascript.jsonl"])
def test_all_fixtures_execute_cleanly(fixture):
    results = run_batch(_fixture_items(fixture), timeout_s=3.0, workers=8)
    failures = [(r.program_id, [c.status for c in r.cases]) for r in results if not r.all_ok]
    assert not failures, f"fixtures must all execute: {failures}"


def test_parallel_fixtures_agree_across_languages():
    """The Python and JavaScript fixture sets implement the same functions. Their
    canonical outputs must be byte-identical — this is the cross-language claim in
    miniature, tested on real programs rather than scalar values."""
    py = {r.program_id: r for r in run_batch(_fixture_items("programs_python.jsonl"), timeout_s=3.0)}
    js = {r.program_id: r for r in run_batch(_fixture_items("programs_javascript.jsonl"), timeout_s=3.0)}
    pairs = [
        ("fx_py_recursion", "fx_js_recursion"),
        ("fx_py_loop_accum", "fx_js_loop_accum"),
        ("fx_py_while_early_return", "fx_js_while_early_return"),
        ("fx_py_dict_build", "fx_js_object_build"),
        ("fx_py_string_ops", "fx_js_string_ops"),
        ("fx_py_nested_def", "fx_js_nested_fn"),
        ("fx_py_nested_loops", "fx_js_nested_loops"),
        ("fx_py_break_continue", "fx_js_break_continue"),
    ]
    mismatches = []
    for p, j in pairs:
        pouts = [c.output for c in py[p].cases]
        jouts = [c.output for c in js[j].cases]
        if pouts != jouts:
            mismatches.append(f"{p} {pouts} != {j} {jouts}")
    assert not mismatches, "cross-language output divergence:\n" + "\n".join(mismatches)


def test_exception_is_recorded_by_type_only():
    """Obfuscation legitimately rewrites exception messages, line numbers and
    tracebacks. Only the type may enter the comparison, or every renamed variant
    would fail the gate."""
    r = run_one(BatchItem("boom", "python",
                          "def f(x):\n    raise ValueError('the message mentions x=%r' % x)\n",
                          "f", ["(1,)", "(2,)"]), timeout_s=2.0)
    assert [c.status for c in r.cases] == ["raised", "raised"]
    assert [c.exc_type for c in r.cases] == ["ValueError", "ValueError"]
    # The two calls raise different *messages* but must compare equal.
    assert r.cases[0].matches(r.cases[1])


def test_different_exception_types_do_not_match():
    a = CaseResult(status="raised", exc_type="ValueError")
    b = CaseResult(status="raised", exc_type="TypeError")
    assert not a.matches(b)


@pytest.mark.parametrize(
    "language,code,entry",
    [
        ("python", "def f():\n    while True:\n        pass\n", "f"),
        ("javascript", "function f(){ while(true){} }", "f"),
    ],
)
def test_hung_program_is_a_timeout_not_a_crash(language, code, entry):
    """`crash` must mean our harness broke; `timeout` means the program was
    unsuitable. Conflating them would hide harness defects behind expected attrition."""
    r = run_one(BatchItem("hang", language, code, entry, ["()"]), timeout_s=1.5)
    statuses = {r.child_status, *(c.status for c in r.cases)}
    assert "timeout" in statuses, f"expected a timeout, got {statuses}"
    assert "crash" not in {c.status for c in r.cases}


@pytest.mark.parametrize(
    "language,code,entry",
    [
        ("python", "def f():\n    return {1, 2}\n", "f"),
        ("javascript", "function f(){ return new Set([1,2]); }", "f"),
    ],
)
def test_unstable_output_types_are_rejected(language, code, entry):
    """Set iteration order is not stable across processes, so a program returning
    one cannot have a reproducible gold label."""
    r = run_one(BatchItem("unstable", language, code, entry, ["()"]), timeout_s=2.0)
    assert r.cases[0].status == "unserializable"


def test_program_cannot_read_the_filesystem():
    """A file read makes the gold label depend on the machine rather than the program.
    The static corpus filter is the primary defense; this asserts the executor does
    not hand back a plausible-looking label when something slips past it."""
    r = run_one(BatchItem("io", "python",
                          "def f():\n    return open('/etc/passwd').read()[:5]\n",
                          "f", ["()"]), timeout_s=2.0)
    assert r.cases[0].status == "raised"
    assert r.cases[0].exc_type == "NameError"


def test_ordinary_imports_still_work():
    """Blocking builtins must not break the many corpus programs that import math,
    itertools or collections."""
    code = ("import math\nfrom collections import Counter\n\n\n"
            "def f(xs):\n    return [math.floor(math.sqrt(9)), Counter(xs).most_common(1)[0][0]]\n")
    r = run_one(BatchItem("imp", "python", code, "f", ["([1, 1, 2],)"]), timeout_s=2.0)
    assert r.cases[0].status == "ok", r.cases[0]
    assert r.cases[0].output == "[3,1]"


def test_javascript_program_cannot_require_modules():
    r = run_one(BatchItem("req", "javascript",
                          "function f(){ return require('fs').readFileSync('/etc/passwd','utf8'); }",
                          "f", ["()"]), timeout_s=2.0)
    assert r.cases[0].status != "ok"


def test_compile_error_is_reported_per_case_not_swallowed():
    r = run_one(BatchItem("bad", "python", "def f(:\n  pass\n", "f", ["()", "()"]), timeout_s=2.0)
    assert len(r.cases) == 2
    assert all(c.status == "error" for c in r.cases)


def test_hash_seed_is_honored():
    """The determinism filter relies on being able to vary PYTHONHASHSEED; if the
    executor ignored it, hash-order-dependent programs would slip through."""
    code = "import os\n\n\ndef f():\n    return os.environ.get('PYTHONHASHSEED')\n"
    a = run_one(BatchItem("h", "python", code, "f", ["()"]), timeout_s=2.0, hash_seed=1)
    b = run_one(BatchItem("h", "python", code, "f", ["()"]), timeout_s=2.0, hash_seed=2)
    assert a.cases[0].output == '"1"'
    assert b.cases[0].output == '"2"'
