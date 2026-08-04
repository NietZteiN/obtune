"""Scope-aware Python identifier renaming — serves L1r, L2 and (via adversarial.py) L1b.

Why symtable + ast rather than tree-sitter
------------------------------------------
Which *binding* an identifier occurrence refers to is not recoverable from a CST.
Python resolves a name against a scope chain that skips class bodies for free
variables, honours `global`/`nonlocal`, and — since 3.12 (PEP 709) — inlines
list/set/dict comprehensions into the enclosing scope while keeping generator
expressions in their own block. Reimplementing those rules is how renamers silently
capture variables, so binding facts come from `symtable` (CPython's own answer) and
`ast` is used only for occurrence byte spans. The two trees are paired by
(block name, line) and any pairing failure raises `Bail` rather than guessing.

Rejected alternatives
---------------------
* regex / `str.replace` on identifiers — rewrites the same characters inside string
  literals, and the corpus is full of programs whose output *is* such a string.
* mutate `Name.id` then `ast.unparse` — loses the original formatting, so an L2
  stimulus would no longer be line-comparable with its L0 parent. (`canonical_text`
  opts into unparsing on purpose, for dedup, where formatting must be normalized.)

Never renamed: builtins, imported names, attribute names, keyword-argument names,
dict string keys, `self`/`cls`, dunders, and anything bound in a class body (methods
and class attributes are reached through attribute syntax, which we deliberately do
not touch, so renaming their binding would break the reference).
"""
from __future__ import annotations

import ast
import builtins
import keyword
import random
import re
import symtable
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from obtune.obf.base import (
    Bail,
    EditList,
    LineIndex,
    SnippetCtx,
    TransformResult,
    adversarial_name,
    fresh_name,
    hex_name,
    seq_name,
)

#: Names a generated identifier may never take, and bindings we never rename.
#: Every builtin is listed whether or not the program uses it, so the set is a
#: constant — that is what lets `seq` double as an alpha-equivalence canonicalizer.
RESERVED: frozenset[str] = frozenset(
    set(dir(builtins)) | set(keyword.kwlist) | set(keyword.softkwlist) | {"self", "cls"}
)

_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef, ast.GeneratorExp)
_SCOPE_TABLE_NAME = {ast.Lambda: "lambda", ast.GeneratorExp: "genexpr"}

_DECL_NAME = "(?:async[ \t]+)?(?:def|class)[ \t]+"

RenameStyle = str  # "hex" | "seq" | "adversarial"


@dataclass
class _Scope:
    sid: int
    table: symtable.SymbolTable
    node: ast.AST | None
    parent: "_Scope | None"
    kind: str  # module | function | class
    path: str
    bound: set[str] = field(default_factory=set)
    blocked: set[str] = field(default_factory=set)


@dataclass
class _Occurrence:
    start: int
    end: int
    name: str
    binder: int  # _Scope.sid
    kind: str  # var | func | class


@dataclass
class _Binding:
    scope: int
    name: str
    kind: str
    first: int  # byte offset of the first occurrence — the order seq names follow
    occurrences: list[_Occurrence] = field(default_factory=list)


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


# --------------------------------------------------------------------------- #
# Scope tree: symtable blocks paired with the AST nodes that opened them


def _expected_table_name(node: ast.AST) -> str:
    for cls, name in _SCOPE_TABLE_NAME.items():
        if isinstance(node, cls):
            return name
    return getattr(node, "name", "?")


def _arg_defaults(args: ast.arguments) -> list[ast.AST]:
    return [d for d in list(args.defaults) + list(args.kw_defaults) if d is not None]


def _all_args(args: ast.arguments) -> list[ast.arg]:
    out = list(args.posonlyargs) + list(args.args)
    if args.vararg is not None:
        out.append(args.vararg)
    out += list(args.kwonlyargs)
    if args.kwarg is not None:
        out.append(args.kwarg)
    return out


def _arg_annotations(args: ast.arguments) -> list[ast.AST]:
    return [a.annotation for a in _all_args(args) if a.annotation is not None]


