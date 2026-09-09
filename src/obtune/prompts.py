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

# ---------------------------------------------------------------------------------
# Inverse task (`task="input"`; src/obtune/inverse.py) — RQ5' in docs/RQ_SUMMARY.md.
#
# The model is given the program and the value one call RETURNED, and must write a
# call that returns it: CRUXEval-I to the forward task's CRUXEval-O. Every adapter in
# the project was trained on the forward direction only, so this prompt is a
# distribution shift for tuned and untuned arms alike — which is the point: it asks
# whether what tuning taught is a fact about the *code* (usable in either direction)
# or a fact about the *forward mapping*. Grading is by execution (inverse.py), not by
# matching the gold call: any call that reproduces the value is correct, exactly as in
# CRUXEval-I.
#
# The entry-point name is given in the prompt. Withholding it would make every reply
# fail on the name under L1b/L1r/L2, where the entry point is renamed, and the task is
# "find an input", not "find the function".
# ---------------------------------------------------------------------------------
SYSTEM_PROMPT_INVERSE = (
    "You are a deterministic code execution engine run in reverse.\n"
    "You are given a program and the value that one call to its entry point returned. "
    "You reply with a call to the entry point that returns exactly that value.\n"
    "\n"
    "Rules:\n"
    "1. Reply with ONLY the call, on one line, in the form name(arg1, arg2, ...).\n"
    "2. No explanation, no reasoning, no code fences, no backticks, no trailing "
    "punctuation.\n"
    "3. Write every argument as a literal in the program's language (numbers, strings, "
    "lists, tuples, dicts, booleans, None/null). No variables, no expressions, no calls.\n"
    "4. Any arguments that make the call return the given value are acceptable.\n"
    "5. The program may have been transformed (identifiers renamed, control flow "
    "restructured). The call must return the value under the code as written."
)

