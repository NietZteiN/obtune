"""Static backward def-use slice of a JavaScript program — tree-sitter twin of slicer_py.

Same contract, same `Slice` shape (see slicer_py for the WHY and the rejected
alternatives). The only reason this is a separate module is the front end: JavaScript
has no `ast`, and the project rule is that no trainable-condition code path may depend
on Node, so the analysis runs on `tree_sitter_javascript` inside Python.

Def-use sources walked here: `variable_declarator`, `assignment_expression`,
`augmented_assignment_expression`, `update_expression`, `formal_parameters`,
`for_statement` initializers, `for_in_statement` (`for..of`/`for..in`) bindings,
`catch_clause` parameters, and function/class declarations. Guards come from the
`condition` field of `if`/`while`/`do`/`for`/`ternary` and the `value` field of
`switch`, plus the `right` field of `for..of`.

Scoping simplification (documented on purpose): scopes are FUNCTION-level, not
block-level, so a `let` shadowed inside a `{ }` block resolves to the function binding.
Block scoping only ever *merges* two bindings of the same name inside one function,
which can add a def-use edge but never removes one — the slice stays an
over-approximation, which is the safe direction for a between-condition contrast.

Property names (`x.length`, object literal keys) are never treated as variable reads:
they are attribute surface, and counting them as dataflow would put a large constant
mass into the dataflow class for every condition alike.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Iterable

from obtune.attention.slicer_py import ScopeInfo, Slice

__all__ = ["slice_javascript", "parse_js", "byte_to_char_map"]

_FUNCTION_TYPES = {
    "function_declaration", "function_expression", "arrow_function",
    "generator_function", "generator_function_declaration", "method_definition",
}
_SCOPE_TYPES = _FUNCTION_TYPES | {"class_declaration", "class"}

# identifier-ish leaves that denote a *binding occurrence or variable read*
_VAR_IDENT_TYPES = {"identifier", "shorthand_property_identifier_pattern"}
# identifier-ish leaves that denote *surface* (property / key) names
_PROP_IDENT_TYPES = {"property_identifier", "shorthand_property_identifier",
                     "private_property_identifier", "statement_identifier"}

_parser = None


def parse_js(code: str):
    """Parse JS source. Returns (root_node, code_bytes). Parser is built once per process."""
    global _parser
    if _parser is None:
        import tree_sitter_javascript as tsjs
        from tree_sitter import Language, Parser

        _parser = Parser(Language(tsjs.language()))
    data = code.encode("utf-8")
    return _parser.parse(data).root_node, data


def byte_to_char_map(code: str) -> list[int]:
    """b2c[i] = character index of UTF-8 byte offset i (length len(bytes)+1).

    tree-sitter reports byte offsets; every span the rest of the pipeline consumes is a
    character offset into the original `str`, so the two must be reconciled exactly once.
    """
    b2c = []
    ci = 0
    for ch in code:
        n = len(ch.encode("utf-8"))
        b2c.extend([ci] * n)
        ci += 1
    b2c.append(ci)
    return b2c


def _text(node, data: bytes) -> str:
    return data[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _is_property_position(node) -> bool:
    p = node.parent
    if p is None:
        return False
    if p.type == "member_expression" and p.child_by_field_name("property") is node:
        return True
    if p.type in ("pair", "object") and node.type in _PROP_IDENT_TYPES:
        return True
    return node.type in _PROP_IDENT_TYPES


def _loaded_names(node, data: bytes) -> set[str]:
    """Variable names read inside `node` (property names excluded)."""
    out: set[str] = set()
    if node is None:
        return out
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type in _VAR_IDENT_TYPES and not _is_property_position(n):
            out.add(_text(n, data))
            continue
        for c in n.children:
            if n.type == "member_expression" and n.child_by_field_name("property") is c:
                continue
            stack.append(c)
    return out


def _stored_names(node, data: bytes) -> set[str]:
    """Names bound by an assignment target / declaration pattern."""
    out: set[str] = set()
    if node is None:
        return out
    if node.type == "member_expression":  # `a.b = x` binds (and reads) `a`
        return _loaded_names(node.child_by_field_name("object"), data)
    if node.type == "subscript_expression":
        return _loaded_names(node.child_by_field_name("object"), data)
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type in _VAR_IDENT_TYPES and not _is_property_position(n):
            out.add(_text(n, data))
            continue
        stack.extend(n.children)
    return out


@dataclass
class _Def:
    name: str
    scope: int
    resolve_scope: int
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


class _Builder:
    def __init__(self, code: str, root, data: bytes) -> None:
        self.code = code
        self.data = data
        self.b2c = byte_to_char_map(code)
        self.scopes: list[_Scope] = []
        self.returns: dict[int, set[str]] = {}
        self.loads: dict[int, set[str]] = {}
        self.fn_scope_of: dict[int, int] = {}  # tree-sitter node id -> scope id
        root_scope = self._new_scope(None, "module", None, 0, len(code))
        self.module_sid = root_scope.sid
        self._walk(root, root_scope.sid, frozenset())

    def _char(self, byte_off: int) -> int:
        return self.b2c[min(byte_off, len(self.b2c) - 1)]

    def _new_scope(self, parent, kind, name, start, end) -> _Scope:
        s = _Scope(sid=len(self.scopes), parent=parent, kind=kind, name=name, start=start, end=end)
        self.scopes.append(s)
        self.returns.setdefault(s.sid, set())
        self.loads.setdefault(s.sid, set())
        return s

    def add_def(self, sid: int, name: str, *, value_names: Iterable[str], guards: Iterable[str],
                kind: str, resolve_scope: int | None = None) -> None:
        d = _Def(name, sid, sid if resolve_scope is None else resolve_scope,
                 frozenset(value_names), frozenset(guards), kind)
        self.scopes[sid].defs.setdefault(name, []).append(d)

    def _fn_name(self, node) -> str | None:
        nm = node.child_by_field_name("name")
        if nm is not None:
            return _text(nm, self.data)
        p = node.parent
        if p is not None and p.type == "variable_declarator" and p.child_by_field_name("value") is node:
            t = p.child_by_field_name("name")
            if t is not None and t.type == "identifier":
                return _text(t, self.data)
        if p is not None and p.type == "assignment_expression" and p.child_by_field_name("right") is node:
            t = p.child_by_field_name("left")
            if t is not None and t.type == "identifier":
                return _text(t, self.data)
        return None

    def _enter_function(self, node, parent_sid: int) -> int:
        name = self._fn_name(node)
        sc = self._new_scope(parent_sid, "function", name,
                             self._char(node.start_byte), self._char(node.end_byte))
        self.fn_scope_of[node.id] = sc.sid
        params = node.child_by_field_name("parameters") or node.child_by_field_name("parameter")
        if params is not None:
            for nm in _stored_names(params, self.data):
                self.add_def(sc.sid, nm, value_names=(), guards=(), kind="param")
        body = node.child_by_field_name("body")
        if body is not None:
            self._walk(body, sc.sid, frozenset())
            if body.type != "statement_block":
                # concise arrow body: the expression *is* the return
                names = _loaded_names(body, self.data)
                self.returns[sc.sid] |= names
                self.loads[sc.sid] |= names
        return sc.sid

    def _walk(self, node, sid: int, guards: frozenset[str]) -> None:
        t = node.type

        if t in _FUNCTION_TYPES:
            child_sid = self._enter_function(node, sid)
            name = self._fn_name(node)
            if name and node.child_by_field_name("name") is not None:
                # a *declaration* binds its name in the enclosing scope; reads inside the
                # body resolve in the function's own scope (calling it pulls the body in)
                self.add_def(sid, name,
                             value_names=self.loads[child_sid] | self.returns[child_sid],
                             guards=guards, kind="funcdef", resolve_scope=child_sid)
            return

        if t in ("class_declaration", "class"):
            nm = node.child_by_field_name("name")
            sc = self._new_scope(sid, "class", _text(nm, self.data) if nm else None,
                                 self._char(node.start_byte), self._char(node.end_byte))
            body = node.child_by_field_name("body")
            if body is not None:
                self._walk(body, sc.sid, frozenset())
            if nm is not None:
                self.add_def(sid, _text(nm, self.data), value_names=self.loads[sc.sid],
                             guards=guards, kind="classdef", resolve_scope=sc.sid)
            return

        if t == "variable_declarator":
            target = node.child_by_field_name("name")
            value = node.child_by_field_name("value")
            if value is not None and value.type in _FUNCTION_TYPES:
                child_sid = self._enter_function(value, sid)
                for nm in _stored_names(target, self.data):
                    self.add_def(sid, nm, value_names=self.loads[child_sid] | self.returns[child_sid],
                                 guards=guards, kind="fnvar", resolve_scope=child_sid)
                return
            vn = _loaded_names(value, self.data)
            self.loads[sid] |= vn
            for nm in _stored_names(target, self.data):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind="declare")
            if value is not None:
                self._walk_children(value, sid, guards)
            return

        if t in ("assignment_expression", "augmented_assignment_expression"):
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            vn = _loaded_names(right, self.data)
            if t == "augmented_assignment_expression":
                vn = vn | _stored_names(left, self.data)
            self.loads[sid] |= vn
            for nm in _stored_names(left, self.data):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind=t)
            if right is not None:
                self._walk_children(right, sid, guards)
            return

        if t == "update_expression":  # i++ / --i : reads and writes the same name
            arg = node.child_by_field_name("argument")
            for nm in _stored_names(arg, self.data):
                self.add_def(sid, nm, value_names={nm}, guards=guards, kind="update")
            return

        if t == "for_statement":
            init = node.child_by_field_name("initializer")
            cond = node.child_by_field_name("condition")
            incr = node.child_by_field_name("increment")
            if init is not None:
                self._walk(init, sid, guards)
            inner = guards | _loaded_names(cond, self.data)
            if incr is not None:
                self._walk(incr, sid, inner)
            body = node.child_by_field_name("body")
            if body is not None:
                self._walk(body, sid, inner)
            return

        if t == "for_in_statement":  # for..of / for..in
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            vn = _loaded_names(right, self.data)
            for nm in _stored_names(left, self.data):
                self.add_def(sid, nm, value_names=vn, guards=guards, kind="for_target")
            body = node.child_by_field_name("body")
            if body is not None:
                self._walk(body, sid, guards | vn)
            return

        if t in ("if_statement", "while_statement", "do_statement", "ternary_expression"):
            cond = node.child_by_field_name("condition")
            inner = guards | _loaded_names(cond, self.data)
            for fname in ("consequence", "alternative", "body"):
                c = node.child_by_field_name(fname)
                if c is not None:
                    self._walk(c, sid, inner)
            if cond is not None:
                self.loads[sid] |= _loaded_names(cond, self.data)
            return

        if t == "switch_statement":
            val = node.child_by_field_name("value")
            inner = guards | _loaded_names(val, self.data)
            body = node.child_by_field_name("body")
            if body is not None:
                self._walk(body, sid, inner)
            self.loads[sid] |= _loaded_names(val, self.data)
            return

        if t == "catch_clause":
            param = node.child_by_field_name("parameter")
            if param is not None:
                for nm in _stored_names(param, self.data):
                    self.add_def(sid, nm, value_names=(), guards=guards, kind="catch")
            body = node.child_by_field_name("body")
            if body is not None:
                self._walk(body, sid, guards)
            return

        if t == "return_statement":
            names: set[str] = set()
            for c in node.named_children:
                names |= _loaded_names(c, self.data)
            self.returns[sid] |= names
            self.loads[sid] |= names
            return

        if t in _VAR_IDENT_TYPES and not _is_property_position(node):
            self.loads[sid].add(_text(node, self.data))
            return

        self._walk_children(node, sid, guards)

    def _walk_children(self, node, sid: int, guards: frozenset[str]) -> None:
        for c in node.children:
            if node.type == "member_expression" and node.child_by_field_name("property") is c:
                continue
            self._walk(c, sid, guards)


def _find_entry_scope(b: _Builder, root, entry_point: str | None) -> tuple[int, str | None]:
    """Scope id of the entry function + its bound name."""
    cands = [(sid, sc) for sid, sc in enumerate(b.scopes) if sc.kind == "function"]
    if entry_point:
        for sid, sc in cands:
            if sc.name == entry_point:
                return sid, sc.name
    # top-level function bindings first (outermost-first order == source order here)
    toplevel = [(sid, sc) for sid, sc in cands if sc.parent == b.module_sid]
    if toplevel:
        sid, sc = toplevel[0]
        return sid, sc.name
    if cands:
        sid, sc = cands[0]
        return sid, sc.name
    return b.module_sid, entry_point


def slice_javascript(code: str, entry_point: str | None = None) -> Slice:
    """Backward def-use slice from the top function's `return` statement(s)."""
    notes: list[str] = []
    try:
        root, data = parse_js(code)
    except Exception as e:  # missing grammar / binary incompat — surface, don't guess
        return Slice("javascript", entry_point, frozenset(), (), 0, False, (f"parse error: {e}",))
    if root.has_error:
        notes.append("tree-sitter reported ERROR nodes; slice computed on a partial parse")

    b = _Builder(code, root, data)
    entry_sid, entry_name = _find_entry_scope(b, root, entry_point)
    seeds = set(b.returns.get(entry_sid, set()))
    if not seeds:
        notes.append("entry function has no return with names; falling back to all loads")
        seeds = set(b.loads.get(entry_sid, set()))

    def resolve(sid: int, name: str) -> int | None:
        cur: int | None = sid
        while cur is not None:
            if name in b.scopes[cur].defs:
                return cur
            cur = b.scopes[cur].parent
        return None

    critical: set[tuple[int | None, str]] = set()
    # Entry-function name is TERMINAL — see the note in slicer_py.slice_python.
    if entry_name:
        critical.add((resolve(entry_sid, entry_name), entry_name))
    work: deque[tuple[int, str]] = deque((entry_sid, n) for n in seeds)
    iterations = 0
    max_iter = 200_000

    while work and iterations < max_iter:
        iterations += 1
        sid, name = work.popleft()
        owner = resolve(sid, name)
        key: tuple[int | None, str] = (owner, name)
        if key in critical:
            continue
        critical.add(key)
        if owner is None:
            continue
        for d in b.scopes[owner].defs.get(name, []):
            for nxt in d.value_names | d.guard_names:
                work.append((d.resolve_scope, nxt))

    if iterations >= max_iter:
        notes.append("fixed-point iteration cap hit; slice may be incomplete")

    scopes = tuple(ScopeInfo(s.sid, s.parent, s.kind, s.name, s.start, s.end) for s in b.scopes)
    return Slice(
        language="javascript", entry_point=entry_name, critical=frozenset(critical),
        scopes=scopes, iterations=iterations, ok=True, notes=tuple(notes),
        seeds=frozenset(seeds),
    )
