"""The semantic gate — the only way a variant enters the corpus.

A variant is accepted only if it is observationally identical to its L0 parent on
every recorded case *and* on the ~20 fuzz `gate_inputs`, stays inside the per-condition
size cap, does not blow up runtime, and carries none of the H1 marker patterns.

Checks run cheap-to-expensive and short-circuit, so a variant that fails to parse never
reaches the (subprocess-heavy) execution stage:

  1. parses                — `compile()` for Python, tree-sitter for JavaScript
  2. non-identity          — every condition except L0 must actually change the text
  3. condition purity      — family invariants + the h1_marker_patterns regex scan,
                             applied to EVERY trainable condition (CLAUDE.md §3.2 layer 4
                             catches leakage after the fact; this catches it before)
  4. exec parity           — exec/pool.run_batch on cases + gate_inputs, compared with
                             CaseResult.matches (exception TYPE only: obfuscation
                             legitimately changes messages, line numbers and tracebacks)
  5. runtime ratio         — variant total_ms / parent total_ms <= gate.runtime_ratio_max
  6. size cap              — len(variant) / len(parent) <= conditions[cond].size_cap

Design note: the H1 scan fails a variant even when the marker is *pre-existing* in the
parent (an `import base64` program). That looks harsh, but scripts/check_manifest.py
scans absolutely, so admitting such a program would guarantee a later manifest failure
on a file nobody can then explain. Rejecting at the gate keeps all four quarantine
layers consistent, and the detail line says which case it was.
"""
from __future__ import annotations

import ast
import re

from obtune.obf.base import iter_nodes as _obf_iter_nodes
from obtune.obf.base import node_text as _obf_node_text
from obtune.obf.base import parse as _obf_parse
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from obtune.config import conditions as load_conditions
from obtune.exec.pool import BatchItem, run_batch
from obtune.obf.base import iter_nodes, node_text, parse, tree_ok
from obtune.schema import BaseProgram, Variant

#: Families whose transform must rename the entry function (conditions.yaml).
_IDENTIFIER_FAMILY = "identifier"
_STRUCTURAL_FAMILY = "structural"
_COMPOSITE_FAMILY = "composite"

_HEX_NAME_RE = re.compile(r"^[vf]_[0-9a-f]{4}$")
_SEQ_NAME_RE = re.compile(r"^[a-z]+$")


@dataclass
class Verdict:
    ok: bool
    checks: dict[str, bool] = field(default_factory=dict)
    mismatch_details: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": dict(self.checks),
            "mismatch_details": list(self.mismatch_details),
            "metrics": dict(self.metrics),
        }


class _Gate:
    """Accumulates checks and short-circuits on the first failure."""

    def __init__(self) -> None:
        self.checks: dict[str, bool] = {}
        self.details: list[str] = []
        self.metrics: dict[str, Any] = {}

    def record(self, name: str, ok: bool, detail: str = "") -> bool:
        self.checks[name] = bool(ok)
        if not ok and detail:
            self.details.append(detail)
        return bool(ok)

    def verdict(self) -> Verdict:
        return Verdict(
            ok=bool(self.checks) and all(self.checks.values()),
            checks=self.checks,
            mismatch_details=self.details,
            metrics=self.metrics,
        )


def _parses(language: str, code: str) -> tuple[bool, str]:
    if language == "python":
        try:
            compile(code, "<variant>", "exec")
        except (SyntaxError, ValueError) as exc:
            return False, f"python compile failed: {exc}"
        return True, ""
    if language == "javascript":
        if not tree_ok("javascript", code):
            return False, "tree-sitter reports syntax errors in the variant"
        return True, ""
    return False, f"unknown language {language!r}"


def _h1_markers(patterns: Sequence[str], code: str) -> list[str]:
    hits: list[str] = []
    for pat in patterns:
        if re.search(pat, code):
            hits.append(pat)
    return hits