USER_TEMPLATE_INVERSE = (
    "Language: {language}\n"
    "{oracle_block}"
    "Program:\n"
    "{code}\n"
    "\n"
    "Entry point: {entry_point}\n"
    "Return value: {output}\n"
    "\n"
    "Call:"
)

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
    task: str = "output",
    output_repr: Optional[str] = None,
) -> str:
    oracle_block = ""
    if oracle:
        if condition is None:
            raise ValueError("oracle=True requires the condition to describe")
        if condition not in ORACLE_DESCRIPTIONS:
            raise KeyError(f"no oracle description for condition {condition!r}")
        oracle_block = f"{ORACLE_PREFIX}{ORACLE_DESCRIPTIONS[condition]}\n"
    if task == "input":
        if trace:
            raise ValueError("task='input' cannot be combined with trace=True")
        if output_repr is None:
            raise ValueError("task='input' needs the gold output_repr to show")
        return USER_TEMPLATE_INVERSE.format(
            language=language,
            oracle_block=oracle_block,
            code=code.rstrip("\n"),
            entry_point=entry_point,
            output=output_repr.strip(),
        )
    if task != "output":
        raise ValueError(f"unknown task {task!r} (output|input)")
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
    task: str = "output",
    output_repr: Optional[str] = None,
) -> list[dict[str, str]]:
    """Return the chat `prompt` message list (no assistant turn).

    Used verbatim by train (as the `prompt` field), by vLLM eval (through
    `render_chat`), by HF eval and by attention extraction.

    `task="input"` builds the inverse prompt (program + return value -> call); the
    one-shot demo then shows the demo's *call* as the assistant turn, and
    `output_repr` is required.
    """
    if trace and one_shot:
        # The frozen demo has no trace and its point (pinning a one-literal format)
        # is exactly what the trace system does not want.
        raise ValueError("trace=True cannot be combined with one_shot=True")
    inverse = task == "input"
    if inverse and trace:
        raise ValueError("task='input' cannot be combined with trace=True")
    system_text = SYSTEM_PROMPT_INVERSE if inverse else (SYSTEM_PROMPT_TRACE if trace else SYSTEM_PROMPT)
    messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]
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
                    task=task, output_repr=d.output_repr,
                ),
            }
        )
        messages.append(
            {"role": "assistant",
             "content": format_call(d.entry_point, d.args_repr) if inverse else d.output_repr}
        )
    messages.append(
        {
            "role": "user",
            "content": build_user_content(
                code, entry_point, args_repr, language, condition=condition, oracle=oracle,
                trace=trace, task=task, output_repr=output_repr,
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


def prompt_id(
    oracle: bool = False, one_shot: bool = False, trace: bool = False, task: str = "output"
) -> str:
    """Stable identifier written into every TrialRow (schema.TrialRow.prompt_id)."""
    if task == "input":
        tag = "inverse" + ("_oracle" if oracle else "") + ("_1shot" if one_shot else "")
        return f"{tag}_{PROMPT_VERSION}"
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
    prompt_id(task="input"),
    prompt_id(task="input", one_shot=True),
    prompt_id(task="input", oracle=True),
    prompt_id(task="input", oracle=True, one_shot=True),
)


def template_sha256(trace: bool = False, task: str = "output") -> str:
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
    if task == "input":
        # Same rule as the trace arm: the inverse templates enter the hash only for
        # inverse cells, so every forward cell's recorded hash stays valid.
        payload["system_inverse"] = SYSTEM_PROMPT_INVERSE
        payload["user_template_inverse"] = USER_TEMPLATE_INVERSE
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def provenance_block(
    oracle: bool = False, one_shot: bool = False, trace: bool = False, task: str = "output"
) -> dict[str, str]:
    """Drop-in for RunManifest.extra / cell_meta.json."""
    return {
        "prompt_id": prompt_id(oracle=oracle, one_shot=one_shot, trace=trace, task=task),
        "prompt_template_sha256": template_sha256(trace=trace, task=task),
        "prompt_version": PROMPT_VERSION,
    }


# --------------------------------------------------------------------------- #
# Template adaptation — ONE policy, applied by every path (2026-09-09)
# --------------------------------------------------------------------------- #
# The panel outgrew the assumption that every base model takes a system role. Measured
# on 2026-09-09 with the real tokenizers:
#
#   CodeLlama / Llama-3.1-Instruct / Granite-3.1  -> system role rendered as its own turn
#   Gemma-3-12b-it                                -> template folds system into the first
#                                                    user turn ("SYS\n\nU1") and returns
#   StarCoder2-15b-instruct                       -> TemplateError: "System messages are
#                                                    not allowed in this template"
#   CodeGemma-7b-it                               -> TemplateError: "System role not supported"
#   Llama-3.1-8B (pretrained)                     -> no chat_template at all
#
# CLAUDE.md §4 silent-failure #3 makes this load-bearing: train, vLLM eval, HF eval and
# attention extraction must build byte-identical prompts, so the adaptation cannot live at
# a call site. It lives here, is resolved once per template, and every renderer goes
# through it.
#
# The two adaptations are content-preserving by construction:
#   "merged" — the system text becomes the head of the first user turn, separated by a
#              blank line. This is exactly what Gemma-3's own template does to a system
#              message, so the merged form is not an invention; it is the one the
#              template family already defines.
#   "plain"  — no template exists, so we render a fixed, versioned plain-text form.
#              REJECTED alternative: borrow the instruct twin's template. It would put
#              control tokens in front of a checkpoint that never saw them, and the
#              base-vs-instruct comparison (the reason the pretrained model is in the
#              panel) would then be confounded by a template the base model cannot read.
#
# A model whose template *silently* drops the system content — rather than raising — would
# defeat this, so `template_mode` verifies that the system text survives rendering and
# raises if it does not.
PLAIN_RENDER_VERSION = "plain_v1"
_PLAIN_HEADERS = {"system": "### System", "user": "### Instruction", "assistant": "### Response"}

_MODE_CACHE: dict[str, str] = {}
_PROBE_SYSTEM = "__OBTUNE_SYS_PROBE__"
_PROBE_USER = "__OBTUNE_USER_PROBE__"


def template_mode(tokenizer: Any) -> str:
    """One of "system" | "merged" | "plain" for this tokenizer's chat template.

    Cached on the template string itself, not on the tokenizer object: two tokenizer
    instances of the same model must resolve identically, and an lru_cache over an
    unhashable tokenizer would not compile.
    """
    tpl = getattr(tokenizer, "chat_template", None)
    if not tpl:
        return "plain"
    key = tpl if isinstance(tpl, str) else json.dumps(tpl, sort_keys=True)
    hit = _MODE_CACHE.get(key)
    if hit is not None:
        return hit
    probe = [{"role": "system", "content": _PROBE_SYSTEM}, {"role": "user", "content": _PROBE_USER}]
    try:
        rendered = tokenizer.apply_chat_template(probe, tokenize=False, add_generation_prompt=True)
        # A template that accepts the role but discards the text is the dangerous case:
        # it would train and evaluate on a prompt with no task description at all.
        if _PROBE_SYSTEM not in rendered:
            raise ValueError(
                "this chat template accepts a system role but drops its content; "
                "refusing to build prompts with it"
            )
        mode = "system"
    except ValueError:
        raise
    except Exception:
        # Any template-side refusal (jinja2 TemplateError and friends). Verify the
        # fallback actually renders before committing to it.
        merged = adapt_messages(probe, None, force="merged")
        rendered = tokenizer.apply_chat_template(merged, tokenize=False, add_generation_prompt=True)
        if _PROBE_SYSTEM not in rendered or _PROBE_USER not in rendered:
            raise ValueError("chat template renders neither a system turn nor a merged user turn")
        mode = "merged"
    _MODE_CACHE[key] = mode
    return mode


def adapt_messages(
    messages: Sequence[Mapping[str, str]], tokenizer: Any, force: Optional[str] = None
) -> list[dict[str, str]]:
    """Messages this tokenizer's template can render, with identical content.

    In "system" mode the list is returned unchanged. In "merged" and "plain" mode the
    system turn is folded into the first user turn. `force` is for the probe above and
    for tests; production callers pass a tokenizer.
    """
    mode = force or template_mode(tokenizer)
    msgs = [dict(m) for m in messages]
    if mode == "system" or not msgs or msgs[0].get("role") != "system":
        return msgs
    system = msgs.pop(0)["content"]
    for m in msgs:
        if m.get("role") == "user":
            m["content"] = f"{system}\n\n{m['content']}"
            return msgs
    # No user turn to carry it (never happens for our prompts, but silently dropping the
    # system text is the one outcome that must not be possible).
    raise ValueError("cannot merge the system turn: the prompt has no user turn")


def render_plain(messages: Sequence[Mapping[str, str]], add_generation_prompt: bool = True) -> str:
    """Fixed plain-text rendering for a checkpoint with no chat template.

    Deterministic and versioned (`PLAIN_RENDER_VERSION`): training and every eval engine
    call this same function, so the pretrained model sees one format everywhere.
    """
    parts = []
    for m in adapt_messages(messages, None, force="merged"):
        parts.append(f"{_PLAIN_HEADERS[m['role']]}\n{m['content']}")
    if add_generation_prompt:
        parts.append(f"{_PLAIN_HEADERS['assistant']}\n")
        return "\n\n".join(parts[:-1]) + "\n\n" + parts[-1]
    return "\n\n".join(parts)


def render_chat(messages: Sequence[Mapping[str, str]], tokenizer: Any) -> str:
    """Apply the model's chat template and open the assistant turn.

    Both eval engines go through here, so the eval prompt is byte-identical to the
    prefix training builds (which renders the same adapted messages with the same
    template — see `to_trl_example`).
    """
    if template_mode(tokenizer) == "plain":
        return render_plain(messages, add_generation_prompt=True)
    return tokenizer.apply_chat_template(
        adapt_messages(messages, tokenizer), tokenize=False, add_generation_prompt=True
    )


def render_full(
    messages: Sequence[Mapping[str, str]], tokenizer: Any, completion: Optional[str] = None
) -> str:
    """Prompt + assistant turn, no generation prompt — what the trainer's loss sees.

    `completion` may be given as text; otherwise the last message is already the
    assistant turn.
    """
    msgs = list(messages)
    if completion is not None:
        msgs = msgs + [{"role": "assistant", "content": completion}]
    if template_mode(tokenizer) == "plain":
        return render_plain(msgs, add_generation_prompt=False)
    return tokenizer.apply_chat_template(adapt_messages(msgs, tokenizer), tokenize=False)


def to_trl_example(example: Mapping[str, Any], tokenizer: Any) -> dict[str, Any]:
    """`build_example`'s output in the form THIS tokenizer's trainer can consume.

    Conversational (adapted messages) when a template exists; TRL's text
    prompt-completion form when it does not. Either way `completion_only_loss=True`
    masks the prompt, and `scripts/inspect_batch.py` asserts it did.
    """
    prompt, completion = example["prompt"], example["completion"]
    if template_mode(tokenizer) != "plain":
        return {"prompt": adapt_messages(prompt, tokenizer), "completion": list(completion)}
    text = completion[0]["content"] if not isinstance(completion, str) else completion
    return {"prompt": render_plain(prompt, add_generation_prompt=True), "completion": text}


def render_provenance(tokenizer: Any) -> dict[str, str]:
    """Recorded in every run manifest beside `prompt_template_sha256`.

    Deliberately NOT folded into that hash: the hash identifies the prompt *text*, and
    every cell already published carries it. How a given model's template lays that text
    out is a separate fact, and it is the one a reader needs to compare two models.
    """
    mode = template_mode(tokenizer)
    return {
        "render_mode": mode,
        "render_version": PLAIN_RENDER_VERSION if mode == "plain" else PROMPT_VERSION,
    }


def assert_demo_disjoint(eval_program_ids: Iterable[str]) -> None:
    """The one-shot demo must never be an eval program (it would be a leak into the
    test set through the prompt itself). Cheap, so it is checked on every eval run."""
    ids = set(eval_program_ids)
    clash = {d.program_id for d in ONE_SHOT_DEMOS.values()} & ids
    if clash:
        raise ValueError(f"one-shot demo program(s) {sorted(clash)} appear in the eval set")
