"""S2 — opaque predicates + never-called dead helpers.

Two kinds of junk, neither of which can change observable behaviour:

1. 1-3 guarded blocks at *reachable* top-level statement boundaries of the entry
   function. Each guard is an opaque predicate over a freshly introduced int local:
     always-false  `(q * q + q) % 2 != 0`   (n^2+n is even for every integer n)
     always-false  `(q ^ q) != 0`           (x ^ x == 0)
     always-true   `(q * q + q) % 2 == 0`   with a no-op body
     always-true   the same, with the junk parked in the never-taken `else`
2. 1-2 module-level functions that nothing ever calls.

Why "reachable boundaries" and not anywhere: an inserted block must run exactly when
the code after it would have run. Insertion points are therefore restricted to the
maximal prefix of top-level statements that always complete normally, so no `return`,
`break` or compound statement can sit between the block and the function's entry. This
is the same rule the Java port uses (JLS §14.21 there; here it is about the *block
actually executing*, since Python has no unreachable-statement error at all).

Junk bodies touch nothing: they declare fresh locals and do integer arithmetic, string
concatenation of literals, and `list.append` on a list they just created. No division,
no indexing, no user calls — and deliberately no builtin calls either, because a corpus
program is free to rebind `str` or `len`, which would turn "inert junk" into a call
into user code.

Transform is a pure text insertion (never an `ast.unparse` round trip) so an S2 variant
stays byte-identical to its L0 parent except for the inserted lines: the condition is
supposed to isolate *added dead code*, and reformatting would confound it with a
whitespace change.
"""
from __future__ import annotations

import ast
import random
from typing import Sequence

from obtune.obf.base import Bail, EditList, LineIndex, SnippetCtx, TransformResult, fresh_name

#: Statement types that always complete normally, so a block inserted after them still
#: runs whenever the following original statement would.
_STRAIGHT_LINE = (
    ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Expr, ast.Pass,
    ast.Delete, ast.Import, ast.ImportFrom,
)

#: Introspection that would observe the locals/globals we add. Rare, but if a program
#: calls any of these the injection is no longer semantics-preserving.
_INTROSPECTION = frozenset({"locals", "vars", "globals", "eval", "exec", "dir", "compile"})

_STEMS = (
    "scratch", "margin", "offset", "stride", "pivot", "carry", "tally", "window",
    "weight", "cursor", "budget", "anchor", "bucket", "spread", "residue",
)
_WORDS = ("ok", "nb", "seg", "idx", "raw", "aux", "tmp", "acc", "kv", "sub")


def _fresh(ctx: SnippetCtx, taken: set[str], prefix: str = "") -> str:
    rng = ctx.rng
    return fresh_name(
        lambda: f"{prefix}{rng.choice(_STEMS)}_{rng.randrange(0x1000):03x}", taken
    )


# --------------------------------------------------------------------------- #
# Junk bodies (each returns un-indented lines; nested lines carry 4 spaces)


def _junk_lines(ctx: SnippetCtx, taken: set[str]) -> list[str]:
    rng = ctx.rng
    acc = _fresh(ctx, taken)
    lines = [f"{acc} = {rng.randint(2, 97)}"]
    for _ in range(rng.randint(1, 3)):
        roll = rng.random()
        if roll < 0.45:
            nxt = _fresh(ctx, taken)
            lines.append(f"{nxt} = {acc} * {rng.randint(2, 9)} + {rng.randint(1, 9)}")
            acc = nxt
        elif roll < 0.75:
            tag = _fresh(ctx, taken)
            lines.append(f"{tag} = '{rng.choice(_WORDS)}' + '{rng.choice(_WORDS)}'")
            lines.append(f"{tag} += '{rng.choice(_WORDS)}'")
        else:
            buf = _fresh(ctx, taken)
            lines.append(f"{buf} = []")
            lines.append(f"{buf}.append({acc})")
            lines.append(f"{buf}.append({acc} + {rng.randint(1, 9)})")
    return lines