def _purity(
    gate: _Gate,
    parent: BaseProgram,
    variant: Variant,
    spec: dict[str, Any],
    cfg: dict[str, Any] | None = None,
) -> bool:
    """Family invariants: each condition must be the transform it claims to be.

    Without this a builder bug (an S1 module silently falling back to the parent, a
    renamer that skipped the entry point) would produce a corpus whose condition labels
    are wrong — the single failure mode that no downstream analysis can detect.
    """
    if spec.get("family") == _COMPOSITE_FAMILY:
        return _purity_composite(gate, parent, variant, spec, cfg or {})
    family = spec.get("family", "none")
    params = spec.get("params", {}) or {}
    cond = variant.condition
    ok = True

    if cond == "L0":
        ok &= gate.record(
            "purity_l0_identity",
            variant.code == parent.code and variant.entry_point == parent.entry_point,
            "L0 must be the parent verbatim",
        )
        return ok

    if family == _IDENTIFIER_FAMILY:
        renamed = dict(variant.rename_map)
        ok &= gate.record("purity_rename_map", bool(renamed), f"{cond}: empty rename_map")
        if params.get("rename_entry", False):
            ok &= gate.record(
                "purity_entry_renamed",
                variant.entry_point != parent.entry_point,
                f"{cond}: entry point {parent.entry_point!r} was not renamed",
            )
        # An identifier transform never changes line structure; L2 additionally deletes
        # annotations, which is still a within-line edit.
        ok &= gate.record(
            "purity_line_count",
            variant.code.count("\n") == parent.code.count("\n"),
            f"{cond}: line count changed ({parent.code.count(chr(10))} -> "
            f"{variant.code.count(chr(10))}) — an identifier transform must not",
        )
        style = params.get("style")
        if style == "hex":
            bad = [v for v in renamed.values() if not _HEX_NAME_RE.match(v)]
            ok &= gate.record("purity_hex_names", not bad, f"L1r: non-hex names {bad[:5]}")
        elif style == "seq":
            bad = [v for v in renamed.values() if not _SEQ_NAME_RE.match(v)]
            ok &= gate.record("purity_seq_names", not bad, f"L2: non-sequential names {bad[:5]}")
        if cond == "L1b":
            same = [k.split("@")[0] for k, v in renamed.items() if k.split("@")[0] == v]
            ok &= gate.record(
                "purity_adversarial_names", not same, f"L1b: names unchanged {same[:5]}"
            )
        if params.get("strip_annotations") and variant.language == "python":
            ok &= gate.record(
                "purity_annotations_stripped",
                not _has_annotations(variant.code),
                "L2: type annotations survived",
            )
    elif family == _STRUCTURAL_FAMILY:
        ok &= gate.record(
            "purity_no_rename",
            not variant.rename_map and variant.entry_point == parent.entry_point,
            f"{cond}: a structural condition must not rename anything",
        )
        if cond == "S1":
            ok &= gate.record(
                "purity_dispatch_loop",
                _has_dispatch_loop(variant.language, variant.code, variant.entry_point),
                "S1: no dispatch loop found in the entry function",
            )
        if cond in ("S2", "S3", "S4", "S5", "S6"):
            ok &= gate.record(
                "purity_code_added",
                variant.code.count("\n") > parent.code.count("\n"),
                f"{cond}: no lines were added",
            )
        # "Lines were added" is satisfied by BOTH halves of S2, so it cannot tell a
        # mislabelled S3 from an S4 — exactly the mislabelling this function exists to
        # prevent. Each split condition therefore gets a POSITIVE invariant naming its own
        # mechanism, verified by parsing the code rather than by trusting transform_meta.
        if cond == "S3":
            ok &= gate.record(
                "purity_dead_helper_added",
                _added_uncalled_def(variant.language, parent.code, variant.code),
                "S3: no uncalled module-level def was added (that is S3's whole mechanism)",
            )
            ok &= gate.record(
                "purity_no_opaque_guard",
                not _added_computed_guard(variant.language, parent.code, variant.code, variant.entry_point),
                "S3: an opaque predicate was inserted — that is S4's mechanism, not S3's",
            )
        if cond == "S4":
            ok &= gate.record(
                "purity_opaque_guard_added",
                _added_computed_guard(variant.language, parent.code, variant.code, variant.entry_point),
                "S4: no computed opaque guard was added to the entry function",
            )
            ok &= gate.record(
                "purity_no_dead_helper",
                _module_def_count(variant.language, variant.code)
                == _module_def_count(variant.language, parent.code),
                "S4: a module-level def was added — that is S3's mechanism, not S4's",
            )
        if cond == "S5":
            ok &= gate.record(
                "purity_unreachable_literal_guard",
                _added_literal_dead_guard(variant.language, parent.code, variant.code, variant.entry_point),
                "S5: no statically-dead literal guard (`if 0:`) was added",
            )
            ok &= gate.record(
                "purity_no_dead_helper",
                _module_def_count(variant.language, variant.code)
                == _module_def_count(variant.language, parent.code),
                "S5: a module-level def was added — that is S3's mechanism, not S5's",
            )
        if cond == "S6":
            ok &= gate.record(
                "purity_loop_removed",
                _entry_loop_count(variant.language, variant.code, variant.entry_point)
                < _entry_loop_count(variant.language, parent.code, parent.entry_point),
                "S6: the entry function has no fewer loops — nothing was unrolled",
            )
    return ok


