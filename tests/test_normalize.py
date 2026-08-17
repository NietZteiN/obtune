"""Symbolic-normalization baseline — the soundness properties it rests on.

The baseline's whole claim is "this rewrite preserves behaviour and makes the program
easier to read". If a pass ever changes what a program computes, the arm is measuring a
DIFFERENT program and its accuracy number is meaningless — worse than absent, because it
would look like evidence. So most of what follows is refusal tests: constructs the
normalizer must decline to touch.
"""
from __future__ import annotations

import ast

import pytest

from obtune.normalize import PROFILES, normalize, normalize_python


def _run(src: str, entry: str, *args):
    """Execute `entry(*args)` in a fresh namespace and return its result."""
    ns: dict = {}
    exec(compile(src, "<t>", "exec"), ns)  # noqa: S102
    return ns[entry](*args)


# --------------------------------------------------------------------------- #
# the property that matters most: behaviour is preserved


PROGRAMS = [
    # (source, entry, args)
    ("def f(a, b):\n    return a + b\n", "f", (1, 2)),
    ("def f(xs):\n    t = 0\n    for v in xs:\n        t += v\n    return t\n", "f", ([1, 2, 3],)),
    ("def helper(x):\n    return x * 2\n\ndef f(a):\n    return helper(a) + 1\n", "f", (5,)),
    # a loop variable that is REASSIGNED inside the body — renaming must stay consistent
    ("def f(n):\n    i = 0\n    for i in range(n):\n        i = i + 1\n    return i\n", "f", (3,)),
    # comprehension scoping (PEP 709 inlines these into the enclosing scope)
    ("def f(n):\n    return [q * q for q in range(n)]\n", "f", (4,)),
    # nonlocal / closure
    ("def f(n):\n    c = 0\n    def bump():\n        nonlocal c\n        c += 1\n    for _ in range(n):\n        bump()\n    return c\n", "f", (3,)),
    # a string whose CONTENT looks like an identifier we might rename
    ("def f(a):\n    name = 'a'\n    return name + str(a)\n", "f", (7,)),
    # dead code + constant arithmetic together
    ("def dead(z):\n    return z\n\ndef f(a):\n    if False:\n        a = 0\n    k = (2 ** 4) - 6\n    return a + k\n", "f", (10,)),
    # exception type must survive
    ("def f(a):\n    if a < 0:\n        raise ValueError('neg')\n    return a\n", "f", (5,)),
    # kwargs and defaults
    ("def f(a, b=3, *rest, **kw):\n    return a + b + len(rest) + len(kw)\n", "f", (1,)),
]


@pytest.mark.parametrize("profile", sorted(PROFILES))
@pytest.mark.parametrize("src,entry,args", PROGRAMS, ids=lambda v: None)
def test_normalization_preserves_behaviour(profile, src, entry, args) -> None:
    out = normalize(src, "python", entry_point=entry, profile=profile)
    assert _run(out.code, entry, *args) == _run(src, entry, *args), (
        f"profile {profile} changed the program's output:\n{out.code}")