def _noop_lines(ctx: SnippetCtx, taken: set[str]) -> list[str]:
    t = _fresh(ctx, taken)
    return [f"{t} = 0", f"{t} += {ctx.rng.randint(1, 5)}"]


def _predicate_block(ctx: SnippetCtx, taken: set[str]) -> tuple[list[str], str]:
    """One opaque-predicate block. Returns (lines, style-name for the manifest)."""
    rng = ctx.rng
    q = _fresh(ctx, taken)
    seed_val = rng.randint(1, 1000)
    style = rng.choice(("false_mod", "false_xor", "true_noop", "true_else"))
    head = [f"{q} = {seed_val}"]
    if style == "false_mod":
        head.append(f"if ({q} * {q} + {q}) % 2 != 0:")
        body = _junk_lines(ctx, taken)
        return head + ["    " + ln for ln in body], style
    if style == "false_xor":
        head.append(f"if ({q} ^ {q}) != 0:")
        body = _junk_lines(ctx, taken)
        return head + ["    " + ln for ln in body], style
    if style == "true_noop":
        head.append(f"if ({q} * {q} + {q}) % 2 == 0:")
        body = _noop_lines(ctx, taken)
        return head + ["    " + ln for ln in body], style
    head.append(f"if ({q} * {q} + {q}) % 2 == 0:")
    out = head + ["    " + ln for ln in _noop_lines(ctx, taken)]
    out.append("else:")
    out += ["    " + ln for ln in _junk_lines(ctx, taken)]
    return out, style


def _dead_helper(ctx: SnippetCtx, taken: set[str]) -> list[str]:
    """A module-level function nothing calls. Never raises, never touches user state."""
    rng = ctx.rng
    name = _fresh(ctx, taken, prefix="_")
    p = _fresh(ctx, taken)
    a = _fresh(ctx, taken)
    style = rng.randint(0, 2)
    if style == 0:
        b = _fresh(ctx, taken)
        return [
            f"def {name}({p}=0):",
            f"    {a} = {p} * {rng.randint(2, 9)} + {rng.randint(1, 99)}",
            f"    {b} = {a} ^ {rng.randint(1, 255)}",
            f"    return {b} - {a}",
        ]
    if style == 1:
        return [
            f"def {name}():",
            f"    {a} = '{rng.choice(_WORDS)}'",
            f"    {a} += '{rng.choice(_WORDS)}'",
            f"    return {a}",
        ]
    return [
        f"def {name}({p}=0):",
        f"    {a} = []",
        f"    {a}.append({p} + {rng.randint(1, 9)})",
        f"    {a}.append({p} * {rng.randint(2, 9)})",
        f"    return {a}",
    ]


# --------------------------------------------------------------------------- #
# Insertion points


def _line_start(index: LineIndex, node: ast.stmt) -> int:
    return index.starts[node.lineno - 1]


def _boundaries(index: LineIndex, data: bytes, body: Sequence[ast.stmt]) -> list[tuple[int, str]]:
    """(byte offset, indent) pairs where a normally-completing block may be inserted.

    Everything before the offset on that line must be whitespace, or the insertion
    would split a statement that shares the line (`def f(): return 1`).
    """
    out: list[tuple[int, str]] = []
    prefix_len = 0
    for stmt in body:
        if isinstance(stmt, _STRAIGHT_LINE):
            prefix_len += 1
        else:
            break
    for i in range(min(prefix_len + 1, len(body))):
        stmt = body[i]
        off = _line_start(index, stmt)
        stmt_off = index.offset(stmt.lineno, stmt.col_offset)
        if data[off:stmt_off].strip():
            continue
        out.append((off, " " * stmt.col_offset))
    if prefix_len == len(body) and body:
        last = body[-1]
        out.append((index.offset(last.end_lineno, last.end_col_offset), " " * last.col_offset))
    return out