def _purity_composite(
    gate: _Gate,
    parent: BaseProgram,
    variant: Variant,
    spec: dict[str, Any],
    cfg: dict[str, Any],
) -> bool:
    """Every constituent's MECHANISM must be present in the stacked output.

    Composites are semantics-verified for free — `gate()` runs `exec_parity` against the
    L0 parent's stored cases regardless of how many transforms produced the variant. They
    are NOT mechanism-verified for free, and without this a composite whose second stage
    silently no-op'd would be labelled `C_L1r_S1` while being plain `L1r`. That variant
    would then carry the headline claim of Part III, which is precisely that a stacked
    variant contains two mechanisms and therefore no single expert can be right.

    WHY THIS IS NOT "run both constituents' `_purity`"
    -------------------------------------------------
    That is unsatisfiable, and `C_S4_S3` proves it: S3's invariant set requires that NO
    opaque guard was added, S4's requires that one WAS. Each condition's exclusion clauses
    exist to separate it from its siblings *when applied alone*; under composition they
    contradict each other by construction. Two further invariants are dropped for the same
    reason, and are named in `purity_composite_relaxed` so the weakening is visible in the
    gate record rather than inferred from this comment:

      * identifier `purity_line_count` — an identifier transform alone cannot change the
        line count, but a structural co-stage adds lines;
      * structural `purity_no_rename` — a structural transform alone renames nothing, but
        an identifier co-stage populates `rename_map`.

    What remains is each part's POSITIVE mechanism invariant, which is the part that
    actually carries the label, and every one is parsed out of the emitted code rather
    than read from `transform_meta` — purity must never trust the transform's self-report.
    """
    parts = list(spec.get("parts") or [])
    ladder = cfg.get("conditions") or {}
    ok = gate.record(
        "purity_composite_parts",
        len(parts) >= 2 and all(p in ladder for p in parts),
        f"{variant.condition}: parts {parts} are not all declared in the ladder",
    )
    if not ok:
        return False

    # Recorded, not silent: which single-transform invariants composition invalidates.
    gate.record("purity_composite_relaxed", True,
                "relaxed under composition: identifier purity_line_count, structural "
                "purity_no_rename, and the S3/S4/S5 mutual-exclusion clauses")

    lang, code, entry = variant.language, variant.code, variant.entry_point
    for part in parts:
        pspec = ladder.get(part, {})
        fam = pspec.get("family", "none")
        params = pspec.get("params", {}) or {}
        tag = f"purity_composite_{part}"

        if fam == _IDENTIFIER_FAMILY:
            renamed = dict(variant.rename_map)
            ok &= gate.record(f"{tag}_rename_map", bool(renamed),
                              f"{variant.condition}: {part} stage left rename_map empty")
            if params.get("rename_entry", False):
                ok &= gate.record(f"{tag}_entry_renamed", entry != parent.entry_point,
                                  f"{variant.condition}: {part} did not rename the entry point")
            style = params.get("style")
            if style == "hex":
                bad = [v for v in renamed.values() if not _HEX_NAME_RE.match(v)]
                ok &= gate.record(f"{tag}_hex_names", not bad,
                                  f"{variant.condition}: {part} non-hex names {bad[:5]}")
            elif style == "seq":
                bad = [v for v in renamed.values() if not _SEQ_NAME_RE.match(v)]
                ok &= gate.record(f"{tag}_seq_names", not bad,
                                  f"{variant.condition}: {part} non-sequential names {bad[:5]}")

        elif fam == _STRUCTURAL_FAMILY:
            # Lines added is weak on its own — it is the reason S3/S4 needed positive
            # invariants — but under composition it still catches a stage that no-op'd.
            ok &= gate.record(f"{tag}_code_added",
                              code.count("\n") > parent.code.count("\n"),
                              f"{variant.condition}: {part} added no lines")
            if part == "S1":
                ok &= gate.record(f"{tag}_dispatch_loop",
                                  _has_dispatch_loop(lang, code, entry),
                                  f"{variant.condition}: {part} left no dispatch loop")
            elif part == "S3":
                ok &= gate.record(f"{tag}_dead_helper",
                                  _added_uncalled_def(lang, parent.code, code),
                                  f"{variant.condition}: {part} added no uncalled def")
            elif part == "S4":
                ok &= gate.record(f"{tag}_opaque_guard",
                                  _added_computed_guard(lang, parent.code, code, entry),
                                  f"{variant.condition}: {part} added no computed guard")
            elif part == "S5":
                ok &= gate.record(f"{tag}_literal_guard",
                                  _added_literal_dead_guard(lang, parent.code, code, entry),
                                  f"{variant.condition}: {part} added no `if 0:` guard")
    return ok


