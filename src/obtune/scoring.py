"""Strict normalized exact match — the grader for every accuracy number in the project.

Why this is a rewrite and not a port
------------------------------------
The old harness (`model_understanding/src/metrics.py::is_answer_correct`) ran a
four-stage cascade. Stages 1-3 (normalize -> literal parse -> numeric tolerance) are
sound and are kept. **Stage 4, "gold is a substring of the prediction", is deleted.**
The audit in `../LOG.md` §2026-06-09 found it produced ~3 % false positives: gold
`927` was scored correct against a prediction containing `9273`, and any prediction
that echoed the prompt scored correct for short golds. On a transfer matrix whose
effects are single-digit points, a 3 % ceiling of free credit is larger than the
effects we are trying to measure.

Two further deliberate tightenings over the old harness:

* **No lowercasing.** `'ABC'` and `'abc'` are different execution outputs. The old
  `normalize_for_compare` lowercased, which silently graded a case-wrong string as
  correct. Numbers and JSON keywords are unaffected because we compare them after
  parsing, not as text.
* **No answer extraction.** The old `extract_answer` hunted for `answer:` markers,
  `\\boxed{}`, XML tags and "last non-empty line". Repairing a non-compliant reply is
  exactly the failure this project must *report* (`format_fail_rate`, CLAUDE.md §4.6),
  so normalization is limited to whitespace, code fences/backticks and one trailing
  period. Anything else is a format failure and is counted as such.

Parser asymmetry (deliberate)
-----------------------------
Python items are parsed with `ast.literal_eval` and, on failure, `json.loads`; a model
tracing Python code may legitimately answer `True`/`None`/`'x'` (Python repr) while the
canonical gold is JSON-ish `true`/`null`/`"x"`. JavaScript items are parsed with
`json.loads` only: a JS program's output vocabulary *is* JSON, so accepting `True`
there would be leniency with no real case behind it.
"""
from __future__ import annotations

import ast
import json
import math
import re
from dataclasses import dataclass, asdict
from typing import Any, Optional

DEFAULT_FLOAT_TOL = 1e-6

