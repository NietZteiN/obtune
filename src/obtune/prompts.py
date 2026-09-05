"""The ONE prompt builder — training, vLLM eval, HF eval and attention extraction all call it.

CLAUDE.md §4 silent-failure #3: a chat-template / prompt divergence between the
training distribution and the evaluation distribution is invisible in the loss curve
and fatal to the claim. Worse for RQ3: attention extraction runs on a *different*
engine (HF eager, because vLLM does not expose attentions), so if it built its own
prompt we would be measuring Δ-attention on a distribution that never produced any
accuracy number. Hence: one module, no re-implementations, and a sha256 of the
template constants recorded in every run manifest.

Design choices worth recording
------------------------------
* The system prompt makes the model an execution *engine*, not an assistant: reply
  with the return value alone, as a literal. No CoT. The constrained format is what
  makes `format_fail_rate` (CLAUDE.md §4.6) a meaningful number — if we allowed prose
  and then extracted an answer from it, the grader would be repairing exactly the
  failure mode we want to report.
* Literal syntax is pinned to the canonical output spec (`exec/canon.py`): JSON-ish,
  sorted object keys, no insignificant whitespace, integral floats printed as ints.
  That is the same spec the gold labels are serialized with, in both languages, so a
  Python and a JavaScript item are graded against the same notion of "the output".
* The optional one-shot demo is **L0** in every case, including the oracle-prompt
  systems. REJECTED alternative: a condition-matched demo (an L1b demo for an L1b
  item). It would turn the oracle-prompt arm into a 1-shot *deobfuscation* demo and
  confound RQ2's "models know how but not when" comparison with in-context transform
  learning. The demo's only job is to pin the output format.
* The demo is a fixed, frozen program that is part of the TRAIN-side distribution and
  is asserted never to collide with an eval program id (`assert_demo_disjoint`).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

PROMPT_VERSION = "v1"

SYSTEM_PROMPT = (
    "You are a deterministic code execution engine.\n"
    "You are given a program and one call to its entry point. You reply with the value "
    "that call returns.\n"
    "\n"
    "Rules:\n"
    "1. Reply with ONLY the return value, written as a single literal on one line.\n"
    "2. No explanation, no reasoning, no restatement of the call, no code fences, no "
    "backticks, no trailing punctuation.\n"
    "3. Use canonical literal syntax: true, false, null; double-quoted strings; arrays "
    "as [1,2,3]; objects as {\"a\":1,\"b\":2} with keys sorted and no spaces.\n"
    "4. Numbers with an integral value are written without a decimal point (2, not 2.0).\n"
    "5. The program may have been transformed (identifiers renamed, control flow "
    "restructured). The answer is whatever the code as written actually computes."
)

# Body of the user turn. `{oracle_block}` is empty for the non-oracle systems, so the
# base prompt is exactly the oracle prompt minus one line — the oracle-vs-base
# comparison is then a clean one-line manipulation rather than two different prompts.
USER_TEMPLATE = (
    "Language: {language}\n"
    "{oracle_block}"
    "Program:\n"
    "{code}\n"
    "\n"
    "Call: {call}\n"
    "\n"
    "Return value:"
)

ORACLE_PREFIX = "Transformation applied to this program: "

# ---------------------------------------------------------------------------------
# Execution-trace variant (`prompt.trace: true`; src/obtune/trace.py).
#
# The task is identical — the answer is still the single literal — but the model is
# asked to write the per-line variable trace first and the answer on a final `=> `
# line. The trace is the model's scratch work; the grader reads only the last `=> `
# line (trace.extract_answer). The user turn is the greedy template with the last
# line swapped, so the program/call block the model reads is byte-identical between
# the greedy and trace systems.
# ---------------------------------------------------------------------------------
SYSTEM_PROMPT_TRACE = (
    "You are a deterministic code execution engine.\n"
    "You are given a program and one call to its entry point. You execute the call "
    "step by step and then reply with the value it returns.\n"
    "\n"
    "Rules:\n"
    "1. First write the execution trace, one line per executed source line that "
    "changes a local variable: `L<line> name=value name=value`. Lines that change "
    "nothing are listed by number only. Write `...` once if the trace is too long, "
    "then stop tracing.\n"
    "2. Then write the return value on its own final line as `=> <value>`, a single "
    "literal. Nothing after it.\n"
    "3. Use canonical literal syntax: true, false, null; double-quoted strings; arrays "
    "as [1,2,3]; objects as {\"a\":1,\"b\":2} with keys sorted and no spaces.\n"
    "4. Numbers with an integral value are written without a decimal point (2, not 2.0).\n"
    "5. The program may have been transformed (identifiers renamed, control flow "
    "restructured). The answer is whatever the code as written actually computes."
)

USER_TEMPLATE_TRACE = USER_TEMPLATE.replace("Return value:", "Trace, then return value:")
assert USER_TEMPLATE_TRACE != USER_TEMPLATE

# One description per condition. H1 is present because the oracle-prompt *system* is
# evaluated on every eval condition including H1 — this is prompt text, not training
# data, and it carries no H1 code (quarantine is about code, CLAUDE.md §3.2).
ORACLE_DESCRIPTIONS: dict[str, str] = {
    "L0": "none: this is the original source with comments and docstrings removed",
    "L1b": (
        "adversarial renaming: every name, including the entry function, has been "
        "replaced with a misleading one that suggests a different purpose than the code has"
    ),
    "L1r": (
        "random renaming: every name, including the entry function, has been replaced "
        "with a meaningless hex-suffixed token such as v_a3f2 or f_91c0"
    ),
    "L2": (
        "minification: every name, including the entry function, has been replaced with "
        "a short sequential identifier (a, b, c, ... aa, ab) and type annotations have been stripped"
    ),
    "S1": (
        "control-flow flattening: the body has been rewritten as a dispatch loop over a "
        "state variable, with non-sequential state ids and the branches in scrambled order"
    ),
    "S2": (
        "opaque predicates and dead code: guards that always take the same branch and "
        "helper functions that are never called have been inserted"
    ),
    "H1": (
        "string encoding and mixed boolean arithmetic: string literals are reconstructed "
        "at run time by a decoder and arithmetic operators have been rewritten as "
        "equivalent bitwise expressions"
    ),
}


@dataclass(frozen=True)
class Demo:
    """A frozen one-shot example. `provenance` is recorded in the template hash."""

    program_id: str
    language: str
    condition: str
    code: str
    entry_point: str
    args_repr: str
    output_repr: str
    provenance: str = "frozen_demo"


_PY_DEMO_CODE = """def running_total(nums, start):
    total = start
    out = []
    for n in nums:
        total = total + n
        out.append(total)
    return out"""

_JS_DEMO_CODE = """function runningTotal(nums, start) {
    let total = start;
    const out = [];
    for (const n of nums) {
        total = total + n;
        out.push(total);
    }
    return out;
}"""

# The demo programs are deliberately trivial and L0: their only job is to show the
# output format. Both were executed through exec/pool.py to obtain output_repr.
ONE_SHOT_DEMOS: dict[str, Demo] = {
    "python": Demo(
        program_id="demo_running_total_py",
        language="python",
        condition="L0",
        code=_PY_DEMO_CODE,
        entry_point="running_total",
        args_repr="([1, 2, 3], 10)",
        output_repr="[11,13,16]",
    ),
    "javascript": Demo(
        program_id="demo_running_total_js",
        language="javascript",
        condition="L0",
        code=_JS_DEMO_CODE,
        entry_point="runningTotal",
        args_repr="([1, 2, 3], 10)",
        output_repr="[11,13,16]",
    ),
}


def format_call(entry_point: str, args_repr: str) -> str:
    """`args_repr` is the literal argument tuple source text, e.g. `(3, [1, 2])`.

    A single-element Python tuple is written `(3,)` upstream; we do not touch it —
    the call text must be valid source in the item's language, and the trailing comma
    is harmless in both.
    """
    a = args_repr.strip()
    if not (a.startswith("(") and a.endswith(")")):
        a = f"({a})"
    return f"{entry_point}{a}"


def build_user_content(
    code: str,
    entry_point: str,
    args_repr: str,
    language: str,
    condition: Optional[str] = None,
    oracle: bool = False,
    trace: bool = False,
) -> str:
    oracle_block = ""
    if oracle:
        if condition is None:
            raise ValueError("oracle=True requires the condition to describe")
        if condition not in ORACLE_DESCRIPTIONS:
            raise KeyError(f"no oracle description for condition {condition!r}")
        oracle_block = f"{ORACLE_PREFIX}{ORACLE_DESCRIPTIONS[condition]}\n"
    return (USER_TEMPLATE_TRACE if trace else USER_TEMPLATE).format(
        language=language,
        oracle_block=oracle_block,
        code=code.rstrip("\n"),
        call=format_call(entry_point, args_repr),
    )


def build_prompt(
    code: str,
    entry_point: str,
    args_repr: str,
    language: str,
    condition: Optional[str] = None,
    oracle: bool = False,
    one_shot: bool = False,
    demo: Optional[Demo] = None,
    trace: bool = False,
) -> list[dict[str, str]]:
    """Return the chat `prompt` message list (no assistant turn).

    Used verbatim by train (as the `prompt` field), by vLLM eval (through
    `render_chat`), by HF eval and by attention extraction.
    """
    if trace and one_shot:
        # The frozen demo has no trace and its point (pinning a one-literal format)
        # is exactly what the trace system does not want.
        raise ValueError("trace=True cannot be combined with one_shot=True")
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT_TRACE if trace else SYSTEM_PROMPT}
    ]
    if one_shot:
        d = demo or ONE_SHOT_DEMOS[language]
        messages.append(
            {
                "role": "user",
                "content": build_user_content(
                    d.code, d.entry_point, d.args_repr, d.language,
                    # The demo is L0; when the oracle line is on, the demo carries its
                    # own (truthful) "none" description so the format of the two user
                    # turns matches.
                    condition=d.condition, oracle=oracle,
                ),
            }
        )
        messages.append({"role": "assistant", "content": d.output_repr})
    messages.append(
        {
            "role": "user",
            "content": build_user_content(
                code, entry_point, args_repr, language, condition=condition, oracle=oracle,
                trace=trace,
            ),
        }
    )
    return messages


def build_example(
    row: Mapping[str, Any],
    oracle: bool = False,
    one_shot: bool = False,
    demo: Optional[Demo] = None,
    completion: Optional[str] = None,
) -> dict[str, list[dict[str, str]]]:
    """TRL 1.x conversational prompt-completion example.

    `{"prompt": [...], "completion": [{"role": "assistant", "content": output_repr}]}`
    — TRL sets `completion_only_loss=True` for this shape and masks the prompt tokens
    to -100 automatically. scripts/inspect_batch.py asserts that it really did.

    `completion` overrides the assistant turn (the trace arm passes the formatted
    trace, `trace.format_completion`) and switches the prompt to the trace template.
    """
    prompt = build_prompt(
        code=row["code"],
        entry_point=row["entry_point"],
        args_repr=row["args_repr"],
        language=row["language"],
        condition=row.get("condition"),
        oracle=oracle,
        one_shot=one_shot,
        demo=demo,
        trace=completion is not None,
    )
    return {
        "prompt": prompt,
        "completion": [
            {"role": "assistant", "content": row["output_repr"] if completion is None else completion}
        ],
    }


def prompt_id(oracle: bool = False, one_shot: bool = False, trace: bool = False) -> str:
    """Stable identifier written into every TrialRow (schema.TrialRow.prompt_id)."""
    if trace:
        return f"trace_oracle_{PROMPT_VERSION}" if oracle else f"trace_{PROMPT_VERSION}"
    if oracle and one_shot:
        return f"oracle_1shot_{PROMPT_VERSION}"
    if oracle:
        return f"oracle_{PROMPT_VERSION}"
    if one_shot:
        return f"base_1shot_{PROMPT_VERSION}"
    return f"base_{PROMPT_VERSION}"


ALL_PROMPT_IDS = (
    prompt_id(),
    prompt_id(one_shot=True),
    prompt_id(oracle=True),
    prompt_id(oracle=True, one_shot=True),
    prompt_id(trace=True),
    prompt_id(trace=True, oracle=True),
)


def template_sha256(trace: bool = False) -> str:
    """Hash of the template *content*, not of this file.

    Cosmetic edits (docstrings, helper refactors) must not change the id; any change
    to what the model actually reads must. Recorded in run_manifest.json and in every
    cell_meta.json so a result can be pinned to the exact prompt that produced it.

    The trace templates enter the payload only for `trace=True`, so adding the trace
    arm (2026-09-04) left every greedy cell's recorded hash valid.
    """
    payload: dict[str, Any] = {
        "version": PROMPT_VERSION,
        "system": SYSTEM_PROMPT,
        "user_template": USER_TEMPLATE,
        "oracle_prefix": ORACLE_PREFIX,
        "oracle_descriptions": ORACLE_DESCRIPTIONS,
        "demos": {
            k: [d.program_id, d.language, d.condition, d.code, d.entry_point, d.args_repr, d.output_repr]
            for k, d in sorted(ONE_SHOT_DEMOS.items())
        },
    }
    if trace:
        payload["system_trace"] = SYSTEM_PROMPT_TRACE
        payload["user_template_trace"] = USER_TEMPLATE_TRACE
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def provenance_block(
    oracle: bool = False, one_shot: bool = False, trace: bool = False
) -> dict[str, str]:
    """Drop-in for RunManifest.extra / cell_meta.json."""
    return {
        "prompt_id": prompt_id(oracle=oracle, one_shot=one_shot, trace=trace),
        "prompt_template_sha256": template_sha256(trace=trace),
        "prompt_version": PROMPT_VERSION,
    }


def render_chat(messages: Sequence[Mapping[str, str]], tokenizer: Any) -> str:
    """Apply the model's chat template and open the assistant turn.

    Both eval engines go through here, so the eval prompt is byte-identical to the
    prefix TRL builds during training (which also calls `apply_chat_template` on the
    `prompt` field with a generation prompt appended).
    """
    return tokenizer.apply_chat_template(
        list(messages), tokenize=False, add_generation_prompt=True
    )


def assert_demo_disjoint(eval_program_ids: Iterable[str]) -> None:
    """The one-shot demo must never be an eval program (it would be a leak into the
    test set through the prompt itself). Cheap, so it is checked on every eval run."""
    ids = set(eval_program_ids)
    clash = {d.program_id for d in ONE_SHOT_DEMOS.values()} & ids
    if clash:
        raise ValueError(f"one-shot demo program(s) {sorted(clash)} appear in the eval set")
