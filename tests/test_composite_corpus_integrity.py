"""The emitted composite corpus, checked against the artifacts rather than the builder.

`obf/validate.gate` runs at BUILD time. These tests read what actually landed on disk, which
is what training and evaluation consume. The distinction matters: an emitter that dropped a
field, mislabelled a condition, or crossed the split boundary would leave the gate's verdict
intact and the corpus wrong.

Skipped entirely when the corpus has not been built, so the suite stays green before
`p3_composites` runs.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from obtune.config import PROJECT_ROOT, load_config

COMPOSITES = ["C_L1r_S1", "C_S1_L1r", "C_L1b_S1", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
TRAIN = PROJECT_ROOT / "data" / "train"

pytestmark = pytest.mark.skipif(
    not (TRAIN / "variants" / "C_L1r_S1" / "python.jsonl").exists(),
    reason="composite corpus not built yet (p3_composites)",
)


def _rows(path: Path, limit: int | None = None):
    out = []
    with open(path) as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            if line.strip():
                out.append(json.loads(line))
    return out


@pytest.fixture(scope="module")
def cfg():
    return load_config("conditions_composite.yaml")


# --------------------------------------------------------------------------- #
# labels and provenance


@pytest.mark.parametrize("code", COMPOSITES)
def test_every_row_carries_its_own_condition_label(code: str) -> None:
    """A mislabelled variant is the one failure no downstream analysis can detect."""
    rows = _rows(TRAIN / "variants" / code / "python.jsonl", limit=200)
    assert rows, f"{code}: no rows emitted"
    bad = {r.get("condition") for r in rows} - {code}
    assert not bad, f"{code}: rows labelled {bad}"


@pytest.mark.parametrize("code", COMPOSITES)
def test_variants_actually_differ_from_their_parent(code: str) -> None:
    """`non_identity` is a gate check; verify it survived emission."""
    base = {r["program_id"]: r["code"] for r in _rows(TRAIN / "base" / "python.jsonl")}
    rows = _rows(TRAIN / "variants" / code / "python.jsonl", limit=200)
    same = [r["program_id"] for r in rows
            if r["program_id"] in base and r["code"] == base[r["program_id"]]]
    assert not same, f"{code}: {len(same)} variant(s) identical to the L0 parent, e.g. {same[:3]}"


@pytest.mark.parametrize("code", COMPOSITES)
def test_transform_meta_records_both_parts(code: str, cfg) -> None:
    parts = list(cfg["composite_conditions"][code]["parts"])
    rows = _rows(TRAIN / "variants" / code / "python.jsonl", limit=50)
    for r in rows[:10]:
        meta = r.get("transform_meta") or {}
        recorded = [str(x) for x in (meta.get("parts") or [])]
        assert recorded == parts, f"{code}: transform_meta parts {recorded} != {parts}"


# --------------------------------------------------------------------------- #
# the mechanism claim — re-verified on the emitted artifact


@pytest.mark.parametrize("code", ["C_L1r_S1", "C_S4_S3"])
def test_emitted_variants_still_pass_composite_purity(code: str, cfg) -> None:
    """Both constituents' mechanisms must be present in what was WRITTEN, not merely in
    what the builder believed it produced. `C_S4_S3` is included because it is the pair
    whose constituents' exclusion clauses contradict each other."""
    from obtune.obf.validate import _Gate, _purity_composite
    from obtune.schema import BaseProgram, Variant

    base = {r["program_id"]: r for r in _rows(TRAIN / "base" / "python.jsonl")}
    rows = _rows(TRAIN / "variants" / code / "python.jsonl", limit=400)
    random.Random(17).shuffle(rows)
    checked = 0
    for r in rows:
        parent_raw = base.get(r["program_id"])
        if parent_raw is None:
            continue
        g = _Gate()
        ok = _purity_composite(g, BaseProgram.model_validate(parent_raw),
                               Variant.model_validate(r),
                               cfg["composite_conditions"][code], cfg)
        assert ok, (f"{code}/{r['program_id']}: emitted variant fails composite purity — "
                    f"{[k for k, v in g.checks.items() if v is False]}")
        checked += 1
        if checked >= 15:
            break
    assert checked >= 5, f"{code}: only {checked} variants could be re-checked"


# --------------------------------------------------------------------------- #
# split hygiene and quarantine


@pytest.mark.parametrize("code", COMPOSITES)
def test_pairs_never_cross_the_split_boundary(code: str) -> None:
    """Splits partition by program_id, never by row (CLAUDE.md §4 silent-failure #1)."""
    splits = json.loads((PROJECT_ROOT / "data" / "splits" / "python.json").read_text())
    by_pid = {}
    for name, pids in splits.items():
        if isinstance(pids, list):
            for pid in pids:
                by_pid[pid] = name
    rows = _rows(TRAIN / "pairs" / code / "python.jsonl", limit=3000)
    assert rows, f"{code}: no pairs emitted"
    wrong = [r["program_id"] for r in rows
             if r["program_id"] in by_pid and by_pid[r["program_id"]] != r.get("split")]
    assert not wrong, f"{code}: {len(wrong)} pair(s) disagree with the split file"


@pytest.mark.parametrize("code", COMPOSITES)
def test_no_h1_anywhere_in_the_composite_pairs(code: str) -> None:
    """Composites are trainable; H1 is not. The marker scan runs in `make check`, but the
    label check belongs with the corpus that training reads."""
    rows = _rows(TRAIN / "pairs" / code / "python.jsonl", limit=3000)
    assert not [r for r in rows if r.get("condition") == "H1"]


@pytest.mark.parametrize("code", COMPOSITES)
def test_pairs_are_loadable_through_the_quarantine_entry_point(code: str) -> None:
    """`load_pairs` is the only training-data entry point; the composites must pass it with
    the narrow allowance and fail without."""
    from obtune import data, paths

    rows = data.load_pairs([code], "python", allow_composites=True)
    assert rows, f"{code}: load_pairs returned nothing"
    assert all(r.condition == code for r in rows[:50])
    with pytest.raises(paths.QuarantineViolation):
        data.load_pairs([code], "python")


def test_coverage_matrix_is_published_and_honest() -> None:
    """Coverage honesty (CLAUDE.md §4): the bail rate is published, not hidden."""
    p = PROJECT_ROOT / "data" / "manifests" / "coverage_matrix_train_composite.json"
    assert p.exists(), "composite coverage matrix was not written"
    d = json.loads(p.read_text())
    for lang, v in d.items():
        assert v["n_common"] > 0
        assert v["n_common"] <= v["n_programs"]
        # Below ~50% the composites select for short programs (plan Gate 0).
        frac = v["n_common"] / v["n_programs"]
        assert frac > 0.4, f"{lang}: composite common subset is only {frac:.0%} — Gate 0"
