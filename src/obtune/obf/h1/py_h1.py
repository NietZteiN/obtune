"""QUARANTINED Python H1 generator — string encoding + guarded MBA rewriting.

HARD RULE (CLAUDE.md §3.2): this module lives under obf/h1/ and may be imported
ONLY by scripts/gen_h1_quarantined.py. H1 is the paper's held-out discriminator;
if its features leak into a trainable condition the headline invariance claim is
dead. tests/test_quarantine_lint.py enforces the import monopoly statically.

Two transforms, both designed to be provably semantics-preserving in a *dynamic*
language:

  1. String encoding. Every ``str`` literal becomes ``_dec("<base64>")`` where
     ``_dec`` is an inline, import-free base64 decoder emitted at the top of the
     module. f-strings are rewritten to a concatenation so only their literal
     chunks are encoded while interpolations keep their exact formatting
     semantics (``format(value, spec)`` after any ``!r/!s/!a`` conversion). Bytes
     literals are left untouched.

  2. MBA (mixed boolean-arithmetic) rewriting. ``+ - ^`` become calls to guarded
     helpers that apply the algebraic identity ONLY when both operands are real
     ints (``type(x) is int`` excludes ``bool``); otherwise they fall back to the
     ordinary operator. The guard is what makes this safe on strings, floats,
     lists, numpy scalars, etc. — a naive ``(a^b)+2*(a&b)`` would raise on those.

     Identities (verified over random ints at import, see ``verify_identities``):
       a + b == (a ^ b) + 2*(a & b)
       a - b == a + ~b + 1
       a ^ b == (a | b) - (a & b)

A variant that degenerates to near-identity (too few encoded strings / MBA sites)
would make H1 spuriously easy, so ``transform`` reports counts and the generator
rejects anything below the ``min_*`` bars from configs/conditions.yaml.
"""
from __future__ import annotations

import ast
import base64
import random
from dataclasses import dataclass, field

# Inline helpers emitted verbatim at the top of every H1 Python variant. NO
# imports: _dec is a hand-rolled base64 decoder; the __mba_* helpers are guarded.
_HELPERS_SRC = '''\
def _dec(_s):
    _al = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    _tab = {_c: _i for _i, _c in enumerate(_al)}
    _s = _s.rstrip("=")
    _bits = 0
    _n = 0
    _out = bytearray()
    for _ch in _s:
        _bits = (_bits << 6) | _tab[_ch]
        _n += 6
        if _n >= 8:
            _n -= 8
            _out.append((_bits >> _n) & 255)
    return _out.decode("utf-8")


def __mba_add(a, b):
    if type(a) is int and type(b) is int:
        return (a ^ b) + 2 * (a & b)
    return a + b


def __mba_sub(a, b):
    if type(a) is int and type(b) is int:
        return a + ~b + 1
    return a - b


def __mba_xor(a, b):
    if type(a) is int and type(b) is int:
        return (a | b) - (a & b)
    return a ^ b
'''

_MBA_FUNC = {ast.Add: "__mba_add", ast.Sub: "__mba_sub", ast.BitXor: "__mba_xor"}


@dataclass
class H1Result:
    ok: bool
    code: str
    n_mba_sites: int = 0
    n_encoded_strings: int = 0
    reason: str | None = None
    meta: dict = field(default_factory=dict)


def _b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def verify_identities(trials: int = 2000, seed: int = 17) -> None:
    """Assert the MBA identities over random ints (incl. negatives). Raises on any
    mismatch so a broken helper can never ship."""
    rng = random.Random(seed)
    for _ in range(trials):
        a = rng.randint(-(1 << 40), 1 << 40)
        b = rng.randint(-(1 << 40), 1 << 40)
        if ((a ^ b) + 2 * (a & b)) != a + b:
            raise AssertionError(f"__mba_add identity failed at ({a},{b})")
        if (a + ~b + 1) != a - b:
            raise AssertionError(f"__mba_sub identity failed at ({a},{b})")
        if ((a | b) - (a & b)) != (a ^ b):
            raise AssertionError(f"__mba_xor identity failed at ({a},{b})")


class _MBARewriter(ast.NodeTransformer):
    """Wrap +, -, ^ in guarded helper calls, and expand int literals into equivalent
    MBA expressions.

    Literal expansion is what makes H1 applicable to ordinary programs. Requiring
    binary +/-/^ alone left most programs below the acceptance bar (a loop that only
    compares and indexes has no MBA sites at all), which would have made H1 a small,
    arithmetic-heavy subset — and H1 is the held-out condition the Invariance Index
    is computed on, so a biased H1 set biases the paper's headline number. It also
    mirrors javascript-obfuscator's ``numbersToExpressions``, which the JS H1 already
    enables, so the two languages now exercise the same feature set.

    ``x += y`` is rewritten only when the target is a plain Name: for a subscript or
    attribute target, ``d[f()] += 1`` -> ``d[f()] = __mba_add(d[f()], 1)`` would
    evaluate the target expression twice.
    """

    #: Literal expansion is capped so a constant-dense program does not blow the
    #: H1 size cap; sites beyond this keep their plain literal.
    MAX_LITERAL_SITES = 24

    def __init__(self, rng: random.Random | None = None) -> None:
        self.count = 0
        self.literal_count = 0
        self._rng = rng or random.Random(0)

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)  # transform operands first
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
        load_target = ast.Name(id=node.target.id, ctx=ast.Load())
        return ast.Assign(
            targets=[ast.Name(id=node.target.id, ctx=ast.Store())],
            value=ast.Call(func=ast.Name(id=fn, ctx=ast.Load()),
                           args=[load_target, node.value], keywords=[]),
        )

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        # `type(v) is int` excludes bool: True is an int subclass, and rewriting it
        # to an arithmetic expression would change `x is True` and repr behaviour.
        if type(node.value) is not int or self.literal_count >= self.MAX_LITERAL_SITES:
            return node
        n = node.value
        if abs(n) > (1 << 31):
            return node
        self.literal_count += 1
        self.count += 1
        k = self._rng.randrange(1, 1 << 16)
        # ((n ^ k) ^ k) == n and ((n + k) - k) == n for every int, with no dependence
        # on operand types at runtime — these are literals, so the guards are moot.
        if self._rng.random() < 0.5:
            inner = ast.BinOp(left=ast.Constant(value=n ^ k), op=ast.BitXor(), right=ast.Constant(value=k))
        else:
            inner = ast.BinOp(left=ast.Constant(value=n + k), op=ast.Sub(), right=ast.Constant(value=k))
        return inner


