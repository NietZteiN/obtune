"""Input-case generation: seeds, a type-directed fuzzer, and the two output filters.

Pipeline per program:

  1. `harvest_seeds`  — take whatever concrete inputs the upstream dataset already has
     (APPS `input_output.inputs`, HumanEval/MBPP `assert` statements, CruxEval's given
     input, the JS corpora's `io_pairs`). Seeds are the ground truth for *shape*: the
     runtime types of a real input tell us more than any signature or annotation.
  2. `infer_arg_types` — read the argument types off the seed values, generalizing to
     a small type lattice (int / float / bool / str / list[T] / dict[K,V] / tuple / any).
  3. `Fuzzer.generate`  — deterministic type-directed synthesis of fresh arguments.
  4. `run_cases`      — execute; keep only cases whose canonical output exists.
  5. `non_trivial`    — the case set must discriminate: >= 2 distinct outputs, no output
     that is just the input echoed back, 1 <= len(output) <= 200.
  6. `determinism_ok` — re-execute the whole case set 3x in separate processes with
     *different* PYTHONHASHSEED values; every canonical output must be byte-identical.

Why a hand-rolled fuzzer instead of Hypothesis
----------------------------------------------
Hypothesis is a property-testing engine: its generation is adaptive (shrinking,
targeting, a database of past failures) and its reproducibility guarantee is tied to a
specific Hypothesis version. This corpus needs the opposite properties — a pure
function from (seed, type) to a value list, stable across library upgrades, and
inspectable so a reviewer can see exactly which value distribution produced a stimulus.
`random.Random(seed)` gives that in ~80 lines with no dependency and no version
coupling. Hypothesis was tried first and rejected for the version-coupling reason: a
corpus regenerated after a `pip install -U` must be byte-identical or the whole
train/test split loses its meaning.
"""
from __future__ import annotations

import ast
import json
import random
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from obtune.exec.pool import BatchItem, CaseResult, run_batch

# The three hash seeds used by the dynamic determinism check. 0 is the pinned value
# used everywhere else; the other two are arbitrary but fixed so the filter itself is
# reproducible. A program whose output depends on dict/set iteration order will differ
# across at least one of these with high probability.
DETERMINISM_HASH_SEEDS = (0, 1, 4919)


@dataclass
class ArgType:
    """A shallow structural type inferred from seed values."""

    kind: str  # int|float|bool|str|list|dict|tuple|none|any
    elem: "ArgType | None" = None
    key: "ArgType | None" = None
    lengths: tuple[int, ...] = ()  # observed container lengths, for scale-matching
    ints: tuple[int, ...] = ()     # observed ints, for magnitude-matching

    def describe(self) -> str:
        if self.kind == "list":
            return f"list[{self.elem.describe() if self.elem else 'any'}]"
        if self.kind == "dict":
            k = self.key.describe() if self.key else "any"
            v = self.elem.describe() if self.elem else "any"
            return f"dict[{k},{v}]"
        return self.kind


@dataclass
class GeneratedCase:
    args_repr: str
    output_canon: str
    case_role: str = "generated"


# --------------------------------------------------------------------- seed harvest


def harvest_seeds(raw_cases: Iterable[Any], language: str) -> list[str]:
    """Turn a source's raw case records into `args_repr` strings.

    Accepts, per element: an already-formatted args_repr string, a list of positional
    argument *values*, or a dict with an ``args`` / ``args_repr`` key.
    """
    out: list[str] = []
    for c in raw_cases:
        if isinstance(c, str):
            out.append(c.strip())
        elif isinstance(c, dict) and "args_repr" in c:
            out.append(str(c["args_repr"]).strip())
        elif isinstance(c, dict) and "args" in c:
            out.append(format_args(list(c["args"]), language))
        elif isinstance(c, (list, tuple)):
            out.append(format_args(list(c), language))
        else:
            raise TypeError(f"unsupported seed case record: {type(c).__name__}")
    return _dedup(out)


def format_args(values: Sequence[Any], language: str) -> str:
    """Render positional argument values as the literal tuple source `pool` expects.

    A trailing comma is always emitted so a single argument still parses as a tuple on
    the Python side (`ast.literal_eval("(6)")` is `6`, not `(6,)`); JavaScript accepts
    the trailing comma in the array literal that runner_js.mjs builds.
    """
    parts = [py_literal(v) if language == "python" else js_literal(v) for v in values]
    return "(" + ", ".join(parts) + ("," if parts else "") + ")"


def py_literal(v: Any) -> str:
    return repr(v)


def js_literal(v: Any) -> str:
    """JS source text for a JSON-shaped Python value.

    json.dumps is the right tool: it already emits `true/false/null`, escapes strings to
    a form both languages read identically, and refuses NaN/Infinity when asked — which
    is exactly canon's rule.
    """
    return json.dumps(v, ensure_ascii=False, allow_nan=False)


