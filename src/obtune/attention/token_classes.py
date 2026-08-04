"""Character-span token classification for Python and JavaScript — one Python API.

WHY
---
The RQ3 attention metric needs to say "this much of the model's attention landed on
identifiers, this much on control keywords, ..." for programs in two languages, at
character resolution, so that any subword tokenizer can be aligned to it afterwards
(metrics.py resolves char spans -> token indices through `offset_mapping`).

The reference implementation this replaces (reallocation/src/token_classification.py)
is Python-`tokenize`-only, returns *averaged scores* rather than spans, and silently
swallows `TokenError` on malformed input. Here the output is a **total partition** of
`[0, len(code))` — every character belongs to exactly one class — which makes the mass
metric a genuine probability decomposition instead of a set of overlapping subsets that
can sum to more or less than 1.

The class set
-------------
    identifier         a variable/function name that is NOT on the backward slice
    control_kw         control-flow / binding keywords (if, for, return, def, function, ...)
    operator           operators and delimiters
    literal            numbers, strings, booleans, null/None
    dataflow_critical  a token whose name is on the entry point's backward def-use slice
    other              whitespace, newlines, indentation, comments, anything unlexed

`dataflow_critical` and `identifier` OVERLAP by construction: a sliced name is still an
identifier. Reviewers always ask about this, so the resolution is explicit and
recoverable: the partition class (`cls`) gives `dataflow_critical` precedence, while
`base_cls` keeps what the token would have been. Therefore

    mass(identifier, excluding sliced defs) = sum over cls == "identifier"
    mass(identifier, including sliced defs) = the above
                                             + sum over cls == "dataflow_critical"
                                               and base_cls == "identifier"

and metrics.py emits both columns. Only identifier-bearing tokens are promoted to
`dataflow_critical` (guard *keywords* stay `control_kw`); the alternative — promoting
guard keywords too — was rejected because the headline statistic already adds
`mass_control_kw + mass_dataflow_critical`, and double-counting there would make the
two halves of `anchoring_shift` non-independent.
"""
from __future__ import annotations

import builtins as _builtins
import io
import keyword
import token as _token
import tokenize
from dataclasses import dataclass, field
from typing import Iterable, Optional

from obtune.attention.slicer_js import _PROP_IDENT_TYPES, _VAR_IDENT_TYPES, byte_to_char_map, parse_js
from obtune.attention.slicer_js import slice_javascript
from obtune.attention.slicer_py import Slice, slice_python

__all__ = [
    "CLASSES", "BASE_CLASSES", "ClassSpan", "Classification", "classify_code",
]

CLASSES = ("identifier", "control_kw", "operator", "literal", "dataflow_critical", "other")
BASE_CLASSES = ("identifier", "control_kw", "operator", "literal", "other")

# ---------------------------------------------------------------------------
# language keyword tables
# ---------------------------------------------------------------------------
_PY_CONTROL = {
    "if", "elif", "else", "for", "while", "break", "continue", "return", "try", "except",
    "finally", "with", "raise", "assert", "yield", "pass", "async", "await",
}
_PY_BINDING = {"def", "class", "lambda", "global", "nonlocal", "import", "from", "as", "del"}
_PY_OPERATOR_KW = {"and", "or", "not", "in", "is"}
_PY_LITERAL_KW = {"True": "boolean", "False": "boolean", "None": "none"}

_JS_CONTROL = {
    "if", "else", "for", "while", "do", "return", "break", "continue", "switch", "case",
    "default", "try", "catch", "finally", "throw", "yield", "await",
}
_JS_BINDING = {"function", "const", "let", "var", "class", "new", "extends", "static",
               "get", "set", "=>"}
