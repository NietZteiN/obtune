"""Lever 2b — a yes/no verifier over (program, call, candidate output).

Prompt shape: the ordinary execution prompt (prompts.build_prompt, so the verifier sees
exactly what the generator saw), the candidate appended as the assistant turn, then a
one-line user question whose answer is a single token. Score = logP("yes") - logP("no")
at the first completion position; at rerank time the highest-scoring distinct candidate
wins. Keeping the generator prompt verbatim is deliberate: the alternative (a bespoke
"is this correct?" template) would let the verifier's accuracy depend on a second prompt
distribution and confound any "the model knows more than it says" conclusion.

Candidates come only from trainable conditions (scripts/28_sample_candidates.py refuses
H1), so the verifier is never trained, selected or tuned on the held-out family.
"""
from __future__ import annotations

from typing import Any, Mapping

from obtune import prompts

VERIFIER_QUESTION = "Is the return value above exactly correct? Answer yes or no."
YES, NO = "yes", "no"
VERIFIER_VERSION = "v1"


def build_verifier_prompt(row: Mapping[str, Any], candidate: str) -> list[dict[str, str]]:
    msgs = prompts.build_prompt(
        code=row["code"], entry_point=row["entry_point"], args_repr=row["args_repr"],
        language=row.get("language", "python"), condition=row.get("condition"),
    )
    msgs.append({"role": "assistant", "content": candidate.strip() or "<empty>"})
    msgs.append({"role": "user", "content": VERIFIER_QUESTION})
    return msgs


def build_verifier_example(row: Mapping[str, Any], candidate: str, correct: bool) -> dict:
    return {
        "prompt": build_verifier_prompt(row, candidate),
        "completion": [{"role": "assistant", "content": YES if correct else NO}],
    }


def yes_no_token_ids(tokenizer) -> tuple[list[int], list[int]]:
    """First-token ids that begin 'yes'/'no' — with and without the sentencepiece space
    marker, lower and capitalised — so the score does not hinge on one tokenizer quirk."""
    def firsts(words):
        out = []
        for w in words:
            for v in (w, " " + w):
                ids = tokenizer.encode(v, add_special_tokens=False)
                if ids and ids[0] not in out:
                    out.append(ids[0])
        return out
    return firsts([YES, YES.capitalize()]), firsts([NO, NO.capitalize()])
