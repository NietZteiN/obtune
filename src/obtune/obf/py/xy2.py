"""X2 / Y2 — a SECOND family pair: computation routed through exception machinery.

WHY THIS EXISTS (E5, docs/PAPER_EXPERIMENTS.md, 2026-09-07). The paper's central claim is
that what a tuned model acquires is the *transformation family* it was shown, not semantic
invariance. All of the evidence for that rests on ONE family pair: X1 (trainable) and H1
(held out), which share string-encoding + MBA arithmetic. One pair cannot distinguish "the
family is what transfers" from "the encoding family in particular is what transfers", and
H1's budget is spent so the original pair can never be extended.

X2 and Y2 are a second pair, built the same way X1 was built against H1:

  * SAME family — every value crosses a `raise`/`except` boundary, so the model must learn
    "follow the value out through the exception machinery and back" to read the program.
    This is a genuinely different mechanism from every existing condition: not renaming
    (L1b/L1r/L2), not dispatch flattening (S1), not inert material (S2), not encoding
    (X1/H1).
  * DIFFERENT surface — X2 raises a `LookupError` carrying the value in `.args[0]` and
    catches it in the same frame. Y2 uses the generator protocol: a `return` inside a
    generator sets `StopIteration.value`, which the helper reads back. Different statements,
    different exception types, different helper names, no shared token beyond `try`/`except`.

X2 is `trainable: true`; **Y2 is eval-only** (`trainable: false`) and is the unseen sibling
the family claim is tested on. Y2 is deliberately NOT quarantined the way H1 is: H1 was the
paper's single discriminator and had a two-read budget, whereas Y2 can be regenerated at any
time from this module, so a re-read costs nothing and forecloses nothing. That is exactly why
Y2 cannot *replace* H1's evidential role, only extend it — stated here so no later reader
mistakes a cheap column for a quarantined one.

BOTH transforms are identity-preserving by construction. Every rewrite is `expr` ->
`helper(expr)` where the helper provably returns its argument unchanged:

    X2:  _thru(v)  raises LookupError(v), catches it in-frame and returns e.args[0]
    Y2:  _pull(v)  runs a generator whose `return v` sets StopIteration.value, read back

Neither helper touches control flow *around* the expression: the argument is evaluated
exactly once, at exactly the point the original expression was evaluated, so short-circuit
order, generator semantics and exception propagation from within `expr` are all unchanged.
`if TEST:` is wrapped as a whole (`if _guard(TEST):`), never per-operand, because wrapping
inside an `and`/`or` would force eager evaluation and change semantics.

Sites counted for the acceptance bar: wrapped `return` values, `if`/`while` tests,
assignment right-hand sides and `for` iterables -- every position that is evaluated exactly
once, in the original order, with no short-circuit to disturb. A program below the bar is DECLINED (`Bail`), never silently returned unchanged --
"correctness beats coverage" (CLAUDE.md §4).
"""
from __future__ import annotations

import ast

from obtune.obf.base import Bail, SnippetCtx, TransformResult

# --- X2: a built-in exception carries the value, raised and caught in one frame ---------
#
# NOT a bespoke `class _Sig(Exception)`, which is what this started as. The execution
# sandbox builds its child globals as `{k: getattr(builtins, k) for k in dir(builtins) if
# not k.startswith("_")}` plus `__import__` -- so `__build_class__` is absent and ANY class
# statement dies with NameError at module exec. That is a pre-existing property of
# src/obtune/exec/runner_py.py (it silently excludes every class-defining program from every
# condition), not something X2 should paper over, so X2 simply does not need a class:
# `LookupError(v)` carries the value in `.args[0]` and is a different vehicle from Y2's
# generator return either way.
X2_HELPERS = '''\
def _thru(v):
    try:
        raise LookupError(v)
    except LookupError as e:
        return e.args[0]


def _guard(c):
    try:
        raise LookupError(c)
    except LookupError as e:
        return e.args[0]
'''
X2_NAMES = ("_thru", "_guard")

# --- Y2: the generator protocol -- `return` inside a generator sets StopIteration.value
Y2_HELPERS = '''\
def _pull(v):
    def _src():
        return v
        yield None
    g = _src()
    try:
        next(g)
    except StopIteration as s:
        return s.value


def _sel(c):
    def _src():
        return c
        yield None
    g = _src()
    try:
        next(g)
    except StopIteration as s:
        return s.value
'''
Y2_NAMES = ("_pull", "_sel", "_src")


def verify_helpers() -> None:
    """Both helper banks must be exact identities before a single program is rewritten."""
    for src, val_fn, test_fn in ((X2_HELPERS, "_thru", "_guard"), (Y2_HELPERS, "_pull", "_sel")):
        ns: dict = {}
        exec(compile(src, "<helpers>", "exec"), ns)  # noqa: S102 — our own literal source
        for probe in (0, 1, -3, "", "abc", None, True, False, 3.5, [1, 2], {"k": 1}, (), object()):
            got = ns[val_fn](probe)
            if got is not probe and got != probe:
                raise AssertionError(f"{val_fn} is not an identity on {probe!r}")
            got = ns[test_fn](probe)
            if got is not probe and got != probe:
                raise AssertionError(f"{test_fn} is not an identity on {probe!r}")


