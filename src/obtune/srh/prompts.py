"""The reverse (`rev`) TRAINING task — deliberately outside `obtune.cft.prompts`.

`cft.prompts` refuses to supervise the reverse direction, and that refusal is the
replication's whole point (§2.3 of the paper: reverse capability must *emerge*, never be
trained). Adding a trainable reverse task there would break two contract tests and
silently change what the replication claims. So it lives here, and `cft.prompts` is
imported read-only.

The one invariant that matters
------------------------------
The reverse *training* prompt is **byte-identical** to the reverse *evaluation* prompt,
`cft.prompts.build_deobf_messages(..., strategy="simple")`. Training on a different
reverse prompt than the one evaluation uses would make reverse accuracy a measurement of
prompt mismatch rather than of capability — CLAUDE.md §4.3's named silent failure, and
invisible in the loss curve. `assert_rev_matches_eval_prompt()` checks it, and
`tests/test_srh_prompts.py` runs that check on real corpus rows rather than on a fixture.

Field contract, unchanged from `CFTInstance`
--------------------------------------------
`code_a` is always the L0 original and `code_b` always the transformed program. The
`rev` task reads `code_b` as *input* and `code_a` as *target*; it does NOT swap the
fields. Swapping them would make the pool rows direction-dependent, and every downstream
consumer (`label_balance`, `pair_pos_neg`, the mutation metadata) assumes they are not.

A confound this module makes visible rather than hides
------------------------------------------------------
Forward generation is cued by `GEN_SYSTEM` ("rewrite as instructed") and reverse by
`DEOBF_SYSTEM` ("recover the original readable source") — two different personas. Under
the Shared Representation Hypothesis that has teeth: a model can hold two *disjoint*
circuits and still look perfectly bidirectional if the directions arrive under different
system prompts, which is exactly the null the mechanistic phase is meant to reject.
`SYMMETRIC_SYSTEM` + `symmetric=True` builds the `FLIP-sym` control arm, where both
directions share one system prompt and the direction is carried only by the user turn.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from obtune.cft import prompts as cft_prompts

SRH_PROMPT_VERSION = "srh_v1"

REV_TASK = "rev"
#: Trainable tasks for this experiment. `cft_prompts.TASKS` stays as it is.
TASKS = cft_prompts.TASKS + (REV_TASK,)

#: One system prompt for BOTH directions, used only by the `FLIP-sym` control arm.
#: Deliberately says nothing about which way the transformation runs — the user turn
#: carries that, so "which direction" is a property of the instruction rather than of
#: the persona.
SYMMETRIC_SYSTEM = (
    "You are a source-to-source code transformation tool.\n"
    "You rewrite programs exactly as instructed and never change what they compute.\n"
    "Reply with the resulting program only: no explanation, no commentary, and no "
    "markdown code fences."
)


def build_rev_messages(
    code_b: str, language: str, symmetric: bool = False
) -> list[dict[str, str]]:
    """The reverse training prompt. Identical to the `simple` eval prompt by delegation.

    Delegation rather than duplication is the point: if the eval prompt is ever edited,
    the training prompt moves with it and cannot silently drift.
    """
    messages = cft_prompts.build_deobf_messages(code_b, language, strategy="simple")
    if symmetric:
        messages = [
            {"role": "system", "content": SYMMETRIC_SYSTEM} if m["role"] == "system" else m
            for m in messages
        ]
    return messages


def build_fwd_messages(
    code_a: str, language: str, condition: str, symmetric: bool = False
) -> list[dict[str, str]]:
    """The forward training prompt, with the same optional symmetric-system swap."""
    messages = cft_prompts.build_gen_messages(code_a, language, condition)
    if symmetric:
        messages = [
            {"role": "system", "content": SYMMETRIC_SYSTEM} if m["role"] == "system" else m
            for m in messages
        ]
    return messages


def build_messages(row: Mapping[str, Any]) -> list[dict[str, str]]:
    """Dispatch on `row["task"]`, extending cft's four formats with `rev`."""
    symmetric = bool(row.get("symmetric", False))
    task = row["task"]
    if task == REV_TASK:
        return build_rev_messages(row["code_b"], row["language"], symmetric)
    if task == "gen" and symmetric:
        return build_fwd_messages(row["code_a"], row["language"], row["condition"], True)
    return cft_prompts.build_messages(row)


