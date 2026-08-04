"""L0 normalization — the canonical parent every condition is generated from.

L0 is not "the original file". It is a *regenerated* form: parse to an AST, delete
docstrings, and print back with one printer per language (`ast.unparse` for Python,
`@babel/generator` for JavaScript). Regeneration is what makes the two languages
comparable — the same policy (comments gone, 4-space indent, LF, no blank lines,
canonical intra-line spacing) is applied by construction rather than by two
different piles of whitespace heuristics.

Rejected alternative: a tokenize-preserving strip that deletes only COMMENT tokens
and re-indents in place. It keeps the author's line breaks, but it cannot repair the
formatting damage already present in the legacy stimuli (Dataset A's double-spaced
human-study rows; the `g =[[]for _ in range (n )]` decompiler spacing in the
LeetCode rows), and it would leave Python normalized by one mechanism and JS by
another. Since the byte-identical legacy rows are preserved separately in
data/eval/testset/legacy_icse/, nothing depends on L0 keeping original bytes.

Every normalization is verified by an AST round-trip: the regenerated text must
parse back to a structurally identical tree (docstrings excepted). A program whose
round-trip fails is rejected rather than silently mangled.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from obtune.config import PROJECT_ROOT

_HERE = Path(__file__).resolve().parent
JS_NORMALIZE_MJS = _HERE / "js_normalize.mjs"
JS_WORKSPACE = PROJECT_ROOT / "js"
NODE_BIN = os.environ.get("OBTUNE_NODE") or shutil.which("node") or "node"


class NormalizationError(ValueError):
    """The program could not be normalized into a trustworthy L0 parent."""


@dataclass
class Normalized:
    code: str
    loc: int
    language: str
    changed: bool  # True when the normalized text differs from the input bytes
    notes: dict[str, Any] = field(default_factory=dict)


def loc_count(code: str) -> int:
    """Lines of code = non-blank physical lines. L0 has no blank lines by policy, so
    this equals the line count for normalized text; it is defined generally because
    filters.py also measures un-normalized candidates."""
    return sum(1 for line in code.splitlines() if line.strip())


def normalize(code: str, language: str) -> Normalized:
    if language == "python":
        return normalize_python(code)
    if language == "javascript":
        return normalize_javascript(code)
    raise ValueError(f"unknown language: {language}")


# --------------------------------------------------------------------------- Python


class _DocstringStripper(ast.NodeTransformer):
    """Delete the leading string-constant Expr of every module/class/function body.

    A body that becomes empty gets an explicit `pass` so the tree stays printable.
    """

    _SCOPES = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)

    def _strip(self, node: ast.AST) -> ast.AST:
        self.generic_visit(node)
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            body = body[1:]
            if not body:
                body = [ast.Pass()]
            node.body = body  # type: ignore[attr-defined]
        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        return self._strip(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        return self._strip(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._strip(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self._strip(node)


def strip_python_docstrings(tree: ast.Module) -> ast.Module:
    return ast.fix_missing_locations(_DocstringStripper().visit(tree))


def normalize_python(code: str) -> Normalized:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError) as e:  # ValueError: null bytes
        raise NormalizationError(f"python parse failed: {e}") from e

    stripped = strip_python_docstrings(tree)
    try:
        out = ast.unparse(stripped)
    except Exception as e:  # noqa: BLE001 — unparse can trip on exotic nodes
        raise NormalizationError(f"python unparse failed: {type(e).__name__}: {e}") from e

    out = _finish(out)

    # Round-trip guard: the printed text must parse back to the same tree. Without
    # this, an unparse bug would silently change program semantics and the whole
    # corpus downstream would be wrong in a way no gate could detect (every variant
    # would agree with the *broken* parent).
    try:
        back = ast.parse(out)
    except SyntaxError as e:
        raise NormalizationError(f"python round-trip reparse failed: {e}") from e
    if ast.dump(strip_python_docstrings(back)) != ast.dump(stripped):
        raise NormalizationError("python round-trip changed the AST")

    return Normalized(code=out, loc=loc_count(out), language="python",
                      changed=out != code, notes={"printer": "ast.unparse"})


# ----------------------------------------------------------------------- JavaScript


def normalize_javascript(code: str) -> Normalized:
    """Normalize JS via the obf/js L0 driver when a peer has provided one, else via
    the local Babel helper. The driver is looked up by name and never imported at
    module scope, so this module stays usable before obf/ exists."""
    driver = _js_l0_driver()
    if driver is not None:
        out = _finish(driver(code))
        return Normalized(code=out, loc=loc_count(out), language="javascript",
                          changed=out != code, notes={"printer": "obf.js.driver.L0"})

    res = _node_js_helper({"op": "normalize", "code": code})
    # The helper has already re-indented and dropped blank lines in a
    # template-literal-aware way; `protected` marks the physical lines whose
    # whitespace is part of a string value and must not be touched again here.
    out = _finish(res["code"], protected=frozenset(res.get("protected_lines", ())))
    return Normalized(code=out, loc=loc_count(out), language="javascript",
                      changed=out != code, notes={"printer": "babel"})


def _js_l0_driver():
    """Return a `code -> code` L0 callable from obf/js if a peer has published one.

    Looked up lazily by name: this package must import cleanly before src/obtune/obf/
    exists, and it must never be the reason obf/ code gets imported into a training
    job. Any import or attribute failure means "no driver", never an exception.
    """
    try:
        import importlib

        mod = importlib.import_module("obtune.obf.js.driver")
    except Exception:  # noqa: BLE001 — absence is the normal case
        return None
    for name in ("normalize_l0", "l0", "apply_l0"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None


def _node_js_helper(payload: dict[str, Any], timeout_s: float = 30.0) -> dict[str, Any]:
    if not JS_NORMALIZE_MJS.exists():
        raise NormalizationError(f"missing helper: {JS_NORMALIZE_MJS}")
    env = dict(os.environ, OBTUNE_JS_ROOT=str(JS_WORKSPACE))
    proc = subprocess.run(
        [NODE_BIN, "--no-warnings", str(JS_NORMALIZE_MJS)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=timeout_s,
        cwd=str(JS_WORKSPACE), env=env,
    )
    if proc.returncode != 0:
        raise NormalizationError(f"js helper failed: {proc.stderr.strip()[:400]}")
    try:
        res = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise NormalizationError(f"js helper emitted non-JSON: {proc.stdout[:200]!r}") from e
    if not res.get("ok"):
        raise NormalizationError(f"js helper error: {res.get('error', '')[:400]}")
    return res


def js_call_args(call_src: str) -> tuple[str, list[str]]:
    """Split a JavaScript call expression into (callee name, argument source texts).

    Babel is used rather than paren matching because arguments legitimately contain
    parentheses, template literals and regex literals ('/[ÄäÏï]/' appears in the
    CruxEval-X stimuli) that no bracket counter gets right.
    """
    res = _node_js_helper({"op": "call", "code": call_src})
    return res["callee"], list(res["args"])


def js_defined_names(code: str) -> list[str]:
    """Top-level binding names in declaration order (function decls, const/let/var,
    and `module.exports`-free ESM exports). Used to resolve a JS entry point when the
    source metadata does not name one, or names one the code does not define."""
    res = _node_js_helper({"op": "names", "code": code})
    return list(res["names"])


# ---------------------------------------------------------------------------- shared


def _finish(code: str, protected: frozenset[int] = frozenset()) -> str:
    """Apply the whitespace policy shared by both languages: LF endings, no trailing
    whitespace, no blank lines, single trailing LF.

    Blank lines are dropped outright rather than collapsed — that is what neutralizes
    Dataset A's double-spaced human-study presentation artifact. `protected` holds
    1-based line numbers whose whitespace is *inside a string value* (JS multi-line
    template literals); those lines are passed through untouched, because trimming
    them would change the program's output.
    """
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for i, line in enumerate(code.split("\n"), start=1):
        if i in protected:
            out.append(line)
        elif line.strip():
            out.append(line.rstrip())
    return "\n".join(out) + ("\n" if out else "")
