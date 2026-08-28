"""Character spans of code the structural normalizer PROVES cannot affect the result.

`normalize(profile="structural")` deletes dead code and returns clean source. That is the right
output for a baseline that re-prompts the model, but it answers only one question: does removing
inert material help? It cannot separate two very different reasons why it might —

  * **the tokens are gone**, so the sequence is shorter and every live token sits closer to the
    answer position; or
  * **attention is no longer spent on them**, which is a claim about allocation, not length.

This module exists to let the second be tested on its own. It reports WHERE the dead code is in
the ORIGINAL source, so the model can be shown the untouched program while attention to those
exact tokens is suppressed (`attn/31_steer.py`). Sequence length, token positions and every live
token's context are then byte-identical to the unmodified condition, and the only thing that
changes is where attention may land. That is the training-free counterpart to the 2026-08-26
knockout result, which showed `tuned_S2` had LEARNED to de-anchor from inert identifiers: if the
policy can simply be handed to the base model, no training is needed to get it.

Fidelity to the real normalizer. The helper analysis is not re-implemented — it RUNS
`py_norm._pass_dce` and reads back which module-level functions disappeared, so the two cannot
drift on the subtle part (reflection bail-out, iterate-to-fixpoint, string-constant
over-inclusion). Only the branch logic is mirrored here, because branch spans must be taken from
the original tree and the transformer rebuilds it; `tests/test_inert_spans.py` pins the two
together by count.

Spans are half-open `[start, end)` character offsets into the source passed in, non-overlapping
and sorted.
"""
from __future__ import annotations

import ast
import copy

from .py_norm import _pass_dce, _pass_fold, _static_truth

__all__ = ["inert_spans"]


def _line_starts(src: str) -> list[int]:
    starts, pos = [0], 0
    for line in src.splitlines(keepends=True):
        pos += len(line)
        starts.append(pos)
    return starts


def _span(node: ast.AST, starts: list[int]) -> tuple[int, int] | None:
    """Half-open char span of `node`, or None if it carries no position (synthesized)."""
    lo, co = getattr(node, "lineno", None), getattr(node, "col_offset", None)
    hi, ce = getattr(node, "end_lineno", None), getattr(node, "end_col_offset", None)
    if lo is None or hi is None or co is None or ce is None:
        return None
    return starts[lo - 1] + co, starts[hi - 1] + ce


def _block_span(block: list[ast.stmt], starts: list[int]) -> tuple[int, int] | None:
    spans = [s for s in (_span(n, starts) for n in block) if s]
    return (min(s[0] for s in spans), max(s[1] for s in spans)) if spans else None


