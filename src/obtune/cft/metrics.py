"""Metrics for the bidirectional evaluation: CodeBLEU, readability, execution.

Three families, with very different epistemic status — kept separate on purpose so a
claim can be traced to the evidence that supports it.

1. **CodeBLEU** (`codebleu_score`). The paper's primary syntactic metric (§3.3, citing
   Ren et al. 2020) and the basis of its S1–S4 comparisons and its reverse-success
   threshold. We call the *published* implementation (`codebleu==0.7.0`, vendored under
   `env/vendor/` so the pinned conda env in `env/lock-obtune.txt` is untouched) rather
   than reimplementing it, because a home-grown CodeBLEU would make every threshold in
   the paper incomparable to ours. It parses with the project's own tree-sitter
   grammars, which is why the vendored tree-sitter copy is deliberately absent.

2. **Readability** (`readability_proxy`). The paper scores with Scalabrino et al.'s
   readability model, which is a Java tool with no Python/JavaScript equivalent. This is
   an explicitly-labelled SUBSTITUTE, not that instrument: a weighted mean of four
   components, each reported alongside the total so that any movement in R can be
   attributed. It is calibrated only in the sense that it returns ~1 for idiomatic
   source and ~0 for hex-renamed minified source; absolute values are NOT comparable to
   the paper's R, and only the *within-our-run* contrasts (R(deobf) vs R(orig) vs
   R(obf)) are interpretable. Every table that reports it must carry that caveat.

3. **Execution** (`exec_equivalence`). obtune has a sandboxed executor and canonical
   outputs, which the paper's setup lacks; this reports whether recovered or generated
   code *actually computes the original's outputs*. It is the metric to believe when it
   disagrees with the syntactic ones, and it is why `reverse_success_exec` exists next
   to the paper's purely-syntactic `reverse_success_paper`.

Reverse-success criteria
------------------------
Paper §4.3.2/§4.3.3: "Effective deobfuscation requires reducing syntactic similarity of
the obfuscated code (S(C_deobf, C_obf) -> 0) while restoring readability to get close to
the original code (R(C_deobf) -> R(C_orig))", with "success requires at least
S(C_output, C_target) < 0.4". The thresholds are stated loosely, so both live in
`configs/cft/eval/bidir_v1.yaml` and are recorded in every result file rather than
buried here.
"""
from __future__ import annotations

import functools
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from obtune.config import PROJECT_ROOT
from obtune.exec.pool import BatchItem, run_batch
from obtune.obf.base import Bail, iter_nodes, node_text, parse, split_words, tree_ok

VENDOR_DIR = PROJECT_ROOT / "env" / "vendor"

#: Pinned so a result file can name the exact metric implementation that produced it.
CODEBLEU_VERSION = "codebleu==0.7.0 (vendored, env/vendor/)"


def _ensure_vendor_on_path() -> None:
    """Append (never prepend) env/vendor to sys.path.

    Appending matters: the vendored distribution's own tree-sitter pin (0.22.3) is
    incompatible with the grammars in the pinned env (0.26), so env packages must keep
    winning. `env/vendor/` intentionally contains only the `codebleu` package itself.
    """
    p = str(VENDOR_DIR)
    if p not in sys.path:
        sys.path.append(p)


@functools.lru_cache(maxsize=1)
def _calc_codebleu():
    _ensure_vendor_on_path()
    from codebleu import calc_codebleu  # type: ignore

    return calc_codebleu


# --------------------------------------------------------------------------- #
# 1. CodeBLEU

CODEBLEU_COMPONENTS = (
    "ngram_match_score",
    "weighted_ngram_match_score",
    "syntax_match_score",
    "dataflow_match_score",
)


def codebleu_score(prediction: str, reference: str, language: str) -> dict[str, float]:
    """CodeBLEU of `prediction` against `reference`, plus its four components.

    An empty or whitespace-only prediction scores 0 everywhere rather than raising: a
    model that answered with nothing has a defined score (it failed), and dropping those
    rows would silently improve the arm that fails most often.
    """
    zero = {"codebleu": 0.0, **{c: 0.0 for c in CODEBLEU_COMPONENTS}}
    if not prediction.strip() or not reference.strip():
        return zero
    try:
        res = _calc_codebleu()([reference], [prediction], lang=language)
    except Exception:
        # CodeBLEU's dataflow extractor can fail on badly-malformed code. That is a
        # property of the prediction, not an error in the harness, so it scores 0.
        return zero
    return {k: float(v) for k, v in res.items()}