def parse_args_repr(args_repr: str) -> list[Any]:
    """Inverse of `format_args`.

    Python-literal text is handled by `ast.literal_eval`; the JavaScript form falls
    through to JSON, whose only divergences from Python literals (`true/false/null`)
    are exactly what json handles. Raises for anything neither can read — a JS regex
    or template literal seed, which the caller drops from type inference but still
    executes verbatim.
    """
    text = args_repr.strip()
    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        inner = text[1:-1] if text.startswith("(") and text.endswith(")") else text
        return list(json.loads("[" + inner.rstrip().rstrip(",") + "]"))
    return list(value) if isinstance(value, tuple) else [value]


def _dedup(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ------------------------------------------------------------------ type inference


def infer_arg_types(seed_args: Sequence[Sequence[Any]]) -> list[ArgType]:
    """Infer one ArgType per positional slot from the runtime types of seed values.

    Runtime types beat signature annotations: annotations are absent in most corpora,
    lie in some (`List[int]` on a function that also accepts floats), and are stripped
    outright by the L2 condition — so a corpus built on them would generate inputs the
    L2 variant could not accept.
    """
    if not seed_args:
        return []
    width = max(len(a) for a in seed_args)
    types: list[ArgType] = []
    for i in range(width):
        column = [a[i] for a in seed_args if len(a) > i]
        types.append(_infer(column))
    return types


def _infer(values: Sequence[Any]) -> ArgType:
    kinds = {_kind(v) for v in values}
    kinds.discard("none")
    if len(kinds) != 1:
        # Mixed int/float collapses to float; anything else is genuinely polymorphic.
        return ArgType("float") if kinds == {"int", "float"} else ArgType("any")
    kind = kinds.pop()
    if kind == "list":
        elems = [e for v in values for e in v]
        return ArgType("list", elem=_infer(elems) if elems else ArgType("int"),
                       lengths=tuple(len(v) for v in values))
    if kind == "tuple":
        elems = [e for v in values for e in v]
        return ArgType("tuple", elem=_infer(elems) if elems else ArgType("int"),
                       lengths=tuple(len(v) for v in values))
    if kind == "dict":
        keys = [k for v in values for k in v]
        vals = [x for v in values for x in v.values()]
        return ArgType("dict", key=_infer(keys) if keys else ArgType("str"),
                       elem=_infer(vals) if vals else ArgType("int"),
                       lengths=tuple(len(v) for v in values))
    if kind == "str":
        return ArgType("str", lengths=tuple(len(v) for v in values))
    if kind == "int":
        return ArgType("int", ints=tuple(v for v in values if isinstance(v, int)))
    return ArgType(kind)


def _kind(v: Any) -> str:
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, tuple):
        return "tuple"
    if isinstance(v, dict):
        return "dict"
    return "any"


# ------------------------------------------------------------------------- fuzzing


ALPHABETS = {
    "lower": "abcdefghijklmnopqrstuvwxyz",
    "mixed": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "words": "abcdefghijklmnopqrstuvwxyz ",
    "alnum": "abcdefghijklmnopqrstuvwxyz0123456789",
}


class Fuzzer:
    """Deterministic type-directed value synthesis.

    Pure function of (seed, types, n): the same arguments always produce the same list
    in the same order, in this process or any other. Every draw goes through
    `self.rng`; nothing consults the global `random` module, the clock, or the
    interpreter's hash seed.
    """

    def __init__(self, seed: int, max_len: int = 8, max_depth: int = 2) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.max_len = max_len
        self.max_depth = max_depth

    def reset(self) -> None:
        self.rng = random.Random(self.seed)

    def generate(self, types: Sequence[ArgType], n: int) -> list[list[Any]]:
        """n argument tuples for the given positional types."""
        self.reset()
        return [[self.value(t) for t in types] for _ in range(n)]

    def value(self, t: ArgType, depth: int = 0) -> Any:
        kind = t.kind
        if kind == "any":
            kind = self.rng.choice(["int", "str", "list", "bool"])
        if kind == "bool":
            return self.rng.random() < 0.5
        if kind == "int":
            return self._int(t)
        if kind == "float":
            # Two decimal places: canon prints shortest round-trip, and a value with a
            # short decimal expansion serializes identically in both languages without
            # relying on float-printing agreement at the 17th digit.
            return round(self.rng.uniform(-100.0, 100.0), 2)
        if kind == "str":
            return self._str(t)
        if kind in ("list", "tuple"):
            length = self._length(t)
            elem = t.elem or ArgType("int")
            vals = [self.value(elem, depth + 1) for _ in range(length)]
            return tuple(vals) if kind == "tuple" else vals
        if kind == "dict":
            length = self._length(t)
            kt = t.key or ArgType("str")
            vt = t.elem or ArgType("int")
            out: dict[Any, Any] = {}
            # Bounded retries, then accept a short dict: with a small key space the
            # loop would otherwise spin trying to reach `length` distinct keys.
            for _ in range(length * 4):
                if len(out) >= length:
                    break
                k = self.value(kt, depth + 1)
                if isinstance(k, (list, dict, tuple)):
                    k = str(k)
                out[k] = self.value(vt, depth + 1)
            return out
        if kind == "none":
            return None
        return self._int(t)

    def _int(self, t: ArgType) -> int:
        if t.ints:
            lo, hi = min(t.ints), max(t.ints)
            span = max(abs(lo), abs(hi), 10)
            # Stay inside the observed magnitude: a function seeded with n=6 is very
            # likely to be exponential in n, and a fuzzed n=10**6 would just time out.
            return self.rng.randint(min(lo, 0) - span, hi + span)
        return self.rng.randint(-50, 50)

    def _str(self, t: ArgType) -> str:
        alpha = ALPHABETS[self.rng.choice(["lower", "mixed", "words", "alnum"])]
        length = self._length(t, default_hi=12)
        return "".join(self.rng.choice(alpha) for _ in range(length))

    def _length(self, t: ArgType, default_hi: int | None = None) -> int:
        hi = default_hi if default_hi is not None else self.max_len
        if t.lengths:
            hi = min(max(max(t.lengths), 1), self.max_len if default_hi is None else default_hi)
        return self.rng.randint(0, max(hi, 1))


