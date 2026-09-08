"""Inverse task — grade a predicted CALL by executing it (RQ5′, docs/RQ_SUMMARY.md §6.5).

The forward task asks for the value a call returns; the inverse task shows the value
and asks for a call that returns it. A predicted call is graded the way CRUXEval-I
grades an input: run the program on the predicted arguments and compare the canonical
output with the gold `output_repr`. Matching the *gold* arguments is not required and
is reported separately (`args_exact`), because many outputs have many pre-images and
"found a different valid input" is a success, not an error.

What counts as a format failure, and why it is strict
-----------------------------------------------------
The reply must be a single call `name(arg, ...)` whose arguments are literals
(`ast.literal_eval` accepts them). Prose, fences around prose, expressions
(`range(3)`, `2*3`), variables and multi-line replies are `format_fail`. This is the
same discipline as the forward grader (scoring.py): the constrained format is what
makes `format_fail_rate` a number, and hunting for a call inside prose would repair
exactly the failure we want to report. Code fences and backticks around an otherwise
clean call are unwrapped, as `scoring.normalize` does for the forward literal.

The name before the parenthesis is NOT graded. Under L1b/L1r/L2 the entry point is
renamed and the prompt states the name, so a model that writes the original name
(`solve` for `f_91c0`) has found the input, which is the task. The call is executed
against the item's true `entry_point`.

Execution is the project's sandbox (exec/pool.py: subprocess, rlimits, fd-1 blackholed).
Arguments are literal-checked in the parent BEFORE anything reaches the sandbox, so an
unparseable prediction is a format failure and never a "raised".
"""
from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Optional, Sequence

from obtune.exec.pool import BatchItem, run_batch
from obtune.scoring import _FENCE_BLOCK, deep_equal, parse_literal

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_\.]*$")


@dataclass(frozen=True)
class InverseGrade:
    """One graded inverse trial. Field names mirror scoring.Grade where they overlap so
    eval_vllm.build_trial_rows can shape both into a TrialRow."""

    correct: bool
    parse_ok: bool
    format_fail: bool
    method: str  # exec | none
    pred_norm: str  # the predicted argument tuple source, e.g. "(3, [1, 2],)"
    gold_norm: str  # the gold argument tuple source
    raw_exact: bool = False  # predicted arguments literal-equal to the gold arguments
    exec_status: str = "not_run"  # ok | raised | unserializable | error | timeout | crash | not_run
    exec_output: Optional[str] = None
    called_name: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def grade_method(self) -> str:
        return "exec"


def _unwrap(text: str) -> str:
    s = text.strip()
    m = _FENCE_BLOCK.search(s)
    if m:
        s = m.group(1).strip()
    else:
        s = re.sub(r"^```[A-Za-z0-9_+-]*\s*", "", s)
        s = re.sub(r"```\s*$", "", s).strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        s = s[1:-1].strip()
    if s.endswith("."):
        s = s[:-1].rstrip()
    return s


def extract_call(text: str) -> tuple[bool, Optional[str], Optional[str]]:
    """(ok, args_repr, called_name). `args_repr` is a tuple source string that
    `exec/runner_py._parse_args` accepts: `(a, b,)`; `()` for a zero-argument call.

    A trailing `,` is appended so a one-argument call becomes a one-tuple rather
    than a parenthesised scalar — `f(3)` must be `(3,)`, not `3`.
    """
    s = _unwrap(text)
    if not s or "\n" in s:
        return False, None, None
    i = s.find("(")
    if i < 0 or not s.endswith(")"):
        return False, None, None
    name = s[:i].strip()
    if name and not _NAME.match(name):
        return False, None, name
    inner = s[i + 1 : -1].strip().rstrip(",").rstrip()
    args_repr = "()" if not inner else f"({inner},)"
    try:
        node = ast.parse(args_repr, mode="eval")
        value = ast.literal_eval(node)
    except (ValueError, SyntaxError, MemoryError, RecursionError, TypeError):
        return False, None, name or None
    if not isinstance(value, tuple):  # cannot happen with the trailing comma; belt and braces
        return False, None, name or None
    return True, args_repr, name or None