_JS_OPERATOR_KW = {"typeof", "instanceof", "in", "of", "delete", "void"}
_JS_LITERAL_NODES = {
    "number": "number", "string": "string", "string_fragment": "string",
    "template_string": "string", "template_substitution": "string", "regex": "regex",
    "regex_pattern": "regex", "true": "boolean", "false": "boolean", "null": "none",
    "undefined": "none",
}
_JS_GLOBALS = {
    "Math", "JSON", "Object", "Array", "String", "Number", "Boolean", "Date", "RegExp",
    "Map", "Set", "Promise", "console", "parseInt", "parseFloat", "isNaN", "isFinite",
    "NaN", "Infinity", "Symbol", "BigInt", "Error", "TypeError", "RangeError",
}
_PY_BUILTINS = frozenset(dir(_builtins))

_DELIMS = set("()[]{},:;.@")
_COMPARE = {"==", "!=", "<", ">", "<=", ">=", "===", "!==", "<>"}
_ARITH = {"+", "-", "*", "/", "//", "%", "**", "++", "--"}
_BITWISE = {"&", "|", "^", "~", "<<", ">>", ">>>"}
_LOGIC = {"&&", "||", "!", "??", "?"}


@dataclass(frozen=True)
class ClassSpan:
    """One classified character span. Spans tile `[0, len(code))` without gaps."""

    start: int
    end: int
    cls: str  # partition class (one of CLASSES)
    base_cls: str  # lexical class ignoring the slice overlay (one of BASE_CLASSES)
    subclass: str  # fine-grained role, e.g. entry_fn / param / builtin / branch / arith
    text: str

    @property
    def on_slice(self) -> bool:
        return self.cls == "dataflow_critical"


@dataclass
class Classification:
    language: str
    code: str
    entry_point: Optional[str]
    spans: list[ClassSpan]
    slice_result: Optional[Slice]
    parse_ok: bool
    notes: list[str] = field(default_factory=list)

    # -- invariants / quality -------------------------------------------------
    def partition_ok(self) -> bool:
        """True iff the spans tile the source exactly once, in order."""
        pos = 0
        for s in self.spans:
            if s.start != pos or s.end < s.start:
                return False
            pos = s.end
        return pos == len(self.code)

    def coverage(self) -> float:
        """Fraction of non-whitespace characters assigned a real lexical class.

        `other` on a non-whitespace character means the front end failed to lex it, so
        this is the number validate.py hard-fails on.
        """
        total = sum(1 for ch in self.code if not ch.isspace())
        if total == 0:
            return 1.0
        covered = 0
        for s in self.spans:
            if s.base_cls == "other" and s.subclass != "comment":
                continue
            covered += sum(1 for ch in s.text if not ch.isspace())
        return covered / total

    def class_spans(self, cls: str) -> list[tuple[int, int]]:
        return [(s.start, s.end) for s in self.spans if s.cls == cls]

    def identifier_spans(self, include_slice: bool = True) -> list[tuple[int, int]]:
        return [
            (s.start, s.end) for s in self.spans
            if s.base_cls == "identifier" and (include_slice or s.cls != "dataflow_critical")
        ]

    def char_classes(self) -> list[str]:
        """Per-character partition class; length == len(code)."""
        out = ["other"] * len(self.code)
        for s in self.spans:
            for i in range(s.start, min(s.end, len(self.code))):
                out[i] = s.cls
        return out

    def counts(self) -> dict[str, int]:
        c = {k: 0 for k in CLASSES}
        for s in self.spans:
            c[s.cls] += s.end - s.start
        return c


# ---------------------------------------------------------------------------
# operator / delimiter subclassing (shared)
# ---------------------------------------------------------------------------
def _op_subclass(text: str) -> str:
    if text in _DELIMS or text in ("->", "=>", "..."):
        return "delimiter"
    if text in _COMPARE:
        return "compare"
    if text in _LOGIC:
        return "logic"
    if text in _BITWISE:
        return "bitwise"
    if text in _ARITH:
        return "arith"
    if text.endswith("=") and text not in _COMPARE:
        return "assign"
    if text == "=":
        return "assign"
    return "other_op"