def _outer_parts(node: ast.AST) -> list[ast.AST]:
    """Sub-nodes of a scope opener that are evaluated in the ENCLOSING scope."""
    out: list[ast.AST] = []
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        out.extend(_arg_defaults(node.args))
        out.extend(node.decorator_list)
        out.extend(_arg_annotations(node.args))
        if node.returns is not None:
            out.append(node.returns)
    elif isinstance(node, ast.ClassDef):
        out.extend(node.bases)
        out.extend(k.value for k in node.keywords)
        out.extend(node.decorator_list)
    elif isinstance(node, ast.Lambda):
        out.extend(_arg_defaults(node.args))
    elif isinstance(node, ast.GeneratorExp):
        out.append(node.generators[0].iter)  # evaluated eagerly, outside the block
    return out


def _scope_body(node: ast.AST) -> list[ast.AST]:
    """The parts of a scope opener that live INSIDE the block it opens."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return list(node.body)
    if isinstance(node, ast.Lambda):
        return [node.body]
    if isinstance(node, ast.GeneratorExp):
        inner: list[ast.AST] = []
        for i, gen in enumerate(node.generators):
            inner.append(gen.target)
            if i > 0:
                inner.append(gen.iter)
            inner.extend(gen.ifs)
        inner.append(node.elt)
        return inner
    raise Bail(f"unhandled scope opener {type(node).__name__}")


def _scope_openers(nodes: Iterable[ast.AST]) -> list[ast.AST]:
    """Scope-opening nodes directly under `nodes`, without descending into the blocks
    they open. Emitted outer-parts-first, matching CPython's symtable visit order."""
    found: list[ast.AST] = []

    def visit(n: ast.AST) -> None:
        if isinstance(n, _SCOPE_NODES):
            for sub in _outer_parts(n):
                visit(sub)
            found.append(n)
            return
        for child in ast.iter_child_nodes(n):
            visit(child)

    for node in nodes:
        visit(node)
    return found


class _ScopeTree:
    def __init__(self, tree: ast.Module, table: symtable.SymbolTable) -> None:
        self.scopes: list[_Scope] = []
        root = self._new(table, None, None, "module")
        self._pair(tree.body, root)

    def _new(
        self, table: symtable.SymbolTable, node: ast.AST | None, parent: _Scope | None, kind: str
    ) -> _Scope:
        path = table.get_name() if parent is None else f"{parent.path}.{table.get_name()}"
        scope = _Scope(sid=len(self.scopes), table=table, node=node, parent=parent, kind=kind, path=path)
        for sym in table.get_symbols():
            name = sym.get_name()
            if not name.isidentifier():
                continue  # symtable's synthetic ".0" genexpr argument
            if sym.is_local() or sym.is_parameter():
                scope.bound.add(name)
                if sym.is_imported() or name in RESERVED or _is_dunder(name):
                    scope.blocked.add(name)
        self.scopes.append(scope)
        return scope

    def _pair(self, body: Iterable[ast.AST], scope: _Scope) -> None:
        """Attach every scope opener under `body` to its symtable child block.

        Matching is by (block name, line) rather than by position: CPython visits a
        decorated class's decorators *after* its block, so a purely positional pairing
        would silently misalign. Anything that cannot be matched raises Bail.
        """
        children = list(scope.table.get_children())
        used = [False] * len(children)
        openers = _scope_openers(body)
        for node in openers:
            want = _expected_table_name(node)
            line = getattr(node, "lineno", -1)
            pick = _match_child(children, used, want, line)
            if pick is None:
                raise Bail(f"no symtable block for {want!r} at line {line} under {scope.path}")
            used[pick] = True
            child_table = children[pick]
            kind = "class" if isinstance(node, ast.ClassDef) else child_table.get_type()
            if kind not in ("module", "function", "class"):
                kind = "function"
            child = self._new(child_table, node, scope, kind)
            self._pair(_scope_body(node), child)
        if not all(used):
            missing = [children[i].get_name() for i, u in enumerate(used) if not u]
            raise Bail(f"unpaired symtable block(s) under {scope.path}: {missing}")

    def by_node(self) -> dict[int, _Scope]:
        return {id(s.node): s for s in self.scopes if s.node is not None}