def _has_introspection(tree: ast.Module) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _INTROSPECTION:
            return node.id
    return None


def _all_identifiers(tree: ast.Module) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        for attr in ("id", "name", "arg", "attr", "asname", "module"):
            val = getattr(node, attr, None)
            if isinstance(val, str):
                out.add(val)
    return out


def _range_param(ctx: SnippetCtx, key: str, default: tuple[int, int]) -> tuple[int, int]:
    raw = ctx.param(key, None)
    if isinstance(raw, (list, tuple)) and len(raw) == 2:
        return int(raw[0]), int(raw[1])
    return default


# --------------------------------------------------------------------------- #


#: The two mechanisms `S2` fuses. Splitting them is not cosmetic: they target different
#: levels of comprehension (a predicate must be *reasoned about*; a dead helper only has
#: to be *ignored*), so a single condition that emits both cannot attribute a degradation
#: to either. `S2` keeps emitting both and is untouched.
MODES = ("both", "predicates", "helpers")


def transform(ctx: SnippetCtx) -> TransformResult:
    """S2 — inject opaque-predicate blocks and dead module-level helpers."""
    return _run(ctx, mode="both")


def transform_opaque(ctx: SnippetCtx) -> TransformResult:
    """S4 (proposal X3) — opaque predicates only, no dead helpers."""
    return _run(ctx, mode="predicates")


def transform_deadhelpers(ctx: SnippetCtx) -> TransformResult:
    """S3 (proposal X2) — dead module-level helpers only, no opaque predicates."""
    return _run(ctx, mode="helpers")


