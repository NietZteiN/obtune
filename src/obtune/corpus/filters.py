"""Static admissibility filters — cheap rejections before anything is executed.

The corpus exists to support an *output-prediction* task, so every program must be a
pure function of its arguments: same inputs, same canonical output, in every process
and on every day. corpus/inputs.py enforces that dynamically (three runs, different
PYTHONHASHSEED); this module is the static pre-filter that stops the obvious cases
from ever reaching a sandbox — clock reads, RNG, I/O, ambient state, network.

Design choice: an import *allowlist* rather than a denylist. A denylist is a promise
that we thought of everything; an allowlist is a promise we can actually keep, and the
cost of rejecting a usable program is one fewer corpus row. The named denials that
follow the allowlist exist for constructs that are not imports at all (`input(`,
`open(`, `id(`, `hash(`) or that come in through an allowed module (`random.random`
is caught by the allowlist, but `datetime.now` would not be if datetime were allowed).

`id()` and `hash()` are rejected even though they are builtins: both are address- or
PYTHONHASHSEED-dependent, and a program that leaks either into its return value looks
deterministic in one process and is not across two.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any, Iterable

# Modules a corpus program may import. Pure, stdlib, deterministic.
PY_IMPORT_ALLOWLIST = frozenset({
    "math", "itertools", "functools", "collections", "re", "string", "heapq",
    "bisect", "typing", "operator", "decimal", "fractions",
})

# Name-level denials that the allowlist alone does not cover. Kept to names that are
# actually nondeterministic (clock, RNG, ambient state, address/hash identity) plus the
# eval family, which can reach any of the above at runtime and so defeats static
# analysis entirely. Deterministic-but-dynamic builtins (getattr, isinstance, type) are
# deliberately NOT denied: rejecting them would cost corpus rows for no determinism gain.
PY_DENY_NAMES = (
    "random", "time", "datetime", "os", "sys", "input", "open", "id", "hash",
    "threading", "socket", "subprocess", "multiprocessing", "requests", "urllib",
    "pickle", "uuid", "secrets", "tempfile", "shutil", "pathlib", "gc", "ctypes",
    "eval", "exec", "compile", "globals", "locals", "vars", "__import__",
)

# `sys.maxsize` is the one sys attribute that is a plain constant, so it is allowed.
PY_SYS_ALLOWED_ATTRS = frozenset({"maxsize"})

JS_DENY_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bDate\b", "Date"),
    (r"\bMath\s*\.\s*random\b", "Math.random"),
    (r"\bprocess\b", "process"),
    (r"\brequire\s*\(", "require("),
    (r"\bimport\s*\(", "import("),
    (r"\bfetch\s*\(", "fetch("),
    (r"\bsetTimeout\b", "setTimeout"),
    (r"\bsetInterval\b", "setInterval"),
    (r"\bperformance\s*\.", "performance."),
    (r"\bglobalThis\b", "globalThis"),
    (r"\bWeakRef\b", "WeakRef"),
    (r"\bFinalizationRegistry\b", "FinalizationRegistry"),
    (r"\beval\s*\(", "eval("),
    (r"\bnew\s+Function\b", "new Function"),
    (r"\bXMLHttpRequest\b", "XMLHttpRequest"),
)
_JS_DENY = tuple((re.compile(p), label) for p, label in JS_DENY_PATTERNS)


@dataclass
class FilterVerdict:
    ok: bool
    reasons: list[str]

    def __bool__(self) -> bool:
        return self.ok


def check_program(
    code: str,
    language: str,
    *,
    loc: int | None = None,
    loc_min: int = 3,
    loc_max: int = 60,
    max_chars: int = 2500,
    entry_point: str | None = None,
) -> FilterVerdict:
    """Full static gate: syntax, determinism-by-construction, size, character set."""
    reasons: list[str] = []
    reasons += _size_reasons(code, loc, loc_min, loc_max, max_chars)
    reasons += _charset_reasons(code)
    if language == "python":
        reasons += python_determinism_reasons(code, entry_point=entry_point)
    elif language == "javascript":
        reasons += javascript_determinism_reasons(code, entry_point=entry_point)
    else:
        reasons.append(f"unknown_language:{language}")
    return FilterVerdict(ok=not reasons, reasons=reasons)


# ----------------------------------------------------------------------- size/charset


def _size_reasons(code: str, loc: int | None, loc_min: int, loc_max: int, max_chars: int) -> list[str]:
    n = loc if loc is not None else sum(1 for ln in code.splitlines() if ln.strip())
    out = []
    if n < loc_min:
        out.append(f"loc_too_small:{n}<{loc_min}")
    if n > loc_max:
        out.append(f"loc_too_large:{n}>{loc_max}")
    if len(code) > max_chars:
        out.append(f"too_many_chars:{len(code)}>{max_chars}")
    return out


def _charset_reasons(code: str) -> list[str]:
    """Reject control characters and non-BMP text.

    Rationale: the tokenizers in configs/models.yaml handle astral-plane code points
    inconsistently (some emit replacement characters), so a program containing one
    would be scored on a prompt that does not match the stimulus. Ordinary accented
    Latin/Greek/CJK below U+10000 is fine and appears in the CruxEval-X stimuli.
    """
    out = []
    if "\x00" in code:
        out.append("null_byte")
    bad_ctrl = {ch for ch in code if ord(ch) < 0x20 and ch not in "\n\t"}
    if bad_ctrl:
        out.append("control_chars:" + ",".join(f"U+{ord(c):04X}" for c in sorted(bad_ctrl)))
    astral = {ch for ch in code if ord(ch) > 0xFFFF}
    if astral:
        out.append("non_bmp_chars:" + ",".join(f"U+{ord(c):05X}" for c in sorted(astral))[:80])
    return out


# ---------------------------------------------------------------------------- Python


def python_determinism_reasons(code: str, entry_point: str | None = None) -> list[str]:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError) as e:
        return [f"syntax_error:{type(e).__name__}"]

    reasons: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in PY_IMPORT_ALLOWLIST:
                    reasons.append(f"import_not_allowed:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level or root not in PY_IMPORT_ALLOWLIST:
                reasons.append(f"import_not_allowed:{node.module or '.' * node.level}")
        elif isinstance(node, ast.Attribute):
            base = _attr_root(node)
            if base == "sys" and node.attr not in PY_SYS_ALLOWED_ATTRS:
                reasons.append(f"denied_name:sys.{node.attr}")
            elif base in ("datetime", "time", "random", "os"):
                reasons.append(f"denied_name:{base}.{node.attr}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in PY_DENY_NAMES:
                reasons.append(f"denied_name:{node.id}")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            # Module-level mutable state makes a program's output depend on how many
            # times it has already been called — invisible to a single-shot gate.
            reasons.append("global_state")

    if entry_point is not None and entry_point not in _py_defined_functions(tree):
        reasons.append(f"entry_point_missing:{entry_point}")
    return sorted(set(reasons))


def python_soft_flags(code: str) -> list[str]:
    """Non-fatal risk notes recorded on kept rows.

    Set iteration is the interesting one: `list({...})` is order-unstable across
    processes, but most set uses (membership, `len`, `sorted`) are perfectly stable.
    Rejecting every program containing a set would cost a large slice of the corpus to
    catch cases the dynamic filter already catches for free — three executions under
    different PYTHONHASHSEED values, plus canon.py's outright refusal to serialize a
    set. So this is a flag on the row, not a rejection.
    """
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return []
    flags = []
    if any(isinstance(n, (ast.Set, ast.SetComp)) for n in ast.walk(tree)):
        flags.append("uses_set")
    if any(isinstance(n, (ast.Dict, ast.DictComp)) for n in ast.walk(tree)):
        flags.append("uses_dict")
    return flags


def _attr_root(node: ast.Attribute) -> str | None:
    cur: ast.AST = node.value
    while isinstance(cur, ast.Attribute):
        cur = cur.value
    return cur.id if isinstance(cur, ast.Name) else None


def _py_defined_functions(tree: ast.AST) -> set[str]:
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


# ------------------------------------------------------------------------ JavaScript


def javascript_determinism_reasons(code: str, entry_point: str | None = None) -> list[str]:
    """Pattern-based, deliberately. The JS sandbox in exec/runner_js.mjs already deletes
    Date/process/require/fetch/timers from the context, so anything this misses fails
    loudly at execution rather than producing a nondeterministic corpus row. The
    patterns are the cheap first pass that keeps those failures out of the log."""
    reasons = [f"denied_name:{label}" for rx, label in _JS_DENY if rx.search(code)]
    if entry_point is not None and not re.search(r"\b" + re.escape(entry_point) + r"\b", code):
        reasons.append(f"entry_point_missing:{entry_point}")
    return sorted(set(reasons))


def partition(
    programs: Iterable[dict[str, Any]], **kw: Any
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split programs into (kept, rejected); rejected rows carry `reject_reasons`."""
    kept, rejected = [], []
    for p in programs:
        v = check_program(p["code"], p["language"], loc=p.get("loc"),
                          entry_point=p.get("entry_point"), **kw)
        if v.ok:
            kept.append(p)
        else:
            rejected.append({**p, "reject_reasons": v.reasons, "reject_stage": "static_filter"})
    return kept, rejected
