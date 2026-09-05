"""X1 — a TRAINABLE sibling of the held-out H1 family (string encoding + guarded MBA).

WHY THIS EXISTS (W6 lever 7, 2026-09-04). H1 measures transfer to an *unseen transform
family*. X1 makes the family seen while the instance stays unseen: the same two
mechanisms — every str literal routed through an inline decoder, every ``+ - ^`` routed
through a type-guarded algebraic helper — built from a DIFFERENT encoding scheme and
DIFFERENT algebraic identities. A model tuned on X1 has seen "call a helper defined at
the top of the module, read what it does, evaluate it"; it has never seen base64, ``_dec``
or ``__mba_*``. Whether that exposure moves H1 is the question X1 exists to ask, and it is
reported in its own namespace, never pooled with the headline systems.

WHAT KEEPS IT OUT OF H1's QUARANTINE. This module shares no code with obf/h1/ (the lint
forbids the import) and emits nothing that matches ``h1_marker_patterns`` in
configs/conditions.yaml — the gate's marker scan and scripts/check_manifest.py both run on
every X1 row exactly as on every other trainable condition, which is the enforced
guarantee that an X1 row is not an H1 row. Helper names are chosen against that list:
``_rs`` (restore string), ``_ar_p/_ar_m/_ar_x`` (arithmetic plus/minus/xor).

The two transforms, both provably semantics-preserving in a dynamic language:

  1. String encoding. ``"abc"`` -> ``_rs([c0, c1, c2], k)`` where the list holds each
     codepoint XOR'd with a per-program key ``k`` in 1..255 and ``_rs`` reverses it with
     ``chr(c ^ k)``. XOR with k < 256 touches only the low byte, so no codepoint can leave
     its plane — but nothing depends on that: the ints are just ints, and decoding returns
     the original ordinal exactly. f-strings become concatenations so only the literal
     chunks are encoded and interpolations keep their exact formatting semantics
     (``format(value, spec)`` after any ``!r/!s/!a`` conversion). Bytes are untouched.
     (H1: base64 text through a hand-rolled bit-shifting decoder.)

  2. MBA rewriting. ``+ - ^`` become guarded helper calls that apply the identity only
     when both operands are real ints (``bool`` excluded — it is an int subclass and
     ``True + 1`` must stay ``2`` of type int, which the identity also gives, but
     ``x is True`` tests and reprs elsewhere are safer left alone), else the plain operator:
       a + b == (a | b) + (a & b)
       a - b == (a ^ b) - 2 * (~a & b)
       a ^ b == (a + b) - 2 * (a & b)
     (H1: (a^b)+2(a&b), a+~b+1, (a|b)-(a&b) — the complementary members of each pair.)
     Int literals are expanded too, as in H1, because a loop that only compares and
     indexes has no binary arithmetic and would otherwise fall below the bar:
       n -> (n - k) + k   |   n -> k - (k - n)
     (H1: (n ^ k) ^ k and (n + k) - k.)

Acceptance is the COMBINED number of sites (H1's rule, for H1's reason: requiring both
mechanisms restricts the condition to programs that are simultaneously string-heavy and
arithmetic-heavy, which would bias the program set the X1 -> H1 comparison rests on).
"""
from __future__ import annotations

import ast
import random

from obtune.obf.base import Bail, SnippetCtx, TransformResult

#: Emitted verbatim at the top of every X1 variant. No imports.
HELPERS_SRC = '''\
def _rs(cs, k):
    return "".join(chr(c ^ k) for c in cs)


def _ar_p(a, b):
    if isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool) and not isinstance(b, bool):
        return (a | b) + (a & b)
    return a + b


def _ar_m(a, b):
    if isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool) and not isinstance(b, bool):
        return (a ^ b) - 2 * (~a & b)
    return a - b


def _ar_x(a, b):
    if isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool) and not isinstance(b, bool):
        return (a + b) - 2 * (a & b)
    return a ^ b
'''

HELPER_NAMES = ("_rs", "_ar_p", "_ar_m", "_ar_x")
_MBA_FUNC = {ast.Add: "_ar_p", ast.Sub: "_ar_m", ast.BitXor: "_ar_x"}


def verify_identities(trials: int = 2000, seed: int = 17) -> None:
    """Assert the three identities over random ints incl. negatives; never ship a
    broken helper."""
    rng = random.Random(seed)
    for _ in range(trials):
        a = rng.randint(-(1 << 40), 1 << 40)
        b = rng.randint(-(1 << 40), 1 << 40)
        if (a | b) + (a & b) != a + b:
            raise AssertionError(f"_ar_p identity failed at ({a},{b})")
        if (a ^ b) - 2 * (~a & b) != a - b:
            raise AssertionError(f"_ar_m identity failed at ({a},{b})")
        if (a + b) - 2 * (a & b) != a ^ b:
            raise AssertionError(f"_ar_x identity failed at ({a},{b})")


