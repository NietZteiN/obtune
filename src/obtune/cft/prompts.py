"""Prompt builders for the four CFT task formats.

This module is deliberately SEPARATE from `obtune.prompts`. That module is the frozen
single prompt builder for obtune's own task (output prediction over still-obfuscated
code) and is depended on by training, both eval engines and attention extraction; the
CFT replication asks the model to *emit code*, which is a different task with a
different system prompt. Mixing the two would silently change the distribution that
every obtune accuracy number was measured on.

The four formats
----------------
`gen`   (L_gen, paper §4.1.2)  — forward: obfuscate this program with technique T.
                                 The paper's prompt verbatim, with the language and
                                 technique substituted.
`pos`   (L_pos, paper §5.0.2)  — "are these two programs semantically equivalent?" on a
                                 (original, obfuscated) pair.  Label YES.
`neg`   (L_neg, paper §5.0.2)  — the SAME template on a pair whose semantics differ.
                                 Label NO.
`deobf` (eval only, §4.3)      — reverse: recover the original source. Never trained on;
                                 that is the entire point of the bidirectional test.

`pos` and `neg` must share one template character-for-character, or the label leaks
through the wording and neither loss measures anything semantic. `EQUIV_TEMPLATE` is
therefore built once and used by both, and `test_cft_prompts.py` asserts that the two
renderings differ only in the two code blocks.

Deviation from the paper, recorded here because it changes what the model can learn:
the paper reports no output-format constraint for the generation task. We add "output
only the code, no fences, no commentary", because an unconstrained format makes the
CodeBLEU comparison a measurement of how much prose the model wrapped around its answer.
`extract_code` still tolerates a fenced answer at eval time, and the evaluator reports
`fence_rate` so the constraint's effectiveness is visible rather than assumed.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

CFT_PROMPT_VERSION = "cft_v1"

TASKS = ("gen", "pos", "neg")  # trainable task formats; `deobf` is eval-only
ALL_FORMATS = TASKS + ("deobf",)

#: Human-readable name of each obfuscation condition, substituted into the forward
#: prompt where the paper writes "[Obfuscation Technique]" (§4.1.2). Wording is short
#: and technique-naming rather than descriptive: the paper's model is told *which*
#: transform to apply, not how to apply it.
TECHNIQUE_NAMES: dict[str, str] = {
    "L0": "normalization only (no obfuscation)",
    "L1b": "misleading variable renaming",
    "L1r": "random variable renaming",
    "L2": "identifier minification",
    "S1": "control-flow flattening",
    "S2": "dead code insertion",
}

LANGUAGE_NAMES = {"python": "Python", "javascript": "JavaScript"}

# --------------------------------------------------------------------------- #
# System prompts

GEN_SYSTEM = (
    "You are a source-to-source code transformation tool.\n"
    "You rewrite programs exactly as instructed and never change what they compute.\n"
    "Reply with the transformed program only: no explanation, no commentary, and no "
    "markdown code fences."
)

EQUIV_SYSTEM = (
    "You are a program equivalence checker.\n"
    "You are given two programs. You decide whether they compute the same result for "
    "every input.\n"
    "Reply with exactly one word: YES if they are semantically equivalent, NO if they "
    "are not. No explanation."
)

DEOBF_SYSTEM = (
    "You are a source-to-source code transformation tool.\n"
    "You are given an obfuscated program. You recover the original, readable source: "
    "meaningful names, straightforward control flow, no dead code.\n"
    "The recovered program must compute exactly what the obfuscated one computes.\n"
    "Reply with the recovered program only: no explanation, no commentary, and no "
    "markdown code fences."
)

DEOBF_COT_SYSTEM = (
    "You are a source-to-source code transformation tool.\n"
    "You are given an obfuscated program. You recover the original, readable source: "
    "meaningful names, straightforward control flow, no dead code.\n"
    "The recovered program must compute exactly what the obfuscated one computes.\n"
    "First reason step by step about what the program computes. Then give the recovered "
    "program as the last thing in your reply, inside a single fenced code block."
)

# --------------------------------------------------------------------------- #
# User templates

#: Paper §4.1.2: "Obfuscate the following Java code by [Obfuscation Technique] while
#: preserving its functionality." Language and technique are the only substitutions.
GEN_TEMPLATE = (
    "Obfuscate the following {language} code by {technique} while preserving its "
    "functionality.\n"
    "\n"
    "{code}"
)

#: ONE template for both L_pos and L_neg. See the module docstring.
EQUIV_TEMPLATE = (
    "Language: {language}\n"
    "\n"
    "Program A:\n"
    "{code_a}\n"
    "\n"
    "Program B:\n"
    "{code_b}\n"
    "\n"
    "Do Program A and Program B compute the same result for every input? Answer YES or NO."
)

DEOBF_TEMPLATE = (
    "The following {language} code has been obfuscated. Recover the original, readable "
    "source code while preserving its functionality.\n"
    "\n"
    "{code}"
)

EQUIV_YES = "YES"
EQUIV_NO = "NO"


# --------------------------------------------------------------------------- #
# Few-shot demo (reverse direction only)

@dataclass(frozen=True)
class DeobfDemo:
    """A frozen one-shot deobfuscation example for the `few_shot` reverse strategy.

    Handwritten rather than sampled from the corpus, for two reasons: a corpus demo
    would have to be re-checked against the eval split on every run, and a demo drawn
    from a training condition would make the few-shot arm a second dose of the same
    distribution the SFT arm was trained on, confounding the prompting comparison.
    `program_id` is namespaced so `assert_demo_disjoint`-style checks can spot it.
    """

    program_id: str
    language: str
    obfuscated: str
    original: str


_PY_DEMO_OBF = """def f_2b71(v_9c04):
    v_31aa = 0
    for v_c7e2 in v_9c04:
        if v_c7e2 % 2 == 0:
            v_31aa = v_31aa + v_c7e2
    return v_31aa"""

_PY_DEMO_ORIG = """def sum_even(numbers):
    total = 0
    for n in numbers:
        if n % 2 == 0:
            total = total + n
    return total"""

_JS_DEMO_OBF = """function f_2b71(v_9c04) {
    let v_31aa = 0;
    for (const v_c7e2 of v_9c04) {
        if (v_c7e2 % 2 === 0) {
            v_31aa = v_31aa + v_c7e2;
        }
    }
    return v_31aa;
}"""

_JS_DEMO_ORIG = """function sumEven(numbers) {
    let total = 0;
    for (const n of numbers) {
        if (n % 2 === 0) {
            total = total + n;
        }
    }
    return total;
}"""

DEOBF_DEMOS: dict[str, DeobfDemo] = {
    "python": DeobfDemo("cft_demo_sum_even_py", "python", _PY_DEMO_OBF, _PY_DEMO_ORIG),
    "javascript": DeobfDemo("cft_demo_sum_even_js", "javascript", _JS_DEMO_OBF, _JS_DEMO_ORIG),
}

#: Reverse-direction prompting strategies. The paper evaluates four (§4.3.2: simple,
#: few-shot, chain-of-thought, augmented = CoT + few-shot) and finds ΔR ≈ 0.01–0.05
#: across all of them. We implement the same four.
DEOBF_STRATEGIES = ("simple", "few_shot", "cot", "augmented")


# --------------------------------------------------------------------------- #
# Builders

def _lang_name(language: str) -> str:
    try:
        return LANGUAGE_NAMES[language]
    except KeyError:
        raise KeyError(f"unknown language {language!r}") from None


def build_gen_messages(code: str, language: str, condition: str) -> list[dict[str, str]]:
    if condition not in TECHNIQUE_NAMES:
        raise KeyError(f"no technique name for condition {condition!r}")
    return [
        {"role": "system", "content": GEN_SYSTEM},
        {
            "role": "user",
            "content": GEN_TEMPLATE.format(
                language=_lang_name(language),
                technique=TECHNIQUE_NAMES[condition],
                code=code.rstrip("\n"),
            ),
        },
    ]


def build_equiv_messages(code_a: str, code_b: str, language: str) -> list[dict[str, str]]:
    """Used by BOTH the positive and the negative task — see the module docstring."""
    return [
        {"role": "system", "content": EQUIV_SYSTEM},
        {
            "role": "user",
            "content": EQUIV_TEMPLATE.format(
                language=_lang_name(language),
                code_a=code_a.rstrip("\n"),
                code_b=code_b.rstrip("\n"),
            ),
        },
    ]


def build_deobf_messages(
    code: str, language: str, strategy: str = "simple"
) -> list[dict[str, str]]:
    if strategy not in DEOBF_STRATEGIES:
        raise ValueError(f"unknown reverse strategy {strategy!r}; expected {DEOBF_STRATEGIES}")
    cot = strategy in ("cot", "augmented")
    few_shot = strategy in ("few_shot", "augmented")
    messages: list[dict[str, str]] = [
        {"role": "system", "content": DEOBF_COT_SYSTEM if cot else DEOBF_SYSTEM}
    ]
    if few_shot:
        demo = DEOBF_DEMOS[language]
        messages.append(
            {
                "role": "user",
                "content": DEOBF_TEMPLATE.format(
                    language=_lang_name(language), code=demo.obfuscated
                ),
            }
        )
        # The demo answer is fenced under CoT and bare otherwise, so the demo models
        # the output format the system prompt just asked for rather than fighting it.
        answer = f"```{language}\n{demo.original}\n```" if cot else demo.original
        messages.append({"role": "assistant", "content": answer})
    messages.append(
        {
            "role": "user",
            "content": DEOBF_TEMPLATE.format(
                language=_lang_name(language), code=code.rstrip("\n")
            ),
        }
    )
    return messages


def build_messages(row: Mapping[str, Any]) -> list[dict[str, str]]:
    """Dispatch on `row["task"]` — the one place the four formats are selected."""
    task = row["task"]
    if task == "gen":
        return build_gen_messages(row["code_a"], row["language"], row["condition"])
    if task in ("pos", "neg"):
        return build_equiv_messages(row["code_a"], row["code_b"], row["language"])
    if task == "deobf":
        return build_deobf_messages(
            row["code_b"], row["language"], row.get("strategy", "simple")
        )
    raise ValueError(f"unknown task {task!r}; expected one of {ALL_FORMATS}")


def completion_for(row: Mapping[str, Any]) -> str:
    """The supervised target. `deobf` has none — it is never trained on (§4.3)."""
    task = row["task"]
    if task == "gen":
        return row["code_b"].rstrip("\n")
    if task == "pos":
        return EQUIV_YES
    if task == "neg":
        return EQUIV_NO
    raise ValueError(
        f"task {task!r} has no training target. The reverse direction is deliberately "
        "never supervised — training on it would answer a different question than the "
        "paper asks (§2.3)."
    )


def build_example(row: Mapping[str, Any]) -> dict[str, list[dict[str, str]]]:
    """TRL 1.x conversational prompt-completion example (same shape as
    `obtune.prompts.build_example`, so `completion_only_loss=True` masks the prompt)."""
    return {
        "prompt": build_messages(row),
        "completion": [{"role": "assistant", "content": completion_for(row)}],
    }


# --------------------------------------------------------------------------- #
# Output parsing

_FENCE_RE = re.compile(r"```[ \t]*([A-Za-z0-9_+-]*)[ \t]*\r?\n(.*?)(?:```|\Z)", re.DOTALL)


def extract_code(text: str) -> tuple[str, bool]:
    """Return `(code, was_fenced)` from a raw model reply.

    The generation prompts forbid fences, so an unfenced reply is used verbatim. When a
    fence is present anyway we take the LAST fenced block: under the CoT strategy the
    instruction is "the recovered program is the last thing in your reply", and a model
    that quotes the input before answering would otherwise be graded on the input.

    An unterminated final fence (a reply cut off at max_tokens) still yields its body,
    because a truncated program is a more informative datum than an empty string — the
    evaluator records truncation separately.
    """
    blocks = _FENCE_RE.findall(text)
    if blocks:
        return blocks[-1][1].strip("\n"), True
    return text.strip("\n"), False


_YES_RE = re.compile(r"\byes\b", re.IGNORECASE)
_NO_RE = re.compile(r"\bno\b", re.IGNORECASE)


def parse_equivalence(text: str) -> Optional[bool]:
    """Parse a YES/NO reply. `None` = format failure, counted, never guessed.

    Only the FIRST of the two words decides, so "NO, they are not the same — yes, the
    names differ" resolves to NO rather than to whichever token the regex met first.
    """
    y = _YES_RE.search(text)
    n = _NO_RE.search(text)
    if y and n:
        return y.start() < n.start()
    if y:
        return True
    if n:
        return False
    return None


# --------------------------------------------------------------------------- #
# Provenance

def template_sha256() -> str:
    """Hash of the prompt CONTENT, mirroring `obtune.prompts.template_sha256`.

    Recorded in every CFT run manifest and result file. Cosmetic edits to this module
    must not move it; any change to text the model reads must.
    """
    payload = {
        "version": CFT_PROMPT_VERSION,
        "gen_system": GEN_SYSTEM,
        "equiv_system": EQUIV_SYSTEM,
        "deobf_system": DEOBF_SYSTEM,
        "deobf_cot_system": DEOBF_COT_SYSTEM,
        "gen_template": GEN_TEMPLATE,
        "equiv_template": EQUIV_TEMPLATE,
        "deobf_template": DEOBF_TEMPLATE,
        "technique_names": TECHNIQUE_NAMES,
        "language_names": LANGUAGE_NAMES,
        "labels": [EQUIV_YES, EQUIV_NO],
        "demos": {
            k: [d.program_id, d.language, d.obfuscated, d.original]
            for k, d in sorted(DEOBF_DEMOS.items())
        },
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def provenance_block() -> dict[str, str]:
    return {
        "cft_prompt_version": CFT_PROMPT_VERSION,
        "cft_prompt_template_sha256": template_sha256(),
    }


def assert_demo_disjoint(eval_program_ids: Sequence[str]) -> None:
    """The reverse-direction few-shot demo must never be an eval program."""
    ids = set(eval_program_ids)
    clash = {d.program_id for d in DEOBF_DEMOS.values()} & ids
    if clash:
        raise ValueError(f"CFT deobfuscation demo(s) {sorted(clash)} appear in the eval set")
