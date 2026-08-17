"""Static Python normalization passes — the zero-training deobfuscation baseline.

WHY THIS BASELINE EXISTS
------------------------
Every adapter, merge and mixture arm in this project buys its gain with GPU hours. A
reviewer is entitled to ask what a *compiler-style* normalizer recovers for free, and the
project already owns most of the machinery: `obf/py/rename.py`'s `seq` style is documented
there as an alpha-equivalence canonicalizer. Applying it as PREPROCESSING — normalize the
obfuscated program, then run the untuned base model on the result — costs nothing and is
the first thing a practitioner would actually try.

If it recovers most of the adapter gain, that is a genuinely important negative for the
fine-tuning framing, and better learned now than in review.

THE DESIGN CONSTRAINT THAT MATTERS MOST
---------------------------------------
The passes are written as a GENERIC normalizer and were deliberately NOT tuned against
`H1`. Inspecting the held-out obfuscator's implementation to decide which rewrites to
implement would be using H1 for hyperparameter selection, which CLAUDE.md §3.2 rule 2
forbids just as squarely as training on it. So `fold` folds constant expressions because
constant folding is what normalizers do — not because anyone checked what H1 emits. What
it happens to recover on H1 is therefore an honest out-of-distribution measurement.

SOUNDNESS
---------
Normalization must preserve behaviour or the baseline is measuring a different program.
Two independent guards:

  1. *Static* — every pass bails (leaving the source untouched) rather than guessing, and
     the result must re-parse.
  2. *Dynamic* — `scripts/analysis/21_build_normalized.py` EXECUTES each normalized program
     against the item's stored canonical output and reverts any program whose behaviour
     changed. The revert rate is recorded, not hidden.

Guard 2 is the load-bearing one: it means a bug in a pass costs coverage, never correctness.

PASSES
------
`alpha`    canonical sequential identifier renaming (`a`, `b`, ...), preserving the entry
           point. Attacks L1b (misleading names) and L1r (hex names). Surgical text edits,
           so formatting survives.
`fold`     constant-fold pure literal expressions and a small allowlist of pure builtin
           calls. Attacks arithmetic/string obfuscation generically.
`dce`      drop statically-unreachable branches and unreferenced module-level helpers.
           Attacks dead-code insertion (S3) and unreachable branches (S5).
`reformat` re-emit through `ast.unparse`. Not a deobfuscation in itself — it is the
           CONTROL that separates "normalization helped" from "reformatting helped", since
           `fold` and `dce` must unparse to take effect and would otherwise confound the two.
"""
from __future__ import annotations

import ast
import builtins
import random
from dataclasses import dataclass, field
from typing import Any, Sequence

from obtune.obf.base import Bail, SnippetCtx

PASSES: tuple[str, ...] = ("alpha", "fold", "dce", "reformat")

#: The evaluated arms. Ordering inside a profile is the ORDER THE PASSES RUN and is not
#: arbitrary: `fold` first so that `dce` can see a test that folded to a constant, then the
#: unparse those two require, and `alpha` last because it edits source text directly.
PROFILES: dict[str, tuple[str, ...]] = {
    "alpha": ("alpha",),
    "reformat": ("reformat",),
    "full": ("fold", "dce", "reformat", "alpha"),
    # `full` MINUS `alpha`. Added 2026-08-13 after the first run showed `alpha` is what
    # sinks the profile: it costs 6.8 pts on L0 by renaming meaningful identifiers to
    # `a`, `b`, `c`, which swamps dce's +4.5 on S3. The structural passes are the ones that
    # remove injected junk without discarding information the model was using, so this
    # should dominate `full` everywhere and is the profile a practitioner would ship.
    "structural": ("fold", "dce", "reformat"),
}


@dataclass
class NormResult:
    code: str
    applied: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.applied)


# --------------------------------------------------------------------------- #
# fold — constant folding

#: Pure, side-effect-free builtins safe to evaluate at normalization time. Deliberately
#: small: anything that can touch the filesystem, the network, the import system or object
#: identity is absent, and there is no `__builtins__` in the eval namespace either.
_SAFE_BUILTINS: dict[str, Any] = {
    n: getattr(builtins, n)
    for n in ("chr", "ord", "len", "str", "int", "float", "bool", "abs", "bytes",
              "bytearray", "hex", "oct", "bin", "min", "max", "sum", "tuple", "list",
              "sorted", "round", "divmod", "repr")
}

