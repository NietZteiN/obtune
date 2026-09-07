"""X2/Y2 (E5) — the second family pair must be exact identities and must not look like H1.

The whole value of this family is that Y2 is an UNSEEN sibling of X2: if either transform
changes a program's output, the transfer number it produces is meaningless, and if either
emits H1 markers the quarantine scan would (correctly) reject the rows.
"""
from __future__ import annotations

import ast
import random

import pytest
import yaml

from obtune.obf.base import Bail, SnippetCtx
from obtune.obf.py.xy2 import (X2_HELPERS, Y2_HELPERS, transform_x2, transform_y2,
                               verify_helpers)

PROGRAMS = [
    # returns + tests + assignments + a loop, i.e. every wrapped position
    "def f(n):\n    t = 0\n    for i in range(n):\n        if i % 2:\n            t += i\n    return t\n",
    # chained comparison: must survive untouched (we never wrap Compare operands)
    "def f(a, b, c):\n    x = 1\n    if a < b < c:\n        x = 2\n    return x\n",
    # short-circuit that would break under eager operand evaluation
    "def f(xs):\n    y = 0\n    if xs and xs[0] > 0:\n        y = xs[0]\n    return y\n",
    # generator function: `return` inside a generator sets StopIteration.value
    "def g(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1\n\ndef f(n):\n    return list(g(n))\n",
    # exception flow of the program's own, which the transform must not swallow
    "def f(d, k):\n    v = None\n    try:\n        v = d[k]\n    except KeyError:\n        v = -1\n    return v\n",
]
ARGS = [(5,), (1, 2, 3), ([3, 1],), (4,), ({"a": 7}, "b")]


def _run(code, args):
    ns: dict = {}
    exec(compile(code, "<t>", "exec"), ns)  # noqa: S102 — fixture source, not user input
    return ns["f"](*args)


def test_helpers_are_identities():
    verify_helpers()


@pytest.mark.parametrize("fn", [transform_x2, transform_y2])
@pytest.mark.parametrize("src,args", list(zip(PROGRAMS, ARGS)))
def test_semantics_preserved(fn, src, args):
    ctx = SnippetCtx(language="python", program_id="t", condition="X2", src=src,
                     entry_point="f", rng=random.Random(17), params={"min_total_sites": 1})
    out = fn(ctx).src_out
    assert _run(out, args) == _run(src, args)


@pytest.mark.parametrize("fn", [transform_x2, transform_y2])
def test_declines_below_the_bar(fn):
    ctx = SnippetCtx(language="python", program_id="t", condition="X2",
                     src="def f():\n    return 1\n", entry_point="f",
                     rng=random.Random(17), params={"min_total_sites": 3})
    with pytest.raises(Bail):
        fn(ctx)


def test_chained_comparison_is_not_wrapped():
    """`a < b < c` short-circuits; wrapping an operand would force `c`'s evaluation."""
    src = "def f(a, b, c):\n    x = 1\n    if a < b < c:\n        x = 2\n    return x\n"
    ctx = SnippetCtx(language="python", program_id="t", condition="X2", src=src,
                     entry_point="f", rng=random.Random(17), params={"min_total_sites": 1})
    tree = ast.parse(transform_x2(ctx).src_out)
    for cmp_node in (n for n in ast.walk(tree) if isinstance(n, ast.Compare)):
        for operand in [cmp_node.left, *cmp_node.comparators]:
            assert not (isinstance(operand, ast.Call) and isinstance(operand.func, ast.Name)
                        and operand.func.id in {"_thru", "_pull"}), "Compare operand was wrapped"


def test_no_h1_markers_emitted():
    """Both banks must pass the same marker scan check_manifest.py runs on training rows."""
    cfg = yaml.safe_load(open("configs/conditions.yaml"))
    pats = None
    for v in cfg.values():
        if isinstance(v, dict) and "h1_marker_patterns" in v:
            pats = v["h1_marker_patterns"]
    if pats is None:
        pats = cfg.get("h1_marker_patterns")
    if not pats:
        pytest.skip("no h1_marker_patterns in conditions.yaml")
    import re
    for bank in (X2_HELPERS, Y2_HELPERS):
        for p in pats:
            assert not re.search(p, bank), f"X2/Y2 helper source matches H1 marker {p!r}"


def test_x2_and_y2_gate_the_same_programs():
    """The comparison is only clean if both siblings accept the same program set."""
    for src, args in zip(PROGRAMS, ARGS):
        outs = []
        for fn in (transform_x2, transform_y2):
            ctx = SnippetCtx(language="python", program_id="t", condition="X2", src=src,
                             entry_point="f", rng=random.Random(17), params={"min_total_sites": 3})
            try:
                fn(ctx)
                outs.append(True)
            except Bail:
                outs.append(False)
        assert outs[0] == outs[1], "X2 and Y2 disagree on acceptance"