# --------------------------------------------------------------------------- #
# Mechanism detectors for the split structural conditions (S3/S4/S5/S6).
#
# These parse the variant rather than reading `transform_meta`: purity must verify what
# the transform DID, not what it says it did, or a transform bug is invisible to the gate.

#: Per-language tree-sitter node types for the constructs the detectors below key on.
#: Using tree-sitter rather than Python's `ast` is not a stylistic choice: `ast.parse` on
#: a JavaScript variant raises SyntaxError, so an `ast`-based detector silently returns
#: "mechanism absent" for EVERY JS variant and the whole language fails purity.
_TS_NODES = {
    "python": {
        "func": ("function_definition",),
        "if": ("if_statement",),
        "computed": ("binary_operator", "comparison_operator", "boolean_operator"),
        "loop": ("for_statement", "while_statement"),
        "falsey": {"0", "False", "None"},
    },
    "javascript": {
        "func": ("function_declaration",),
        "if": ("if_statement",),
        "computed": ("binary_expression", "logical_expression"),
        "loop": ("for_statement", "for_in_statement", "while_statement", "do_statement"),
        "falsey": {"0", "false", "null"},
    },
}


def _ts_root(language: str, code: str):
    try:
        return _obf_parse(language, code)
    except Exception:
        return None


def _top_level_funcs(language: str, code: str) -> dict[str, Any]:
    """Name -> node for functions declared at the top level of the module."""
    root = _ts_root(language, code)
    spec = _TS_NODES.get(language)
    if root is None or spec is None:
        return {}
    out = {}
    for child in root.children:
        node = child
        # JS wraps some declarations; walk one level for `export`/`statement` wrappers.
        if node.type not in spec["func"] and node.child_count == 1:
            node = node.children[0]
        if node.type in spec["func"]:
            name = node.child_by_field_name("name")
            if name is not None:
                out[_obf_node_text(code, name)] = node
    return out