# ---------------------------------------------------------------------------
# Python front end
# ---------------------------------------------------------------------------
def _py_line_offsets(code: str) -> list[int]:
    offs = [0]
    for line in code.splitlines(keepends=True):
        offs.append(offs[-1] + len(line))
    return offs


def _classify_python_raw(code: str) -> tuple[list[tuple[int, int, str, str, str]], bool, list[str]]:
    """-> [(start, end, base_cls, subclass, text)], parse_ok, notes"""
    notes: list[str] = []
    offs = _py_line_offsets(code)

    def abs_idx(rc: tuple[int, int]) -> int:
        row, col = rc
        if row - 1 >= len(offs) - 1:
            return len(code)
        return min(offs[row - 1] + col, len(code))

    raw: list[tuple[int, int, str, str, str]] = []
    parse_ok = True
    try:
        for tk in tokenize.generate_tokens(io.StringIO(code).readline):
            s, e = abs_idx(tk.start), abs_idx(tk.end)
            if e <= s:
                continue
            text = tk.string
            tt = tk.type
            if tt == _token.NAME:
                if text in _PY_LITERAL_KW:
                    base, sub = "literal", _PY_LITERAL_KW[text]
                elif keyword.iskeyword(text):
                    if text in _PY_OPERATOR_KW:
                        base, sub = "operator", "logic" if text in ("and", "or", "not") else "membership"
                    elif text in _PY_BINDING:
                        base, sub = "control_kw", "binding"
                    elif text in _PY_CONTROL:
                        base, sub = "control_kw", _py_kw_role(text)
                    else:
                        base, sub = "control_kw", "keyword"
                else:
                    base, sub = "identifier", "name"
            elif tt == _token.NUMBER:
                base, sub = "literal", "number"
            elif tt == _token.STRING or tk.type == getattr(_token, "FSTRING_MIDDLE", -1):
                base, sub = "literal", "string"
            elif tt == tokenize.COMMENT:
                base, sub = "other", "comment"
            elif tt == _token.OP:
                base, sub = "operator", _op_subclass(text)
            elif tt in (_token.NEWLINE, tokenize.NL):
                base, sub = "other", "newline"
            elif tt in (_token.INDENT, _token.DEDENT):
                base, sub = "other", "indent"
            else:
                base, sub = "other", "misc"
            raw.append((s, e, base, sub, code[s:e]))
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        parse_ok = False
        notes.append(f"python tokenize failed after {len(raw)} tokens: {exc}")
    return raw, parse_ok, notes


def _py_kw_role(text: str) -> str:
    if text in ("if", "elif", "else"):
        return "branch"
    if text in ("for", "while"):
        return "loop"
    if text in ("return", "break", "continue", "yield", "pass"):
        return "jump"
    if text in ("try", "except", "finally", "raise", "assert"):
        return "exception"
    return "keyword"


def _py_identifier_roles(code: str, entry_point: Optional[str]) -> dict[str, str]:
    """name -> role, from the AST (entry_fn / func_def / param / local / builtin)."""
    import ast

    roles: dict[str, str] = {}
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return roles
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            roles.setdefault(n.name, "entry_fn" if n.name == entry_point else "func_def")
            args = n.args
            for a in (list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
                      + ([args.vararg] if args.vararg else []) + ([args.kwarg] if args.kwarg else [])):
                roles.setdefault(a.arg, "param")
        elif isinstance(n, ast.ClassDef):
            roles.setdefault(n.name, "class_def")
        elif isinstance(n, ast.Lambda):
            args = n.args
            for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs):
                roles.setdefault(a.arg, "param")
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            roles.setdefault(n.id, "local")
    if entry_point:
        roles[entry_point] = "entry_fn"
    return roles