def _match_child(children: list, used: list[bool], name: str, line: int) -> int | None:
    for i, table in enumerate(children):
        if not used[i] and table.get_name() == name and table.get_lineno() == line:
            return i
    for i, table in enumerate(children):  # PEP 695 blocks etc. can shift the line
        if not used[i] and table.get_name() == name:
            return i
    return None


# --------------------------------------------------------------------------- #
# Occurrence collection


class _Collector(ast.NodeVisitor):
    """Records every identifier occurrence together with the scope that binds it."""

    def __init__(self, src: str, tree: ast.Module, scopes: _ScopeTree) -> None:
        self.data = src.encode("utf-8")
        self.index = LineIndex(src)
        self.scopes = scopes
        self.by_node = scopes.by_node()
        self.occurrences: list[_Occurrence] = []
        #: Names that survive into the output untouched — the collision domain.
        self.skipped_names: set[str] = set()
        self._stack: list[_Scope] = [scopes.scopes[0]]
        for stmt in tree.body:
            self.visit(stmt)

    @property
    def scope(self) -> _Scope:
        return self._stack[-1]

    def _span(self, node: ast.AST) -> tuple[int, int]:
        return (
            self.index.offset(node.lineno, node.col_offset),
            self.index.offset(node.end_lineno, node.end_col_offset),
        )

    def _binder(self, name: str, scope: _Scope) -> _Scope | None:
        """Scope binding `name` as seen from `scope`; None means builtin or unbound."""
        try:
            sym = scope.table.lookup(name)
        except KeyError:
            return None
        if sym.is_declared_global() or sym.is_global():
            module = self.scopes.scopes[0]
            return module if name in module.bound else None
        if sym.is_nonlocal() or sym.is_free():
            p = scope.parent
            while p is not None:
                if p.kind != "class" and name in p.bound:  # class bodies are skipped
                    return p
                p = p.parent
            return None
        if sym.is_local() or sym.is_parameter():
            return scope
        return None

    def _record(self, name: str, start: int, end: int, kind: str = "var") -> None:
        if name in RESERVED or _is_dunder(name):
            self.skipped_names.add(name)
            return
        binder = self._binder(name, self.scope)
        if binder is None or binder.kind == "class" or name in binder.blocked:
            self.skipped_names.add(name)
            return
        text = self.data[start:end].decode("utf-8", "replace")
        if text != name:
            raise Bail(f"span {start}:{end} holds {text!r}, expected identifier {name!r}")
        self.occurrences.append(_Occurrence(start, end, name, binder.sid, kind))

    def _enter(self, node: ast.AST) -> None:
        scope = self.by_node.get(id(node))
        if scope is None:
            raise Bail(f"no symtable block paired with {type(node).__name__}")
        self._stack.append(scope)

    def _visit_all(self, nodes: Iterable[ast.AST | None]) -> None:
        for n in nodes:
            if n is not None:
                self.visit(n)

    # -- leaf identifiers -------------------------------------------------- #

    def visit_Name(self, node: ast.Name) -> None:
        start, end = self._span(node)
        self._record(node.id, start, end)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.visit(node.value)  # `.attr` lives in the object's namespace

    def visit_keyword(self, node: ast.keyword) -> None:
        self.visit(node.value)  # `f(name=...)` — `name` belongs to the callee

    def visit_alias(self, node: ast.alias) -> None:
        self.skipped_names.add(node.asname or node.name.split(".")[0])

    def visit_arg(self, node: ast.arg) -> None:
        start = self.index.offset(node.lineno, node.col_offset)
        self._record(node.arg, start, start + len(node.arg.encode("utf-8")))

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._visit_all([node.type])
        if node.name:
            lo = self._span(node)[0]
            hi = self.index.offset(node.body[0].lineno, node.body[0].col_offset)
            pos = self.data.rfind(b" as ", lo, hi)
            if pos < 0:
                raise Bail("cannot locate `as` in except handler")
            needle = node.name.encode("utf-8")
            at = self.data.find(needle, pos + 4, hi)
            if at < 0:
                raise Bail("cannot locate except-handler binding name")
            self._record(node.name, at, at + len(needle))
        self._visit_all(node.body)

    def visit_Global(self, node: ast.Global) -> None:
        self._record_name_list(node, node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self._record_name_list(node, node.names)

    def _record_name_list(self, node: ast.AST, names: list[str]) -> None:
        lo, hi = self._span(node)
        cursor = lo
        for name in names:
            needle = name.encode("utf-8")
            at = self.data.find(needle, cursor, hi)
            if at < 0:
                raise Bail(f"cannot locate {name!r} in {type(node).__name__}")
            self._record(name, at, at + len(needle))
            cursor = at + len(needle)

    def visit_Match(self, node: ast.Match) -> None:
        # Only the bare capture pattern (`case [a, b]`) has a span equal to its name.
        # `case P as n`, `*rest` and `**rest` need tail parsing we decline to do:
        # the corpus has no match statements, so coverage loss here costs nothing.
        for case in node.cases:
            for sub in ast.walk(case.pattern):
                if isinstance(sub, ast.MatchAs) and sub.pattern is not None:
                    raise Bail("match: `as` capture pattern")
                if isinstance(sub, ast.MatchStar) and sub.name:
                    raise Bail("match: starred capture")
                if isinstance(sub, ast.MatchMapping) and sub.rest:
                    raise Bail("match: `**rest` capture")
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name:
            start, end = self._span(node)
            self._record(node.name, start, end)

    # -- scope openers ----------------------------------------------------- #

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._visit_all(node.decorator_list)
        self._visit_all(_arg_annotations(node.args))
        self._visit_all(_arg_defaults(node.args))
        self._visit_all([node.returns])
        start, end = _decl_name_span(self.data, self.index, node, node.name)
        self._record(node.name, start, end, kind="func")
        self._enter(node)
        try:
            for arg in _all_args(node.args):
                self.visit_arg(arg)
            self._visit_all(node.body)
        finally:
            self._stack.pop()

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_all(node.decorator_list)
        self._visit_all(node.bases)
        self._visit_all([k.value for k in node.keywords])
        start, end = _decl_name_span(self.data, self.index, node, node.name)
        self._record(node.name, start, end, kind="class")
        self._enter(node)
        try:
            self._visit_all(node.body)
        finally:
            self._stack.pop()

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._visit_all(_arg_defaults(node.args))
        self._enter(node)
        try:
            for arg in _all_args(node.args):
                self.visit_arg(arg)
            self.visit(node.body)
        finally:
            self._stack.pop()

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.visit(node.generators[0].iter)
        self._enter(node)
        try:
            for i, gen in enumerate(node.generators):
                if i > 0:
                    self.visit(gen.iter)
                self.visit(gen.target)
                self._visit_all(gen.ifs)
            self.visit(node.elt)
        finally:
            self._stack.pop()


def _decl_name_span(data: bytes, index: LineIndex, node: ast.AST, name: str) -> tuple[int, int]:
    """Byte span of the identifier in `def NAME(...)` / `class NAME(...)`.

    `node.col_offset` points at the `def`/`class`/`async` keyword (decorators carry
    their own positions since 3.8), so the name is the first identifier after it.
    """
    start = index.offset(node.lineno, node.col_offset)
    pat = re.compile(_DECL_NAME.encode() + b"(" + re.escape(name.encode()) + rb")\b")
    m = pat.match(data, start)
    if m is None:
        raise Bail(f"cannot locate declaration name {name!r} at byte {start}")
    return m.start(1), m.end(1)


# --------------------------------------------------------------------------- #
# Annotation stripping (L2)


def _annotation_spans(tree: ast.Module, index: LineIndex, data: bytes) -> list[tuple[int, int]]:
    """Byte spans to delete so annotations disappear without breaking syntax.

    A span is only emitted when the bytes it removes really begin with the `:`/`->`
    that introduces the annotation; a parenthesised AnnAssign target (`(x): int = 1`)
    would otherwise lose its closing paren. A bare `x: int` (no value) is left alone
    because deleting the annotation leaves `x:`, and deleting the statement would
    change whether `x` is a local.
    """
    spans: list[tuple[int, int]] = []

    def lo_of(node: ast.AST) -> int:
        return index.offset(node.lineno, node.col_offset)

    def hi_of(node: ast.AST) -> int:
        return index.offset(node.end_lineno, node.end_col_offset)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in _all_args(node.args):
                if arg.annotation is None:
                    continue
                lo = lo_of(arg) + len(arg.arg.encode("utf-8"))
                hi = hi_of(arg.annotation)
                if data[lo:hi].lstrip().startswith(b":"):
                    spans.append((lo, hi))
            if node.returns is not None:
                arrow = data.rfind(b"->", lo_of(node), lo_of(node.returns))
                if arrow >= 0:
                    # Swallow the whitespace before `->` too, or `def f(x) -> int:`
                    # would leave the tell-tale `def f(x) :`.
                    while arrow > 0 and data[arrow - 1 : arrow] in (b" ", b"\t"):
                        arrow -= 1
                    spans.append((arrow, hi_of(node.returns)))
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            lo, hi = hi_of(node.target), hi_of(node.annotation)
            if data[lo:hi].lstrip().startswith(b":"):
                spans.append((lo, hi))
    return spans


# --------------------------------------------------------------------------- #
# The transform


def _analyze(src: str) -> tuple[ast.Module, _ScopeTree, _Collector, list[_Binding]]:
    try:
        tree = ast.parse(src)
        table = symtable.symtable(src, "<obtune>", "exec")
    except SyntaxError as exc:
        raise Bail(f"input does not parse: {exc}") from exc
    scopes = _ScopeTree(tree, table)
    collector = _Collector(src, tree, scopes)

    bindings: dict[tuple[int, str], _Binding] = {}
    for occ in collector.occurrences:
        key = (occ.binder, occ.name)
        b = bindings.get(key)
        if b is None:
            bindings[key] = b = _Binding(occ.binder, occ.name, "var", occ.start)
        b.occurrences.append(occ)
        b.first = min(b.first, occ.start)
        if occ.kind in ("func", "class"):
            b.kind = occ.kind
    ordered = sorted(bindings.values(), key=lambda b: (b.first, b.name))
    return tree, scopes, collector, ordered


def binding_plan(src: str) -> list[tuple[str, str]]:
    """Ordered, de-duplicated (original_name, kind) for every renamable binding.

    L1b's vocabulary chooser (obf/py/adversarial.py) needs the name list before it can
    pick misdirections, and must see exactly the names `rename` will act on.
    """
    _, _, _, bindings = _analyze(src)
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for b in bindings:
        if b.name in seen:
            continue
        seen.add(b.name)
        out.append((b.name, b.kind))
    return out


def rename(ctx: SnippetCtx, style: RenameStyle, *, hints: dict[str, str] | None = None) -> TransformResult:
    """Consistently rename every renamable binding in `ctx.src`.

    style="hex"          -> L1r (`v_a3f2` / `f_9c01`)
    style="seq"          -> L2  (a, b, ... aa, ab) plus type-annotation stripping
    style="adversarial"  -> L1b; `hints[original]` supplies the misleading stem.

    `rename_map` is orig -> new. When one original name has several distinct bindings,
    the first (document order) keeps the plain key and the rest are recorded as
    `orig@scope.path`, so the map stays lossless while remaining a plain
    `dict[str, str]` for `schema.Variant`.
    """
    if style not in ("hex", "seq", "adversarial"):
        raise Bail(f"unknown rename style {style!r}")
    src = ctx.src
    tree, scopes, collector, bindings = _analyze(src)
    if not bindings:
        return TransformResult(src, False, notes=["no renamable bindings"])

    data = src.encode("utf-8")
    index = LineIndex(src)
    strip = style == "seq"
    strip_spans = _annotation_spans(tree, index, data) if strip else []

    taken = set(RESERVED) | collector.skipped_names
    new_names: dict[tuple[int, str], str] = {}

    if style == "adversarial":
        hints = hints or {}
        for b in bindings:
            hint = hints.get(b.name)
            if hint is None:
                raise Bail(f"adversarial rename called without a hint for {b.name!r}")
            new_names[(b.scope, b.name)] = _uniquify(adversarial_name(ctx.rng, b.name, hint), taken)
    elif style == "hex":
        for b in bindings:
            new_names[(b.scope, b.name)] = fresh_name(lambda k=b.kind: hex_name(ctx.rng, k), taken)
    else:  # seq — the counter advances past reserved words, keeping the map canonical
        counter = 0

        def next_seq() -> str:
            nonlocal counter
            name = seq_name(counter)
            counter += 1
            return name

        for b in bindings:
            new_names[(b.scope, b.name)] = fresh_name(next_seq, taken)

    edits = EditList(src)
    for occ in collector.occurrences:
        if strip and any(lo <= occ.start and occ.end <= hi for lo, hi in strip_spans):
            continue  # the whole annotation is about to be deleted
        edits.add(occ.start, occ.end, new_names[(occ.binder, occ.name)])
    for lo, hi in strip_spans:
        edits.add(lo, hi, "")

    rename_map: dict[str, str] = {}
    seen_original: set[str] = set()
    for b in bindings:
        new = new_names[(b.scope, b.name)]
        if b.name in seen_original:
            rename_map[f"{b.name}@{scopes.scopes[b.scope].path}"] = new
        else:
            rename_map[b.name] = new
            seen_original.add(b.name)

    out = edits.apply()
    try:
        ast.parse(out)
    except SyntaxError as exc:
        raise Bail(f"renamed source does not parse: {exc}") from exc

    extra: dict[str, Any] = {"style": style, "n_bindings": len(bindings)}
    if ctx.entry_point:
        entry_new = next(
            (
                new_names[(b.scope, b.name)]
                for b in bindings
                if b.name == ctx.entry_point and scopes.scopes[b.scope].kind == "module"
            ),
            None,
        )
        if entry_new is None:
            raise Bail(f"entry point {ctx.entry_point!r} was not renamed (rename_entry is mandatory)")
        extra["entry_point_new"] = entry_new

    notes = [f"renamed {len(bindings)} bindings ({style})"]
    if strip_spans:
        notes.append(f"stripped {len(strip_spans)} type annotations")
    return TransformResult(out, True, notes=notes, rename_map=rename_map, extra=extra)


def _uniquify(candidate: str, taken: set[str]) -> str:
    """First non-colliding variant of `candidate` (`name`, `name2`, `name3`, ...)."""
    stem = candidate if candidate.isidentifier() else "value"
    if stem not in taken:
        taken.add(stem)
        return stem
    for i in range(2, 1000):
        cand = f"{stem}{i}"
        if cand not in taken:
            taken.add(cand)
            return cand
    raise Bail(f"could not uniquify {candidate!r}")


# --------------------------------------------------------------------------- #
# Public transform entry points (resolved by name from obf/builder.py)


def transform_hex(ctx: SnippetCtx) -> TransformResult:
    """L1r — random hex renaming of all bindings including the entry function."""
    return rename(ctx, "hex")


def transform_seq(ctx: SnippetCtx) -> TransformResult:
    """L2 — sequential minification + type-annotation stripping."""
    return rename(ctx, "seq")


def canonical_text(src: str) -> str:
    """Alpha-equivalence canonical form used by corpus/dedup.py.

    L2-renames, then re-emits via `ast.unparse`. The extra unparse is what the
    *condition* L2 deliberately does not do: as a training stimulus L2 must stay
    line-comparable with its L0 parent, whereas for dedup two programs differing only
    in whitespace must hash the same.
    """
    ctx = SnippetCtx(
        language="python",
        program_id="<canon>",
        condition="L2",
        src=src,
        entry_point="",
        rng=random.Random(0),
    )
    try:
        res = rename(ctx, "seq")
        text = res.src_out if res.applied else src
    except Bail:
        text = src
    return ast.unparse(ast.parse(text))