def completion_for(row: Mapping[str, Any]) -> str:
    """The supervised target. `rev` recovers the L0 original; everything else delegates."""
    if row["task"] == REV_TASK:
        return row["code_a"].rstrip("\n")
    return cft_prompts.completion_for(row)


def build_example(row: Mapping[str, Any]) -> dict[str, list[dict[str, str]]]:
    """TRL 1.x conversational prompt-completion example (same shape as cft's)."""
    return {
        "prompt": build_messages(row),
        "completion": [{"role": "assistant", "content": completion_for(row)}],
    }


def build_example_factory(symmetric: bool = False):
    """A `build_example` bound to a system-prompt style.

    `CFTInstance` has no `symmetric` field and should not grow one — whether the two
    directions share a system prompt is a property of the *arm*, not of the data. Binding
    it here keeps the pools identical across arms, so `FLIP` and `FLIP-sym` differ in
    exactly the thing under test.
    """

    def _build(row: Mapping[str, Any]) -> dict[str, list[dict[str, str]]]:
        return build_example({**row, "symmetric": symmetric})

    return _build


# --------------------------------------------------------------------------- #
# Invariants

def assert_rev_matches_eval_prompt(code_b: str, language: str) -> None:
    """The reverse training prompt must equal the reverse EVAL prompt, character for
    character. See the module docstring — this is CLAUDE.md §4.3's silent failure."""
    train = build_rev_messages(code_b, language)
    evalp = cft_prompts.build_deobf_messages(code_b, language, strategy="simple")
    if train != evalp:
        raise AssertionError(
            "the reverse TRAINING prompt has drifted from the reverse EVAL prompt; "
            "reverse accuracy would then measure prompt mismatch, not capability"
        )


def assert_replication_untouched() -> None:
    """The replication must still refuse to supervise its reverse direction.

    Cheap, and it fails loudly at import time in a training job rather than three days
    later in an analysis that quietly compared two different experiments.
    """
    if "deobf" in cft_prompts.TASKS or REV_TASK in cft_prompts.TASKS:
        raise AssertionError(
            "obtune.cft.prompts.TASKS now contains a reverse task — the replication's "
            "guarantee that its reverse direction is unsupervised has been broken"
        )
    try:
        cft_prompts.completion_for({"task": "deobf", "code_a": "x", "code_b": "y"})
    except ValueError:
        return
    raise AssertionError(
        "obtune.cft.prompts.completion_for no longer raises for the reverse direction"
    )


# --------------------------------------------------------------------------- #
# Provenance

def template_sha256() -> str:
    """Hash of what THIS module adds. `cft.prompts.template_sha256()` is unchanged and
    is recorded alongside it, so a run is pinned to both."""
    payload = {
        "version": SRH_PROMPT_VERSION,
        "rev_task": REV_TASK,
        "symmetric_system": SYMMETRIC_SYSTEM,
        "delegates_to": "cft.prompts.build_deobf_messages(strategy='simple')",
        "cft_template_sha256": cft_prompts.template_sha256(),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def provenance_block() -> dict[str, str]:
    return {
        **cft_prompts.provenance_block(),
        "srh_prompt_version": SRH_PROMPT_VERSION,
        "srh_prompt_template_sha256": template_sha256(),
    }


def assert_tasks_known(tasks: Sequence[str]) -> None:
    bad = [t for t in tasks if t not in TASKS]
    if bad:
        raise ValueError(f"unknown task(s) {bad}; SRH trainable tasks are {list(TASKS)}")
