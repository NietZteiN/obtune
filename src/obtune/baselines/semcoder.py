"""SemCoder as an external baseline (NeurIPS'24, arXiv:2406.01006).

WHY this baseline specifically. SemCoder is trained for *execution-semantics
reasoning* — output prediction is its native task, and SemCoder-S-6.7B beats
GPT-3.5-turbo on CRUXEval-O (63.9 vs 59.0), which is the same task obtune measures.
That makes it the sharpest available test of the project's question: if a model
explicitly trained to simulate execution is ALSO robust to obfuscation, then semantic
training confers invariance and our negative results are about LoRA, not about the
idea. If it degrades under obfuscation like everything else, the finding generalizes
well beyond one adapter recipe.

FAIRNESS. Running SemCoder on obtune's own bare-literal prompt would measure "SemCoder
in a foreign format" and understate it. This module reproduces its native contract
exactly, from experiments/cruxeval_prompts.py and cruxeval_utils.py in the upstream
repo:

  * the monologue prompt, with each line annotated `# [Lx]` (the form it was trained
    on), or the CoT prompt with two worked examples
  * generation stops at `[/ANSWER]`
  * the answer is the text after `[ANSWER]`, then the right-hand side of `==`
    (OutputPrediction; the left-hand side is the *input*-prediction task)

Two adaptations are forced by our stimuli and are recorded here because they are
deviations from upstream:

  1. CRUXEval always names the function `f`; our entry points are arbitrary and the
     identifier conditions RENAME them (that is the manipulation). We substitute the
     real entry point rather than rewriting programs to use `f`, which would destroy
     exactly what L1b/L1r/L2 manipulate.
  2. Upstream offsets line labels by 4 (`# [L{i+4}]`) because CRUXEval wraps code in a
     fixed preamble. Our programs have no preamble, so the offset is a parameter with
     default 0 — keeping their +4 would mislabel every line.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

#: Upstream stop sequence. Without it the model keeps generating past the answer.
STOP = ["[/ANSWER]"]

#: The monologue is a chain of reasoning before the answer, so the 64-token budget
#: obtune uses for bare literals would truncate it before `[ANSWER]` is ever emitted.
DEFAULT_MAX_TOKENS = 1024

MODELS = {
    "semcoder": "semcoder/semcoder_1030",
    "semcoder-s": "semcoder/semcoder_s_1030",
}


def _label_lines(code: str, offset: int = 0) -> str:
    """Annotate each non-blank line `# [Lx]`, the form SemCoder was trained on."""
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip():
            lines[i - 1] = f"{line} # [L{i + offset}]"
    return "\n".join(lines)


def monologue_prompt(code: str, entry_point: str, args_repr: str, line_offset: int = 0) -> str:
    """SemCoder's native execution-reasoning prompt (forward monologue)."""
    call = f"{entry_point}({_bare_args(args_repr)})"
    return (
        "Simulate the Execution: You are given a Python function and an assertion "
        "containing a function input. Complete the assertion containing the execution "
        "output corresponding to the given input in [ANSWER] and [/ANSWER] tags.\n"
        "[PYTHON]\n"
        f"{_label_lines(code, line_offset)}\n"
        f"assert {call} == ??\n"
        "[/PYTHON]\n"
        "[MONOLOGUE]\n"
    )


def cot_prompt(code: str, entry_point: str, args_repr: str) -> str:
    """SemCoder's chain-of-thought prompt, with the upstream worked example."""
    call = f"{entry_point}({_bare_args(args_repr)})"
    return (
        "You are given a Python function and an assertion containing an input to the "
        "function. Complete the assertion with a literal (no unsimplified expressions, "
        "no function calls) containing the output when executing the provided code on "
        "the given input, even if the function is incorrect or incomplete. Do NOT "
        "output any extra information. Execute the program step by step before arriving "
        "at an answer, and provide the full assertion with the correct output in "
        "[ANSWER] and [/ANSWER] tags, following the examples.\n\n"
        "[PYTHON]\n"
        "def f(s):\n"
        "    s = s + s\n"
        '    return "b" + s + "a"\n'
        'assert f("hi") == ??\n'
        "[/PYTHON]\n"
        "[THOUGHT]\n"
        "Let's execute the code step by step:\n\n"
        "1. The function f is defined, which takes a single argument s.\n"
        '2. The function is called with the argument "hi", so within the function, s is initially "hi".\n'
        '3. Inside the function, s is concatenated with itself, so s becomes "hihi".\n'
        '4. The function then returns a new string that starts with "b", followed by the '
        'value of s (which is now "hihi"), and ends with "a".\n'
        '5. The return value of the function is therefore "bhihia".\n'
        "[/THOUGHT]\n"
        "[ANSWER]\n"
        'assert f("hi") == "bhihia"\n'
        "[/ANSWER]\n\n"
        "[PYTHON]\n"
        f"{code}\n"
        f"assert {call} == ??\n"
        "[/PYTHON]\n"
        "[THOUGHT]\n"
    )


def _bare_args(args_repr: str) -> str:
    """`"(3, [1, 2])"` -> `"3, [1, 2]"`.

    obtune stores the argument tuple with its parentheses; SemCoder's template supplies
    its own, so leaving ours in would emit `f((3, [1, 2]))` — a one-argument call whose
    argument is a tuple, i.e. a different call than the gold output came from.
    """
    s = args_repr.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    # A single-argument tuple keeps its trailing comma ("(x,)"); harmless in a call
    # but noise in the prompt, so drop one trailing comma whatever the arity.
    return s[:-1].strip() if s.endswith(",") else s


_ANSWER_RE = re.compile(r"\[ANSWER\](.*?)(?:\[/ANSWER\]|$)", re.DOTALL)


def extract_answer(generation: str) -> str:
    """Recover the predicted literal, following upstream OutputPrediction exactly.

    Upstream: split on `[ANSWER]`, then take the text to the RIGHT of `==`. (The
    left-hand side is the answer for *input* prediction, a different task — taking the
    wrong side is a silent way to score zero.)
    """
    text = generation
    m = _ANSWER_RE.search(text)
    if m:
        text = m.group(1)
    text = text.replace("[/ANSWER]", "").strip()
    if "==" in text:
        text = text.split("==", 1)[1]
    # A model that restates the assertion across lines: keep the first non-empty line.
    for line in text.strip().splitlines():
        if line.strip():
            return line.strip()
    return text.strip()


@dataclass
class SemCoderSpec:
    """How to prompt and parse one SemCoder variant."""

    model_key: str = "semcoder-s"
    style: str = "monologue"  # monologue | cot
    line_offset: int = 0
    max_tokens: int = DEFAULT_MAX_TOKENS

    @property
    def hf_id(self) -> str:
        return MODELS[self.model_key]

    def build(self, code: str, entry_point: str, args_repr: str) -> str:
        if self.style == "cot":
            return cot_prompt(code, entry_point, args_repr)
        return monologue_prompt(code, entry_point, args_repr, self.line_offset)