class _MBARewriter(ast.NodeTransformer):
    """Wrap ``+ - ^`` in guarded helper calls and expand int literals.

    ``x += y`` is rewritten only when the target is a plain Name — for a subscript or
    attribute target ``d[f()] += 1`` -> ``d[f()] = _ar_p(d[f()], 1)`` would evaluate the
    target expression twice.
    """

    MAX_LITERAL_SITES = 24

    def __init__(self, rng: random.Random) -> None:
        self.count = 0
        self.literal_count = 0
        self._rng = rng

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        fn = _MBA_FUNC.get(type(node.op))
        if fn is None:
            return node
        self.count += 1
        return ast.Call(func=ast.Name(id=fn, ctx=ast.Load()), args=[node.left, node.right], keywords=[])

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        self.generic_visit(node)
        fn = _MBA_FUNC.get(type(node.op))
        if fn is None or not isinstance(node.target, ast.Name):
            return node
        self.count += 1
        return ast.Assign(
            targets=[ast.Name(id=node.target.id, ctx=ast.Store())],
            value=ast.Call(func=ast.Name(id=fn, ctx=ast.Load()),
                           args=[ast.Name(id=node.target.id, ctx=ast.Load()), node.value], keywords=[]),
        )

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is not int or self.literal_count >= self.MAX_LITERAL_SITES:
            return node
        n = node.value
        if abs(n) > (1 << 31):
            return node
        self.literal_count += 1
        self.count += 1
        k = self._rng.randrange(1, 1 << 16)
        # Literal-only arithmetic: the guards are moot, and the expanded BinOp is returned
        # rather than revisited, so it stays a plain operator and is not itself wrapped.
        if self._rng.random() < 0.5:  # (n - k) + k
            return ast.BinOp(left=ast.Constant(value=n - k), op=ast.Add(), right=ast.Constant(value=k))
        # k - (k - n)
        return ast.BinOp(left=ast.Constant(value=k), op=ast.Sub(),
                         right=ast.BinOp(left=ast.Constant(value=k), op=ast.Sub(), right=ast.Constant(value=n)))


class _StringEncoder(ast.NodeTransformer):
    """``"abc"`` -> ``_rs([..], k)``; f-strings -> concatenation of encoded chunks and
    exactly-formatted interpolations."""

    def __init__(self, key: int) -> None:
        self.count = 0
        self.key = key

    def _rs_call(self, s: str) -> ast.Call:
        self.count += 1
        cps = ast.List(elts=[ast.Constant(value=ord(ch) ^ self.key) for ch in s], ctx=ast.Load())
        return ast.Call(func=ast.Name(id="_rs", ctx=ast.Load()),
                        args=[cps, ast.Constant(value=self.key)], keywords=[])

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            return self._rs_call(node.value)
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        return self._convert_joinedstr(node)

    def _convert_joinedstr(self, node: ast.JoinedStr) -> ast.expr:
        parts: list[ast.expr] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                if v.value != "":
                    parts.append(self._rs_call(v.value))
            elif isinstance(v, ast.FormattedValue):
                parts.append(self._convert_formatted(v))
            else:
                parts.append(ast.Call(func=ast.Name(id="str", ctx=ast.Load()),
                                      args=[self.visit(v)], keywords=[]))
        if not parts:
            return self._rs_call("")
        expr = parts[0]
        for p in parts[1:]:
            expr = ast.BinOp(left=expr, op=ast.Add(), right=p)
        return expr

    def _convert_formatted(self, fv: ast.FormattedValue) -> ast.expr:
        value = self.visit(fv.value)
        conv = {ord("r"): "repr", ord("s"): "str", ord("a"): "ascii"}.get(fv.conversion)
        converted: ast.expr | None = (
            ast.Call(func=ast.Name(id=conv, ctx=ast.Load()), args=[value], keywords=[]) if conv else None
        )
        if fv.format_spec is not None:
            spec = self._convert_joinedstr(fv.format_spec)
            arg = converted if converted is not None else value
            return ast.Call(func=ast.Name(id="format", ctx=ast.Load()), args=[arg, spec], keywords=[])
        if converted is not None:
            return converted
        return ast.Call(func=ast.Name(id="format", ctx=ast.Load()),
                        args=[value, ast.Constant(value="")], keywords=[])


def count_helper_calls(code: str) -> int:
    """Number of calls to an X1 helper in ``code`` — the positive purity invariant."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0
    return sum(
        1 for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in HELPER_NAMES
    )


def _const_binop(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) or (
        isinstance(n, ast.BinOp) and _const_binop(n.left) and _const_binop(n.right)
    )


def count_literal_expansions(code: str) -> int:
    """Number of constant-only arithmetic BinOps (``(n - k) + k``, ``k - (k - n)``). The
    L0 parent can contain a few of its own (``60 * 60``), so callers compare against it."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.BinOp) and _const_binop(n))


def transform(ctx: SnippetCtx) -> TransformResult:
    """X1 on a Python program. Bails (never silently degrades) below the site bar."""
    verify_identities()
    try:
        tree = ast.parse(ctx.src)
    except SyntaxError as exc:
        raise Bail(f"input does not parse: {exc}") from exc
    for name in HELPER_NAMES:
        if any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(tree)):
            raise Bail(f"program already uses the helper name {name!r}")

    min_sites = int(ctx.param("min_total_sites", 3))
    # MBA first so the `+` that joins f-string chunks stays a plain str concatenation.
    mba = _MBARewriter(ctx.rng)
    tree = mba.visit(tree)
    enc = _StringEncoder(key=ctx.rng.randrange(1, 256))
    tree = enc.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        body = ast.unparse(tree)
    except Exception as exc:  # noqa: BLE001 — an unparse failure is a decline, not a crash
        raise Bail(f"unparse failed: {exc}") from exc

    out = HELPERS_SRC + "\n\n" + body
    try:
        compile(out, "<x1>", "exec")
    except SyntaxError as exc:
        # e.g. a str literal in a `match` pattern position, which cannot become a call
        raise Bail(f"emitted module does not compile: {exc}") from exc

    total = mba.count + enc.count
    if total < min_sites:
        raise Bail(f"too few X1 sites: {mba.count} mba + {enc.count} strings = {total} < {min_sites}")
    return TransformResult(
        src_out=out, applied=True,
        notes=[f"X1: {mba.count} mba sites ({mba.literal_count} literal expansions), "
               f"{enc.count} encoded strings, key {enc.key}"],
        extra={"n_mba_sites": mba.count, "n_literal_sites": mba.literal_count,
               "n_encoded_strings": enc.count, "x1_key": enc.key},
    )
