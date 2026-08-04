"""Shared infrastructure for the source-to-source obfuscator (both languages).

Design constraints
------------------
* Conditions are SINGLE-TRANSFORM from the L0 parent (configs/conditions.yaml), so
  every transform reads the same `SnippetCtx` and returns a `TransformResult`; the
  builder never chains two transforms.
* Edits are byte-span replacements applied bottom-up (`EditList`). Rewriting text by
  regex or by `str.replace` was rejected outright: it cannot tell an identifier from
  the same characters inside a string literal, and the corpus is full of programs
  whose *output* is a string containing variable-looking words.
* Determinism is per (language, condition, program, attempt) rather than per run, so
  re-generating one program's variant reproduces byte-for-byte what a full corpus
  build produced. `make_ctx` seeds `random.Random` from a repr'd tuple; the builder
  additionally strides the base seed by a prime per retry (see `obf/builder.py`).
* tree-sitter is the CST for JavaScript and for cheap syntax checks in both
  languages; the Python transforms use `ast`/`symtable` instead because Python's
  binding rules (comprehension inlining, class-scope skipping, free variables) are
  not recoverable from a CST alone.
"""
from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

import tree_sitter_javascript
import tree_sitter_python
from tree_sitter import Language, Node, Parser, Tree

from obtune.config import GLOBAL_SEED

LANGUAGES: dict[str, Language] = {
    "python": Language(tree_sitter_python.language()),
    "javascript": Language(tree_sitter_javascript.language()),
}
_PARSERS: dict[str, Parser] = {name: Parser(lang) for name, lang in LANGUAGES.items()}


class Bail(Exception):
    """A transform declines this program: correctness beats coverage.

    Raised (never swallowed silently) when a construct cannot be transformed with
    certainty. The builder records it as `technique_unavailable`, which is reported
    in data/manifests/coverage_matrix.json rather than being hidden as a failure.
    """


class EditConflict(Exception):
    """Two edits claim overlapping byte spans — the transform is buggy, not the input."""


# --------------------------------------------------------------------------- #
# Parsing helpers


def parse_tree(language: str, src: str) -> Tree:
    try:
        parser = _PARSERS[language]
    except KeyError:
        raise ValueError(f"unknown language: {language!r}") from None
    return parser.parse(src.encode("utf-8"))


def parse(language: str, src: str) -> Node:
    """Root CST node. The returned Node keeps its Tree alive (py-tree-sitter owns the ref)."""
    return parse_tree(language, src).root_node


def tree_ok(language: str, src: str) -> bool:
    """True when tree-sitter parsed `src` without an ERROR/MISSING node."""
    root = parse(language, src)
    if root.has_error:
        return False
    return not any(n.is_missing for n in iter_nodes(root))


def iter_nodes(root: Node) -> Iterator[Node]:
    stack = [root]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(reversed(n.children))


def node_text(src: str, node: Node) -> str:
    return src.encode("utf-8")[node.start_byte : node.end_byte].decode("utf-8")


def find_all(root: Node, type_: str) -> list[Node]:
    return [n for n in iter_nodes(root) if n.type == type_]


class LineIndex:
    """Byte offset of each line start — converts `ast` (line, col) pairs to byte spans.

    CPython's `col_offset` is a UTF-8 *byte* offset into the line, which is exactly
    what `EditList` wants, so no decoding round-trip is needed.
    """

    def __init__(self, src: str) -> None:
        self.data = src.encode("utf-8")
        starts = [0]
        for i, byte in enumerate(self.data):
            if byte == 0x0A:
                starts.append(i + 1)
        self.starts = starts

    def offset(self, lineno: int, col: int) -> int:
        if not 1 <= lineno <= len(self.starts):
            raise Bail(f"line {lineno} out of range (file has {len(self.starts)} lines)")
        return self.starts[lineno - 1] + col


# --------------------------------------------------------------------------- #
# Edits


@dataclass
class EditList:
    """Collect byte-span replacements; apply bottom-up so earlier offsets stay valid.

    Zero-length spans are insertions and several may share one offset (S2 stacks
    predicate blocks at the same statement boundary); they are applied in a stable
    reverse order so the output is a deterministic function of the edit list.
    """

    src: str
    edits: list[tuple[int, int, str]] = field(default_factory=list)

    def add(self, start_byte: int, end_byte: int, replacement: str) -> None:
        n = len(self.src.encode("utf-8"))
        if not 0 <= start_byte <= end_byte <= n:
            raise EditConflict(f"edit span {start_byte}:{end_byte} outside 0:{n}")
        self.edits.append((start_byte, end_byte, replacement))

    def apply(self) -> str:
        data = self.src.encode("utf-8")
        prev_start: int | None = None
        # Descending by (start, end, insertion index): applying from the back keeps
        # every not-yet-applied offset valid, and the index tiebreak makes the result
        # of co-located insertions a deterministic function of the edit list.
        order = sorted(
            enumerate(self.edits), key=lambda item: (item[1][0], item[1][1], item[0]), reverse=True
        )
        for _, (start, end, repl) in order:
            if prev_start is not None and end > prev_start:
                raise EditConflict(
                    f"overlapping edits at bytes {start}:{end} (next edit starts at {prev_start})"
                )
            prev_start = start
            data = data[:start] + repl.encode("utf-8") + data[end:]
        return data.decode("utf-8")


# --------------------------------------------------------------------------- #
# Snippet context