class _StringEncoder(ast.NodeTransformer):
    """Encode str literals as ``_dec("<b64>")``; rewrite f-strings to concatenation
    so only literal chunks are encoded and interpolations keep exact semantics."""

    def __init__(self) -> None:
        self.count = 0

    def _dec_call(self, s: str) -> ast.Call:
        self.count += 1
        return ast.Call(func=ast.Name(id="_dec", ctx=ast.Load()),
                        args=[ast.Constant(value=_b64(s))], keywords=[])

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            return self._dec_call(node.value)
        return node  # bytes / numbers / None untouched

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.AST:
        return self._convert_joinedstr(node)

    def _convert_joinedstr(self, node: ast.JoinedStr) -> ast.expr:
        parts: list[ast.expr] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                if v.value != "":
                    parts.append(self._dec_call(v.value))
            elif isinstance(v, ast.FormattedValue):
                parts.append(self._convert_formatted(v))
            else:  # defensive: unexpected node -> coerce to str
                parts.append(ast.Call(func=ast.Name(id="str", ctx=ast.Load()),
                                      args=[self.visit(v)], keywords=[]))
        if not parts:
            return self._dec_call("")
        expr = parts[0]
        for p in parts[1:]:
            expr = ast.BinOp(left=expr, op=ast.Add(), right=p)
        return expr

    def _convert_formatted(self, fv: ast.FormattedValue) -> ast.expr:
        value = self.visit(fv.value)  # recurse: nested strings/f-strings get encoded
        if fv.conversion == ord("r"):
            converted: ast.expr | None = ast.Call(func=ast.Name(id="repr", ctx=ast.Load()), args=[value], keywords=[])
        elif fv.conversion == ord("s"):
            converted = ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[value], keywords=[])
        elif fv.conversion == ord("a"):
            converted = ast.Call(func=ast.Name(id="ascii", ctx=ast.Load()), args=[value], keywords=[])
        else:
            converted = None
        if fv.format_spec is not None:
            spec = self._convert_joinedstr(fv.format_spec)
            arg = converted if converted is not None else value
            return ast.Call(func=ast.Name(id="format", ctx=ast.Load()), args=[arg, spec], keywords=[])
        if converted is not None:
            return converted
        # Default field == format(value, "") — precise semantics of ``{value}``.
        return ast.Call(func=ast.Name(id="format", ctx=ast.Load()),
                        args=[value, ast.Constant(value="")], keywords=[])


def transform(code: str, min_total_sites: int = 3, seed: int = 0) -> H1Result:
    """Apply H1 to Python source. Returns an H1Result; ``ok`` is False (with a
    reason) when parsing fails or the variant is too close to the identity.

    The acceptance bar is the COMBINED number of transformed sites, not a per-feature
    conjunction. H1 is a transform *family* (string encoding + MBA), and requiring
    both would restrict it to programs that are simultaneously arithmetic-heavy and
    string-heavy: measured on the fixture corpus, a conjunctive bar accepted 0/12
    Python programs while rejecting variants with 3 MBA sites and 0 strings, or 3
    strings and 0 MBA sites. Since the Invariance Index is computed on H1 alone, a
    biased H1 program set would bias the paper's headline number, so what matters is
    that the variant is *meaningfully* transformed by some H1-family machinery.
    """
    verify_identities()  # never ship a broken guard
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return H1Result(ok=False, code=code, reason=f"parse-error: {e}")

    # MBA first (counts genuine arithmetic operators), then encode strings — the
    # f-string concatenations MBA would otherwise wrap stay as plain str '+'.
    mba = _MBARewriter(random.Random(seed))
    tree = mba.visit(tree)
    enc = _StringEncoder()
    tree = enc.visit(tree)
    ast.fix_missing_locations(tree)

    try:
        body_src = ast.unparse(tree)
    except Exception as e:  # noqa: BLE001 — unparse failure is a rejectable outcome
        return H1Result(ok=False, code=code, reason=f"unparse-error: {e}")

    out = _HELPERS_SRC + "\n\n" + body_src
    # Self-check: the emitted module must at least compile.
    try:
        compile(out, "<h1>", "exec")
    except SyntaxError as e:
        return H1Result(ok=False, code=out, reason=f"emit-syntax-error: {e}")

    total = mba.count + enc.count
    if total < min_total_sites:
        return H1Result(ok=False, code=out, n_mba_sites=mba.count, n_encoded_strings=enc.count,
                        reason=f"too-few-h1-sites: {mba.count} mba + {enc.count} strings "
                               f"= {total} < {min_total_sites}")

    return H1Result(ok=True, code=out, n_mba_sites=mba.count, n_encoded_strings=enc.count)