def _merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for lo, hi in sorted(s for s in spans if s and s[1] > s[0]):
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def inert_spans(src: str, entry_point: str) -> list[tuple[int, int]]:
    """Char spans in `src` that the structural profile proves dead.

    Returns [] rather than raising when `src` does not parse — callers are eval harnesses and a
    syntax error there means "nothing provably inert", not a crash.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    starts = _line_starts(src)
    spans: list[tuple[int, int] | None] = []

    # (a) statically-decidable branches. The DEAD part is the test (an opaque predicate carries no
    # information at runtime) plus whichever arm can never be entered — never the whole `If`, since
    # the taken arm is live code that must stay visible and attendable.
    #
    # Truth must be read AFTER folding: the `structural` profile is ("fold", "dce", "reformat"),
    # and S2's opaque predicates are written as arithmetic (`if 4 % 4 == 1:`), which `_static_truth`
    # cannot decide until `fold` has collapsed it to a Constant. But the SPANS have to come from
    # the original tree, because folding rewrites the very expressions we want to locate. So the
    # decision is taken on a folded copy and paired back positionally: `_Folder` transforms
    # expressions, never statements, so the If/While sequences of the two trees align 1:1 in walk
    # order. If that ever stops holding the counts diverge and this falls back to the unfolded
    # decision — fewer spans reported, never wrong ones.
    folded, _ = _pass_fold(copy.deepcopy(tree), entry_point)
    branches = [n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.While))]
    fbranches = [n for n in ast.walk(folded) if isinstance(n, (ast.If, ast.While))]
    paired = zip(branches, fbranches) if len(branches) == len(fbranches) else zip(branches, branches)
    for node, decider in paired:
        if type(node) is not type(decider):
            continue
        truth = _static_truth(decider.test)
        if truth is None:
            continue
        if isinstance(node, ast.If):
            spans.append(_span(node.test, starts))
            untaken = node.orelse if truth else node.body
            spans.append(_block_span(untaken, starts))
        elif truth is False:
            # `while False: ... else: X` RUNS X, so only test+body are dead.
            # A statically-TRUE while still exits via break/return and is not dead.
            spans.append(_span(node.test, starts))
            spans.append(_block_span(node.body, starts))

    # (b) unreachable module-level helpers — decided by the real pass, not by a copy of its rules.
    before = {s.name for s in tree.body
              if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))}
    pruned, _ = _pass_dce(copy.deepcopy(tree), entry_point)
    after = {s.name for s in pruned.body
             if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))}
    dropped = before - after
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name in dropped:
            spans.append(_span(stmt, starts))

    # (c) effect-free code — dead stores and branches whose every arm is one. Run per function
    # scope so liveness is not smeared across unrelated locals, plus once over module level.
    for scope in [tree] + [n for n in ast.walk(tree)
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        spans.extend(_effectfree_spans(scope, starts))

    return _merge([s for s in spans if s])


# --------------------------------------------------------------------------- #
# effect-free code — the second kind of inert material, which DCE cannot see
#
# The measurement that forced this. Running the DCE-only analysis above over 150 programs per
# condition marked 32.3 % of `S3` and 18.9 % of `S2` as inert — and **0.4 % of `S4`**, which is
# the condition made ENTIRELY of inert material. `L0`, `S1` and `L1r` came in at 0.2-0.7 %, so the
# analysis was not simply over-firing; it was blind to S4's mechanism. Looking at the corpus says
# why. A real S4 block is:
#
#     offset_f2f = 160
#     if (offset_f2f * offset_f2f + offset_f2f) % 2 == 0:   # n*n + n is always even
#         scratch_9d8 = 0
#         scratch_9d8 += 2
#     else:
#         budget_ec2 = 'kv' + 'acc'
#
# Nothing here is UNREACHABLE — the `if` is entered, one branch does run. Constant folding cannot
# decide the guard either, because it is a function of a variable, and proving it needs the
# number-theoretic fact that n*n + n is even. Yet the whole block is inert, for a reason that
# needs no such proof: **every branch only writes names that are never read again**. Whichever arm
# executes, nothing observable happens.
#
# That is the rule implemented here, and it is deliberately NOT "decide the opaque predicate".
# Deciding predicates is an arms race with the obfuscator (the H1 family escalates to MBA
# identities precisely to defeat it). Asking instead whether the code has any effect sidesteps the
# guard entirely, and it stays sound as the guards get harder.
#
# Soundness. `_required_names` runs a backward liveness fixpoint at NAME granularity, seeded with
# every position where a value can escape or be observed (returns, calls, subscripts, attributes,
# `yield`, `raise`, live branch tests, loop iterables, `global`/`nonlocal`, and anything at all
# inside a nested scope). A name survives as inert only if it is never read in any of those
# positions, and a store is dead only if its right-hand side is additionally side-effect-free. The
# analysis is one-sided: it can miss inert code, and by construction it does not mark live code.

_PURE_NODES = (ast.Constant, ast.Name, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
               ast.IfExp, ast.Tuple, ast.List, ast.Set, ast.Load, ast.Store,
               ast.operator, ast.unaryop, ast.boolop, ast.cmpop, ast.expr_context)


def _is_pure(node: ast.AST | None) -> bool:
    """Whether evaluating this EXPRESSION can be observed. Pass a value, never a statement.

    No calls, no subscripts, no attributes, no awaits, no comprehensions, no f-strings.
    Deliberately strict: a `Subscript` can raise `IndexError` and an `Attribute` can run a
    descriptor, so both are observable events even when the resulting value is discarded.
    `None` (an annotation-only `AnnAssign`) evaluates nothing and is pure.
    """
    return node is None or all(isinstance(n, _PURE_NODES) for n in ast.walk(node))


def _pure_store(node: ast.AST) -> tuple[set[str], set[str]] | None:
    """`(targets, rhs names)` when `node` is an assignment to plain names with a pure RHS.

    None when it is anything else — a destructuring store, a store through a subscript or an
    attribute, or a store whose right-hand side could be observed.
    """
    if not isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        return None
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    if not all(isinstance(t, ast.Name) for t in targets) or not _is_pure(node.value):
        return None
    tgt = {t.id for t in targets}
    rhs = _names_in(node.value) if node.value is not None else set()
    if isinstance(node, ast.AugAssign):
        rhs -= tgt                      # `x += 1` reads x only to write x back
    return tgt, rhs


def _names_in(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _required_names(fn: ast.AST) -> set[str]:
    """Names whose value can be observed, computed to a fixpoint."""
    req: set[str] = set()
    assigns: list[tuple[set[str], set[str]]] = []  # (targets, rhs names)

    def seed(node: ast.AST | None) -> None:
        if node is not None:
            req.update(_names_in(node))

    for node in ast.walk(fn):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda,
                             ast.ClassDef, ast.ListComp, ast.SetComp, ast.DictComp,
                             ast.GeneratorExp)) and node is not fn:
            seed(node)                      # nested scopes: give up, everything inside is required
        elif isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom, ast.Raise, ast.Assert,
                               ast.Expr, ast.Await, ast.Delete)):
            seed(node)
        elif isinstance(node, (ast.Call, ast.Subscript, ast.Attribute, ast.Starred,
                               ast.JoinedStr, ast.FormattedValue)):
            seed(node)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            req.update(node.names)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            seed(node.iter)
        elif isinstance(node, (ast.If, ast.While, ast.IfExp)):
            seed(node.test)
        elif isinstance(node, ast.With):
            seed(node)
        elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            store = _pure_store(node)
            if store is not None:
                assigns.append(store)
            else:
                seed(node)              # impure or destructuring store: treat every name as read

    changed = True
    while changed:                      # propagate: if a target is observable, so are its inputs
        changed = False
        for tgt, rhs in assigns:
            if tgt & req and not rhs <= req:
                req |= rhs
                changed = True
    return req


def _effectfree_spans(fn: ast.AST, starts: list[int]) -> list[tuple[int, int] | None]:
    req = _required_names(fn)
    out: list[tuple[int, int] | None] = []

    def inert_stmt(s: ast.stmt) -> bool:
        """True when executing `s` cannot change anything observable."""
        if isinstance(s, ast.Pass):
            return True
        store = _pure_store(s)
        if store is not None:
            return not (store[0] & req)
        if isinstance(s, ast.If):
            # No need to decide the guard: if NEITHER arm does anything, the branch is inert
            # whichever way it goes. This is what catches S4's computed opaque predicates.
            return (_is_pure(s.test)
                    and all(inert_stmt(x) for x in s.body)
                    and all(inert_stmt(x) for x in s.orelse))
        return False

    for node in ast.walk(fn):
        for attr in ("body", "orelse", "finalbody"):
            block = getattr(node, attr, None)
            if not isinstance(block, list):
                continue
            for s in block:
                if inert_stmt(s):
                    out.append(_span(s, starts))
    return out