@dataclass
class SnippetCtx:
    """Everything a transform needs, plus the only RNG it is allowed to use."""

    language: str
    program_id: str
    condition: str
    src: str
    entry_point: str
    rng: random.Random
    params: dict[str, Any] = field(default_factory=dict)
    seed: int = GLOBAL_SEED
    attempt: int = 0

    def param(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)


def make_ctx(
    language: str,
    program_id: str,
    condition: str,
    src: str,
    entry_point: str,
    *,
    attempt: int = 0,
    seed: int = GLOBAL_SEED,
    params: dict[str, Any] | None = None,
) -> SnippetCtx:
    """Build a context whose RNG is a pure function of its coordinates.

    The seed material is the repr of the coordinate tuple rather than a hash: `hash()`
    is salted per process for str, so a hash-derived seed would silently produce a
    different corpus on every run.
    """
    rng = random.Random(repr(("obtune", seed, language, condition, program_id, attempt)))
    return SnippetCtx(
        language=language,
        program_id=program_id,
        condition=condition,
        src=src,
        entry_point=entry_point,
        rng=rng,
        params=dict(params or {}),
        seed=seed,
        attempt=attempt,
    )


# --------------------------------------------------------------------------- #
# Name generation

HEX_NAME_RE = re.compile(r"^[vf]_[0-9a-f]{4}$")
SEQ_NAME_RE = re.compile(r"^[a-z]+$")

#: Bindings that look like functions get the `f_` prefix (conditions.yaml L1r params).
FUNC_KINDS = frozenset({"func", "class"})


def hex_name(rng: random.Random, kind: str = "var") -> str:
    """`v_a3f2` / `f_9c01` — the L1r style from configs/conditions.yaml."""
    prefix = "f" if kind in FUNC_KINDS else "v"
    return f"{prefix}_{rng.randrange(0x10000):04x}"


def seq_name(index: int) -> str:
    """Bijective base-26: 0->a, 25->z, 26->aa, 27->ab ... (the L2 minifier alphabet)."""
    if index < 0:
        raise ValueError("seq_name index must be non-negative")
    out: list[str] = []
    n = index
    while True:
        out.append(string.ascii_lowercase[n % 26])
        n = n // 26 - 1
        if n < 0:
            break
    return "".join(reversed(out))


_SNAKE_SPLIT = re.compile(r"[^A-Za-z0-9]+")
_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def split_words(name: str) -> list[str]:
    """`find_maxSubArray` -> ['find', 'max', 'Sub', 'Array']; keeps original casing."""
    parts: list[str] = []
    for chunk in _SNAKE_SPLIT.split(name):
        if not chunk:
            continue
        parts.extend(p for p in _CAMEL_SPLIT.split(chunk) if p)
    return parts


def naming_style(name: str) -> str:
    """snake | camel | pascal | upper | flat — the convention `name` is written in."""
    core = name.strip("_")
    if not core:
        return "flat"
    if "_" in core:
        return "upper" if core.isupper() else "snake"
    if core.isupper():
        return "upper"
    if core[0].isupper():
        return "pascal"
    if any(c.isupper() for c in core):
        return "camel"
    return "flat"


def apply_style(words: list[str], style: str) -> str:
    """Render `words` in `style`. Used so a misleading name looks hand-written."""
    lowered = [w.lower() for w in words if w]
    if not lowered:
        return "value"
    if style == "snake":
        return "_".join(lowered)
    if style == "upper":
        return "_".join(w.upper() for w in lowered)
    if style == "pascal":
        return "".join(w.capitalize() for w in lowered)
    if style == "camel":
        return lowered[0] + "".join(w.capitalize() for w in lowered[1:])
    return "".join(lowered)


def adversarial_name(
    rng: random.Random, original: str, hint: str, *, multiword_style: str = "snake"
) -> str:
    """Re-case a misleading stem so it matches `original`'s naming convention.

    The *vocabulary* (which stem misleads about what) is language-agnostic data and
    lives in obf/py/adversarial.py; this is only the mechanical part, shared with the
    JavaScript side, whose corpus is camelCase where Python's is snake_case. The rng
    is used only to break the tie when `hint` collapses onto `original`.

    `multiword_style` decides how a multi-word hint is joined when `original` itself
    is a single lowercase word and therefore carries no convention signal (`fibfib`
    gives no hint whether the file writes `smooth_area` or `smoothArea`).
    """
    style = naming_style(original)
    words = split_words(hint) or [hint]
    if style == "flat" and len(words) > 1:
        style = multiword_style
    out = apply_style(words, style)
    if out == original:
        # A hint that reproduces the original misleads nobody; perturb minimally.
        out = apply_style(words + [rng.choice(("value", "state", "step", "slot"))], style)
    if original.startswith("_") and not out.startswith("_"):
        out = "_" + out
    return out


def fresh_name(gen: Callable[[], str], taken: set[str], *, attempts: int = 400) -> str:
    """First `gen()` result not already in `taken`; registers it. Raises Bail if starved."""
    for _ in range(attempts):
        cand = gen()
        if cand and cand not in taken:
            taken.add(cand)
            return cand
    raise Bail(f"could not generate a fresh identifier after {attempts} attempts")


# --------------------------------------------------------------------------- #
# Transform result


@dataclass
class TransformResult:
    """What every transform returns. `applied=False` means "declined", not "failed"."""

    src_out: str
    applied: bool
    notes: list[str] = field(default_factory=list)
    skipped_constructs: list[str] = field(default_factory=list)
    rename_map: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def entry_point_out(self) -> str | None:
        """Post-transform entry-point name, when the transform renamed it."""
        return self.extra.get("entry_point_new")
