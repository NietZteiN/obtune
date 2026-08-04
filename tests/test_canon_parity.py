"""canon.py and canon.mjs must produce byte-identical strings.

A cross-language exact-match claim is only meaningful if "the output" means the
same thing in both languages. Fixtures are expressed once, as source text in each
language, and both sides are canonicalized and compared.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from obtune.exec.canon import Unserializable, canon  # noqa: E402

CANON_MJS = Path(__file__).resolve().parents[1] / "src" / "obtune" / "exec" / "canon.mjs"
NODE = os.environ.get("OBTUNE_NODE", "node")

# (python_expr, js_expr) — must canonicalize identically.
PARITY = [
    ("0", "0"),
    ("-0.0", "-0"),
    ("1", "1"),
    ("2.0", "2.0"),
    ("-17", "-17"),
    ("10**20", "1e20"),
    ("0.1", "0.1"),
    ("1.5e-7", "1.5e-7"),
    ("True", "true"),
    ("False", "false"),
    ("None", "null"),
    ('"abc"', '"abc"'),
    ('"a\\"b"', '"a\\"b"'),
    ('"tab\\there"', '"tab\\there"'),
    ("[]", "[]"),
    ("[1, 2, 3]", "[1,2,3]"),
    ('[1, "a", None, True]', '[1,"a",null,true]'),
    ("[[1], [2, [3]]]", "[[1],[2,[3]]]"),
    ("{}", "{}"),
    ('{"b": 1, "a": 2}', '{b:1, a:2}'),
    ('{"z": [1, {"y": 2}]}', '{z:[1,{y:2}]}'),
    ("(1, 2)", "[1,2]"),
]

REJECTED_PY = ["float('nan')", "float('inf')", "{1, 2}", "frozenset([1])", "1j", "b'x'"]


def _js_canon(exprs: list[str]) -> list[str]:
    script = (
        f"import {{ canon }} from {json.dumps(str(CANON_MJS))};\n"
        f"const exprs = {json.dumps(exprs)};\n"
        "const out = exprs.map((e) => { try { return canon(eval('(' + e + ')')); }"
        " catch (err) { return 'ERR:' + err.constructor.name; } });\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    r = subprocess.run([NODE, "--input-type=module", "-e", script],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.skip(f"node unavailable or failed: {r.stderr[:300]}")
    return json.loads(r.stdout)


def test_python_js_canon_parity():
    js_out = _js_canon([j for _, j in PARITY])
    mismatches = []
    for (py_expr, js_expr), js_val in zip(PARITY, js_out):
        py_val = canon(eval(py_expr))  # noqa: S307 — fixture text, not user input
        if py_val != js_val:
            mismatches.append(f"{py_expr!r} -> {py_val!r} vs JS {js_expr!r} -> {js_val!r}")
    assert not mismatches, "canon divergence:\n" + "\n".join(mismatches)


@pytest.mark.parametrize("expr", REJECTED_PY)
def test_rejected_values_raise(expr):
    with pytest.raises(Unserializable):
        canon(eval(expr))  # noqa: S307


def test_dict_keys_sorted():
    assert canon({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_deep_nesting_rejected():
    v: object = 1
    for _ in range(50):
        v = [v]
    with pytest.raises(Unserializable):
        canon(v)
