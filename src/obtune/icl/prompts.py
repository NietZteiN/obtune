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
) -> list[dict[str, str]]:
    """The chat message list for a k-shot prompt, k = len(demos).

    Demos are laid out as alternating user/assistant turns in order, exactly as the
    one-shot path does, then the query as the final user turn.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": prompts.SYSTEM_PROMPT}]
    for d in demos:
        messages.append({
            "role": "user",
            "content": prompts.build_user_content(
                d.code, d.entry_point, d.args_repr, d.language,
                # Matches build_prompt: when the oracle line is on, a demo carries its own
                # truthful condition description so both user turns have the same shape.
                condition=d.condition, oracle=oracle,
            ),
        })
        messages.append({"role": "assistant", "content": d.output_repr})
    messages.append({
        "role": "user",
        "content": prompts.build_user_content(
            code, entry_point, args_repr, language, condition=condition, oracle=oracle
        ),
    })
    return messages