# --------------------------------------------------------------------- execution


def run_cases(
    program_id: str, language: str, code: str, entry_point: str,
    args_reprs: Sequence[str], timeout_s: float = 2.0, hash_seed: int = 0,
) -> list[CaseResult]:
    if not args_reprs:
        return []
    item = BatchItem(program_id, language, code, entry_point, list(args_reprs))
    return run_batch([item], timeout_s=timeout_s, hash_seed=hash_seed, workers=1)[0].cases


def non_trivial(
    args_reprs: Sequence[str], outputs: Sequence[str],
    min_distinct: int = 2, max_output_chars: int = 200, max_args_chars: int = 2000,
) -> tuple[bool, list[str]]:
    """A case set must actually discriminate between models that understand the program
    and models that pattern-match.

    Three failure modes are rejected:
      * a constant function (every case returns the same thing) — answerable from one
        example without reading the code;
      * identity-ish cases where the output is literally the argument text — answerable
        by copying the prompt;
      * degenerate output sizes (empty, or a 200+ character blob that the grader would
        be comparing on formatting rather than semantics).
    """
    reasons: list[str] = []
    if len(set(outputs)) < min_distinct:
        reasons.append(f"constant_output:{len(set(outputs))}<{min_distinct}")
    for a, o in zip(args_reprs, outputs):
        if len(a) > max_args_chars:
            reasons.append(f"args_too_long:{len(a)}>{max_args_chars}")
            continue
        if not 1 <= len(o) <= max_output_chars:
            reasons.append(f"output_len_out_of_range:{len(o)}")
            break
    echoes = sum(1 for a, o in zip(args_reprs, outputs) if _is_echo(a, o))
    if echoes == len(outputs) and outputs:
        reasons.append("output_echoes_input")
    return (not reasons), reasons


def _is_echo(args_repr: str, output: str) -> bool:
    """True when the canonical output is just the argument, re-serialized."""
    try:
        values = parse_args_repr(args_repr)
    except Exception:  # noqa: BLE001 — an unparseable repr is not an echo
        return False
    if len(values) != 1:
        return False
    from obtune.exec.canon import canon_or_none

    return canon_or_none(values[0]) == output


def determinism_ok(
    program_id: str, language: str, code: str, entry_point: str,
    args_reprs: Sequence[str], repeats: int = 3, timeout_s: float = 2.0,
) -> tuple[bool, list[str] | None]:
    """Run the case set `repeats` times in fresh processes with different
    PYTHONHASHSEED values and require byte-identical canonical outputs.

    Different hash seeds — not just repeated runs — is the point: the failure this
    catches is `list({...})` / `for k in some_dict` ordering, which is perfectly stable
    within one process and changes between processes only when the hash seed changes.
    Returns (ok, outputs_from_the_first_run).
    """
    seeds = DETERMINISM_HASH_SEEDS[:repeats]
    runs: list[list[CaseResult]] = [
        run_cases(program_id, language, code, entry_point, args_reprs,
                  timeout_s=timeout_s, hash_seed=s)
        for s in seeds
    ]
    if any(not all(c.ok for c in r) for r in runs):
        return False, None
    first = [c.output or "" for c in runs[0]]
    for r in runs[1:]:
        if [c.output or "" for c in r] != first:
            return False, None
    return True, first


# --------------------------------------------------------------------- orchestration


