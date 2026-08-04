"""Static backward def-use slice of a Python program from its entry point's return.

WHY this exists
---------------
RQ3 asks whether obfuscation-tuning moves attention off *surface* identifiers and onto
the tokens that actually carry the answer. That contrast is only meaningful if we can
say which identifiers are load-bearing. A rename-based obfuscation (L1b) changes every
name, so "identifier mass" alone cannot distinguish a decoy name from the accumulator
that produces the return value. The backward slice supplies that split: names on the
transitive def-use closure of the entry function's return expression(s) are
`dataflow_critical`; every other identifier occurrence stays plain `identifier`.

Method (deliberately *static* and over-approximate)
--------------------------------------------------
Per-scope def-use chains are collected for assignments, annotated/augmented assigns,
for/comprehension targets, `with ... as`, walrus, except-handler names, imports, and
function/class definitions. Each definition records (a) the names read by its RHS and
(b) the names read by every `if`/`while`/`for` test that guards it — a def under a
guard is only reachable through that guard, so the guard's names are part of the
closure. A function-definition binding resolves its RHS names *inside* the function's
own scope, which is what pulls a helper's body onto the slice when the helper is called.
Seeds are the names loaded in every `return` of the entry function (or the lambda body
if the entry point is a lambda). Iterate to a fixed point.

Rejected alternatives
---------------------
* Dynamic slicing by tracing an execution: exact, but it needs a working interpreter run
  per (program, condition) and would silently drop programs whose obfuscated variant is
  slow; the gate already executes everything once and we do not want a second dependency.
* Name-level (scope-blind) closure: much shorter, but on S1/S2 variants the dispatch
  state variable and dead-helper locals collide with real locals, inflating the
  dataflow class exactly in the conditions the RQ3 contrast is about.
* SSA/CFG construction: correct for reassignment order, but the metric is a *between-
  condition contrast* on the same parent program, so a constant over-approximation
  cancels; the extra machinery is not worth the failure modes.

Span marking is scope-aware: an occurrence is critical iff (innermost enclosing scope
chain of that character position, name) is in the closure.
"""
from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable

__all__ = ["Slice", "ScopeInfo", "slice_python"]


@dataclass(frozen=True)
class ScopeInfo:
    """A lexical scope, addressed by character span so tokens can be located in it."""

    sid: int
    parent: int | None
    kind: str  # module | function | lambda | class
    name: str | None
    start: int
    end: int


@dataclass
class Slice:
    """Result of a backward slice. Shared shape with slicer_js.Slice."""

    language: str
    entry_point: str | None
    critical: frozenset[tuple[int | None, str]]  # (scope id, name); None scope = free/global
    scopes: tuple[ScopeInfo, ...]
    iterations: int
    ok: bool
    notes: tuple[str, ...] = ()
    seeds: frozenset[str] = frozenset()

    @property
    def critical_names(self) -> frozenset[str]:
        return frozenset(n for _, n in self.critical)

    def scope_chain(self, pos: int) -> list[int]:
        """Innermost-first list of scope ids whose span contains `pos`."""
        hits = [s for s in self.scopes if s.start <= pos < s.end]
        hits.sort(key=lambda s: s.end - s.start)
        return [s.sid for s in hits]

    def is_critical(self, pos: int, name: str) -> bool:
        if (None, name) in self.critical:
            return True
        for sid in self.scope_chain(pos):
            if (sid, name) in self.critical:
                return True
        return False


@dataclass
class _Def:
    name: str
    scope: int
    resolve_scope: int  # scope in which value/guard names are looked up
    value_names: frozenset[str]
    guard_names: frozenset[str]
    kind: str


@dataclass
class _Scope:
    sid: int
    parent: int | None
    kind: str
    name: str | None
    start: int
    end: int
    defs: dict[str, list[_Def]] = field(default_factory=dict)
    declared_global: set[str] = field(default_factory=set)
    declared_nonlocal: set[str] = field(default_factory=set)


def _line_offsets(code: str) -> list[int]:
    offs = [0]
    for line in code.splitlines(keepends=True):
        offs.append(offs[-1] + len(line))
    return offs