# ---------------------------------------------------------------------------
# JavaScript front end (tree-sitter; NO Node dependency)
# ---------------------------------------------------------------------------
def _classify_javascript_raw(code: str) -> tuple[list[tuple[int, int, str, str, str]], bool, list[str],
                                                 set[str], set[str], Optional[str]]:
    notes: list[str] = []
    try:
        root, data = parse_js(code)
    except Exception as exc:
        return [], False, [f"tree-sitter parse failed: {exc}"], set(), set(), None
    parse_ok = not root.has_error
    if not parse_ok:
        notes.append("tree-sitter reported ERROR nodes; classification is on a partial parse")
    b2c = byte_to_char_map(code)

    params: set[str] = set()
    declared: set[str] = set()
    top_fn: Optional[str] = None

    raw: list[tuple[int, int, str, str, str]] = []
    stack = [root]
    leaves = []
    while stack:
        n = stack.pop()
        if n.child_count == 0:
            leaves.append(n)
        else:
            stack.extend(n.children)
    leaves.sort(key=lambda n: n.start_byte)

    for n in leaves:
        s, e = b2c[n.start_byte], b2c[min(n.end_byte, len(b2c) - 1)]
        if e <= s:
            continue
        text = code[s:e]
        t = n.type
        if t == "comment":
            base, sub = "other", "comment"
        elif t in _JS_LITERAL_NODES:
            base, sub = "literal", _JS_LITERAL_NODES[t]
        elif t in _PROP_IDENT_TYPES:
            base, sub = "identifier", "attribute"
        elif t in _VAR_IDENT_TYPES:
            base, sub = "identifier", "name"
        elif t in _JS_CONTROL:
            base, sub = "control_kw", _js_kw_role(t)
        elif t in _JS_BINDING:
            base, sub = "control_kw", "binding"
        elif t in _JS_OPERATOR_KW:
            base, sub = "operator", "membership" if t in ("in", "of") else "logic"
        elif t == "this" or t == "super":
            base, sub = "identifier", "builtin"
        elif not n.is_named:
            base, sub = "operator", _op_subclass(text)
        elif t in ("escape_sequence",):
            base, sub = "literal", "string"
        else:
            base, sub = "other", "misc"
        raw.append((s, e, base, sub, text))

    # role harvesting for identifier subclasses
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type in ("function_declaration", "function_expression", "arrow_function",
                      "generator_function_declaration", "method_definition"):
            p = n.child_by_field_name("parameters") or n.child_by_field_name("parameter")
            if p is not None:
                params |= _collect_idents(p, code, b2c)
            nm = n.child_by_field_name("name")
            if top_fn is None and nm is not None and n.parent is not None and n.parent.type == "program":
                top_fn = code[b2c[nm.start_byte]:b2c[nm.end_byte]]
        elif n.type == "for_in_statement":
            # `for (const v of xs)` binds through the `left` field, not a variable_declarator
            lft = n.child_by_field_name("left")
            if lft is not None:
                declared |= _collect_idents(lft, code, b2c)
        elif n.type == "catch_clause":
            prm = n.child_by_field_name("parameter")
            if prm is not None:
                declared |= _collect_idents(prm, code, b2c)
        elif n.type == "variable_declarator":
            tgt = n.child_by_field_name("name")
            val = n.child_by_field_name("value")
            if tgt is not None:
                names = _collect_idents(tgt, code, b2c)
                declared |= names
                if (top_fn is None and val is not None
                        and val.type in ("arrow_function", "function_expression")
                        and n.parent is not None and n.parent.parent is not None
                        and n.parent.parent.type == "program"):
                    top_fn = next(iter(sorted(names)), None)
        stack.extend(n.children)

    return raw, parse_ok, notes, params, declared, top_fn


def _collect_idents(node, code: str, b2c: list[int]) -> set[str]:
    out: set[str] = set()
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type in _VAR_IDENT_TYPES:
            out.add(code[b2c[n.start_byte]:b2c[min(n.end_byte, len(b2c) - 1)]])
        stack.extend(n.children)
    return out