# --------------------------------------------------------------------------- #
# 2. Readability proxy

_WORDLIST_PATHS = ("/usr/share/dict/words", "/usr/share/dict/linux.words")
_MIN_WORD_LEN = 3

#: Short names that are idiomatic rather than obfuscated. Without this, ordinary source
#: is penalised for writing `i`, `n` or `x`, and the proxy would report clean code as
#: unreadable — which would invert the very contrast it exists to measure.
_IDIOMATIC_SHORT = {
    "i", "j", "k", "n", "m", "x", "y", "z", "s", "t", "a", "b", "c", "f", "g", "p", "q",
    "r", "u", "v", "w", "l", "d", "e", "h", "o", "id", "ok", "dp", "lo", "hi", "mid",
    "idx", "res", "ans", "acc", "buf", "cnt", "cur", "num", "obj", "out", "pos", "ret",
    "seq", "str", "sum", "tmp", "val", "arr", "key", "map", "max", "min", "len",
}

_IDENT_NODE_TYPES = {"identifier", "property_identifier", "type_identifier"}

# Names introduced by our own transforms, matched so the proxy is not merely counting
# "is this a dictionary word" for the hex/sequential conditions.
_HEXNAME_RE = re.compile(r"^[vf]_[0-9a-f]{4}$")
_SEQNAME_RE = re.compile(r"^[a-z]{1,2}$")


@functools.lru_cache(maxsize=1)
def _wordlist() -> frozenset[str]:
    for path in _WORDLIST_PATHS:
        p = Path(path)
        if p.exists():
            try:
                words = {
                    w.strip().lower()
                    for w in p.read_text(errors="ignore").splitlines()
                    if len(w.strip()) >= _MIN_WORD_LEN and w.strip().isalpha()
                }
                if words:
                    return frozenset(words)
            except OSError:
                continue
    return frozenset()


def identifiers(code: str, language: str) -> list[str]:
    """Every identifier token in `code`, in source order (duplicates kept)."""
    try:
        root = parse(language, code)
    except Bail:
        return []
    return [
        node_text(code, n) for n in iter_nodes(root) if n.type in _IDENT_NODE_TYPES
    ]


#: Above this share of one/two-character identifiers, short names are read as the
#: product of minification rather than as idiom. Real source uses `i` and `n` for a
#: minority of its bindings; `L2` uses `a, b, c, ...` for all of them. Without this
#: test the whitelist below would score fully-minified code as perfectly meaningful,
#: which is exactly the condition the metric most needs to catch.
#:
#: Chosen by measurement, not taste. Over 400 Python corpus programs and their L2
#: variants the short-name ratio separates cleanly (L0 mean 0.239, p95 0.500; L2 mean
#: 0.663, p05 0.429), and the separation is best at 0.5:
#:     threshold   L0 flagged   L2 flagged
#:       0.4          17.2 %       97.8 %
#:       0.5           8.0 %       89.0 %     <- max(TPR - FPR)
#:       0.6           3.0 %       70.8 %
_MINIFIED_SHORT_RATIO = 0.5


def _name_is_meaningful(name: str, short_is_idiomatic: bool = True) -> bool:
    """True if `name` reads as English rather than as an obfuscator's output.

    `short_is_idiomatic` is decided per *program* by `readability_proxy`, not per name:
    whether `a` is a loop counter or a minified binding is not a property of the token.
    """
    low = name.lower()
    if _HEXNAME_RE.match(low):
        return False
    if low in _IDIOMATIC_SHORT:
        return short_is_idiomatic and len(low) <= 3
    if _SEQNAME_RE.match(low):  # single/double-letter minified name, not in the idiom set
        return False
    words = [w.lower() for w in split_words(name) if w]
    if not words:
        return False
    vocab = _wordlist()
    if not vocab:  # no system dictionary: fall back on shape alone
        return len(low) >= 4
    hits = sum(1 for w in words if len(w) >= _MIN_WORD_LEN and w in vocab)
    return hits >= max(1, (len(words) + 1) // 2)


@dataclass
class Readability:
    score: float
    components: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"readability": self.score, **{f"read_{k}": v for k, v in self.components.items()}}


#: Component weights. Identifier meaningfulness dominates because that is the dimension
#: every identifier-family condition (L1b/L1r/L2) actually destroys, and the one the
#: paper's renaming result turns on. Recorded in results so a re-weighting is visible.
READABILITY_WEIGHTS = {
    "identifier_meaning": 0.55,
    "identifier_length": 0.15,
    "line_length": 0.15,
    "nesting": 0.15,
}