def _args_equal(pred_repr: str, gold_repr: str) -> bool:
    try:
        p = ast.literal_eval(ast.parse(pred_repr, mode="eval"))
        g = ast.literal_eval(ast.parse(gold_repr, mode="eval"))
    except (ValueError, SyntaxError, MemoryError, RecursionError, TypeError):
        return False
    if not isinstance(g, tuple):
        g = (g,)
    return p == g


def grade_batch(
    items: Sequence[Any],
    outputs: Sequence[str],
    timeout_s: float = 2.0,
    mem_mb: int = 512,
    workers: int = 16,
    float_tol: float = 1e-6,
) -> list[InverseGrade]:
    """Grade `outputs[i]` as a call to `items[i]` (an EvalItem: code, entry_point,
    output_repr, language, program_id). Programs are executed once per distinct
    (item code) with all their predicted calls as cases, so a 1.5k-item cell costs a
    few hundred sandbox launches rather than 1.5k."""
    if len(items) != len(outputs):
        raise ValueError(f"length mismatch: {len(items)} items vs {len(outputs)} outputs")
    if any(getattr(it, "language", "python") != "python" for it in items):
        raise NotImplementedError("inverse grading is implemented for python only (no node on juno)")

    parsed: list[tuple[bool, Optional[str], Optional[str]]] = [extract_call(o) for o in outputs]

    # Group runnable predictions by (program_id, code) so one sandbox serves every
    # item of the same program variant.
    groups: dict[tuple[str, str, str], list[int]] = {}
    for i, (ok, _, _) in enumerate(parsed):
        if ok:
            it = items[i]
            groups.setdefault((it.program_id, it.entry_point, it.code), []).append(i)
    batch = [
        BatchItem(program_id=k[0], language="python", code=k[2], entry_point=k[1],
                  args_reprs=[parsed[i][1] for i in idxs])
        for k, idxs in groups.items()
    ]
    results = run_batch(batch, timeout_s=timeout_s, mem_mb=mem_mb, workers=workers)
    exec_of: dict[int, tuple[str, Optional[str]]] = {}
    for (k, idxs), res in zip(groups.items(), results):
        if res.child_status != "ok" or len(res.cases) != len(idxs):
            for i in idxs:
                exec_of[i] = (res.child_status if res.child_status != "ok" else "crash", None)
            continue
        for i, case in zip(idxs, res.cases):
            exec_of[i] = (case.status, case.output)

    grades: list[InverseGrade] = []
    for i, it in enumerate(items):
        ok, args_repr, name = parsed[i]
        gold_args = it.args_repr
        if not ok:
            grades.append(InverseGrade(
                correct=False, parse_ok=False, format_fail=True, method="none",
                pred_norm=_unwrap(outputs[i])[:200], gold_norm=gold_args, called_name=name,
            ))
            continue
        status, out = exec_of.get(i, ("not_run", None))
        correct = False
        if status == "ok" and out is not None:
            if out == it.output_repr:
                correct = True
            else:
                okp, pv = parse_literal(out, "python")
                okg, gv = parse_literal(it.output_repr, "python")
                correct = bool(okp and okg and deep_equal(pv, gv, float_tol))
        grades.append(InverseGrade(
            correct=correct, parse_ok=True, format_fail=False,
            method="exec" if correct else "none",
            pred_norm=args_repr, gold_norm=gold_args,
            raw_exact=_args_equal(args_repr, gold_args),
            exec_status=status, exec_output=out, called_name=name,
        ))
    return grades


def error_category(g: InverseGrade) -> Optional[str]:
    """Coarse bucket, descriptive only (mirrors scoring.error_category)."""
    if g.correct:
        return None
    if g.format_fail:
        if not g.pred_norm:
            return "empty"
        if "\n" in g.pred_norm:
            return "multiline"
        return "unparseable"
    if g.exec_status == "raised":
        return "call_raised"
    if g.exec_status in ("timeout", "crash", "error", "unserializable", "not_run"):
        return f"exec_{g.exec_status}"
    return "wrong_value"
