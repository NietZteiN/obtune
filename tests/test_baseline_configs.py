"""The zero-training baseline configs must not write into `main`.

WHAT WENT WRONG ON 2026-08-13
-----------------------------
`main` holds two grids that CLAUDE.md says are never pooled: `base__L0` is n=1670 (Grid A,
the 557-program corpus) and `base__S3` is n=176 (Grid B, the testset). The ICL and
normalization baselines run on Grid B, and both originally declared `phase: main`.

`output.resume: true` then did exactly what it is supposed to: it saw an existing
`base__L0` cell and skipped regenerating it. So the results table ended up with
`norm_full__L0` at n=176 sitting beside `base__L0` at n=1670 — a base-vs-arm delta computed
on different programs, presented as a result. It would also have collapsed
`trial_table.compute_is_core`, which intersects programs across a whole
(phase, model, language) group.

The fix is a separate phase, so every arm in these configs — INCLUDING its own `base` —
is regenerated on exactly the items it is scored on. These tests keep it that way.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

CONFIGS = [
    "configs/eval/icl_cross_h1_qwen1.5b.yaml",
    "configs/eval/normalize_baseline_qwen1.5b.yaml",
    "configs/eval/zeroshot_7b.yaml",
]

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text())


@pytest.mark.parametrize("rel", CONFIGS)
def test_baseline_config_does_not_write_into_main(rel) -> None:
    cfg = _load(rel)
    assert cfg["phase"] != "main", (
        f"{rel} writes into `main`, where `resume: true` will silently reuse a `base` cell "
        f"built on a different grid. Give it its own phase.")
    assert cfg["phase"] == "baselines", f"{rel}: expected phase 'baselines', got {cfg['phase']!r}"


@pytest.mark.parametrize("rel", CONFIGS)
def test_declared_phase_is_accepted_by_the_trial_schema(rel) -> None:
    """`TrialRow.phase` is a CLOSED pydantic Literal, so inventing a phase name in a config
    is not a config change — it is a schema change.

    Missing that cost two GPU jobs on 2026-08-13: both loaded their model, generated a full
    cell, and only then raised `ValidationError` on the first row. Worse, neither process
    exited afterwards — they wedged in vLLM shutdown still holding ~43 GB each. A config
    that names an unrepresentable phase must fail here, in a CPU test, not after a model load.
    """
    from obtune.schema import TrialRow

    allowed = TrialRow.model_fields["phase"].annotation.__args__
    assert _load(rel)["phase"] in allowed, (
        f"{rel} declares phase {_load(rel)['phase']!r}, which TrialRow rejects; "
        f"allowed: {allowed}. Add it to the Literal in schema.py first.")


@pytest.mark.parametrize("rel", CONFIGS)
def test_baseline_config_carries_its_own_base_arm(rel) -> None:
    """A separate phase only helps if the config actually REGENERATES the floor it
    compares against. Without a `base` row there is nothing on matched items to subtract."""
    names = [s["name"] for s in _load(rel)["systems"]]
    assert "base" in names, f"{rel} has no `base` arm, so its deltas have no matched floor"


@pytest.mark.parametrize("rel", CONFIGS)
def test_baseline_arms_declare_no_adapter(rel) -> None:
    """These are the ZERO-TRAINING baselines. An adapter here would make the comparison
    something else entirely, and `assert_adapter_effective` does not run for these arms
    (it is gated on `system.adapter or system.is_routed`), so it would not be caught."""
    # `oracle_prompt` is zero-training too — it adds a hint to the PROMPT, not weights —
    # so it belongs here; anything that loads trained parameters does not.
    zero_training = {"none", "oracle_prompt"}
    for s in _load(rel)["systems"]:
        assert not s.get("adapter"), f"{rel}: system {s['name']!r} declares an adapter"
        assert s.get("arch", "none") in zero_training, (
            f"{rel}: system {s['name']!r} has arch={s.get('arch')!r}, which is not zero-training")


def test_normalize_arms_name_a_real_profile() -> None:
    from obtune.normalize import PROFILES

    for s in _load("configs/eval/normalize_baseline_qwen1.5b.yaml")["systems"]:
        if "normalize" in s:
            assert s["normalize"] in PROFILES, f"unknown profile {s['normalize']!r}"


def test_h1_is_never_an_icl_demo_source() -> None:
    """Defence in depth for CLAUDE.md §3.2 rule 2 — a demo is prompt conditioning.
    `pick_demos` also refuses at runtime; this catches it at config-review time."""
    for s in _load("configs/eval/icl_cross_h1_qwen1.5b.yaml")["systems"]:
        assert "H1" not in (s.get("icl_source") or []), f"{s['name']} sources demos from H1"