def readability_proxy(code: str, language: str) -> Readability:
    """A [0, 1] readability substitute. NOT Scalabrino et al.'s model — see the module
    docstring. Only within-run contrasts are interpretable."""
    # Non-code scores 0, not "some middling value". tree-sitter is error-tolerant, so a
    # reply like `<stub:a1b2c3>` still yields identifier-ish tokens and would otherwise
    # earn ~0.7 here — which, combined with its trivially-low similarity to the
    # obfuscated input, let pure garbage satisfy the paper's reverse-success criterion
    # ~20 % of the time in a stub run. Readability of a non-program is undefined; 0 is
    # the conservative resolution and the only one that cannot manufacture success.
    if not code.strip() or not tree_ok(language, code):
        return Readability(0.0, {k: 0.0 for k in READABILITY_WEIGHTS})

    names = identifiers(code, language)
    unique = sorted(set(names))
    if unique:
        short_ratio = sum(1 for n in unique if len(n) <= 2) / len(unique)
        short_is_idiomatic = short_ratio < _MINIFIED_SHORT_RATIO
        meaning = sum(
            1 for n in unique if _name_is_meaningful(n, short_is_idiomatic)
        ) / len(unique)
        lengths = [len(n) for n in unique]
        mean_len = sum(lengths) / len(lengths)
        # Idiomatic identifier length is roughly 4-16 characters; both shorter (minified)
        # and much longer (machine-generated) names read worse.
        length_score = max(0.0, min(1.0, (mean_len - 1.0) / 5.0)) if mean_len <= 16 else max(
            0.0, 1.0 - (mean_len - 16.0) / 16.0
        )
    else:
        meaning, length_score = 0.0, 0.0

    lines = [ln for ln in code.splitlines() if ln.strip()]
    if lines:
        line_score = sum(1 for ln in lines if len(ln) <= 100) / len(lines)
        indents = [len(ln) - len(ln.lstrip(" ")) for ln in lines]
        max_depth = max(indents) / 4.0
        nesting_score = max(0.0, 1.0 - max(0.0, max_depth - 2.0) / 6.0)
    else:
        line_score, nesting_score = 0.0, 0.0

    comps = {
        "identifier_meaning": meaning,
        "identifier_length": length_score,
        "line_length": line_score,
        "nesting": nesting_score,
    }
    score = sum(READABILITY_WEIGHTS[k] * v for k, v in comps.items())
    return Readability(score, comps)


def identifier_recall(prediction: str, reference: str, language: str) -> float:
    """Fraction of the reference's meaningful identifiers that reappear in `prediction`.

    Not in the paper, and the crispest available replication of its variable-renaming
    result: it asks directly whether the original names came back, with no dependence on
    n-gram overlap or on a readability model. Restricted to *meaningful* reference names
    so that a reference which itself uses `i` and `n` does not hand out free credit.
    """
    ref_names = {n for n in identifiers(reference, language) if _name_is_meaningful(n, True)}
    if not ref_names:
        return float("nan")
    pred_names = set(identifiers(prediction, language))
    return len(ref_names & pred_names) / len(ref_names)


# --------------------------------------------------------------------------- #
# 3. Execution

_FUNC_NODE_TYPES = {
    "python": ("function_definition",),
    "javascript": ("function_declaration", "function_expression", "generator_function_declaration"),
}


def defined_functions(code: str, language: str) -> list[str]:
    """Names of the functions defined in `code`, in source order."""
    try:
        root = parse(language, code)
    except Bail:
        return []
    wanted = _FUNC_NODE_TYPES.get(language, ())
    out: list[str] = []
    for node in iter_nodes(root):
        if node.type not in wanted:
            continue
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            out.append(node_text(code, name_node))
    return out


def resolve_entry_point(code: str, language: str, preferred: str) -> Optional[str]:
    """Which function to call in model-generated code.

    A deobfuscating model is free to rename the entry point (recovering the original
    name is part of the task), so we cannot simply assume `preferred` exists:
      1. `preferred` if the code defines it — the model recovered the name;
      2. otherwise the single defined function, if there is exactly one;
      3. otherwise the LAST defined function, which is the convention for generated code
         that emits helpers before the function they serve.
    Returning None means the reply defined no callable function at all.
    """
    names = defined_functions(code, language)
    if not names:
        return None
    if preferred in names:
        return preferred
    if len(names) == 1:
        return names[0]
    return names[-1]


