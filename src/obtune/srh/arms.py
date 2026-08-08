"""The Experiment-1 arm registry — one place that says what each arm IS.

Kept as data rather than as six near-identical YAML files with divergent comments,
because the whole design rests on arms differing in exactly one thing at a time and that
is far easier to audit in a table than across files. The YAML configs under
`configs/srh/train/` are thin: they name the arm and the model, and inherit everything
else.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from obtune.srh import prompts as srh_prompts


@dataclass(frozen=True)
class ArmSpec:
    name: str
    tasks: tuple[str, ...]
    #: MIX50 only — replaces forward rows rather than adding reverse ones.
    direction_mix: Optional[Mapping[str, Any]] = None
    epochs: Optional[float] = None
    #: `FLIP-sym` only — both directions share one system prompt.
    symmetric: bool = False
    role: str = ""
    reuses: Optional[str] = None  # an existing adapter this arm is identical to

    def mixture_kwargs(self) -> dict[str, Any]:
        return {"direction_mix": dict(self.direction_mix)} if self.direction_mix else {}


ARMS: dict[str, ArmSpec] = {
    "fwd": ArmSpec(
        "fwd", ("gen",), role="forward-only baseline (the paper's SFT)",
        reuses="runs/adapters_cft/<model>/<lang>/sft_r32_s17/final",
    ),
    "rev": ArmSpec(
        "rev", (srh_prompts.REV_TASK,),
        role="reverse ceiling; the kill-gate — if this is ~0, reverse is not learnable here",
    ),
    "flip": ArmSpec(
        "flip", ("gen", srh_prompts.REV_TASK),
        role="the missing baseline: reverse data is free, just swap the pair",
    ),
    "mix50": ArmSpec(
        "mix50", ("gen",),
        direction_mix={"reverse_fraction": 0.5, "disjoint_programs": True, "seed": 17},
        role=(
            "the decisive arm: matched to fwd on instances, sequence tokens and steps "
            "simultaneously, with strictly LESS supervised signal"
        ),
    ),
    "fwd2x": ArmSpec(
        "fwd2x", ("gen",), epochs=6.0,
        role="compute control — matches flip's FLOPs and steps with forward-only data",
    ),
    "cft": ArmSpec(
        "cft", ("gen", "pos", "neg"), role="the paper's contrastive objective",
        reuses="runs/adapters_cft/<model>/<lang>/cft_r32_s17/final",
    ),
    "cftflip": ArmSpec(
        "cftflip", ("gen", srh_prompts.REV_TASK, "pos", "neg"),
        role="does the objective add anything over bidirectional exposure?",
    ),
    "flipsym": ArmSpec(
        "flipsym", ("gen", srh_prompts.REV_TASK), symmetric=True,
        role=(
            "confound control: forward and reverse share one system prompt, so "
            "'two personas' cannot masquerade as 'two disjoint circuits'"
        ),
    ),
}

#: Arms that already exist as replication adapters and must NOT be retrained — doing so
#: would spend GPU-hours reproducing a run we already have, and risk a different result
#: from a different seed being read as an arm effect.
REUSED = tuple(name for name, spec in ARMS.items() if spec.reuses)


def resolve(name: str) -> ArmSpec:
    if name not in ARMS:
        raise KeyError(f"unknown arm {name!r}; known: {sorted(ARMS)}")
    return ARMS[name]


def as_config_overrides(name: str) -> dict[str, Any]:
    """The config keys this arm needs on top of `configs/srh/train/_base_srh.yaml`."""
    spec = resolve(name)
    cfg: dict[str, Any] = {"arm": spec.name, "tasks": list(spec.tasks)}
    train: dict[str, Any] = {}
    if spec.direction_mix:
        train["mixture_kwargs"] = {"direction_mix": dict(spec.direction_mix)}
    if spec.epochs is not None:
        train["epochs"] = spec.epochs
    if spec.symmetric:
        cfg["symmetric"] = True
    if train:
        cfg["train"] = train
    return cfg