class _ExcRewriter(ast.NodeTransformer):
    """Wrap `return <expr>` and `if`/`while` tests in the family's identity helper."""

    def __init__(self, value_fn: str, test_fn: str):
        self.value_fn, self.test_fn = value_fn, test_fn
        # Wrapping inside a loop body multiplies the cost by the iteration count, and this
        # family is intrinsically expensive: every wrapped site raises and catches an
        # exception (X2) or builds and exhausts a generator (Y2). Unrestricted, that blew the
        # gate's runtime_ratio_max of 5.0 on hot programs -- at DIFFERENT rates for X2 and Y2
        # (2/60 vs 6/60), which would have left the two siblings gated on different program
        # sets and confounded the very comparison E5 exists to make. Sites in loop bodies are
        # therefore skipped; `return` is still wrapped everywhere because it fires once per
        # call, not once per iteration.
        self._loop_depth = 0
        self.n_return = 0
        self.n_test = 0
        self.n_value = 0

    def _call(self, fn: str, node: ast.expr) -> ast.Call:
        return ast.Call(func=ast.Name(id=fn, ctx=ast.Load()), args=[node], keywords=[])

    def visit_Return(self, node: ast.Return):
        self.generic_visit(node)
        # A bare `return` carries no value; there is nothing to route.
        if node.value is None:
            return node
        self.n_return += 1
        node.value = self._call(self.value_fn, node.value)
        return node

    def _wrap_test(self, node):
        is_loop = isinstance(node, ast.While)
        outer = self._loop_depth
        if is_loop:
            self._loop_depth += 1
        self.generic_visit(node)
        self._loop_depth = outer
        if self._loop_depth:
            return node
        self.n_test += 1
        # The WHOLE test, never an operand: wrapping inside `and`/`or` would make both
        # sides eager and change semantics for `if xs and xs[0]`.
        node.test = self._call(self.test_fn, node.test)
        return node

    def visit_If(self, node: ast.If):
        return self._wrap_test(node)

    def visit_While(self, node: ast.While):
        return self._wrap_test(node)

    # Returns and tests alone are too sparse: on data/train/base/python.jsonl the median
    # program has 1 return and 1 test, below any useful bar. These three positions are the
    # safe way to raise the density -- each is evaluated EXACTLY ONCE in the original, in
    # the same order, with no short-circuit to disturb. (`Compare` operands are deliberately
    # NOT wrapped: `a < b < c` short-circuits, so wrapping `c` would force its evaluation.)
    def visit_Assign(self, node: ast.Assign):
        self.generic_visit(node)
        if self._loop_depth:
            return node
        self.n_value += 1
        node.value = self._call(self.value_fn, node.value)
        return node

    def visit_AugAssign(self, node: ast.AugAssign):
        self.generic_visit(node)
        if self._loop_depth:
            return node
        self.n_value += 1
        node.value = self._call(self.value_fn, node.value)
        return node

    def visit_For(self, node: ast.For):
        outer = self._loop_depth
        self._loop_depth += 1
        self.generic_visit(node)
        self._loop_depth = outer
        if self._loop_depth:
            return node
        self.n_value += 1
        # The iterable is evaluated once, before the loop, exactly as `iter(expr)` would be.
        node.iter = self._call(self.value_fn, node.iter)
        return node


def _apply(ctx: SnippetCtx, code: str, helpers: str, names: tuple[str, ...],
           value_fn: str, test_fn: str, tag: str) -> TransformResult:
    verify_helpers()
    try:
        tree = ast.parse(ctx.src)
    except SyntaxError as exc:
        raise Bail(f"input does not parse: {exc}") from exc
    for name in names:
        if any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(tree)):
            raise Bail(f"program already uses the helper name {name!r}")
        if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name
               for n in ast.walk(tree)):
            raise Bail(f"program already defines {name!r}")

    rw = _ExcRewriter(value_fn, test_fn)
    tree = rw.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        body = ast.unparse(tree)
    except Exception as exc:  # noqa: BLE001 — an unparse failure is a decline, not a crash
        raise Bail(f"unparse failed: {exc}") from exc

    out = helpers + "\n\n" + body
    try:
        compile(out, f"<{tag}>", "exec")
    except SyntaxError as exc:
        raise Bail(f"emitted module does not compile: {exc}") from exc

    total = rw.n_return + rw.n_test + rw.n_value
    min_sites = int(ctx.param("min_total_sites", 3))
    if total < min_sites:
        raise Bail(f"too few {tag} sites: {rw.n_return} returns + {rw.n_test} tests + "
                   f"{rw.n_value} values = {total} < {min_sites}")
    return TransformResult(
        src_out=out, applied=True,
        notes=[f"{tag}: {rw.n_return} returns, {rw.n_test} tests, {rw.n_value} values routed "
               f"through {'a raised LookupError' if tag == 'X2' else 'StopIteration.value'}"],
        extra={"n_return_sites": rw.n_return, "n_test_sites": rw.n_test,
               "n_value_sites": rw.n_value, "family": "exceptional"},
    )


def transform_x2(ctx: SnippetCtx) -> TransformResult:
    """X2 — trainable member of the exception-routing family (raised `LookupError`)."""
    return _apply(ctx, ctx.src, X2_HELPERS, X2_NAMES, "_thru", "_guard", "X2")


def transform_y2(ctx: SnippetCtx) -> TransformResult:
    """Y2 — the UNSEEN sibling (generator `StopIteration.value`). Never trained on."""
    return _apply(ctx, ctx.src, Y2_HELPERS, Y2_NAMES, "_pull", "_sel", "Y2")