@dataclass
class CaseBundle:
    cases: list[GeneratedCase]       # the training/eval cases (seeds first, then fuzz)
    gate_inputs: list[GeneratedCase]  # extra fuzz cases for the semantic gate
    arg_types: list[str]
    reasons: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.reasons


def build_cases(
    program_id: str,
    language: str,
    code: str,
    entry_point: str,
    seed_args_reprs: Sequence[str],
    *,
    n_cases: int = 3,
    n_gate_inputs: int = 20,
    min_gate_inputs: int = 5,
    seed: int = 17,
    fuzz_pool: int = 60,
    min_distinct_outputs: int = 2,
    max_output_chars: int = 200,
    max_args_chars: int = 2000,
    determinism_repeats: int = 3,
    timeout_s: float = 2.0,
    keep_roles: Sequence[str] | None = None,
) -> CaseBundle:
    """Full per-program case pipeline. Returns a bundle with `reasons` set on rejection.

    `keep_roles` lets a caller pin the role of the first N seed cases (the test-set
    ingest pins its one human-provided case as `case_role="human"`).

    `min_gate_inputs` is the honesty knob: configs/conditions.yaml asks for 20 gate
    inputs, but a program with a tiny input domain (a predicate over a 3-element enum)
    cannot supply 20 distinct executable ones. Rather than silently shipping a 2-input
    gate, such a program is dropped below `min_gate_inputs` and the actual count is
    recorded on the ones that are kept.
    """
    seeds = _dedup([s.strip() for s in seed_args_reprs if s and s.strip()])
    seed_values: list[list[Any]] = []
    for s in seeds:
        try:
            seed_values.append(parse_args_repr(s))
        except Exception:  # noqa: BLE001 — an unparseable seed is dropped, not fatal
            continue
    types = infer_arg_types(seed_values)
    type_desc = [t.describe() for t in types]

    if not types:
        return CaseBundle([], [], type_desc, ["no_usable_seed_inputs"])

    fuzzer = Fuzzer(seed=seed + _stable_offset(program_id))
    candidates = list(seeds)
    for values in fuzzer.generate(types, fuzz_pool):
        try:
            candidates.append(format_args(values, language))
        except (TypeError, ValueError):
            continue
    candidates = _dedup(candidates)

    results = run_cases(program_id, language, code, entry_point, candidates, timeout_s=timeout_s)
    # `candidates` is seeds-then-fuzz, and run_batch preserves order, so `usable` is
    # already ordered "real inputs first".
    usable = [(a, r.output or "") for a, r in zip(candidates, results)
              if r.ok and r.output and 1 <= len(r.output) <= max_output_chars]
    need = n_cases + min_gate_inputs
    if len(usable) < need:
        return CaseBundle([], [], type_desc, [f"too_few_executable_cases:{len(usable)}<{need}"])

    # Prefer cases with distinct outputs so the kept set discriminates; fall back to
    # duplicates only if the program cannot produce enough distinct answers.
    chosen: list[tuple[str, str]] = []
    seen_outputs: set[str] = set()
    for a, o in usable:
        if len(chosen) >= n_cases:
            break
        if o in seen_outputs:
            continue
        chosen.append((a, o))
        seen_outputs.add(o)
    for pair in usable:
        if len(chosen) >= n_cases:
            break
        if pair not in chosen:
            chosen.append(pair)

    ok, reasons = non_trivial([a for a, _ in chosen], [o for _, o in chosen],
                              min_distinct=min_distinct_outputs,
                              max_output_chars=max_output_chars)
    if not ok:
        return CaseBundle([], [], type_desc, reasons)

    gate_pool = [p for p in usable if p not in chosen][:n_gate_inputs]
    all_reprs = [a for a, _ in chosen] + [a for a, _ in gate_pool]
    det_ok, _ = determinism_ok(program_id, language, code, entry_point, all_reprs,
                               repeats=determinism_repeats, timeout_s=timeout_s)
    if not det_ok:
        return CaseBundle([], [], type_desc, ["nondeterministic_across_hash_seeds"])

    roles = list(keep_roles or [])
    cases = [
        GeneratedCase(a, o, roles[i] if i < len(roles) else ("seed" if a in seeds else "generated"))
        for i, (a, o) in enumerate(chosen)
    ]
    gate = [GeneratedCase(a, o, "gate") for a, o in gate_pool]
    return CaseBundle(cases, gate, type_desc)


def _stable_offset(program_id: str) -> int:
    """Per-program RNG offset that does not depend on PYTHONHASHSEED.

    `hash(program_id)` would be seeded by the interpreter and would silently change the
    generated inputs between processes — exactly the failure this module exists to
    prevent. A fixed FNV-1a walk is stable forever.
    """
    h = 0x811C9DC5
    for b in program_id.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h % 1_000_003
