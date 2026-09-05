"""X1 — the trainable sibling of H1 — must (1) preserve semantics on every fixture that
crosses the site bar, (2) never emit an H1 marker, (3) carry its own purity invariants,
and (4) be reproducible from its recorded seed. Uses the shared Python fixtures."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.obf.base import Bail, make_ctx  # noqa: E402
from obtune.obf.builder import _params_for, load_transform  # noqa: E402
from obtune.obf.py import x1  # noqa: E402
from obtune.obf.validate import gate  # noqa: E402
from obtune.schema import Variant  # noqa: E402

from test_transforms_py import CFG, FIXTURES, programs  # noqa: E402,F401  (fixture re-export)

SPEC = CFG["conditions"]["X1"]


def _x1(program):
    fn = load_transform("python", "X1")
    assert fn is not None
    ctx = make_ctx("python", program.program_id, "X1", program.code, program.entry_point,
                   params=_params_for(SPEC))
    return fn(ctx)


def test_spec_is_trainable_encoding_family():
    assert SPEC["trainable"] is True
    assert SPEC["family"] == "encoding"
    assert "X1" in CFG["conditions"]


def test_identities_hold():
    x1.verify_identities(trials=5000, seed=3)


@pytest.mark.parametrize("pid", [f[0] for f in FIXTURES])
def test_x1_passes_gate_or_bails_with_reason(programs, pid):
    program = programs[pid]
    try:
        result = _x1(program)
    except Bail as exc:
        assert "too few X1 sites" in str(exc) or "does not compile" in str(exc), str(exc)
        return
    assert result.applied and result.src_out != program.code
    variant = Variant(program_id=pid, condition="X1", language="python", code=result.src_out,
                      entry_point=program.entry_point, entry_point_parent=program.entry_point)
    verdict = gate(program, variant, CFG)
    assert verdict.ok, (
        f"{pid}/X1 failed: {[k for k, v in verdict.checks.items() if not v]} "
        f"{verdict.mismatch_details}\n{result.src_out}"
    )
    assert verdict.checks["h1_markers_absent"] is True
    assert verdict.checks["purity_x1_mechanism_present"] is True
    assert result.extra["n_mba_sites"] + result.extra["n_encoded_strings"] >= 3


def test_no_h1_marker_in_helper_prelude_or_output(programs):
    pats = CFG["h1_marker_patterns"]
    assert not [p for p in pats if re.search(p, x1.HELPERS_SRC)]
    for program in programs.values():
        try:
            out = _x1(program).src_out
        except Bail:
            continue
        assert not [p for p in pats if re.search(p, out)], program.program_id


def test_x1_encoding_differs_from_h1_family_surface(programs):
    """Not a clone: no base64 alphabet decoder, no `_dec`, no `__mba_` — by construction."""
    out = _x1(programs["fx_self_naming_strings"]).src_out
    assert "_dec(" not in out and "__mba_" not in out and "b64" not in out
    assert "_rs([" in out and "_ar_p(" in out


def test_x1_is_reproducible_from_seed(programs):
    program = programs["fx_dict_keys"]
    assert _x1(program).src_out == _x1(program).src_out


def test_x1_bails_when_helper_name_is_taken():
    src = "def f(x):\n    _rs = x + 1\n    return _rs + 2\n"
    ctx = make_ctx("python", "p", "X1", src, "f", params={"min_total_sites": 1})
    with pytest.raises(Bail, match="helper name"):
        x1.transform(ctx)


def test_purity_rejects_identity_labelled_x1(programs):
    program = programs["fx_dict_keys"]
    fake = Variant(program_id=program.program_id, condition="X1", language="python",
                   code=program.code + "\n", entry_point=program.entry_point,
                   entry_point_parent=program.entry_point)
    verdict = gate(program, fake, CFG)
    assert not verdict.ok
    assert verdict.checks.get("purity_x1_helpers_defined") is False


def test_x1_not_registered_for_javascript():
    assert load_transform("javascript", "X1") is None
