"""S1 — control-flow flattening of the entry function into a dispatch loop.

Shape (configs/conditions.yaml S1: randomized non-sequential state ids, shuffled cases)

    def entry(...):
        _sn_<hex> = object()            # only when a `for` was desugared
        _st_<hex> = 41
        while _st_<hex> != -1:
            if _st_<hex> == 41:
                <verbatim statements>
                _st_<hex> = 17
            elif _st_<hex> == 17:
                _st_<hex> = 63 if <test> else 8
            ...
            else:
                raise RuntimeError(...)

This is the László & Kiss switch-dispatch construction (the same IR the Java
obfuscator in ../allocation_replication uses), retargeted to Python. Two things get
much easier in Python and one gets harder:

* Easier: no declarations, so nothing has to be hoisted. A local written inside a
  dispatch case is the same function-scope local it was inside the original block, and
  closures over it keep working unchanged. The Java port's whole hoisting/shadowing
  apparatus disappears.
* Easier: `-1` can be the exit state because falling out of the `while` reaches the end
  of the function, which is exactly the implicit `return None` the original had.
* Harder: `for` has no index form to desugar into. We use the *total* protocol
  `it = iter(x)` / `v = next(it, SENTINEL)` / `if v is SENTINEL: exit`, with a
  per-call `object()` sentinel. `try/except StopIteration` was rejected: it would put a
  handler around user code and swallow a StopIteration the body itself raised.

Emission is via `ast` node reuse + `ast.unparse` rather than text splicing, because
re-indenting statement *text* corrupts multi-line string literals — the corpus is full
of programs whose output is such a string.

BAIL policy — correctness beats coverage. try/except/finally, with, yield, async,
match, loop-else, decorators and global/nonlocal are left verbatim and recorded in
`skipped_constructs`; nested def/class bodies are atomic single statements.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Sequence

from obtune.obf.base import Bail, EditList, LineIndex, SnippetCtx, TransformResult, fresh_name

_EXIT = -1  # internal sentinel state: fall off the end of the function

#: Statements copied into a dispatch case verbatim (they always complete normally).
_PLAIN = (
    ast.Expr, ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Delete, ast.Assert,
    ast.Import, ast.ImportFrom, ast.Pass, ast.FunctionDef, ast.ClassDef,
)

#: Builtins the emitted dispatch depends on. If the program rebinds any of them the
#: rewrite would silently call user code, so we decline instead.
_REQUIRED_BUILTINS = ("iter", "next", "object", "RuntimeError")


class _Loop:
    """Jump targets for `break` / `continue` in the innermost enclosing loop."""

    __slots__ = ("brk", "cont")

    def __init__(self, brk: int, cont: int) -> None:
        self.brk = brk
        self.cont = cont


@dataclass
class _Block:
    """One basic unit == one arm of the dispatch chain."""

    sid: int
    stmts: list[ast.stmt] = field(default_factory=list)
    kind: str = "goto"  # goto | cond | exit
    target: int | None = None
    test: ast.expr | None = None
    t_target: int | None = None
    f_target: int | None = None


def _bail_reason(body: Sequence[ast.stmt]) -> str | None:
    """First construct in the entry function's own scope we refuse to linearise.

    Nested function/class bodies are not inspected: they are emitted as single atomic
    statements, so whatever they contain is irrelevant.
    """
    stack: list[ast.AST] = list(body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.Try, ast.TryStar)):
            return "try"
        if isinstance(node, (ast.With, ast.AsyncWith)):
            return "with"
        if isinstance(node, ast.Match):
            return "match"
        if isinstance(node, (ast.AsyncFor, ast.AsyncFunctionDef)):
            return "async"
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            return "yield"
        if isinstance(node, ast.Await):
            return "await"
        if isinstance(node, ast.Global):
            return "global"
        if isinstance(node, ast.Nonlocal):
            return "nonlocal"
        if isinstance(node, (ast.For, ast.While)) and node.orelse:
            return "loop_else"
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Lambda)):
            continue  # atomic unit
        stack.extend(ast.iter_child_nodes(node))
    return None


def _bound_names(tree: ast.Module) -> set[str]:
    """Every name the module binds anywhere — used to detect builtin shadowing."""
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.arg):
            out.add(node.arg)
        elif isinstance(node, ast.alias):
            out.add(node.asname or node.name.split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
    return out


def _all_identifiers(tree: ast.Module) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        for attr in ("id", "name", "arg", "attr", "asname", "module"):
            val = getattr(node, attr, None)
            if isinstance(val, str):
                out.add(val)
    return out


def _load(name: str) -> ast.Name:
    return ast.Name(id=name, ctx=ast.Load())


def _store(name: str) -> ast.Name:
    return ast.Name(id=name, ctx=ast.Store())


class _Flattener:
    def __init__(self, ctx: SnippetCtx, fn: ast.FunctionDef, taken: set[str]) -> None:
        self.ctx = ctx
        self.fn = fn
        self.taken = taken
        self.blocks: dict[int, _Block] = {}
        self._next_sid = 0
        self.state_var = self._tmp("st")
        self.sentinel: str | None = None

    def _tmp(self, stem: str) -> str:
        return fresh_name(lambda: f"_{stem}_{self.ctx.rng.randrange(0x10000):04x}", self.taken)

    def _need_sentinel(self) -> str:
        if self.sentinel is None:
            self.sentinel = self._tmp("sn")
        return self.sentinel

    def _sid(self) -> int:
        s = self._next_sid
        self._next_sid += 1
        self.blocks[s] = _Block(sid=s)
        return s

    # -- linearisation ----------------------------------------------------- #

    def build_seq(self, nodes: Sequence[ast.stmt], nxt: int, loop: _Loop | None) -> int:
        cur = nxt
        for node in reversed(list(nodes)):
            cur = self.build_stmt(node, cur, loop)
        return cur

    def build_stmt(self, node: ast.stmt, nxt: int, loop: _Loop | None) -> int:
        if isinstance(node, _PLAIN):
            sid = self._sid()
            self.blocks[sid].stmts = [] if isinstance(node, ast.Pass) else [node]
            self.blocks[sid].target = nxt
            return sid
        if isinstance(node, (ast.Return, ast.Raise)):
            sid = self._sid()
            self.blocks[sid].stmts = [node]
            self.blocks[sid].kind = "exit"
            return sid
        if isinstance(node, ast.Break):
            if loop is None:
                raise Bail("break outside a flattened loop")
            sid = self._sid()
            self.blocks[sid].target = loop.brk
            return sid
        if isinstance(node, ast.Continue):
            if loop is None:
                raise Bail("continue outside a flattened loop")
            sid = self._sid()
            self.blocks[sid].target = loop.cont
            return sid
        if isinstance(node, ast.If):
            then_sid = self.build_seq(node.body, nxt, loop)
            else_sid = self.build_seq(node.orelse, nxt, loop) if node.orelse else nxt
            sid = self._sid()
            b = self.blocks[sid]
            b.kind, b.test, b.t_target, b.f_target = "cond", node.test, then_sid, else_sid
            return sid
        if isinstance(node, ast.While):
            if node.orelse:
                raise Bail("while-else")
            guard = self._sid()
            body_sid = self.build_seq(node.body, guard, _Loop(brk=nxt, cont=guard))
            g = self.blocks[guard]
            g.kind, g.test, g.t_target, g.f_target = "cond", node.test, body_sid, nxt
            return guard
        if isinstance(node, ast.For):
            if node.orelse:
                raise Bail("for-else")
            return self._build_for(node, nxt)
        raise Bail(f"unsupported statement {type(node).__name__}")

    def _build_for(self, node: ast.For, nxt: int) -> int:
        """`for T in X: B` via the total iterator protocol (no exception handling).

        `next(it, SENTINEL)` cannot raise StopIteration, so the loop needs no
        try/except — which matters because a try/except here would also swallow a
        StopIteration raised by the loop *body*.
        """
        sentinel = self._need_sentinel()
        it = self._tmp("it")
        val = self._tmp("v")

        guard = self._sid()
        head = self._sid()
        body_sid = self.build_seq(node.body, guard, _Loop(brk=nxt, cont=guard))

        self.blocks[head].stmts = [ast.Assign(targets=[node.target], value=_load(val))]
        self.blocks[head].target = body_sid

        g = self.blocks[guard]
        g.stmts = [
            ast.Assign(
                targets=[_store(val)],
                value=ast.Call(func=_load("next"), args=[_load(it), _load(sentinel)], keywords=[]),
            )
        ]
        g.kind = "cond"
        g.test = ast.Compare(left=_load(val), ops=[ast.IsNot()], comparators=[_load(sentinel)])
        g.t_target, g.f_target = head, nxt

        pre = self._sid()
        self.blocks[pre].stmts = [
            ast.Assign(
                targets=[_store(it)],
                value=ast.Call(func=_load("iter"), args=[node.iter], keywords=[]),
            )
        ]
        self.blocks[pre].target = guard
        return pre

    # -- emission ---------------------------------------------------------- #

    def run(self) -> tuple[ast.FunctionDef, dict[str, Any]]:
        entry = self.build_seq(self.fn.body, _EXIT, None)
        if not self.blocks:
            raise Bail("empty function body")
        min_states = int(self.ctx.param("min_states", 3) or 0)
        if len(self.blocks) < min_states:
            raise Bail(f"only {len(self.blocks)} states (min_states={min_states})")

        rng = self.ctx.rng
        n = len(self.blocks)
        # Non-sequential ids: sampled from a range several times larger than the block
        # count so consecutive states are never consecutive integers. 11.. keeps every
        # id clear of the -1 exit sentinel and of small literals in the program.
        ids = rng.sample(range(11, 11 + max(64, n * 9)), n)
        sids = sorted(self.blocks)
        if self.ctx.param("randomize_state_ids", True):
            rng.shuffle(sids)
        mapping = {s: ids[i] for i, s in enumerate(sids)}
        mapping[_EXIT] = -1

        order = sorted(self.blocks)
        if self.ctx.param("shuffle_cases", True):
            rng.shuffle(order)

        st = self.state_var
        arms: list[tuple[int, list[ast.stmt]]] = []
        for sid in order:
            b = self.blocks[sid]
            body = list(b.stmts)
            if b.kind == "goto":
                body.append(ast.Assign(targets=[_store(st)], value=ast.Constant(mapping[b.target])))
            elif b.kind == "cond":
                assert b.test is not None
                body.append(
                    ast.Assign(
                        targets=[_store(st)],
                        value=ast.IfExp(
                            test=b.test,
                            body=ast.Constant(mapping[b.t_target]),
                            orelse=ast.Constant(mapping[b.f_target]),
                        ),
                    )
                )
            # "exit" arms end in return/raise; nothing follows them.
            arms.append((mapping[sid], body))

        # The final `else` is unreachable by construction; it exists so a corrupted
        # state can never fall through the dispatch silently.
        chain: list[ast.stmt] = [
            ast.Raise(
                exc=ast.Call(
                    func=_load("RuntimeError"),
                    args=[ast.Constant("invalid dispatch state")],
                    keywords=[],
                ),
                cause=None,
            )
        ]
        for state, body in reversed(arms):
            chain = [
                ast.If(
                    test=ast.Compare(left=_load(st), ops=[ast.Eq()], comparators=[ast.Constant(state)]),
                    body=body,
                    orelse=chain,
                )
            ]

        loop = ast.While(
            test=ast.Compare(left=_load(st), ops=[ast.NotEq()], comparators=[ast.Constant(-1)]),
            body=chain,
            orelse=[],
        )
        prologue: list[ast.stmt] = []
        if self.sentinel is not None:
            prologue.append(
                ast.Assign(
                    targets=[_store(self.sentinel)],
                    value=ast.Call(func=_load("object"), args=[], keywords=[]),
                )
            )
        prologue.append(ast.Assign(targets=[_store(st)], value=ast.Constant(mapping[entry])))

        new_fn = ast.FunctionDef(
            name=self.fn.name,
            args=self.fn.args,
            body=prologue + [loop],
            decorator_list=[],
            returns=self.fn.returns,
            type_comment=None,
            type_params=list(getattr(self.fn, "type_params", []) or []),
        )
        # `ast.unparse` reads `lineno` (for type-comment lookup) even though it emits
        # none of the position data, so synthesised nodes need locations filled in.
        ast.copy_location(new_fn, self.fn)
        ast.fix_missing_locations(new_fn)
        meta = {
            "n_states": n,
            "state_ids": [mapping[s] for s in sorted(self.blocks)],
            "state_var": st,
            "desugared_for": self.sentinel is not None,
        }
        return new_fn, meta


def transform(ctx: SnippetCtx) -> TransformResult:
    """S1 — flatten only the entry function; every other top-level def is untouched."""
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
    skipped: list[str] = []
    if isinstance(fn, ast.AsyncFunctionDef):
        return TransformResult(ctx.src, False, ["entry is async"], ["async_entry"])
    if fn.decorator_list:
        return TransformResult(ctx.src, False, ["entry is decorated"], ["decorator"])

    shadowed = sorted(set(_REQUIRED_BUILTINS) & _bound_names(tree))
    if shadowed:
        return TransformResult(
            ctx.src, False, [f"program rebinds {shadowed}"], [f"shadowed_builtin:{','.join(shadowed)}"]
        )

    reason = _bail_reason(fn.body)
    if reason is not None:
        return TransformResult(ctx.src, False, [f"entry body contains {reason}"], [reason])

    taken = _all_identifiers(tree)
    try:
        new_fn, meta = _Flattener(ctx, fn, taken).run()
    except Bail as exc:
        return TransformResult(ctx.src, False, [str(exc)], [str(exc)])
    except RecursionError:
        return TransformResult(ctx.src, False, ["body too deeply nested"], ["recursion"])

    index = LineIndex(ctx.src)
    start = index.offset(fn.lineno, fn.col_offset)
    end = index.offset(fn.end_lineno, fn.end_col_offset)
    if fn.col_offset != 0:
        raise Bail("entry function is not at module level")

    edits = EditList(ctx.src)
    edits.add(start, end, ast.unparse(new_fn))
    out = edits.apply()
    try:
        ast.parse(out)
    except SyntaxError as exc:  # pragma: no cover — unparse round-trip failure
        raise Bail(f"flattened source does not parse: {exc}") from exc

    return TransformResult(
        out,
        True,
        notes=[f"flattened {fn.name} into {meta['n_states']} dispatch states"],
        skipped_constructs=skipped,
        extra=meta,
    )