def _js_kw_role(text: str) -> str:
    if text in ("if", "else", "switch", "case", "default"):
        return "branch"
    if text in ("for", "while", "do"):
        return "loop"
    if text in ("return", "break", "continue", "yield"):
        return "jump"
    if text in ("try", "catch", "finally", "throw"):
        return "exception"
    return "keyword"


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------
def _fill_gaps(code: str, raw: Iterable[tuple[int, int, str, str, str]]) -> list[tuple[int, int, str, str, str]]:
    """Sort, drop overlaps (first token wins), and pad the holes with `other`."""
    items = sorted(raw, key=lambda r: (r[0], r[1]))
    out: list[tuple[int, int, str, str, str]] = []
    pos = 0
    for s, e, base, sub, text in items:
        if s < pos:  # overlapping lexer output (e.g. f-string middles): keep the first
            if e <= pos:
                continue
            s = pos
            text = code[s:e]
        if s > pos:
            out.append((pos, s, "other", _gap_subclass(code[pos:s]), code[pos:s]))
        out.append((s, e, base, sub, text))
        pos = e
    if pos < len(code):
        out.append((pos, len(code), "other", _gap_subclass(code[pos:]), code[pos:]))
    return out


def _gap_subclass(text: str) -> str:
    if text == "":
        return "empty"
    if text.isspace():
        return "newline" if "\n" in text else "whitespace"
    return "unlexed"


def classify_code(
    code: str,
    language: str,
    entry_point: Optional[str] = None,
    *,
    apply_slice: bool = True,
) -> Classification:
    """Full-coverage character-span classification of `code`.

    `entry_point` steers both the backward slice (which function's return seeds it) and
    the `entry_fn` identifier subclass — the L1b trap renames the entry function itself,
    so its occurrences must be separable from ordinary locals.
    """
    notes: list[str] = []
    if language == "python":
        raw, parse_ok, n1 = _classify_python_raw(code)
        notes += n1
        roles = _py_identifier_roles(code, entry_point)
        sl = slice_python(code, entry_point) if apply_slice else None
        js_params: set[str] = set()
        js_declared: set[str] = set()
        top_fn = None
    elif language == "javascript":
        raw, parse_ok, n1, js_params, js_declared, top_fn = _classify_javascript_raw(code)
        notes += n1
        roles = {}
        sl = slice_javascript(code, entry_point) if apply_slice else None
    else:
        raise ValueError(f"unknown language: {language!r} (expected python|javascript)")

    if sl is not None and sl.notes:
        notes += [f"slice: {m}" for m in sl.notes]

    filled = _fill_gaps(code, raw)
    spans: list[ClassSpan] = []
    entry_name = entry_point or (sl.entry_point if sl else None) or top_fn

    for s, e, base, sub, text in filled:
        if base == "identifier" and sub == "name":
            if language == "python":
                sub = _py_ident_subclass(text, roles, entry_name)
            else:
                sub = _js_ident_subclass(text, js_params, js_declared, entry_name)
        cls = base
        if (sl is not None and base == "identifier" and sub != "attribute"
                and sl.is_critical(s, text)):
            cls = "dataflow_critical"
        spans.append(ClassSpan(start=s, end=e, cls=cls, base_cls=base, subclass=sub, text=text))

    return Classification(
        language=language, code=code, entry_point=entry_name, spans=spans,
        slice_result=sl, parse_ok=parse_ok, notes=notes,
    )


def _py_ident_subclass(text: str, roles: dict[str, str], entry: Optional[str]) -> str:
    if entry and text == entry:
        return "entry_fn"
    r = roles.get(text)
    if r:
        return r
    if text in _PY_BUILTINS:
        return "builtin"
    return "free"


def _js_ident_subclass(text: str, params: set[str], declared: set[str], entry: Optional[str]) -> str:
    if entry and text == entry:
        return "entry_fn"
    if text in params:
        return "param"
    if text in declared:
        return "local"
    if text in _JS_GLOBALS:
        return "builtin"
    return "free"
