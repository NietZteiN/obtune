"""Semantics-ALTERING mutations — the source of CFT's negative examples (L_neg).

The paper says only that negatives use "functionally different code" (§5.0.2) and does
not say how that code is produced or how "functionally different" is established. Both
gaps matter here, because a negative pool built badly makes L_neg trivially learnable:

  * If negatives were *unrelated* programs, "do A and B look alike?" solves the task and
    nothing semantic is learned. So a negative here is a **single-operator mutation of
    the very program it is paired with** — a classic mutation-testing operator (Jia &
    Harman's AOR/ROR/LCR/ICR families). The two programs differ in one token.
  * If negatives were merely *assumed* different, some would be equivalent mutants (the
    standard failure of mutation testing) and L_neg would be training the model to call
    equivalent programs inequivalent. So every mutant is **executed** against its parent
    on the parent's own case list and kept only if an output genuinely differs.

Rejected alternative: LLM-generated "subtly different" variants, as some contrastive
code work does. It needs a GPU, is unverifiable without exactly the execution check
below, and would make the negative pool a function of whichever model generated it.

Acceptance rule (`verify`)
--------------------------
A candidate is accepted iff, over the cases where the PARENT ran cleanly:
  1. it differs from the parent on at least one case (`CaseResult.matches` is False), and
  2. it still runs cleanly on at least `min_ok_fraction` of them.

(2) is what keeps negatives *hard*. Without it the pool fills with mutants that raise a
TypeError on every input — "different" in a way that needs no semantic reasoning to spot,
since a program that crashes everywhere is recognisable from its traceback alone.
`CaseResult.matches` compares raised exceptions by TYPE only, so a mutant that raises a
different exception type than the parent counts as a legitimate difference.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence

from obtune.exec.pool import BatchItem, CaseResult, run_batch
from obtune.obf.base import Bail, EditList, iter_nodes, node_text, parse

# --------------------------------------------------------------------------- #
# Mutation operators
#
# Keyed by the operator token's source text. Values are the replacements tried, in
# order. Both languages share one table: tree-sitter gives us the operator token of a
# binary/comparison/boolean expression as an unnamed leaf in both grammars, and the
# symbols that overlap (`+`, `<`, `==`) mean the same thing in both.

ARITH_SWAPS: dict[str, tuple[str, ...]] = {
    "+": ("-",),
    "-": ("+",),
    "*": ("+",),
    "/": ("*",),
    "//": ("*",),
    "%": ("*",),
    "**": ("*",),
}

REL_SWAPS: dict[str, tuple[str, ...]] = {
    "<": ("<=", ">"),
    "<=": ("<",),
    ">": (">=", "<"),
    ">=": (">",),
    "==": ("!=",),
    "!=": ("==",),
    "===": ("!==",),
    "!==": ("===",),
}

LOGIC_SWAPS: dict[str, tuple[str, ...]] = {
    "and": ("or",),
    "or": ("and",),
    "&&": ("||",),
    "||": ("&&",),
}

#: Node types whose direct children include the operator token we may rewrite.
#: Python: binary_operator / comparison_operator / boolean_operator / augmented_assignment.
#: JavaScript: binary_expression / augmented_assignment_expression.
OPERATOR_PARENTS = {
    "binary_operator",
    "comparison_operator",
    "boolean_operator",
    "binary_expression",
    "augmented_assignment",
    "augmented_assignment_expression",
}

#: Integer-literal node types (ICR — integer constant replacement).
INT_LITERAL_TYPES = {"integer", "number"}

OP_FAMILIES = ("AOR", "ROR", "LCR", "ICR")


@dataclass(frozen=True)
class Candidate:
    """One proposed single-token edit. `family` is the mutation-testing operator class."""

    family: str  # AOR | ROR | LCR | ICR
    start_byte: int
    end_byte: int
    original: str
    replacement: str

    @property
    def note(self) -> str:
        return f"{self.family}: {self.original!r} -> {self.replacement!r} @byte {self.start_byte}"


@dataclass
class Mutant:
    program_id: str
    language: str
    entry_point: str
    code: str
    parent_code: str
    candidate: Candidate
    #: filled in by `verify`
    n_cases_checked: int = 0
    n_cases_differing: int = 0
    n_cases_ok: int = 0
    verified: bool = False
    reject_reason: Optional[str] = None

    def as_meta(self) -> dict[str, Any]:
        return {
            "family": self.candidate.family,
            "op": f"{self.candidate.original}->{self.candidate.replacement}",
            "byte": self.candidate.start_byte,
            "n_cases_checked": self.n_cases_checked,
            "n_cases_differing": self.n_cases_differing,
            "n_cases_ok": self.n_cases_ok,
        }


# --------------------------------------------------------------------------- #
# Candidate enumeration

def _int_replacement(text: str) -> Optional[str]:
    """`n -> n+1`, except that `1 -> 0` and `0 -> 1`.

    Off-by-one on a small literal is the mutation most likely to survive execution as a
    *runnable* program, which is what makes it a hard negative; `+1` on a 0/1 flag would
    often just turn a boolean-ish constant into another truthy value, so those two are
    flipped across the truthiness boundary instead.
    """
    if not text.isdigit():  # skip hex/binary/float/underscored literals
        return None
    value = int(text)
    if value == 0:
        return "1"
    if value == 1:
        return "0"
    return str(value + 1)


def candidates(language: str, code: str) -> list[Candidate]:
    """Every single-token edit this module knows how to make to `code`.

    Operators are found through the parse tree rather than by regex, so a `+` inside a
    string literal or a comment is never touched.
    """
    try:
        root = parse(language, code)
    except Bail:
        return []
    out: list[Candidate] = []
    for node in iter_nodes(root):
        if node.type in INT_LITERAL_TYPES:
            text = node_text(code, node)
            repl = _int_replacement(text)
            if repl is not None:
                out.append(Candidate("ICR", node.start_byte, node.end_byte, text, repl))
            continue
        if node.type not in OPERATOR_PARENTS:
            continue
        for child in node.children:
            if child.is_named:  # operands, not the operator token
                continue
            text = node_text(code, child)
            for family, table in (("AOR", ARITH_SWAPS), ("ROR", REL_SWAPS), ("LCR", LOGIC_SWAPS)):
                if text in table:
                    for repl in table[text]:
                        out.append(
                            Candidate(family, child.start_byte, child.end_byte, text, repl)
                        )
                    break
    return out


def apply_candidate(code: str, cand: Candidate) -> str:
    edits = EditList(code)
    edits.add(cand.start_byte, cand.end_byte, cand.replacement)
    return edits.apply()


def propose(
    program_id: str,
    language: str,
    code: str,
    entry_point: str,
    n: int,
    seed: int,
    families: Sequence[str] = OP_FAMILIES,
) -> list[Mutant]:
    """Up to `n` candidate mutants, sampled deterministically from `seed`.

    Candidates are shuffled and then taken one per distinct byte offset, so a program's
    mutants land on different parts of the program instead of all rewriting the same
    hot expression in different ways.
    """
    allowed = set(families)
    cands = [c for c in candidates(language, code) if c.family in allowed]
    if not cands:
        return []
    rng = random.Random(f"{program_id}:{seed}")
    rng.shuffle(cands)
    picked: list[Candidate] = []
    used_offsets: set[int] = set()
    for c in cands:
        if c.start_byte in used_offsets:
            continue
        used_offsets.add(c.start_byte)
        picked.append(c)
        if len(picked) >= n:
            break
    out: list[Mutant] = []
    for c in picked:
        try:
            mutated = apply_candidate(code, c)
        except Exception:  # EditConflict etc. — a bad candidate is skipped, never fatal
            continue
        out.append(
            Mutant(
                program_id=program_id,
                language=language,
                entry_point=entry_point,
                code=mutated,
                parent_code=code,
                candidate=c,
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Execution-based verification

@dataclass
class VerifyStats:
    n_parents: int = 0
    n_proposed: int = 0
    n_verified: int = 0
    reject_reasons: dict[str, int] = field(default_factory=dict)
    by_family: dict[str, int] = field(default_factory=dict)

    def reject(self, reason: str) -> None:
        self.reject_reasons[reason] = self.reject_reasons.get(reason, 0) + 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "n_parents": self.n_parents,
            "n_proposed": self.n_proposed,
            "n_verified": self.n_verified,
            # `program_coverage` is the number to read: the share of programs that got a
            # usable negative. `verify_rate` is per-*proposal* and is deflated by design,
            # because verification stops as soon as a program has its quota — the
            # remaining proposals for that program are never adjudicated.
            "program_coverage": self.n_verified / self.n_parents if self.n_parents else 0.0,
            "verify_rate": self.n_verified / self.n_proposed if self.n_proposed else 0.0,
            "reject_reasons": dict(sorted(self.reject_reasons.items())),
            "verified_by_family": dict(sorted(self.by_family.items())),
        }


def _case_args(program: Mapping[str, Any], max_cases: int) -> list[str]:
    """Args to check against: the program's own cases first, then gate fuzz inputs.

    Cases come first because they are the inputs the corpus already knows are
    non-trivial and deterministic; the gate inputs broaden coverage so a mutation on a
    rarely-taken branch is still detected.
    """
    args = [c["args_repr"] for c in program.get("cases", [])]
    args += [c["args_repr"] for c in program.get("gate_inputs", [])]
    seen: set[str] = set()
    uniq = []
    for a in args:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    return uniq[:max_cases]


def verify(
    programs: Sequence[Mapping[str, Any]],
    n_per_program: int,
    seed: int,
    max_cases: int = 12,
    min_ok_fraction: float = 0.5,
    timeout_s: float = 2.0,
    workers: int = 32,
    families: Sequence[str] = OP_FAMILIES,
    keep_per_program: int = 1,
) -> tuple[list[Mutant], VerifyStats]:
    """Propose and execution-verify mutants for a batch of base programs.

    `programs` are `BaseProgram`-shaped mappings (data/train/base/<lang>.jsonl rows).
    Parent and mutants run in ONE batch so the executor's process pool is saturated
    once rather than per program.
    """
    stats = VerifyStats(n_parents=len(programs))
    items: list[BatchItem] = []
    index: list[tuple[int, Optional[int]]] = []  # (program idx, mutant idx or None=parent)
    proposals: list[list[Mutant]] = []
    case_args: list[list[str]] = []

    for pi, prog in enumerate(programs):
        args = _case_args(prog, max_cases)
        case_args.append(args)
        muts = (
            propose(
                program_id=prog["program_id"],
                language=prog["language"],
                code=prog["code"],
                entry_point=prog["entry_point"],
                n=n_per_program,
                seed=seed,
                families=families,
            )
            if args
            else []
        )
        if not args:
            stats.reject("no_cases")
        proposals.append(muts)
        stats.n_proposed += len(muts)
        if not muts:
            continue
        items.append(
            BatchItem(
                program_id=prog["program_id"],
                language=prog["language"],
                code=prog["code"],
                entry_point=prog["entry_point"],
                args_reprs=args,
            )
        )
        index.append((pi, None))
        for mi, m in enumerate(muts):
            items.append(
                BatchItem(
                    program_id=f"{prog['program_id']}::mut{mi}",
                    language=m.language,
                    code=m.code,
                    entry_point=m.entry_point,
                    args_reprs=args,
                )
            )
            index.append((pi, mi))

    if not items:
        return [], stats

    results = run_batch(items, timeout_s=timeout_s, workers=workers)
    parent_results: dict[int, list[CaseResult]] = {}
    mutant_results: dict[tuple[int, int], list[CaseResult]] = {}
    for (pi, mi), res in zip(index, results):
        if mi is None:
            parent_results[pi] = res.cases
        else:
            mutant_results[(pi, mi)] = res.cases

    kept: list[Mutant] = []
    for pi, muts in enumerate(proposals):
        parent = parent_results.get(pi)
        if not parent:
            continue
        ok_idx = [i for i, c in enumerate(parent) if c.ok]
        if not ok_idx:
            # The parent itself does not run cleanly on any case — nothing this program
            # produces can be trusted as a semantic reference.
            stats.reject("parent_never_ok")
            continue
        accepted_here = 0
        for mi, m in enumerate(muts):
            cases = mutant_results.get((pi, mi))
            if cases is None:
                m.reject_reason = "no_result"
                stats.reject("no_result")
                continue
            m.n_cases_checked = len(ok_idx)
            m.n_cases_ok = sum(1 for i in ok_idx if cases[i].ok)
            m.n_cases_differing = sum(1 for i in ok_idx if not parent[i].matches(cases[i]))
            if m.n_cases_differing == 0:
                m.reject_reason = "equivalent_mutant"
                stats.reject("equivalent_mutant")
                continue
            if m.n_cases_ok < min_ok_fraction * len(ok_idx):
                # Broken everywhere: a trivially-spottable negative, see the module docstring.
                m.reject_reason = "mutant_mostly_broken"
                stats.reject("mutant_mostly_broken")
                continue
            m.verified = True
            kept.append(m)
            stats.n_verified += 1
            stats.by_family[m.candidate.family] = stats.by_family.get(m.candidate.family, 0) + 1
            accepted_here += 1
            if accepted_here >= keep_per_program:
                break

    return kept, stats


def iter_programs(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Normalize base-program rows to the mapping shape `verify` expects."""
    return [
        {
            "program_id": r["program_id"],
            "language": r["language"],
            "code": r["code"],
            "entry_point": r["entry_point"],
            "cases": r.get("cases", []),
            "gate_inputs": r.get("gate_inputs", []),
        }
        for r in rows
    ]