@pytest.mark.parametrize("profile", sorted(PROFILES))
@pytest.mark.parametrize("src,entry,args", PROGRAMS, ids=lambda v: None)
def test_entry_point_survives(profile, src, entry, args) -> None:
    """The harness calls the program BY NAME. Renaming the entry point would turn every
    item into an AttributeError and the arm would score a flat zero for a plumbing reason."""
    out = normalize(src, "python", entry_point=entry, profile=profile)
    assert entry in {n.name for n in ast.walk(ast.parse(out.code))
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


# --------------------------------------------------------------------------- #
# alpha


def test_alpha_canonicalizes_hex_and_adversarial_names_to_the_same_form() -> None:
    """The mechanism the L1b/L1r arms are supposed to test. Two programs differing ONLY in
    their identifiers must normalize to identical text — otherwise `alpha` is not a
    canonicalizer and the baseline has no reason to help on renaming conditions."""
    a = "def f(v_a3f2, v_9c01):\n    t_ff = v_a3f2 + v_9c01\n    return t_ff\n"
    b = "def f(customerCount, isValid):\n    totalPrice = customerCount + isValid\n    return totalPrice\n"
    na = normalize(a, "python", entry_point="f", profile="alpha").code
    nb = normalize(b, "python", entry_point="f", profile="alpha").code
    assert na == nb


def test_alpha_preserves_formatting() -> None:
    """`alpha` edits source spans; it must NOT re-emit. Otherwise it silently carries the
    `reformat` treatment and the two arms stop being separable."""
    src = "def f(aaa):\n\n    # a comment\n    return (aaa)\n"
    out = normalize(src, "python", entry_point="f", profile="alpha").code
    assert "# a comment" in out
    assert "(a)" in out or "( a )" in out


def test_alpha_does_not_rename_inside_string_literals() -> None:
    src = "def f(alpha):\n    return 'alpha' + str(alpha)\n"
    out = normalize(src, "python", entry_point="f", profile="alpha").code
    assert "'alpha'" in out


# --------------------------------------------------------------------------- #
# fold — refusals


def test_fold_evaluates_pure_literal_arithmetic() -> None:
    out = normalize_python("def f():\n    return (2 ** 3) + (10 - 4)\n",
                           entry_point="f", passes=("fold", "reformat"))
    assert "14" in out.code


def test_fold_refuses_names() -> None:
    """A `Name` could be anything. Folding across one is how a constant folder breaks."""
    src = "def f(a):\n    return a + 1\n"
    out = normalize_python(src, entry_point="f", passes=("fold",))
    assert "fold" not in out.applied


def test_fold_refuses_unknown_calls() -> None:
    src = "def f():\n    return open('/etc/passwd').read()\n"
    out = normalize_python(src, entry_point="f", passes=("fold",))
    assert "fold" not in out.applied
    assert "open" in out.code


def test_fold_refuses_a_giant_power() -> None:
    """`9 ** 9 ** 9` is a foldable expression and a denial of service.

    `**` is right-associative, so the inner `9 ** 9` folds to 387420489 — small, correct,
    and fine. What must NOT happen is the outer fold: the exponent cap refuses it, leaving
    `9 ** 387420489` symbolic. The test is that the enormous value is never MATERIALIZED,
    not that no fold occurred at all.
    """
    src = "def f():\n    return 9 ** 9 ** 9\n"
    out = normalize_python(src, entry_point="f", passes=("fold", "reformat"))
    assert "9 ** 387420489" in out.code, out.code
    assert max((len(t) for t in out.code.split() if t.isdigit()), default=0) < 100


def test_fold_growth_is_bounded_by_the_operand_caps() -> None:
    """The chain that would defeat a naive exponent cap: fold, then use the RESULT as the
    next base. `_const_ok`'s digit cap is what terminates it."""
    src = "def f():\n    return ((10 ** 16) ** 16) ** 16\n"
    out = normalize_python(src, entry_point="f", passes=("fold", "reformat"))
    assert max((len(t) for t in out.code.split() if t.isdigit()), default=0) <= 300, out.code


def test_fold_declines_values_that_do_not_round_trip() -> None:
    """nan is foldable and its repr does not evaluate back to itself."""
    src = "def f():\n    return float('nan')\n"
    out = normalize_python(src, entry_point="f", passes=("fold",))
    assert "nan" in out.code


def test_fold_handles_a_chr_chain() -> None:
    """Generic constant folding, NOT a rewrite tuned against any particular obfuscator —
    see the module docstring on why tuning against H1 would breach CLAUDE.md §3.2."""
    src = "def f():\n    return chr(72) + chr(105)\n"
    out = normalize_python(src, entry_point="f", passes=("fold", "reformat"))
    assert "'Hi'" in out.code


# --------------------------------------------------------------------------- #
# dce — refusals


def test_dce_removes_an_unreferenced_helper() -> None:
    src = "def dead(x):\n    return x\n\ndef f(a):\n    return a\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "dead" not in out.code


def test_dce_keeps_a_referenced_helper() -> None:
    src = "def used(x):\n    return x\n\ndef f(a):\n    return used(a)\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "used" in out.code


def test_dce_never_removes_the_entry_point_even_if_unreferenced() -> None:
    src = "def f(a):\n    return a\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "def f" in out.code


def test_dce_refuses_when_the_module_uses_reflection() -> None:
    """`globals()['dead']` reaches a definition without naming it. One such call anywhere
    makes the whole unused-helper analysis unsound, so the pass declines outright."""
    src = "def dead(x):\n    return x\n\ndef f(a):\n    return globals()['dead'](a)\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "dead" in out.code


def test_dce_keeps_a_helper_named_only_in_a_string() -> None:
    """Over-broad on purpose: a false 'unused' is a semantic change, a false 'used' only
    costs coverage."""
    src = "def dead(x):\n    return x\n\ndef f(a):\n    return getattr(None, 'dead', a)\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "dead" in out.code


def test_dce_keeps_a_statically_true_while_loop() -> None:
    """`while True:` terminates via break/return. It is not dead code."""
    src = "def f(n):\n    i = 0\n    while True:\n        i += 1\n        if i >= n:\n            return i\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert _run(out.code, "f", 4) == 4


def test_dce_preserves_the_else_of_a_never_entered_while() -> None:
    """`while False: ... else: X` RUNS X. Dropping the else changes the answer."""
    src = "def f():\n    while False:\n        pass\n    else:\n        return 7\n    return 0\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert _run(out.code, "f") == 7


def test_dce_keeps_a_class_body() -> None:
    """Class bodies execute at module level; an 'unreferenced' class may still have had
    side effects, so removing one is not dead-code elimination."""
    src = "class C:\n    x = 1\n\ndef f(a):\n    return a\n"
    out = normalize_python(src, entry_point="f", passes=("dce", "reformat"))
    assert "class C" in out.code


# --------------------------------------------------------------------------- #
# driver contracts


def test_a_syntax_error_yields_the_original_untouched() -> None:
    src = "def f(:\n"
    out = normalize(src, "python", entry_point="f", profile="full")
    assert out.code == src and not out.applied


def test_javascript_passes_through() -> None:
    src = "function f(a) { return a; }"
    out = normalize(src, "javascript", entry_point="f", profile="full")
    assert out.code == src and not out.applied


def test_unknown_profile_and_pass_are_rejected_loudly() -> None:
    with pytest.raises(ValueError):
        normalize("def f(): pass", "python", profile="nope")
    with pytest.raises(ValueError):
        normalize_python("def f(): pass", passes=("nope",))


def test_normalization_is_deterministic() -> None:
    src = "def f(zzz, yyy):\n    return zzz + yyy\n"
    outs = {normalize(src, "python", entry_point="f", profile="full").code for _ in range(5)}
    assert len(outs) == 1


def test_conditions_are_unaffected_by_the_preserve_hook() -> None:
    """`preserve` was added to `rename` for this baseline. The L1r/L2/L1b CONDITIONS pass
    it empty, and their output must be byte-identical to before — a change there would
    silently invalidate every adapter trained on those variants."""
    import random as _r

    from obtune.obf.base import SnippetCtx
    from obtune.obf.py.rename import rename

    src = "def solve(alpha, beta):\n    gamma = alpha + beta\n    return gamma\n"
    mk = lambda: SnippetCtx(language="python", program_id="p", condition="L2", src=src,
                            entry_point="solve", rng=_r.Random(0))
    assert rename(mk(), "seq").src_out == rename(mk(), "seq", preserve=frozenset()).src_out