#: Methods folded on a constant receiver. All are pure on str/bytes/tuple/list.
_SAFE_METHODS = frozenset({
    "join", "encode", "decode", "upper", "lower", "strip", "lstrip", "rstrip",
    "replace", "split", "rsplit", "title", "capitalize", "swapcase", "zfill",
    "count", "find", "index", "startswith", "endswith", "removeprefix", "removesuffix",
})

_FOLD_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd)

#: Caps that stop folding from building an enormous literal (or hanging on `9**9**9`).
#: A rejected fold costs coverage; an unbounded one costs the machine.
_MAX_POW_EXP = 16
_MAX_INT_DIGITS = 64
_MAX_REPR = 4096


def _const_ok(v: Any) -> bool:
    """Is this constant small enough to participate in a fold?"""
    if isinstance(v, int) and not isinstance(v, bool):
        return len(str(abs(v))) <= _MAX_INT_DIGITS
    if isinstance(v, (str, bytes)):
        return len(v) <= _MAX_REPR
    return isinstance(v, (float, bool, complex)) or v is None


def _foldable(node: ast.AST) -> bool:
    """True when `node` is a pure literal expression we are willing to evaluate.

    Whitelist, never blacklist: an unrecognised node type is not foldable. That is what
    keeps a `Name`, an attribute load, a comprehension or a call to unknown code out of
    the eval below.
    """
    if isinstance(node, ast.Constant):
        return _const_ok(node.value)
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.op, (ast.UAdd, ast.USub, ast.Invert, ast.Not)) and _foldable(node.operand)
    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, _FOLD_BINOPS):
            return False
        if isinstance(node.op, ast.Pow):
            # `2 ** 10 ** 10` is a foldable expression and a denial of service.
            r = node.right
            if not (isinstance(r, ast.Constant) and isinstance(r.value, int)
                    and not isinstance(r.value, bool) and abs(r.value) <= _MAX_POW_EXP):
                return False
        return _foldable(node.left) and _foldable(node.right)
    if isinstance(node, ast.BoolOp):
        return all(_foldable(v) for v in node.values)
    if isinstance(node, ast.Compare):
        return _foldable(node.left) and all(_foldable(c) for c in node.comparators)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(_foldable(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(k is not None and _foldable(k) for k in node.keys) and all(_foldable(v) for v in node.values)
    if isinstance(node, ast.Subscript):
        return _foldable(node.value) and _foldable(node.slice)
    if isinstance(node, ast.Slice):
        return all(p is None or _foldable(p) for p in (node.lower, node.upper, node.step))
    if isinstance(node, ast.Call):
        if node.keywords or any(isinstance(a, ast.Starred) for a in node.args):
            return False
        if not all(_foldable(a) for a in node.args):
            return False
        if isinstance(node.func, ast.Name):
            return node.func.id in _SAFE_BUILTINS
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in _SAFE_METHODS and _foldable(node.func.value)
    return False


def _literalize(value: Any) -> ast.expr | None:
    """A Constant node for `value`, but only if it round-trips through its own repr.

    The round-trip is the check that matters: if `ast.literal_eval(repr(v))` does not
    reproduce `v`, substituting a literal would silently change the program, so we decline.
    """
    if not isinstance(value, (int, float, complex, bool, str, bytes, type(None))):
        return None
    try:
        text = repr(value)
        if len(text) > _MAX_REPR:
            return None
        if ast.literal_eval(text) != value or type(ast.literal_eval(text)) is not type(value):
            return None
    except Exception:
        return None
    return ast.Constant(value=value)


class _Folder(ast.NodeTransformer):
    def __init__(self) -> None:
        self.n = 0

    def visit(self, node: ast.AST) -> Any:
        node = self.generic_visit(node)  # bottom-up: children fold before their parent
        if not isinstance(node, ast.expr) or isinstance(node, ast.Constant):
            return node
        if not _foldable(node):
            return node
        try:
            code = compile(ast.Expression(body=node), "<fold>", "eval")
            value = eval(code, {"__builtins__": {}}, dict(_SAFE_BUILTINS))  # noqa: S307
        except Exception:
            return node  # a fold that raises is simply not performed
        lit = _literalize(value)
        if lit is None:
            return node
        self.n += 1
        return ast.copy_location(lit, node)


def _pass_fold(tree: ast.Module, entry_point: str) -> tuple[ast.Module, int]:
    f = _Folder()
    out = f.visit(tree)
    return out, f.n


# --------------------------------------------------------------------------- #
# dce — unreachable branches and unreferenced module-level helpers


def _static_truth(node: ast.expr) -> bool | None:
    """The compile-time truth value of `node`, or None when it is not statically known."""
    if isinstance(node, ast.Constant):
        try:
            return bool(node.value)
        except Exception:
            return None
    if isinstance(node, (ast.Tuple, ast.List)) and not node.elts:
        return False
    if isinstance(node, (ast.Tuple, ast.List)) and all(isinstance(e, ast.Constant) for e in node.elts):
        return True
    return None


def _body_or_pass(body: list[ast.stmt]) -> list[ast.stmt]:
    return body if body else [ast.Pass()]


class _Unreachable(ast.NodeTransformer):
    """Drop branches the interpreter can never enter."""

    def __init__(self) -> None:
        self.n = 0

    def visit_If(self, node: ast.If) -> Any:
        self.generic_visit(node)
        truth = _static_truth(node.test)
        if truth is None:
            return node
        self.n += 1
        # Inlining the taken branch is safe: `if` does not introduce a scope in Python.
        taken = node.body if truth else node.orelse
        return taken if taken else ast.Pass()

    def visit_While(self, node: ast.While) -> Any:
        self.generic_visit(node)
        # Only the never-entered case. A statically-true `while` still terminates via
        # `break`/`return`, so it is NOT dead and must be left exactly as written.
        if _static_truth(node.test) is False:
            self.n += 1
            # `while False: ... else: X` runs X — dropping the else would change behaviour.
            return node.orelse if node.orelse else ast.Pass()
        return node


#: Names whose presence anywhere in the module makes the unused-helper analysis unsound:
#: they can reach a definition without ever mentioning it as a `Name` load.
_REFLECTION = frozenset({"exec", "eval", "globals", "locals", "vars", "getattr",
                         "setattr", "__import__", "compile"})


def _referenced_names(tree: ast.Module, skip: set[int]) -> set[str]:
    """Every name the module could plausibly reach, ignoring the definitions in `skip`.

    String constants are included wholesale. That is deliberately over-broad — a program
    that merely *mentions* a helper's name in a docstring keeps it — because a false
    "unused" is a semantic change and a false "used" only costs coverage.
    """
    used: set[str] = set()
    for node in ast.walk(tree):
        if id(node) in skip:
            continue
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            used.update(node.value.replace(".", " ").replace(",", " ").split())
    return used


def _pass_dce_helpers(tree: ast.Module, entry_point: str) -> tuple[ast.Module, int]:
    """Remove module-level defs that nothing can reach. Conservative by construction."""
    if any(isinstance(n, ast.Name) and n.id in _REFLECTION for n in ast.walk(tree)):
        return tree, 0
    removed = 0
    changed = True
    while changed:  # removing one helper can orphan another it was the only caller of
        changed = False
        for stmt in list(tree.body):
            # Functions only. A `class` body EXECUTES at module level, so an apparently
            # unreferenced class can still have had side effects; removing it would be a
            # semantic change rather than dead-code elimination.
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if stmt.name == entry_point or stmt.decorator_list:
                continue
            # Everything the module can see EXCEPT this definition's own subtree.
            own = {id(n) for n in ast.walk(stmt)}
            if stmt.name in _referenced_names(tree, own):
                continue
            tree.body.remove(stmt)
            removed += 1
            changed = True
    if not tree.body:
        tree.body = [ast.Pass()]
    return tree, removed


def _drop_redundant_pass(tree: ast.AST) -> None:
    """`if False: ...` leaves a `pass` behind; strip it wherever it is not load-bearing.

    Cosmetic, but this baseline is measured on a MODEL reading the result, so leftover
    scaffolding is not cosmetic to the thing being measured.
    """
    for node in ast.walk(tree):
        for attr in ("body", "orelse", "finalbody"):
            block = getattr(node, attr, None)
            if not isinstance(block, list) or len(block) <= 1:
                continue
            kept = [s for s in block if not isinstance(s, ast.Pass)]
            setattr(node, attr, kept if kept else [ast.Pass()])


def _pass_dce(tree: ast.Module, entry_point: str) -> tuple[ast.Module, int]:
    u = _Unreachable()
    tree = u.visit(tree)
    # ONLY `body`. An empty `orelse`/`finalbody` is the normal state — it means the clause
    # is absent — so filling those with `pass` turns "no else" into "else: pass" and makes
    # every `if` and `for` in the program LONGER. Behaviour is unchanged, so the execution
    # gate cannot see it; it would simply have biased the `full` arm downwards by feeding
    # the model more scaffolding than the un-normalized program had.
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and not body:
            node.body = _body_or_pass([])
    _drop_redundant_pass(tree)
    tree, n_helpers = _pass_dce_helpers(tree, entry_point)
    return tree, u.n + n_helpers


# --------------------------------------------------------------------------- #
# alpha — canonical renaming, entry point preserved


def _pass_alpha(src: str, entry_point: str) -> tuple[str, int]:
    from obtune.obf.py.rename import rename

    ctx = SnippetCtx(
        language="python",
        program_id="<normalize>",
        # `entry_point=""` on purpose: a non-empty value makes `rename` ASSERT the entry
        # point was renamed (mandatory for the L1r/L2/L1b conditions). Here it must NOT
        # be renamed, because the harness calls the program by that name.
        condition="L2",
        src=src,
        entry_point="",
        rng=random.Random(0),
    )
    res = rename(ctx, "seq", preserve=frozenset({entry_point}) if entry_point else frozenset())
    if not res.applied:
        return src, 0
    return res.src_out, int(res.extra.get("n_bindings", 0)) if res.extra else 0


# --------------------------------------------------------------------------- #
# driver


def normalize_python(src: str, *, entry_point: str = "", passes: Sequence[str] = ("alpha",)) -> NormResult:
    """Apply `passes` in order. A pass that bails is skipped; the source is never corrupted.

    Bails are recorded in `notes` rather than raised: a program the normalizer cannot handle
    is a coverage fact to report, not a run-ending error.
    """
    unknown = [p for p in passes if p not in PASSES]
    if unknown:
        raise ValueError(f"unknown normalization pass(es): {unknown}; known: {list(PASSES)}")

    code = src
    applied: list[str] = []
    notes: list[str] = []
    #: True once an AST pass has run, so the result must be re-emitted to take effect.
    needs_unparse = False
    tree: ast.Module | None = None

    def _tree() -> ast.Module:
        nonlocal tree
        if tree is None:
            tree = ast.parse(code)
        return tree

    for name in passes:
        try:
            if name == "alpha":
                if needs_unparse and tree is not None:
                    code, tree, needs_unparse = _emit(tree), None, False
                new, n = _pass_alpha(code, entry_point)
                if n:
                    code, applied = new, applied + ["alpha"]
                    notes.append(f"alpha: renamed {n} bindings")
            elif name == "fold":
                t, n = _pass_fold(_tree(), entry_point)
                tree = t
                if n:
                    applied.append("fold")
                    needs_unparse = True
                    notes.append(f"fold: folded {n} expressions")
            elif name == "dce":
                t, n = _pass_dce(_tree(), entry_point)
                tree = t
                if n:
                    applied.append("dce")
                    needs_unparse = True
                    notes.append(f"dce: removed {n} constructs")
            elif name == "reformat":
                _tree()
                needs_unparse = True
                if "reformat" not in applied:
                    applied.append("reformat")
        except (Bail, SyntaxError, RecursionError, ValueError) as exc:
            notes.append(f"{name}: bailed ({type(exc).__name__}: {exc})")
            tree = None  # a half-transformed tree is not trustworthy; re-parse from `code`

    if needs_unparse and tree is not None:
        try:
            code = _emit(tree)
        except (SyntaxError, RecursionError, ValueError, AttributeError) as exc:
            notes.append(f"unparse: bailed ({type(exc).__name__}: {exc})")
            return NormResult(src, [], notes + ["reverted: unparse failed"])

    try:
        ast.parse(code)
    except SyntaxError as exc:
        # Belt and braces. Nothing above should be able to produce this, and if it ever
        # does, the honest outcome is the untouched program rather than a broken one.
        return NormResult(src, [], notes + [f"reverted: result does not parse ({exc})"])

    return NormResult(code, applied, notes)


def _emit(tree: ast.Module) -> str:
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def normalize(code: str, language: str, *, entry_point: str = "", profile: str = "alpha") -> NormResult:
    """Profile-level entry point. Non-Python languages pass through untouched.

    JavaScript normalization would need its own scope analysis (`let`-per-iteration
    bindings, hoisting) and is deliberately out of scope — the baseline is reported on
    Python, and a silent no-op is better than a wrong rewrite.
    """
    if profile not in PROFILES:
        raise ValueError(f"unknown normalization profile {profile!r}; known: {sorted(PROFILES)}")
    if language != "python":
        return NormResult(code, [], [f"normalization not implemented for {language}"])
    return normalize_python(code, entry_point=entry_point, passes=PROFILES[profile])
