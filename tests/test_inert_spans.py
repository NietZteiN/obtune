"""`normalize.inert` + the `inert` profile + the emitter's round-trip guard.

The span analysis underwrites two things that must agree: the `dse` normalization pass (which
DELETES the spans) and the attention-steering intervention (which leaves them in place and stops
the model attending to them). If it marked live code, the first would silently corrupt programs
and the second would suppress attention to material the answer depends on.
"""
import ast

import pytest

from obtune.normalize import normalize
from obtune.normalize.inert import inert_spans
from obtune.normalize.py_norm import UnparseUnfaithful, _emit


def marked(src, entry="solve"):
    return [src[a:b] for a, b in inert_spans(src, entry)]


# --------------------------------------------------------------------------- #
# what it must catch

def test_unreachable_helper():
    src = "def helper(x):\n    return x\n\ndef solve(n):\n    return n + 1\n"
    assert any("def helper" in m for m in marked(src))


def test_statically_false_branch():
    src = "def solve(n):\n    if 1 == 2:\n        n = 99\n    return n\n"
    assert any("n = 99" in m for m in marked(src))


def test_computed_opaque_predicate_with_inert_arms():
    """S4's mechanism: the guard is undecidable, but NEITHER arm does anything."""
    src = ("def solve(n):\n"
           "    off = 160\n"
           "    if (off * off + off) % 2 == 0:\n"
           "        scratch = 0\n"
           "        scratch += 2\n"
           "    else:\n"
           "        other = 'a' + 'b'\n"
           "    return n\n")
    assert any("scratch" in m or "if (off" in m for m in marked(src))


def test_dead_store():
    src = "def solve(n):\n    unused = n * 3\n    return n\n"
    assert any("unused" in m for m in marked(src))


# --------------------------------------------------------------------------- #
# what it must NOT catch — a false positive here corrupts a program

def test_live_store_is_never_marked():
    src = "def solve(n):\n    t = n * 3\n    return t\n"
    assert marked(src) == []


def test_store_read_only_later_is_live():
    src = "def solve(n):\n    t = 0\n    for i in range(n):\n        t += i\n    return t\n"
    assert marked(src) == []


def test_impure_rhs_is_never_marked():
    """`unused` is never read, but computing it can raise — so the store is observable."""
    src = "def solve(n):\n    unused = n[5]\n    return 1\n"
    assert marked(src) == []


def test_call_with_side_effects_is_never_marked():
    src = "def solve(n):\n    unused = print(n)\n    return 1\n"
    assert marked(src) == []


def test_reflection_blocks_helper_removal():
    src = ("def helper(x):\n    return x\n\n"
           "def solve(n):\n    return eval('helper')(n)\n")
    assert not any("def helper" in m for m in marked(src))


def test_syntax_error_returns_empty_not_raise():
    assert inert_spans("def solve(:\n", "solve") == []


# --------------------------------------------------------------------------- #
# the emitter guard

def test_emit_rejects_the_pow_precedence_bug():
    """`(-1) ** r` folded to `Constant(-1)` unparses to `-1 ** r`, which means `-(1 ** r)`."""
    tree = ast.parse("c = (-1) ** r")
    tree.body[0].value.left = ast.Constant(-1)
    with pytest.raises(UnparseUnfaithful):
        _emit(tree)


def test_emit_allows_folded_negative_literals():
    """The guard must not fire on `Constant(-1)` in an ordinary position (78/200 did)."""
    tree = ast.parse("c = x[-1]")
    assert "x[-1]" in _emit(tree)


def test_normalize_reverts_rather_than_corrupting():
    """A program the guard rejects comes back untouched, never half-normalized."""
    src = "import math\ndef solve(n):\n    return (-1) ** n * 2\n"
    out = normalize(src, "python", entry_point="solve", profile="structural")
    assert eval_same(src, out.code)


def eval_same(a, b):
    ns_a, ns_b = {}, {}
    exec(compile(a, "<a>", "exec"), ns_a)
    exec(compile(b, "<b>", "exec"), ns_b)
    return all(ns_a["solve"](i) == ns_b["solve"](i) for i in range(6))


# --------------------------------------------------------------------------- #
# the profile

def test_inert_profile_is_separate_from_structural():
    """`structural` is a published arm; strengthening it in place would invalidate its cells."""
    from obtune.normalize.py_norm import PROFILES
    assert PROFILES["structural"] == ("fold", "dce", "reformat")
    assert "dse" in PROFILES["inert"]


def test_inert_removes_what_structural_cannot():
    src = ("def solve(n):\n"
           "    off = 160\n"
           "    if (off * off + off) % 2 == 0:\n"
           "        scratch = 0\n"
           "    return n\n")
    st = normalize(src, "python", entry_point="solve", profile="structural").code
    ie = normalize(src, "python", entry_point="solve", profile="inert").code
    assert "scratch" in st and "scratch" not in ie
    assert eval_same(src, ie)
