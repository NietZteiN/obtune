"""The gate must be trained on the task it is scored on, and composites must not widen H1's door.

Both tests pin bugs found on 2026-08-11 by auditing code that had never run.
"""
from __future__ import annotations

import pytest

from obtune import data, paths


# --------------------------------------------------------------------------- #
# 1. train/eval task parity


def test_gate_trains_on_output_prediction_not_code_rewriting() -> None:
    """`train_mole` once built records with `cft.prompts.build_gen_messages`, whose prompt is
    *"Obfuscate the following Python code..."* with the obfuscated PROGRAM as the target —
    while `eval_mole` scores through `eval_vllm.run_cell`, whose prompt is *"You are a
    deterministic code execution engine ... Return value:"* with the RETURN VALUE as target.

    Different tasks, not different templates. The gate would have trained cleanly, converged,
    and produced a plausible accuracy answering no question at all (CLAUDE.md §4 #3).

    This asserts the record builder emits the EVAL task, by checking the artefact that
    distinguishes them: the completion is a return value, and the prompt is the execution
    engine's, not the rewriter's.
    """
    from obtune import prompts

    row = {"code": "def f(x): return x + 1", "entry_point": "f", "args_repr": "(1,)",
           "language": "python", "condition": "L1r", "output_repr": "2"}
    ex = prompts.build_example(row)

    assert list(ex) == ["prompt", "completion"]
    assert ex["completion"] == [{"role": "assistant", "content": "2"}]
    system = ex["prompt"][0]["content"]
    assert "execution engine" in system, "gate is not being trained on output prediction"
    assert "Obfuscate" not in ex["prompt"][-1]["content"], (
        "this is the code-rewriting prompt — the train/eval task mismatch has returned")


def test_measure_truncation_accepts_the_record_shape() -> None:
    """`measure_truncation` does `list(ex["prompt"]) + list(ex["completion"])`. A string
    completion would be iterated character-by-character and the rate measured on nonsense."""
    from obtune import prompts

    ex = prompts.build_example({"code": "def f(): return 1", "entry_point": "f",
                                "args_repr": "()", "language": "python",
                                "condition": "L0", "output_repr": "1"})
    assert isinstance(ex["completion"], list)
    assert all(isinstance(m, dict) and "role" in m for m in ex["completion"])


# --------------------------------------------------------------------------- #
# 2. the composite training allowance is narrow, and H1 never widens


def test_composites_are_refused_by_default() -> None:
    """Every pre-existing caller must keep the exact strictness it had."""
    with pytest.raises(paths.QuarantineViolation):
        data.load_pairs(["C_L1r_S1"], "python")


def test_allowance_covers_only_declared_trainable_composites() -> None:
    allowed = data._trainable_composites()
    assert allowed, "composite ladder declares no trainable codes — allowance is inert"
    assert all(c.startswith("C_") for c in allowed)
    assert "H1" not in allowed


def test_h1_is_refused_even_with_the_allowance_on() -> None:
    """The allowance is not a bypass. H1 is the discriminator; if it leaks the headline
    claim is dead and no analysis can recover it (CLAUDE.md §3.2)."""
    with pytest.raises(paths.QuarantineViolation):
        data.load_pairs(["H1"], "python", allow_composites=True)


def test_undeclared_composite_code_is_refused(monkeypatch) -> None:
    """A code cannot become trainable by being named at a call site — it must be declared
    in the ladder, which is what makes it gate-validated."""
    with pytest.raises(paths.QuarantineViolation):
        data.load_pairs(["C_MADE_UP"], "python", allow_composites=True)


def test_composite_containing_h1_would_be_excluded(monkeypatch) -> None:
    """Defence in depth: no composite names H1 today, but the ladder is data and could."""
    monkeypatch.setattr(
        "obtune.config.load_config",
        lambda name: {"composite_conditions": {
            "C_L1r_H1": {"parts": ["L1r", "H1"], "trainable": True},
            "C_L1r_S1": {"parts": ["L1r", "S1"], "trainable": True},
        }} if "composite" in name else {},
    )
    allowed = data._trainable_composites()
    assert "C_L1r_H1" not in allowed
    assert "C_L1r_S1" in allowed
