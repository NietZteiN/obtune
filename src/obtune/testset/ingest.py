"""Ingest the ICSE stimuli into the two test-set namespaces.

Produces:
  * ``data/eval/testset/legacy_icse/{dataset_a,dataset_b}.jsonl`` — all 350 original
    rows, code preserved **byte-identical** with a ``source_sha256``. These carry
    ``tier_icse`` and are the only rows comparable to the human baselines.
  * ``data/eval/testset/base/{dataset_a,dataset_b}.jsonl`` — the unique L0 parents as
    ``BaseProgram`` rows, from which obf/builder.py regenerates all seven new
    conditions with language-identical semantics.

Three I/O encodings have to be reconciled, which is why this is a module rather than
a one-liner (all three verified against the real files, 2026-08-04):

  * Dataset A / Python — no ``input``/``expected_output``/``fn_name`` at all. The
    call lives in ``inputs`` as source text (``"myFunct(6)"``) and the answer in
    ``outputs`` in *human* formatting (``"FALSE"``, not ``False``). The entry point
    has to be recovered from the call expression.
  * Dataset A / JavaScript — ``input`` is a JSON **argument array** (``"[14]"``),
    not a call.
  * Dataset B / both — ``input`` is a call expression (``'f("")'``).

Canonical outputs are always re-derived by executing the L0 parent, never trusted
from the file: the stored answers are in whatever format the survey displayed, and
the whole project scores against exec/canon.py. The human answer is kept verbatim
alongside, and every disagreement is written to the ingest report — ``FALSE`` vs
``False`` is expected formatting drift, anything else is a finding about the answer
key rather than about us.
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from obtune.config import load_config
from obtune.corpus.normalize import normalize
from obtune.exec import BatchItem, canon, run_batch
from obtune.paths import EVAL_ROOT, MANIFESTS_ROOT, write_jsonl
from obtune.provenance import sha256_text
from obtune.schema import BaseProgram, InputCase

#: Dataset A capitalizes Python but not JavaScript; Dataset B lowercases both.
_LANG = {"python": "python", "javascript": "javascript"}


def _lang(row: dict[str, Any]) -> str:
    return _LANG[str(row.get("language", "")).strip().lower()]


def _tuple_repr(parts: list[str]) -> str:
    """Argument sources -> the tuple literal exec/pool.py expects."""
    return f"({', '.join(parts)}{',' if len(parts) == 1 else ''})"


def _param_names(code: str, entry: str, language: str) -> list[str]:
    """Positional parameter names of `entry`, for resolving keyword arguments."""
    if language != "python":
        return []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == entry:
            a = node.args
            names = [p.arg for p in (*a.posonlyargs, *a.args)]
            # LeetCode stimuli are `Solution` methods lifted to module level, so they
            # keep a leading `self` that no stored call supplies.
            if names and names[0] in ("self", "cls"):
                names = names[1:]
            return names
    return []


def _call_parts(text: str, code: str = "", language: str = "python") -> tuple[str | None, str | None]:
    """Split a call expression into (callee, argument-tuple source).

    Keyword arguments are resolved to positions against the callee's signature: the
    LeetCode rows in Dataset B are written `myFunct(nums=[1,2], k=2)`, and dropping
    the keywords (or passing them through) would silently produce a zero-argument
    call that fails at execution.
    """
    try:
        node = ast.parse(text.strip(), mode="eval").body
    except SyntaxError:
        return None, None
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        return None, None

    parts = [ast.unparse(a) for a in node.args]
    if node.keywords:
        named = {k.arg: ast.unparse(k.value) for k in node.keywords if k.arg}
        # The stored callee may be a placeholder that does not exist in the code
        # (Dataset B's LeetCode rows all say `myFunct`), so resolve the signature
        # against the function the code actually defines.
        entry = node.func.id
        params = _param_names(code, entry, language)
        if not params:
            fallback = _entry_from_code(code, language)
            if fallback:
                params = _param_names(code, fallback, language)
        if not params:
            return node.func.id, None
        for name in params[len(parts):]:
            if name not in named:
                return node.func.id, None
            parts.append(named.pop(name))
        if named:  # a keyword we could not place
            return node.func.id, None
    return node.func.id, _tuple_repr(parts)


def _args_from_array_literal(text: str) -> str | None:
    """Dataset A / JS stores arguments as an array rather than a call.

    Tries JSON first, then a Python literal: some rows use single quotes
    (``['world']``), which is not valid JSON.
    """
    values: Any = None
    try:
        values = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        try:
            values = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None
    if not isinstance(values, (list, tuple)):
        return None
    return _tuple_repr([json.dumps(v) for v in values])


def _drop_self_parameter(code: str, entry: str) -> tuple[str, bool]:
    """Remove a vestigial ``self``/``cls`` from `entry`'s signature.

    The LeetCode stimuli are ``Solution`` methods lifted to module level; they keep a
    receiver parameter that no stored call supplies, so the arguments would bind one
    position off and raise TypeError. Dropping it makes the program the plain function
    it is meant to be — but only when the body never references the receiver, since
    otherwise the program is genuinely not self-contained and belongs out of the corpus.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code, False
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != entry:
            continue
        args = node.args
        first = (args.posonlyargs + args.args)[:1]
        if not first or first[0].arg not in ("self", "cls"):
            return code, False
        receiver = first[0].arg
        used = any(isinstance(n, ast.Name) and n.id == receiver for n in ast.walk(node))
        if used:
            return code, False
        if args.posonlyargs:
            args.posonlyargs = args.posonlyargs[1:]
        else:
            args.args = args.args[1:]
        return ast.unparse(tree), True
    return code, False