class _Positions:
    """AST (lineno, col_offset) -> absolute character offset.

    `col_offset` is a UTF-8 *byte* offset inside the line (CPython contract), so it is
    decoded back to a character count rather than used directly.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        self.lines = code.splitlines(keepends=True)
        self.offs = _line_offsets(code)

    def abs(self, lineno: int, col: int) -> int:
        i = lineno - 1
        if i < 0:
            return 0
        if i >= len(self.lines):
            return len(self.code)
        prefix = self.lines[i].encode("utf-8")[:col].decode("utf-8", errors="ignore")
        return self.offs[i] + len(prefix)

    def span(self, node: ast.AST) -> tuple[int, int]:
        start = self.abs(getattr(node, "lineno", 1), getattr(node, "col_offset", 0))
        end_lineno = getattr(node, "end_lineno", None)
        end_col = getattr(node, "end_col_offset", None)
        if end_lineno is None or end_col is None:
            return start, len(self.code)
        return start, self.abs(end_lineno, end_col)


def _names_loaded(node: ast.AST | None) -> set[str]:
    """Names read by an expression. Attribute bases count; attribute names do not."""
    out: set[str] = set()
    if node is None:
        return out
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            out.add(n.id)
        elif isinstance(n, (ast.Attribute, ast.Subscript)):
            base = n
            while isinstance(base, (ast.Attribute, ast.Subscript)):
                base = base.value
            if isinstance(base, ast.Name):
                out.add(base.id)
    return out


def _names_stored(target: ast.AST) -> set[str]:
    """Names bound by an assignment target. `a[i] = x` / `a.f = x` bind (and read) `a`."""
    out: set[str] = set()
    for n in ast.walk(target):
        if isinstance(n, ast.Name):
            out.add(n.id)
    return out


class _Builder:
    """Builds scopes + per-scope definitions, tracking the guard stack."""

    def __init__(self, code: str, tree: ast.Module) -> None:
        self.code = code
        self.pos = _Positions(code)
        self.scopes: list[_Scope] = []
        self.returns: dict[int, set[str]] = {}
        self.loads: dict[int, set[str]] = {}
        self.notes: list[str] = []
        root = self._new_scope(None, "module", None, 0, len(code))
        self.module_sid = root.sid
        self.visit_body(tree.body, root.sid, frozenset())

    # -- scopes ---------------------------------------------------------------
    def _new_scope(self, parent: int | None, kind: str, name: str | None, start: int, end: int) -> _Scope:
        s = _Scope(sid=len(self.scopes), parent=parent, kind=kind, name=name, start=start, end=end)
        self.scopes.append(s)
        self.returns.setdefault(s.sid, set())
        self.loads.setdefault(s.sid, set())
        return s

    def add_def(self, sid: int, name: str, *, value_names: Iterable[str], guards: Iterable[str],
                kind: str, resolve_scope: int | None = None) -> None:
        sc = self.scopes[sid]
        d = _Def(name=name, scope=sid, resolve_scope=sid if resolve_scope is None else resolve_scope,
                 value_names=frozenset(value_names), guard_names=frozenset(guards), kind=kind)
        sc.defs.setdefault(name, []).append(d)

    # -- traversal ------------------------------------------------------------
    def visit_body(self, body: list[ast.stmt], sid: int, guards: frozenset[str]) -> None:
        for stmt in body:
            self.visit_stmt(stmt, sid, guards)

    def visit_stmt(self, node: ast.stmt, sid: int, guards: frozenset[str]) -> None:
        self.loads[sid] |= _names_loaded(node)
        self._collect_inline(node, sid, guards)

        if isinstance(node, ast.Assign):
            vn = _names_loaded(node.value)
            if isinstance(node.value, ast.Lambda):
                lam_sid = self._lambda_scope(node.value, sid, guards)
                for t in node.targets:
                    for nm in _names_stored(t):
                        self.add_def(sid, nm, value_names=self.loads[lam_sid], guards=guards,
                                     kind="lambda", resolve_scope=lam_sid)
                return
            for t in node.targets:
                for nm in _names_stored(t):
                    self.add_def(sid, nm, value_names=vn, guards=guards, kind="assign")

        elif isinstance(node, ast.AnnAssign):
            vn = _names_loaded(node.value)
            for nm in _names_stored(node.target):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind="annassign")

        elif isinstance(node, ast.AugAssign):
            vn = _names_loaded(node.value) | _names_stored(node.target)
            for nm in _names_stored(node.target):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind="augassign")

        elif isinstance(node, (ast.For, ast.AsyncFor)):
            vn = _names_loaded(node.iter)
            for nm in _names_stored(node.target):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind="for_target")
            inner = guards | vn  # the iterable guards every def in the loop body
            self.visit_body(node.body, sid, inner)
            self.visit_body(node.orelse, sid, inner)

        elif isinstance(node, (ast.While, ast.If)):
            inner = guards | _names_loaded(node.test)
            self.visit_body(node.body, sid, inner)
            self.visit_body(node.orelse, sid, inner)

        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                vn = _names_loaded(item.context_expr)
                if item.optional_vars is not None:
                    for nm in _names_stored(item.optional_vars):
                        self.add_def(sid, nm, value_names=vn, guards=guards, kind="with")
            self.visit_body(node.body, sid, guards)

        elif isinstance(node, ast.Try):
            self.visit_body(node.body, sid, guards)
            for h in node.handlers:
                if h.name:
                    self.add_def(sid, h.name, value_names=_names_loaded(h.type), guards=guards,
                                 kind="except")
                self.visit_body(h.body, sid, guards)
            self.visit_body(node.orelse, sid, guards)
            self.visit_body(node.finalbody, sid, guards)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end = self.pos.span(node)
            child = self._new_scope(sid, "function", node.name, start, end)
            self._params(node.args, child.sid, guards)
            self.visit_body(node.body, child.sid, frozenset())
            # The binding for the function *name* resolves its reads inside the function's
            # own scope: calling the helper is what drags the helper's body onto the slice.
            self.add_def(sid, node.name,
                         value_names=self.loads[child.sid] | self.returns[child.sid],
                         guards=guards, kind="funcdef", resolve_scope=child.sid)

        elif isinstance(node, ast.ClassDef):
            start, end = self.pos.span(node)
            child = self._new_scope(sid, "class", node.name, start, end)
            self.visit_body(node.body, child.sid, frozenset())
            self.add_def(sid, node.name, value_names=self.loads[child.sid], guards=guards,
                         kind="classdef", resolve_scope=child.sid)

        elif isinstance(node, ast.Return):
            self.returns[sid] |= _names_loaded(node.value)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                bound = a.asname or a.name.split(".")[0]
                self.add_def(sid, bound, value_names=(), guards=guards, kind="import")

        elif isinstance(node, ast.Global):
            self.scopes[sid].declared_global |= set(node.names)
        elif isinstance(node, ast.Nonlocal):
            self.scopes[sid].declared_nonlocal |= set(node.names)

    def _params(self, args: ast.arguments, sid: int, guards: frozenset[str]) -> None:
        allargs = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
        if args.vararg:
            allargs.append(args.vararg)
        if args.kwarg:
            allargs.append(args.kwarg)
        for a in allargs:
            # Parameters are roots of the closure: no incoming def-use edge.
            self.add_def(sid, a.arg, value_names=(), guards=guards, kind="param")

    def _lambda_scope(self, node: ast.Lambda, parent: int, guards: frozenset[str]) -> int:
        start, end = self.pos.span(node)
        child = self._new_scope(parent, "lambda", None, start, end)
        self._params(node.args, child.sid, guards)
        body_names = _names_loaded(node.body)
        self.loads[child.sid] |= body_names
        self.returns[child.sid] |= body_names  # a lambda body *is* its return expression
        return child.sid

    def _collect_inline(self, node: ast.AST, sid: int, guards: frozenset[str]) -> None:
        """Walrus targets, comprehension targets and bare lambdas anywhere in a statement.

        Comprehensions get their own scope in Python 3, but a comprehension target is
        never visible outside it and never reassigned, so folding it into the enclosing
        scope cannot create a false def-use edge — only a redundant one.
        """
        for n in ast.walk(node):
            if isinstance(n, ast.NamedExpr):
                for nm in _names_stored(n.target):
                    self.add_def(sid, nm, value_names=_names_loaded(n.value), guards=guards,
                                 kind="walrus")
            elif isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                for comp in n.generators:
                    vn = _names_loaded(comp.iter)
                    ifs = set().union(*(_names_loaded(i) for i in comp.ifs)) if comp.ifs else set()
                    for nm in _names_stored(comp.target):
                        self.add_def(sid, nm, value_names=vn, guards=guards | frozenset(ifs),
                                     kind="comprehension")
            elif isinstance(n, ast.Lambda) and not isinstance(node, ast.Assign):
                self._lambda_scope(n, sid, guards)


def _find_entry(tree: ast.Module, entry_point: str | None) -> tuple[ast.AST | None, str | None]:
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    lambdas = [
        (t.id, n.value)
        for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Lambda)
        for t in n.targets if isinstance(t, ast.Name)
    ]
    if entry_point:
        for f in funcs:
            if f.name == entry_point:
                return f, f.name
        for nm, lam in lambdas:
            if nm == entry_point:
                return lam, nm
    if funcs:
        return funcs[-1], funcs[-1].name
    if lambdas:
        return lambdas[-1][1], lambdas[-1][0]
    return None, entry_point


def slice_python(code: str, entry_point: str | None = None) -> Slice:
    """Backward def-use slice from the entry function's return expression(s)."""
    notes: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return Slice("python", entry_point, frozenset(), (), 0, False, (f"parse error: {e}",))

    b = _Builder(code, tree)
    entry_node, entry_name = _find_entry(tree, entry_point)
    if entry_node is None:
        notes.append("no function definition found; seeding from module-level loads")
        entry_sid = b.module_sid
        seeds = set(b.returns[b.module_sid]) or set(b.loads[b.module_sid])
    else:
        start, _ = b.pos.span(entry_node)
        chain = [s for s in b.scopes if s.start <= start < s.end and s.kind in ("function", "lambda")]
        chain.sort(key=lambda s: s.end - s.start)
        entry_sid = chain[0].sid if chain else b.module_sid
        seeds = set(b.returns.get(entry_sid, set()))
        if not seeds:
            notes.append("entry function has no return with names; falling back to all loads")
            seeds = set(b.loads.get(entry_sid, set()))

    def resolve(sid: int, name: str) -> int | None:
        cur: int | None = sid
        while cur is not None:
            sc = b.scopes[cur]
            if name in sc.declared_global:
                return b.module_sid if name in b.scopes[b.module_sid].defs else None
            if name in sc.defs:
                return cur
            cur = sc.parent
        return None

    critical: set[tuple[int | None, str]] = set()
    # The entry function's own name is on the slice (a recursive call reads it), but it is
    # seeded as a TERMINAL: expanding its funcdef binding would pull in every name the
    # entry body reads — including dead stores and decoy locals — and collapse the
    # identifier/dataflow_critical distinction the whole metric rests on.
    if entry_name:
        critical.add((resolve(entry_sid, entry_name), entry_name))
    work: deque[tuple[int, str]] = deque((entry_sid, n) for n in seeds)
    iterations = 0
    max_iter = 200_000  # guards against a pathological program; never hit in practice

    while work and iterations < max_iter:
        iterations += 1
        sid, name = work.popleft()
        owner = resolve(sid, name)
        key: tuple[int | None, str] = (owner, name)
        if key in critical:
            continue
        critical.add(key)
        if owner is None:
            continue  # free name / builtin: a root, nothing further to expand
        for d in b.scopes[owner].defs.get(name, []):
            for nxt in d.value_names | d.guard_names:
                work.append((d.resolve_scope, nxt))

    if iterations >= max_iter:
        notes.append("fixed-point iteration cap hit; slice may be incomplete")

    scopes = tuple(ScopeInfo(s.sid, s.parent, s.kind, s.name, s.start, s.end) for s in b.scopes)
    return Slice(
        language="python", entry_point=entry_name, critical=frozenset(critical), scopes=scopes,
        iterations=iterations, ok=True, notes=tuple(notes + b.notes), seeds=frozenset(seeds),
    )
