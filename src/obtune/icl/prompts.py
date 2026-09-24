"""Multi-demonstration prompt assembly for the ICL baseline.

WHY THIS IS NOT IN `obtune/prompts.py`
--------------------------------------
`prompts.py` is frozen: its template sha256 is pinned in every run manifest, so every
adapter and every eval cell in the project is tied to its exact bytes. Adding a `demos:
list` parameter there would change nothing about the rendered k=1 prompt but would still
invalidate the pin. `cft/prompts.py`, `srh/prompts.py` and `trace/prompts.py` are the
established precedent for adding a task format alongside it rather than inside it.

THE CONTRACT THAT KEEPS THE SWEEP INTERPRETABLE
-----------------------------------------------
`build_icl_prompt(..., demos=[d])` must be **byte-identical** to
`prompts.build_prompt(..., one_shot=True, demo=d)`, and `demos=[]` byte-identical to
`one_shot=False`. Without that, the k-sweep would confound "more demonstrations" with "a
different prompt format", and the k=1 column would not be comparable to the k=1 cells
already collected. `tests/test_icl_prompts.py` asserts both, and asserts the frozen
template hash is unchanged.

So this module composes `prompts.build_user_content` — the same helper `build_prompt` uses —
rather than reimplementing any formatting.
"""
from __future__ import annotations

from typing import Optional, Sequence

from obtune import prompts
from obtune.prompts import Demo


def build_icl_prompt(
    code: str,
    entry_point: str,
    args_repr: str,
    language: str,
    condition: Optional[str] = None,
    oracle: bool = False,
    demos: Sequence[Demo] = (),
    task: str = "output",
    output_repr: Optional[str] = None,
) -> list[dict[str, str]]:
    """The chat message list for a k-shot prompt, k = len(demos).

    Demos are laid out as alternating user/assistant turns in order, exactly as the
    one-shot path does, then the query as the final user turn.

    `task="input"` is the BACKWARD form (2026-09-24, A2's missing ICL column): each demo
    shows program + return value and answers with its call, and the query carries
    `output_repr`. Same contract as forward -- at k=1 it is byte-identical to
    `prompts.build_prompt(task="input", one_shot=True, demo=d)`, pinned in the tests.
    """
    inverse = task == "input"
    if inverse and output_repr is None:
        raise ValueError("task='input' needs the query's output_repr")
    system = prompts.SYSTEM_PROMPT_INVERSE if inverse else prompts.SYSTEM_PROMPT
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for d in demos:
        messages.append({
            "role": "user",
            "content": prompts.build_user_content(
                d.code, d.entry_point, d.args_repr, d.language,
                # Matches build_prompt: when the oracle line is on, a demo carries its own
                # truthful condition description so both user turns have the same shape.
                condition=d.condition, oracle=oracle,
                **({"task": task, "output_repr": d.output_repr} if inverse else {}),
            ),
        })
        messages.append({"role": "assistant",
                         "content": (prompts.format_call(d.entry_point, d.args_repr)
                                     if inverse else d.output_repr)})
    messages.append({
        "role": "user",
        "content": prompts.build_user_content(
            code, entry_point, args_repr, language, condition=condition, oracle=oracle,
            **({"task": task, "output_repr": output_repr} if inverse else {}),
        ),
    })
    return messages