@dataclass
class ExecVerdict:
    status: str  # match | mismatch | error | no_entry_point | parse_fail
    n_cases: int = 0
    n_match: int = 0
    entry_point: Optional[str] = None

    @property
    def all_match(self) -> bool:
        return self.status == "match"

    def as_dict(self) -> dict[str, Any]:
        return {
            "exec_status": self.status,
            "exec_n_cases": self.n_cases,
            "exec_n_match": self.n_match,
            "exec_pass_rate": self.n_match / self.n_cases if self.n_cases else 0.0,
            "exec_entry_point": self.entry_point,
        }


def exec_equivalence(
    candidates: Sequence[Mapping[str, Any]],
    timeout_s: float = 2.0,
    workers: int = 32,
) -> list[ExecVerdict]:
    """Batch-check generated programs against stored canonical outputs.

    Each candidate is `{code, language, entry_point, cases}` where `cases` is a list of
    `{args_repr, output_canon}` — the gold the corpus already holds, so the reference
    program does not have to be re-run.

    Statuses: `parse_fail` (does not parse), `no_entry_point` (parses but defines no
    function), `match` (every case reproduces gold), `mismatch` (runs, wrong answer
    somewhere), `error` (raised/timed out where gold expects a value).
    """
    verdicts: list[Optional[ExecVerdict]] = [None] * len(candidates)
    items: list[BatchItem] = []
    slots: list[int] = []

    for i, cand in enumerate(candidates):
        code = cand.get("code") or ""
        lang = cand["language"]
        cases = list(cand.get("cases") or [])
        if not code.strip() or not tree_ok(lang, code):
            verdicts[i] = ExecVerdict("parse_fail")
            continue
        entry = resolve_entry_point(code, lang, cand.get("entry_point", ""))
        if entry is None:
            verdicts[i] = ExecVerdict("no_entry_point")
            continue
        if not cases:
            verdicts[i] = ExecVerdict("error", entry_point=entry)
            continue
        items.append(
            BatchItem(
                program_id=str(i),
                language=lang,
                code=code,
                entry_point=entry,
                args_reprs=[c["args_repr"] for c in cases],
            )
        )
        slots.append(i)

    if items:
        results = run_batch(items, timeout_s=timeout_s, workers=workers)
        for slot, res in zip(slots, results):
            cand = candidates[slot]
            cases = list(cand.get("cases") or [])
            n_match = 0
            n_error = 0
            for case, got in zip(cases, res.cases):
                if not got.ok:
                    n_error += 1
                    continue
                if got.output == case["output_canon"]:
                    n_match += 1
            if n_match == len(cases):
                status = "match"
            elif n_error == len(cases):
                status = "error"
            else:
                status = "mismatch"
            verdicts[slot] = ExecVerdict(
                status=status,
                n_cases=len(cases),
                n_match=n_match,
                entry_point=resolve_entry_point(
                    cand.get("code") or "", cand["language"], cand.get("entry_point", "")
                ),
            )

    return [v if v is not None else ExecVerdict("error") for v in verdicts]


# --------------------------------------------------------------------------- #
# Success criteria

def reverse_success_paper(
    sim_to_obfuscated: float,
    readability_deobf: float,
    readability_original: float,
    parses: bool,
    sim_threshold: float = 0.4,
    readability_tolerance: float = 0.1,
) -> bool:
    """The paper's criterion (§4.3.2): break similarity to the obfuscated input AND
    recover readability toward the original.

    `parses` is OUR addition, and it is not optional. As stated, the criterion is two
    inequalities, and *any* reply that is not the obfuscated input satisfies the first
    one — an empty string satisfies it perfectly. A stub run of this evaluator, in which
    every "generation" was the literal placeholder `<stub:a1b2c3>`, scored 17–25 %
    "reverse success" before this guard existed. The paper evidently assumes model
    output is code and never says so; we require it, because a deobfuscation that is not
    a program has not deobfuscated anything.

    The guard can only ever LOWER a reported number, so it cannot manufacture a
    replication — it can only prevent a false one.
    """
    return (
        parses
        and sim_to_obfuscated < sim_threshold
        and readability_deobf >= readability_original - readability_tolerance
    )


def forward_success_exec(verdict: ExecVerdict) -> bool:
    """Forward obfuscation is correct only if the generated program still computes the
    original outputs — the paper's "semantic evaluation" (§3.3) made executable."""
    return verdict.all_match
