"""codeparrot/apps — call-based problems only (~3062 of the 5000 train rows).

APPS has two problem styles. The stdin/stdout style is useless here: this project
predicts a *function's return value*, and a program that reads stdin has no arguments
to vary. Only rows whose `input_output` JSON carries `fn_name` are yielded, and their
`inputs`/`outputs` lists give real, curated seed cases.

The LeetCode heritage shows up as `class Solution: def <fn_name>(self, ...)`. Those are
unwrapped into a module-level function (drop `self`, dedent the body) when the class has
a single method and never touches instance state; anything more entangled is skipped
rather than wrapped, because a `Solution()` wrapper would put a class definition in
every stimulus and change what the obfuscation conditions are being measured on.
"""
from __future__ import annotations

import ast
import json
from typing import Any, Iterator

from obtune.corpus.sources import find_cached, take

REPO_ID = "codeparrot/apps"
SOURCE = "apps"


def dataset_path():
    return find_cached(REPO_ID, "train.jsonl")


def load(limit: int | None = None, max_solutions: int = 1) -> Iterator[dict[str, Any]]:
    """Yield raw program records. `max_solutions` > 1 keeps several accepted solutions
    for the same problem — they share an upstream id, so dedup will collapse the
    alpha-equivalent ones and keep genuinely different algorithms."""
    return take(_iter(max_solutions), limit)


def _iter(max_solutions: int) -> Iterator[dict[str, Any]]:
    with open(dataset_path()) as f:
        for line in f:
            row = json.loads(line)
            io = _json_or_none(row.get("input_output"))
            if not io or not io.get("fn_name"):
                continue
            fn_name = io["fn_name"]
            seeds = _seed_cases(io)
            if not seeds:
                continue
            solutions = _json_or_none(row.get("solutions")) or []
            kept = 0
            for si, sol in enumerate(solutions):
                if kept >= max_solutions:
                    break
                code = _standalone(sol, fn_name)
                if code is None:
                    continue
                kept += 1
                yield {
                    "program_id": f"apps_{row['id']}_{si}",
                    "language": "python",
                    "source": SOURCE,
                    "code": code,
                    "entry_point": fn_name,
                    "seed_cases": seeds,
                    "meta": {"upstream_id": f"apps/{row['id']}",
                             "difficulty": row.get("difficulty"),
                             "url": row.get("url")},
                }


def _json_or_none(text: Any) -> Any:
    if not text:
        return None
    if not isinstance(text, str):
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _seed_cases(io: dict[str, Any]) -> list[str]:
    """APPS stores call-based inputs as a list of positional-argument lists."""
    out: list[str] = []
    for args in io.get("inputs", []) or []:
        values = args if isinstance(args, list) else [args]
        try:
            out.append("(" + ", ".join(repr(v) for v in values) + ("," if values else "") + ")")
        except Exception:  # noqa: BLE001 — an unrepresentable seed is skipped, not fatal
            continue
    return out[:8]


_TYPING_NAMES = frozenset({
    "List", "Dict", "Set", "Tuple", "Optional", "Union", "Any", "Callable", "Iterable",
    "Sequence", "Mapping", "Deque", "FrozenSet", "DefaultDict", "Iterator", "Counter",
})


def _standalone(solution: str, fn_name: str) -> str | None:
    """Return module-level source defining `fn_name`, or None if that is not possible."""
    try:
        tree = ast.parse(solution)
    except (SyntaxError, ValueError):
        return None

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fn_name:
            fixed = _ensure_typing_import(tree)
            # Annotations are evaluated at def time, so an un-imported `List[int]`
            # raises NameError before a single case runs. APPS relies on its own
            # harness injecting typing into globals; we make the program self-contained.
            return ast.unparse(fixed) if fixed is not tree else solution

    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if len(classes) != 1:
        return None
    cls = classes[0]
    methods = [m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(methods) != 1 or methods[0].name != fn_name:
        return None
    method = methods[0]
    if not method.args.args or method.args.args[0].arg != "self":
        return None
    # `self` may only be the vestigial first parameter; a body that actually uses it
    # needs the class, and unwrapping would change semantics.
    if any(isinstance(n, ast.Name) and n.id == "self" for n in ast.walk(method)):
        return None

    method.args.args = method.args.args[1:]
    method.decorator_list = []
    preamble = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    module = ast.Module(body=preamble + [method], type_ignores=[])
    try:
        return ast.unparse(ast.fix_missing_locations(_ensure_typing_import(module)))
    except Exception:  # noqa: BLE001
        return None


def _ensure_typing_import(module: ast.Module) -> ast.Module:
    """Prepend `from typing import ...` when annotations use typing names the module
    never imported. Returns the same object when nothing is needed, so the caller can
    tell "unchanged" from "rewritten" and keep the original source text in that case."""
    bound: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom):
            bound |= {a.asname or a.name for a in node.names}
            if any(a.name == "*" for a in node.names) and node.module == "typing":
                return module
        elif isinstance(node, ast.Import):
            bound |= {(a.asname or a.name).split(".")[0] for a in node.names}

    used: set[str] = set()
    for node in ast.walk(module):
        annotations = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotations = [a.annotation for a in node.args.args] + [node.returns]
        elif isinstance(node, ast.AnnAssign):
            annotations = [node.annotation]
        for ann in annotations:
            if ann is None:
                continue
            for sub in ast.walk(ann):
                if isinstance(sub, ast.Name) and sub.id in _TYPING_NAMES:
                    used.add(sub.id)

    missing = sorted(used - bound)
    if not missing:
        return module
    imp = ast.ImportFrom(module="typing", names=[ast.alias(name=n) for n in missing], level=0)
    return ast.fix_missing_locations(ast.Module(body=[imp] + module.body, type_ignores=[]))
