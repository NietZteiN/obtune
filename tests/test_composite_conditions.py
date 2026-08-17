"""Composite (stacked) conditions — the namespace, the chaining, and what is NOT yet checked.

Composites exist for the RouterLoRA experiment: the learned router is saturated on single
conditions (100 % route accuracy, entropy ~1e-6), so a mixture-over-experts has no headroom
there. A stacked input genuinely contains two mechanisms, which is the condition the hypothesis
predicts and which does not exist anywhere in the current corpus.

Two properties are load-bearing and both are pinned here:

  * **The ladder must be untouched.** CLAUDE.md §3.1 mandates single-transform conditions, and
    the RQ1 transfer matrix attributes a degradation to ONE mechanism. `conditions.yaml` has no
    `composite_conditions` key, so the single-transform build path never enters the composite
    branch — and `schema.Condition` stays a closed Literal so composites cannot leak into
    `TRAINABLE_CONDITIONS`, the router's 8-class head, or the matrix.
  * **The entry-point rethread.** `obf/py/flatten.py` raises `Bail("no module-level def named
    ...")` when handed a name absent from the source, so rename-then-flatten fails outright
    unless stage 2 is told the name stage 1 produced. `rename_map` is old -> new and contains
    the entry point, so the new name is read rather than guessed. If this regresses,
    `C_L1r_S1` silently drops to zero coverage.
"""
from __future__ import annotations

import typing
from pathlib import Path

import pytest

from obtune.config import PROJECT_ROOT, load_config
from obtune.obf.base import Bail, make_ctx
from obtune.obf.builder import _params_for, load_composite_transform
from obtune.paths import iter_jsonl
from obtune.schema import AnyCondition, CompositeCondition, Condition

BASE_DIR = PROJECT_ROOT / "data" / "eval" / "testset" / "base"

pytestmark = pytest.mark.skipif(not BASE_DIR.exists(), reason="corpus not present")


@pytest.fixture(scope="module")
def cfg() -> dict:
    return load_config("conditions_composite.yaml")


@pytest.fixture(scope="module")
def programs() -> list:
    from obtune.schema import BaseProgram

    out = []
    for p in sorted(BASE_DIR.glob("*.jsonl")):
        for row in iter_jsonl(p):
            b = BaseProgram.model_validate(row)
            if b.language == "python":
                out.append(b)
    return out


def _apply(cfg: dict, code: str, prog):
    spec = cfg["composite_conditions"][code]
    fn = load_composite_transform("python", spec["parts"], cfg)
    assert fn is not None, f"{code}: transforms did not resolve"
    ctx = make_ctx("python", prog.program_id, code, prog.code, prog.entry_point,
                   attempt=0, seed=17, params=_params_for(spec))
    return fn(ctx)


# --------------------------------------------------------------------------- #
# the ladder must not move


def test_condition_literal_stays_closed() -> None:
    """Composites must NOT be members of `Condition`."""
    ladder = set(typing.get_args(Condition))
    comps = set(typing.get_args(CompositeCondition))
    assert ladder == {"L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4", "H1"}
    assert not (ladder & comps), "a composite leaked into the ladder Literal"
    # get_args on a Union of Literals yields the two Literal TYPES, not their members —
    # flatten one level before comparing.
    flat = {v for arg in typing.get_args(AnyCondition) for v in typing.get_args(arg)}
    assert comps <= flat and ladder <= flat


def test_composites_are_not_trainable_ladder_conditions() -> None:
    from obtune.paths import ALL_CONDITIONS, TRAINABLE_CONDITIONS

    comps = set(typing.get_args(CompositeCondition))
    assert not (comps & set(TRAINABLE_CONDITIONS))
    assert not (comps & set(ALL_CONDITIONS))


def test_plain_conditions_yaml_has_no_composite_key() -> None:
    """This is what makes the single-transform build path provably unchanged."""
    assert "composite_conditions" not in load_config("conditions.yaml")


def test_every_composite_part_is_a_ladder_condition(cfg: dict) -> None:
    """A composite of a composite, or of H1, must be impossible."""
    from obtune.paths import TRAINABLE_CONDITIONS

    for code, spec in cfg["composite_conditions"].items():
        parts = spec["parts"]
        assert len(parts) >= 2, f"{code}: not a composite"
        for part in parts:
            assert part in TRAINABLE_CONDITIONS, f"{code}: part {part!r} is not trainable"


# --------------------------------------------------------------------------- #
# chaining


def test_entry_point_rethreads_when_the_rename_comes_first(cfg: dict, programs) -> None:
    """`C_L1r_S1`: stage 2 must be handed the name stage 1 produced, or flatten Bails."""
    applied = 0
    for prog in programs[:12]:
        try:
            res = _apply(cfg, "C_L1r_S1", prog)
        except Bail:
            continue
        if not res.applied:
            continue
        applied += 1
        st = res.extra["stages"]
        assert st[0]["entry_in"] == prog.entry_point
        assert st[0]["entry_out"] != prog.entry_point, "the rename stage did not rename the entry"
        assert st[1]["entry_in"] == st[0]["entry_out"], "stage 2 got the STALE entry point"
        assert res.extra["entry_point_new"] in res.src_out
    assert applied >= 5, f"only {applied} programs applied — the rethread is likely broken"