def _run(ctx: SnippetCtx, *, mode: str = "both") -> TransformResult:
    """Shared body. `mode` gates the two sections; everything else is identical.

    S2 byte-identity is preserved by construction: the `both` path runs exactly the
    original statements in the original order, so it consumes the RNG identically. S3/S4
    draw a *different* stream anyway — `make_ctx` seeds from the condition code — so they
    cannot perturb S2 even in principle. `tests/test_transforms_py.py` pins it regardless.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}; got {mode!r}")
    try:
        tree = ast.parse(ctx.src)
    except SyntaxError as exc:
        raise Bail(f"input does not parse: {exc}") from exc

    fn = next(
        (
            n
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == ctx.entry_point
        ),
        None,
    )
    if fn is None:
        raise Bail(f"no module-level def named {ctx.entry_point!r}")

    probe = _has_introspection(tree)
    if probe is not None:
        return TransformResult(
            ctx.src, False, [f"program calls {probe}()"], [f"introspection:{probe}"]
        )

    rng = ctx.rng
    index = LineIndex(ctx.src)
    data = ctx.src.encode("utf-8")
    taken = _all_identifiers(tree)
    edits = EditList(ctx.src)
    notes: list[str] = []
    skipped: list[str] = []
    styles: list[str] = []

    # The gate enforces conditions.yaml's per-condition `size_cap`; a 9-line program
    # would blow through S2's 4x cap on three junk blocks alone, so the injection is
    # budgeted here instead of being generated blind and rejected five times. 0.85
    # leaves headroom for the blank lines that join the spliced text.
    # The allowance must use the SAME formula as obf/validate.py: the larger of the
    # ratio and a fixed character floor. Budgeting from the ratio alone starves short
    # programs (a 115-char program got 293 chars, not enough for one predicate block),
    # so S2 emitted nothing on exactly the programs the floor exists to protect.
    cap = float(ctx.param("size_cap", 4.0) or 4.0)
    floor_chars = int(ctx.param("size_cap_floor_chars", 0) or 0)
    allowance = max(len(ctx.src) * (cap - 1.0), float(floor_chars))
    budget = max(0, int(allowance * 0.85))
    # A third of the budget is held back for the dead helpers, so a short program does
    # not spend its whole allowance on predicate blocks and end up with the half of S2
    # that is easiest to spot and none of the half that is not. With helpers disabled
    # there is nothing to starve, so the reserve goes to zero and S4 gets the full budget
    # — otherwise S4 would emit systematically fewer predicates than S2 does.
    helper_reserve = budget // 3 if mode == "both" else 0

    # --- opaque predicates in the entry function -------------------------- #
    boundaries = _boundaries(index, data, fn.body) if mode != "helpers" else []
    if mode == "helpers":
        pass  # S3 emits no predicates
    elif not boundaries:
        skipped.append("no_reachable_boundary")
    else:
        lo, hi = _range_param(ctx, "n_predicate_blocks", (1, 3))
        grouped: dict[tuple[int, str], list[str]] = {}
        spent = 0
        for _ in range(rng.randint(lo, hi)):
            off, indent = boundaries[rng.randrange(len(boundaries))]
            # Several blocks may share one boundary: with a single insertion point (a
            # body that opens straight into a loop) that is the only way to honour the
            # configured block count.
            lines, style = _predicate_block(ctx, taken)
            cost = sum(len(indent) + len(ln) + 1 for ln in lines)
            if spent + cost > budget - helper_reserve:
                break
            grouped.setdefault((off, indent), []).extend(lines)
            styles.append(style)
            spent += cost
        for (off, indent), lines in grouped.items():
            edits.add(off, off, "".join(f"{indent}{ln}\n" for ln in lines))
        if grouped:
            notes.append(f"{len(styles)} opaque-predicate block(s) at {len(grouped)} boundary(ies)")
        else:
            skipped.append("predicate_over_size_budget")
        budget -= spent

    # --- dead module-level helpers ---------------------------------------- #
    anchor = _helper_anchor(index, data, tree, fn, rng) if mode != "predicates" else None
    n_helpers = 0
    if mode == "predicates":
        pass  # S4 emits no helpers
    elif anchor is None:
        skipped.append("no_module_anchor")
    else:
        lo, hi = _range_param(ctx, "n_dead_helpers", (1, 2))
        helper_lines: list[str] = []
        spent = 0
        for _ in range(rng.randint(lo, hi)):
            body = _dead_helper(ctx, taken)
            cost = sum(len(ln) + 1 for ln in body) + 1
            if spent + cost > budget:
                break
            helper_lines.extend(body)
            helper_lines.append("")
            spent += cost
            n_helpers += 1
        if n_helpers:
            off, at_eof = anchor
            block = "\n".join(helper_lines).rstrip("\n")
            edits.add(off, off, f"\n{block}\n" if at_eof else f"{block}\n\n")
            notes.append(f"{n_helpers} dead module-level helper(s)")
        else:
            skipped.append("helpers_over_size_budget")

    if not edits.edits:
        return TransformResult(ctx.src, False, notes or ["nothing fits the size budget"], skipped)

    out = edits.apply()
    try:
        ast.parse(out)
    except SyntaxError as exc:  # pragma: no cover — indentation bug guard
        raise Bail(f"injected source does not parse: {exc}") from exc

    return TransformResult(
        out,
        True,
        notes=notes,
        skipped_constructs=skipped,
        extra={
            "mode": mode,
            "n_predicate_blocks": len(styles),
            "predicate_styles": styles,
            "n_dead_helpers": n_helpers,
        },
    )


def _helper_anchor(
    index: LineIndex, data: bytes, tree: ast.Module, fn: ast.stmt, rng: random.Random
) -> tuple[int, bool] | None:
    """Where to splice the dead helpers: before the entry def, or at end of file."""
    if rng.random() < 0.5:
        first = min(
            [fn.lineno] + [d.lineno for d in getattr(fn, "decorator_list", [])]
        )  # decorators precede the `def` line and must not be split from it
        off = index.starts[first - 1]
        if not data[off : index.offset(first, fn.col_offset if first == fn.lineno else 0)].strip():
            return off, False
    if not tree.body:
        return None
    return len(data), True