_JS_FN = re.compile(r"(?:function\s+([A-Za-z_$][\w$]*)|(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=)")


def _entry_from_code(code: str, language: str) -> str | None:
    if language == "python":
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None
        funcs = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        return funcs[-1] if funcs else None
    names = [a or b for a, b in _JS_FN.findall(code)]
    return names[-1] if names else None


def _extract_io(row: dict[str, Any], language: str) -> tuple[str | None, str | None, str | None]:
    """Return (entry_point, args_repr, human_answer) for any of the three encodings."""
    human = row.get("expected_output")
    if human is None:
        human = row.get("outputs")
    entry = row.get("fn_name")

    raw_input = row.get("input")
    if raw_input is None:
        raw_input = row.get("inputs")
    if raw_input is None:
        return entry, None, human
    raw_input = str(raw_input).strip()
    code = row.get("code", "")

    args = None
    if raw_input.startswith("["):
        args = _args_from_array_literal(raw_input)
    if args is None:
        callee, args = _call_parts(raw_input, code, language)
        if callee and not entry:
            entry = callee

    # A stored fn_name that the code does not define is a placeholder, not the entry
    # point (Dataset B's LeetCode rows all claim `myFunct`). Trust the code.
    defined = _entry_from_code(code, language)
    if entry and language == "python" and not _param_names(code, entry, language):
        if defined and _param_names(code, defined, language) is not None:
            entry = defined
    if not entry:
        entry = defined
    return entry, args, (str(human) if human is not None else None)


def _answers_agree(canonical: str, human: str | None) -> bool:
    """Whether a stored answer matches the executed one modulo *presentation only*.

    The stored keys are in whatever the survey displayed — Python repr (``['a', 'b']``,
    ``True``, ``{1: None}``), sometimes uppercased (``FALSE``). Comparing those to a
    canon.py string textually would flag ~40 % of rows as disagreements and bury the
    handful of real ones. So the human key is parsed as a literal and re-canonicalized;
    only what survives that is a genuine mismatch worth reporting.
    """
    if human is None:
        return False
    text = human.strip()
    if canonical.strip() == text:
        return True

    for parse in (json.loads, ast.literal_eval):
        try:
            return canon(parse(text)) == canonical
        except Exception:  # noqa: BLE001 — not parseable in this dialect; try the next
            continue

    # Survey-style renderings of booleans/None that are not literals in either dialect.
    lowered = text.strip('"').strip("'").lower()
    alias = {"true": "true", "false": "false", "none": "null", "null": "null"}
    if lowered in alias:
        return canonical == alias[lowered]
    return canonical.strip('"') == text.strip('"').strip("'")


@dataclass
class IngestReport:
    dataset: str
    legacy_rows: int = 0
    parents: int = 0
    per_language: dict[str, int] = field(default_factory=dict)
    executed_ok: int = 0
    answer_agreements: int = 0
    answer_disagreements: list[dict[str, Any]] = field(default_factory=list)
    unparsed: list[dict[str, Any]] = field(default_factory=list)
    exec_failures: list[dict[str, Any]] = field(default_factory=list)
    whitespace_normalized: int = 0