def test_order_matters(cfg: dict, programs) -> None:
    """Composition does not commute, so the two orderings must differ."""
    prog = programs[0]
    a, b = _apply(cfg, "C_L1r_S1", prog), _apply(cfg, "C_S1_L1r", prog)
    if a.applied and b.applied:
        assert a.src_out != b.src_out, "C_L1r_S1 and C_S1_L1r produced identical output"


def test_composite_differs_from_each_of_its_parts(cfg: dict, programs) -> None:
    """A composite that equals one part would be a silently degenerate condition."""
    from obtune.obf.builder import load_transform

    prog = programs[0]
    comp = _apply(cfg, "C_S4_S3", prog)
    assert comp.applied
    for part in ("S4", "S3"):
        fn = load_transform("python", part)
        single = fn(make_ctx("python", prog.program_id, part, prog.code, prog.entry_point,
                             attempt=0, seed=17,
                             params=_params_for((load_config("conditions.yaml")
                                                 .get("conditions") or {}).get(part, {}))))
        assert comp.src_out != single.src_out, f"C_S4_S3 collapsed to {part} alone"


def test_a_failed_stage_does_not_half_apply(cfg: dict, programs) -> None:
    """If either stage declines, the result must be the untouched input, not a partial."""
    for prog in programs[:20]:
        try:
            res = _apply(cfg, "C_L1r_S1", prog)
        except Bail:
            continue
        if not res.applied:
            assert res.src_out == prog.code, "a declined composite returned partial output"
            return


# --------------------------------------------------------------------------- #
# mechanism verification — composites are semantics-verified for free, not mechanism-verified


def _variant(cfg: dict, code: str, prog):
    from obtune.schema import Variant

    res = _apply(cfg, code, prog)
    assert res.applied, f"{code} did not apply to {prog.program_id}"
    return Variant(program_id=prog.program_id, condition=code, language="python",
                   code=res.src_out, entry_point=res.extra["entry_point_new"],
                   entry_point_parent=prog.entry_point, rename_map=res.rename_map,
                   transform_meta={"parts": list(cfg["composite_conditions"][code]["parts"])},
                   gate={})


def test_purity_runs_for_composites_and_names_both_mechanisms(cfg: dict, programs) -> None:
    """Was pinned as a known gap; `_purity_composite` closed it, so this is now positive.

    `C_S4_S3` is the case that forced the design: S4's own invariant set requires that no
    uncalled def was added and S3's requires that no opaque guard was — so running both
    constituents' `_purity` unmodified is UNSATISFIABLE. Only the positive mechanism
    invariants compose, and both must be present and passing.
    """
    from obtune.obf.validate import gate

    checks = gate(programs[0], _variant(cfg, "C_S4_S3", programs[0]), cfg).checks
    assert checks.get("exec_parity") is True
    assert checks.get("purity_composite_S4_opaque_guard") is True
    assert checks.get("purity_composite_S3_dead_helper") is True
    # The relaxation is recorded in the gate, not just in a comment.
    assert "purity_composite_relaxed" in checks


def test_composite_purity_rejects_a_stage_that_no_opped(cfg: dict, programs) -> None:
    """The failure this exists to catch: a second stage that silently did nothing.

    Label the plain `L1r` output as `C_L1r_S1`. Semantics still hold — it IS a valid
    variant — so `exec_parity` passes and the old vacuous purity would have accepted it
    into the corpus under a composite label carrying Part III's entire claim.
    """
    from obtune.obf.validate import gate
    from obtune.schema import Variant

    from obtune.obf.builder import load_transform

    prog = programs[0]
    spec = cfg["conditions"]["L1r"]
    fn = load_transform("python", "L1r")
    ctx = make_ctx("python", prog.program_id, "L1r", prog.code, prog.entry_point,
                   attempt=0, seed=17, params=dict(spec.get("params") or {}))
    res = fn(ctx)
    assert res.applied
    mislabelled = Variant(program_id=prog.program_id, condition="C_L1r_S1", language="python",
                          code=res.src_out, entry_point=res.extra["entry_point_new"],
                          entry_point_parent=prog.entry_point, rename_map=res.rename_map,
                          transform_meta={"parts": ["L1r", "S1"]}, gate={})
    verdict = gate(prog, mislabelled, cfg)
    assert verdict.ok is False
    assert verdict.checks.get("purity_composite_S1_dispatch_loop") is False


def test_composite_h1_content_scan_is_not_skipped(cfg: dict, programs) -> None:
    """Resolving the spec from `conditions` alone left `trainable` falsy for composites,
    which skipped the H1 marker scan for exactly the new arm — silently."""
    from obtune.obf import validate as V

    seen: list[str] = []
    orig = V._h1_markers
    V._h1_markers = lambda pats, code: (seen.append(code[:1]), orig(pats, code))[1]
    try:
        V.gate(programs[0], _variant(cfg, "C_L1r_S1", programs[0]), cfg)
    finally:
        V._h1_markers = orig
    assert seen, "H1 marker scan never ran for a trainable composite"