def _module_def_count(language: str, code: str) -> int:
    return len(_top_level_funcs(language, code))


def _added_uncalled_def(language: str, parent_code: str, code: str) -> bool:
    """A top-level function that is new AND never referenced — i.e. genuinely dead.

    Everything is derived from ONE parse of `code`. Node identity in tree-sitter is
    per-tree, so comparing nodes taken from two separate parses of the same source never
    matches — which silently left each declaration's own name in the "used" set and made
    every dead helper look referenced.
    """
    parent_funcs = set(_top_level_funcs(language, parent_code))
    root = _ts_root(language, code)
    spec = _TS_NODES.get(language)
    if root is None or spec is None:
        return False

    funcs: dict[str, Any] = {}
    for child in root.children:
        node = child
        if node.type not in spec["func"] and node.child_count == 1:
            node = node.children[0]
        if node.type in spec["func"]:
            name = node.child_by_field_name("name")
            if name is not None:
                funcs[_obf_node_text(code, name)] = name

    added = set(funcs) - parent_funcs
    if not added:
        return False
    # Byte offsets, not node objects: unambiguous within this one tree.
    declared_at = {n.start_byte for n in funcs.values()}
    used = {
        _obf_node_text(code, n)
        for n in _obf_iter_nodes(root)
        if n.type == "identifier" and n.start_byte not in declared_at
    }
    return bool(added - used)


def _entry_fn_node(language: str, code: str, entry_point: str):
    """The entry function's node, across every form the corpus actually uses.

    A plain `function_declaration` lookup is not enough for JavaScript: the corpus also
    contains `const f = (x) => {...}` and `const f = function (x) {...}`, which
    `obf/js/transforms.mjs::findEntryFunctionPath` handles and this must too. Without the
    extra forms `_added_ifs` found no entry function, returned no guards, and 20 of 30
    JavaScript S4 variants were rejected for "no opaque guard" that was in fact present.
    """
    direct = _top_level_funcs(language, code).get(entry_point)
    if direct is not None or language != "javascript":
        return direct

    root = _ts_root(language, code)
    if root is None:
        return None
    for node in _obf_iter_nodes(root):
        if node.type != "variable_declarator":
            continue
        name = node.child_by_field_name("name")
        value = node.child_by_field_name("value")
        if name is None or value is None:
            continue
        if _obf_node_text(code, name) != entry_point:
            continue
        if value.type in ("arrow_function", "function_expression", "function"):
            return value
    return None


def _added_ifs(language: str, parent_code: str, code: str, entry_point: str) -> list[Any]:
    """`if` nodes inside the entry function that the parent did not have."""
    spec = _TS_NODES.get(language)
    fn = _entry_fn_node(language, code, entry_point)
    if fn is None or spec is None:
        return []
    pfn = _entry_fn_node(language, parent_code, entry_point)
    n_parent = (
        len([n for n in _obf_iter_nodes(pfn) if n.type in spec["if"]]) if pfn is not None else 0
    )
    ifs = [n for n in _obf_iter_nodes(fn) if n.type in spec["if"]]
    return ifs if len(ifs) > n_parent else []


def _guard_test(node, language: str):
    """The condition node of an `if`, across both grammars."""
    for field in ("condition", "test"):
        t = node.child_by_field_name(field)
        if t is not None:
            return t
    return None


