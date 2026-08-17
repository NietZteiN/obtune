"""Normalization must not make programs BIGGER.

The bug this file exists to catch shipped once already and the execution gate could not see
it. `_pass_dce` filled every empty `orelse` with `pass`, turning "no else clause" into
"else: pass" on every `if` and `for` in the program. Behaviour was identical — so
21_validate_normalized.py passed with zero unsound programs — but the model was being shown
MORE scaffolding than the un-normalized program had, which would have biased the `norm_full`
arm downwards and been read as "normalization does not help".

The lesson generalizes: for this baseline, semantic equivalence is necessary and nowhere
near sufficient. The arm's whole premise is that the output is EASIER TO READ, so size and
shape need their own assertions.
"""
from __future__ import annotations

import pytest

from obtune.normalize import normalize

CASES = [
    ("if-without-else",
     "def f(a):\n    if not a:\n        return []\n    return a\n"),
    ("for-without-else",
     "def f(xs):\n    t = 0\n    for v in xs:\n        t += v\n    return t\n"),
    ("while-without-else",
     "def f(n):\n    i = 0\n    while i < n:\n        i += 1\n    return i\n"),
    ("try-without-finally",
     "def f(a):\n    try:\n        return int(a)\n    except ValueError:\n        return 0\n"),
    ("nested",
     "def f(xs):\n    out = []\n    for v in xs:\n        if v > 0:\n            out.append(v)\n    return out\n"),
]


@pytest.mark.parametrize("name,src", CASES, ids=[c[0] for c in CASES])
@pytest.mark.parametrize("profile", ["alpha", "reformat", "full"])
def test_normalization_never_invents_an_empty_clause(name, src, profile) -> None:
    out = normalize(src, "python", entry_point="f", profile=profile).code
    assert "else:\n        pass" not in out and "else:\n    pass" not in out, out
    # `pass` appears nowhere in these inputs, so any `pass` in the output was invented.
    assert "pass" not in out, f"{profile} invented scaffolding:\n{out}"


@pytest.mark.parametrize("name,src", CASES, ids=[c[0] for c in CASES])
def test_full_profile_does_not_grow_the_program(name, src) -> None:
    """`full` is the most aggressive profile and must still be a net simplification."""
    out = normalize(src, "python", entry_point="f", profile="full").code
    assert out.count("\n") <= src.count("\n"), f"gained lines:\n{out}"


def test_alpha_shrinks_obfuscated_identifiers() -> None:
    """The mechanism on L1r: hex names are long, canonical names are short."""
    src = ("def f_72ed(v_1f1e):\n    v_5b78 = []\n    for v_0680 in v_1f1e:\n"
           "        v_5b78.append(v_0680)\n    return v_5b78\n")
    out = normalize(src, "python", entry_point="f_72ed", profile="alpha").code
    assert len(out) < len(src)
    assert "f_72ed" in out, "the entry point must keep its name"
    assert "v_1f1e" not in out and "v_5b78" not in out


def test_dce_output_has_no_leftover_pass_from_a_removed_branch() -> None:
    src = "def f(a):\n    if False:\n        a = 0\n    return a\n"
    out = normalize(src, "python", entry_point="f", profile="full").code
    assert "pass" not in out, out
    assert "False" not in out, out