def ingest_dataset(path: str | Path, dataset: str, n_gate_inputs: int = 20) -> tuple[list[dict], list[dict], IngestReport]:
    """Return (legacy_rows, base_programs, report) for one dataset file."""
    rows = json.loads(Path(path).read_text())
    report = IngestReport(dataset=dataset)

    legacy: list[dict[str, Any]] = []
    for row in rows:
        legacy.append({
            "dataset": dataset,
            "task_id": row.get("task_id"),
            "language": _lang(row),
            "tier_icse": row.get("obfuscation_level"),
            "code": row["code"],  # byte-identical, deliberately un-normalized
            "source_sha256": sha256_text(row["code"]),
            "fn_name": row.get("fn_name"),
            "input": row.get("input", row.get("inputs")),
            "expected_output": row.get("expected_output", row.get("outputs")),
            "question_number": row.get("question_number"),
            "dataset_source": row.get("dataset_source"),
        })
    report.legacy_rows = len(legacy)

    # --- L0 parents ------------------------------------------------------- #
    l0 = [r for r in rows if r.get("obfuscation_level") == "L0"]
    candidates: list[dict[str, Any]] = []
    for row in l0:
        language = _lang(row)
        entry, args, human = _extract_io(row, language)
        if not entry or not args:
            report.unparsed.append({"task_id": row.get("task_id"), "language": language,
                                    "reason": "no entry point" if not entry else "no arguments",
                                    "raw_input": row.get("input", row.get("inputs"))})
            continue
        # Survey stimuli are double-spaced for on-screen readability. The legacy rows
        # keep those exact bytes; new conditions are generated from a normalized copy.
        norm = normalize(row["code"], language)
        if norm.code != row["code"]:
            report.whitespace_normalized += 1
        code = norm.code
        dropped_self = False
        if language == "python":
            code, dropped_self = _drop_self_parameter(code, entry)
        candidates.append({"row": row, "language": language, "entry": entry, "args": args,
                           "human": human, "code": code, "dropped_self": dropped_self})

    results = run_batch(
        [BatchItem(c["row"]["task_id"], c["language"], c["code"], c["entry"], [c["args"]])
         for c in candidates],
        timeout_s=5.0,
    )

    programs: list[dict[str, Any]] = []
    for cand, res in zip(candidates, results):
        case = res.cases[0]
        if not case.ok:
            report.exec_failures.append({"task_id": cand["row"]["task_id"], "language": cand["language"],
                                         "status": case.status, "exc_type": case.exc_type,
                                         "entry_point": cand["entry"], "args": cand["args"]})
            continue
        report.executed_ok += 1
        if _answers_agree(case.output or "", cand["human"]):
            report.answer_agreements += 1
        else:
            report.answer_disagreements.append({
                "task_id": cand["row"]["task_id"], "language": cand["language"],
                "executed": case.output, "human_key": cand["human"],
            })
        program = BaseProgram(
            program_id=f"{dataset}:{cand['row']['task_id']}",
            language=cand["language"],
            source=f"dataset_{dataset.lower()}",
            code=cand["code"],
            entry_point=cand["entry"],
            cases=[InputCase(args_repr=cand["args"], output_canon=case.output or "", case_role="human")],
            gate_inputs=[],
            loc=len(cand["code"].splitlines()),
            meta={
                "task_id": cand["row"]["task_id"],
                "dataset": dataset,
                "dataset_source": cand["row"].get("dataset_source"),
                "whitespace_normalized": cand["code"] != cand["row"]["code"],
                "receiver_param_dropped": cand["dropped_self"],
                "human_answer_key": cand["human"],
                "n_gate_inputs_requested": n_gate_inputs,
            },
        )
        programs.append(program.model_dump())
        report.per_language[cand["language"]] = report.per_language.get(cand["language"], 0) + 1

    report.parents = len(programs)
    return legacy, programs, report


def run(write: bool = True) -> dict[str, Any]:
    cfg = load_config("data.yaml")
    n_gate = int(cfg["cases"]["n_gate_inputs"])
    out: dict[str, Any] = {"datasets": {}}

    for key, dataset in (("dataset_a", "A"), ("dataset_b", "B")):
        legacy, programs, report = ingest_dataset(cfg["test_set"][key], dataset, n_gate)
        if write:
            write_jsonl(EVAL_ROOT / "testset" / "legacy_icse" / f"{key}.jsonl", legacy)
            write_jsonl(EVAL_ROOT / "testset" / "base" / f"{key}.jsonl", programs)
        out["datasets"][dataset] = {
            "legacy_rows": report.legacy_rows,
            "parents": report.parents,
            "per_language": report.per_language,
            "executed_ok": report.executed_ok,
            "answer_agreements": report.answer_agreements,
            "answer_disagreements": report.answer_disagreements,
            "unparsed": report.unparsed,
            "exec_failures": report.exec_failures,
            "whitespace_normalized": report.whitespace_normalized,
        }

    out["total_parents"] = sum(d["parents"] for d in out["datasets"].values())
    out["total_legacy_rows"] = sum(d["legacy_rows"] for d in out["datasets"].values())
    if write:
        MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)
        (MANIFESTS_ROOT / "testset_ingest_report.json").write_text(json.dumps(out, indent=2))
    return out