def _added_computed_guard(language: str, parent_code: str, code: str, entry_point: str) -> bool:
    """An added guard whose test is COMPUTED — the S4 mechanism.

    Computed, not literal: the reader must evaluate arithmetic to see the branch is never
    taken. A literal `if 0:` is S5's mechanism and must not satisfy this.
    """
    spec = _TS_NODES.get(language, {})
    for n in _added_ifs(language, parent_code, code, entry_point):
        t = _guard_test(n, language)
        if t is None:
            continue
        # JS wraps the condition in parentheses.
        while t.type == "parenthesized_expression" and t.named_child_count == 1:
            t = t.named_children[0]
        if t.type in spec.get("computed", ()):
            return True
    return False


def _added_literal_dead_guard(language: str, parent_code: str, code: str, entry_point: str) -> bool:
    """An added guard whose test is a falsey LITERAL — the S5 mechanism (`if 0:`)."""
    spec = _TS_NODES.get(language, {})
    for n in _added_ifs(language, parent_code, code, entry_point):
        t = _guard_test(n, language)
        if t is None:
            continue
        while t.type == "parenthesized_expression" and t.named_child_count == 1:
            t = t.named_children[0]
        if _obf_node_text(code, t).strip() in spec.get("falsey", set()):
            return True
    return False


def _entry_loop_count(language: str, code: str, entry_point: str) -> int:
    spec = _TS_NODES.get(language)
    fn = _entry_fn_node(language, code, entry_point)
    if fn is None or spec is None:
        return 0
    return len([n for n in _obf_iter_nodes(fn) if n.type in spec["loop"]])