# ``` or ```python ... ```  — captured non-greedily so only the first block is used.
_FENCE_BLOCK = re.compile(r"```[A-Za-z0-9_+-]*\s*\n?(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class Grade:
    """One graded trial. Field names are consumed by eval_vllm/eval_hf -> TrialRow."""

    correct: bool
    parse_ok: bool
    format_fail: bool
    method: str  # exact | normalized | structural | numeric | none
    pred_norm: str
    gold_norm: str
    raw_exact: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def grade_method(self) -> str:
        """Mapped onto schema.TrialRow.grade_method's Literal['exact','normalized','manual']."""
        return "exact" if self.method == "exact" else "normalized"


def normalize(text: str) -> str:
    """Whitespace strip -> unwrap code fences/backticks -> drop ONE trailing period.

    Order matters: the fence must be removed before the trailing-period rule, or a
    reply of "```\\n[1,2]\\n```." would keep its period.
    """
    s = text.strip()
    m = _FENCE_BLOCK.search(s)
    if m:
        s = m.group(1).strip()
    else:
        # An unterminated fence (generation hit max_tokens or a stop string) still
        # needs its opening marker removed.
        s = re.sub(r"^```[A-Za-z0-9_+-]*\s*", "", s)
        s = re.sub(r"```\s*$", "", s)
        s = s.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()
    if s.endswith("."):
        s = s[:-1].rstrip()
    return s


def raw_exact_match(pred: str, gold: str) -> bool:
    """Byte equality after whitespace stripping only — the strictest possible grader.

    Reported alongside `correct` so the paper can carry a grading-sensitivity
    appendix ("how much of the effect survives if normalization is switched off?").
    """
    return pred.strip() == gold.strip()


def parse_literal(text: str, language: str) -> tuple[bool, Any]:
    """(ok, value). See the module docstring for why the two languages differ."""
    s = text.strip()
    if not s:
        return False, None
    if language == "python":
        try:
            return True, ast.literal_eval(s)
        except (ValueError, SyntaxError, MemoryError, RecursionError, TypeError):
            pass
        try:
            return True, json.loads(s)
        except (json.JSONDecodeError, RecursionError):
            return False, None
    if language == "javascript":
        try:
            return True, json.loads(s)
        except (json.JSONDecodeError, RecursionError):
            return False, None
    raise ValueError(f"unknown language: {language!r}")


def _num_eq(a: Any, b: Any, tol: float) -> bool:
    """Numeric comparison with absolute-or-relative tolerance.

    Relative is needed because canon prints full-precision bignums and large floats;
    an absolute 1e-6 on 1e18 would be meaningless. Non-finite values never compare
    equal — canon rejects them outright, so seeing one means the prediction invented it.
    """
    fa, fb = float(a), float(b)
    if math.isnan(fa) or math.isnan(fb) or math.isinf(fa) or math.isinf(fb):
        return fa == fb and not math.isnan(fa)
    if fa == fb:
        return True
    if tol <= 0:
        return False
    return abs(fa - fb) <= max(tol, tol * max(abs(fa), abs(fb)))


def deep_equal(a: Any, b: Any, tol: float = 0.0) -> bool:
    """Recursive structural equality with numeric tolerance applied at every depth.

    Type discipline (this is what kills the `[2,4,6,8]` vs `2, 4, 6, 8` trap):
      * list and tuple are NOT interchangeable — `literal_eval('2, 4, 6, 8')` yields a
        tuple, and a model that dropped the brackets did not emit the gold literal.
      * bool is checked before int, so `True` never equals `1`.
      * int and float ARE interchangeable, because canon collapses integral floats.
    """
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, int) and isinstance(b, int):
        # Integers compare exactly. Applying the relative tolerance here would make
        # 10**18 and 10**18 + 1 "equal" (1e-6 * 1e18 = 1e12 of slack) — canon prints
        # Python bignums in full precisely so that they stay distinguishable.
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return _num_eq(a, b, tol)
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return isinstance(a, str) and isinstance(b, str) and a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(deep_equal(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(deep_equal(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(deep_equal(a[k], b[k], tol) for k in a)
    return type(a) is type(b) and a == b


def grade(
    pred: str,
    gold: str,
    language: str,
    float_tol: float = DEFAULT_FLOAT_TOL,
) -> Grade:
    """Grade one prediction against one canonical gold literal.

    Stages, in order, first hit wins:
      exact       — raw strings equal after whitespace strip
      normalized  — equal after `normalize`
      structural  — both parse and are deeply equal with NO numeric slack
      numeric     — both parse and are deeply equal within `float_tol`
      none        — wrong
    """
    pred_norm = normalize(pred)
    gold_norm = normalize(gold)
    raw = raw_exact_match(pred, gold)

    ok_pred, pv = parse_literal(pred_norm, language)
    ok_gold, gv = parse_literal(gold_norm, language)

    # A prediction that does not parse as a literal did not follow the output
    # contract. This is the reported format_fail_rate, not an excuse to go hunting
    # for an answer inside prose.
    format_fail = not ok_pred

    if raw:
        method = "exact"
    elif pred_norm == gold_norm:
        method = "normalized"
    elif ok_pred and ok_gold and deep_equal(pv, gv, 0.0):
        method = "structural"
    elif ok_pred and ok_gold and deep_equal(pv, gv, float_tol):
        method = "numeric"
    else:
        method = "none"

    return Grade(
        correct=method != "none",
        parse_ok=ok_pred,
        format_fail=format_fail,
        method=method,
        pred_norm=pred_norm,
        gold_norm=gold_norm,
        raw_exact=raw,
    )


def error_category(g: Grade, language: str) -> Optional[str]:
    """Coarse bucket for TrialRow.error_category — descriptive only, never a grade.

    Kept small on purpose: fine-grained error taxonomies invite post-hoc storytelling.
    """
    if g.correct:
        return None
    if g.format_fail:
        if not g.pred_norm:
            return "empty"
        if "\n" in g.pred_norm:
            return "multiline"
        return "unparseable"
    ok_p, pv = parse_literal(g.pred_norm, language)
    ok_g, gv = parse_literal(g.gold_norm, language)
    if ok_p and ok_g:
        if type(pv) is not type(gv) and not (
            isinstance(pv, (int, float)) and isinstance(gv, (int, float))
        ):
            return "wrong_type"
        if isinstance(pv, (list, tuple, dict)) and isinstance(gv, (list, tuple, dict)):
            if len(pv) != len(gv):
                return "wrong_length"
            return "wrong_elements"
    return "wrong_value"


def grade_batch(
    preds: list[str], golds: list[str], language: str, float_tol: float = DEFAULT_FLOAT_TOL
) -> list[Grade]:
    if len(preds) != len(golds):
        raise ValueError(f"length mismatch: {len(preds)} preds vs {len(golds)} golds")
    return [grade(p, g, language, float_tol) for p, g in zip(preds, golds)]