def _has_annotations(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                return True
            args = node.args
            every = (
                list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
                + [a for a in (args.vararg, args.kwarg) if a is not None]
            )
            if any(a.annotation is not None for a in every):
                return True
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            return True
    return False


def _has_dispatch_loop(language: str, code: str, entry_point: str) -> bool:
    """The entry function's own body must contain the dispatch loop.

    Checked at the top level of the body rather than anywhere in the file, so an S1
    module that silently returned its input (a program that already happened to
    contain a `while`) cannot pass.
    """
    if language == "python":
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry_point:
                return any(isinstance(s, ast.While) for s in node.body)
        return False
    body = _js_entry_body(code, entry_point)
    if body is None:
        return False
    return any(
        child.type in ("while_statement", "for_statement", "do_statement", "switch_statement")
        for child in body.named_children
    )


#: JS function forms that can carry an entry point. The ICSE stimuli are mostly
#: `const f = (n) => {...}`, so matching only `function_declaration` misses them —
#: which silently failed S1's purity check on 20 of 30 JavaScript test programs even
#: though the transform had produced a correct dispatch loop.
_JS_FUNC_TYPES = (
    "function_declaration", "generator_function_declaration",
    "function_expression", "generator_function", "arrow_function", "function",
)


def _js_entry_body(code: str, entry_point: str):
    """Statement-block body of `entry_point`, whichever way JavaScript binds it."""
    root = parse("javascript", code)
    for node in iter_nodes(root):
        if node.type not in _JS_FUNC_TYPES:
            continue

        name_node = node.child_by_field_name("name")
        name = node_text(code, name_node) if name_node is not None else None
        if name is None:
            # Anonymous: take the name from the binding it is attached to —
            # `const f = () => {}`, `f = function () {}`, `{ f() {} }`.
            parent = node.parent
            while parent is not None and parent.type in ("parenthesized_expression",):
                parent = parent.parent
            if parent is None:
                continue
            if parent.type in ("variable_declarator", "assignment_expression", "pair",
                               "method_definition", "public_field_definition"):
                target = parent.child_by_field_name("name") or parent.child_by_field_name("left")
                if target is not None:
                    name = node_text(code, target)
        if name != entry_point:
            continue

        body = node.child_by_field_name("body")
        if body is None:
            return None
        # A concise arrow body (`n => expr`) is an expression, not a block, so it
        # cannot contain a dispatch loop.
        return body if body.type == "statement_block" else None
    return None


def _batch(program_id: str, language: str, code: str, entry: str, args: Sequence[str]) -> BatchItem:
    return BatchItem(
        program_id=program_id, language=language, code=code, entry_point=entry, args_reprs=list(args)
    )


def gate(
    parent_program: BaseProgram,
    variant: Variant,
    conditions_cfg: dict[str, Any] | None = None,
    *,
    exec_workers: int = 2,
) -> Verdict:
    """Full acceptance check for one variant. See the module docstring for the order."""
    cfg = conditions_cfg or load_conditions()
    # Composites live under their own top-level key. Looking only in `conditions` would
    # return {} for them: `_purity` would find family "none" and pass vacuously, and
    # `spec["trainable"]` would be falsy so the H1 CONTENT SCAN below would be skipped
    # for exactly the new arm. Both failures are silent.
    spec = ((cfg.get("conditions") or {}).get(variant.condition)
            or (cfg.get("composite_conditions") or {}).get(variant.condition, {}))
    gate_cfg = cfg.get("gate") or {}
    g = _Gate()

    # -- 1. parses --------------------------------------------------------- #
    ok, detail = _parses(variant.language, variant.code)
    if not g.record("parses", ok, detail):
        return g.verdict()

    # -- 2. non-identity --------------------------------------------------- #
    if variant.condition != "L0":
        if not g.record(
            "non_identity",
            variant.code != parent_program.code,
            f"{variant.condition}: output is byte-identical to the L0 parent",
        ):
            return g.verdict()
    else:
        g.record("non_identity", True)

    # -- 3. condition purity + H1 markers ---------------------------------- #
    if not _purity(g, parent_program, variant, spec, cfg):
        return g.verdict()
    if spec.get("trainable", False):
        hits = _h1_markers(cfg.get("h1_marker_patterns") or [], variant.code)
        pre = _h1_markers(cfg.get("h1_marker_patterns") or [], parent_program.code)
        if not g.record(
            "h1_markers_absent",
            not hits,
            f"{variant.condition}: H1 marker pattern(s) {hits} present"
            + (f" (pre-existing in the L0 parent: {pre})" if pre else " (introduced by the transform)"),
        ):
            return g.verdict()
    else:
        g.record("h1_markers_absent", True)

    # -- 6a. size cap (cheap, do it before spawning subprocesses) ---------- #
    # The cap exists to catch pathological blowup (an obfuscator exploding output
    # 50x, quadratic codegen), NOT to bound normal transform overhead. A pure ratio
    # is the wrong shape for that: structural transforms add a roughly FIXED amount
    # of code (a dispatch scaffold, opaque-predicate blocks, dead helpers), so
    # overhead/parent_size diverges as the parent shrinks. Enforcing a ratio alone
    # rejected every short program at S1/S2 while passing every long one — which
    # would have silently confounded "structural condition" with "longer program"
    # in the RQ1 family contrast. The allowance is therefore the LARGER of the
    # ratio and a fixed per-condition character floor.
    cap = float(spec.get("size_cap", 99.0))
    floor_chars = int(spec.get("size_cap_floor_chars", 0))
    parent_chars = max(1, len(parent_program.code))
    allowed = max(cap * parent_chars, parent_chars + floor_chars)
    ratio = len(variant.code) / parent_chars
    g.metrics["size_ratio"] = round(ratio, 4)
    g.metrics["size_allowed_chars"] = int(allowed)
    g.metrics["size_chars"] = len(variant.code)
    if not g.record(
        "size_cap",
        len(variant.code) <= allowed,
        f"{variant.condition}: {len(variant.code)} chars > allowed {int(allowed)} "
        f"(ratio {ratio:.2f} vs cap {cap}, floor +{floor_chars} on {parent_chars} parent chars)",
    ):
        return g.verdict()

    # -- 4. exec parity ---------------------------------------------------- #
    cases = list(parent_program.cases) + list(parent_program.gate_inputs)
    if not cases:
        g.record("exec_parity", False, "parent program has no cases or gate_inputs")
        return g.verdict()
    args = [c.args_repr for c in cases]
    timeout_s = float(gate_cfg.get("exec_timeout_s", 2.0))
    mem_mb = int(gate_cfg.get("mem_mb", 512))

    parent_res, variant_res = run_batch(
        [
            _batch(
                parent_program.program_id, parent_program.language, parent_program.code,
                parent_program.entry_point, args,
            ),
            _batch(
                variant.program_id, variant.language, variant.code, variant.entry_point, args
            ),
        ],
        timeout_s=timeout_s,
        mem_mb=mem_mb,
        workers=max(1, exec_workers),
    )

    if not g.record(
        "parent_runs",
        parent_res.child_status == "ok",
        f"parent child_status={parent_res.child_status}: {parent_res.stderr[:200]}",
    ):
        return g.verdict()

    # The parent must still reproduce the outputs recorded in its own InputCases,
    # otherwise the gate is comparing the variant against an unverified reference.
    ref_bad: list[str] = []
    for i, (case, res) in enumerate(zip(cases, parent_res.cases)):
        if not case.output_canon:
            continue
        if res.status != "ok" or res.output != case.output_canon:
            ref_bad.append(f"case {i}: recorded {case.output_canon!r} vs {res.status}/{res.output!r}")
    if not g.record(
        "parent_reference", not ref_bad, f"parent drifted from its recorded outputs: {ref_bad[:3]}"
    ):
        return g.verdict()

    mismatches: list[str] = []
    for i, (p, v) in enumerate(zip(parent_res.cases, variant_res.cases)):
        if not p.matches(v):
            mismatches.append(
                f"case {i} ({cases[i].args_repr[:60]}): parent {p.status}/{p.output!r}"
                f"/{p.exc_type} vs variant {v.status}/{v.output!r}/{v.exc_type}"
            )
    g.metrics["n_cases"] = len(cases)
    g.metrics["n_mismatch"] = len(mismatches)
    if not g.record(
        "exec_parity",
        not mismatches and variant_res.child_status == "ok",
        f"{len(mismatches)} case mismatch(es) "
        f"[variant child_status={variant_res.child_status}]: " + "; ".join(mismatches[:3]),
    ):
        return g.verdict()

    # -- 5. runtime ratio -------------------------------------------------- #
    ratio_max = float(gate_cfg.get("runtime_ratio_max", 5.0))
    # 1 ms floor: sub-millisecond parents make the ratio pure measurement noise, and a
    # program that fast cannot be made slow enough to matter by any of our transforms.
    base_ms = max(parent_res.total_ms, 1.0)
    rt_ratio = variant_res.total_ms / base_ms
    g.metrics["runtime_ratio"] = round(rt_ratio, 3)
    g.metrics["parent_ms"] = round(parent_res.total_ms, 3)
    g.metrics["variant_ms"] = round(variant_res.total_ms, 3)
    g.record(
        "runtime_ratio",
        rt_ratio <= ratio_max,
        f"runtime ratio {rt_ratio:.2f} > max {ratio_max} "
        f"({parent_res.total_ms:.1f}ms -> {variant_res.total_ms:.1f}ms)",
    )
    return g.verdict()


def gate_many(
    pairs: Iterable[tuple[BaseProgram, Variant]],
    conditions_cfg: dict[str, Any] | None = None,
    *,
    exec_workers: int = 8,
) -> list[Verdict]:
    """Convenience wrapper; kept sequential because run_batch already parallelizes."""
    cfg = conditions_cfg or load_conditions()
    return [gate(p, v, cfg, exec_workers=exec_workers) for p, v in pairs]


__all__ = ["Verdict", "gate", "gate_many"]
