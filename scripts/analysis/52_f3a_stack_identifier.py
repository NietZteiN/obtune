#!/usr/bin/env python
"""F3a — does breadth's advantage on a deep stack depend on an IDENTIFIER transform being in it?

    python scripts/analysis/52_f3a_stack_identifier.py

THE HYPOTHESIS (H-stack-identifier, opened 2026-09-07). RQ2's claim is that breadth helps on
stacks because the stack still contains a transform the breadth arm was trained on, and that the
identifier transforms are the ones carrying it. The depth-3/4 composites are a natural test: three
of the four contain `L1r`, one (`C3_S1_S3_S4`) is structural-only.

The rule as opened was "CONFIRM if structural-only stacks show no breadth gain at depth 3", and
`composite_depth_codellama7b.json` already satisfies it as written: +1.61 [-1.02, +4.31] on the
structural-only stack against +6.10, +5.17 and +3.73, all significant, on the three containing L1r.

WHY THIS SCRIPT EXISTS ANYWAY. "One interval excludes zero and another does not" is not a test of
the difference between them, and the structural-only interval reaches +4.31 -- overlapping the
significant ones. Reading the rule as written would let a difference that was never measured carry
the claim. This computes the DIFFERENCE OF DIFFERENCES directly:

    [ (mono_all - tuned_L0) on the three L1r stacks ] - [ same on C3_S1_S3_S4 ]

on one program-clustered bootstrap (2,000 resamples, seed 17), which is legitimate here because all
four composites were evaluated on the SAME 394 programs, so the two halves are paired.

The verdict this script writes is the one that goes in the paper; the original rule's verdict is
reported beside it, and they are allowed to disagree.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402
from obtune.control_relative import bootstrap_delta  # noqa: E402

MODEL = "codellama-7b"
TREAT, CONTROL = "mono_all", "tuned_L0"
N_BOOT, SEED = 2000, 17

# TWO STIMULUS SETS, ONE RULE.
#
# `depth_seen` is the original: depth-3/4 composites built entirely from SEEN transforms, three of
# which contain `L1r` and one of which is structural-only.
#
# `f2_unseen` is an OUT-OF-SAMPLE test of the same rule. F2's six composites each contain the
# unseen family, and the rule being applied -- "breadth's stack gain is larger when an identifier
# transform is present" -- was committed at 2026-09-11 19:15:53 (`acfe301`), 91 minutes BEFORE
# F2's first cell was written at 20:47. That ordering is checkable in git and is what makes this a
# test rather than a description: the hypothesis could not have been shaped by these numbers.
# `C3_L1r_S1_X1` carries BOTH an identifier and a structural transform, so it belongs to neither
# group; it is reported beside the contrast and excluded from it.
STIMULI = {
    "depth_seen": {
        "phases": ["composite_depth", "composite_generic", "rq2_generic", "x1_generic"],
        "with_id": ["C3_L1r_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4"],
        "structural": ["C3_S1_S3_S4"],
        "both": [],
    },
    "f2_unseen": {
        "phases": ["f2_divergence"],
        "with_id": ["C_L1r_X1", "C_L1r_X1m"],
        "structural": ["C_X1_S1", "C_S2_X1", "C_S1_X1s"],
        "both": ["C3_L1r_S1_X1"],
    },
}


def _by_program(df):
    out = {}
    for pid, g in df.groupby("snippet_id"):
        out[pid] = g["correct"].to_numpy(dtype=float)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stimulus", choices=sorted(STIMULI), default="depth_seen")
    a = ap.parse_args()
    spec = STIMULI[a.stimulus]
    PHASES, WITH_ID, STRUCT_ONLY = spec["phases"], spec["with_id"], spec["structural"]
    BOTH = spec["both"]

    cells = {}
    for cond in WITH_ID + STRUCT_ONLY + BOTH:
        for sysname in (TREAT, CONTROL):
            df = load_cell(PHASES, MODEL, sysname, cond)
            if df is None:
                print(f"MISSING cell: {sysname}__{cond}", file=sys.stderr)
                return 1
            cells[(sysname, cond)] = df

    # The programs every one of the eight cells shares. Doing this once, up front, is what makes
    # the two halves paired -- a per-composite intersection would let the groups rest on different
    # program sets and turn a stimulus difference into a group difference.
    progs = None
    for df in cells.values():
        s = set(df["snippet_id"])
        progs = s if progs is None else (progs & s)
    progs = sorted(progs)
    by = {k: _by_program(v) for k, v in cells.items()}

    rng = np.random.default_rng(SEED)
    idx = np.arange(len(progs))
    draws_id, draws_st, draws_dd = (np.empty(N_BOOT) for _ in range(3))

    def grp_delta(pick, conds):
        a = np.concatenate([np.concatenate([by[(TREAT, c)][progs[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([by[(CONTROL, c)][progs[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0

    for i in range(N_BOOT):
        pick = rng.choice(idx, size=len(progs), replace=True)
        draws_id[i] = grp_delta(pick, WITH_ID)
        draws_st[i] = grp_delta(pick, STRUCT_ONLY)
        draws_dd[i] = draws_id[i] - draws_st[i]

    full = np.arange(len(progs))
    pt_id, pt_st = grp_delta(full, WITH_ID), grp_delta(full, STRUCT_ONLY)

    def ci(d):
        lo, hi = (float(x) for x in np.percentile(d, [2.5, 97.5]))
        return lo, hi

    out = {
        "script": "52_f3a_stack_identifier.py",
        "stimulus": a.stimulus,
        "rule_committed": ("acfe301, 2026-09-11 19:15:53 -- before f2_divergence's first cell at "
                           "20:47, so f2_unseen is out-of-sample for this rule"),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "model": MODEL, "n_programs": len(progs),
        "n_resamples": N_BOOT, "seed": SEED,
        "groups": {"with_identifier": WITH_ID, "structural_only": STRUCT_ONLY},
        "per_composite": {},
        "pooled": {},
    }
    for cond in WITH_ID + STRUCT_ONLY + BOTH:
        # ON THE COMMON SUBSET, like the pooled rows. `bootstrap_delta` intersects only the two
        # cells it is handed, which is each composite's OWN full set -- 405 programs for
        # `C_L1r_X1` against the 287 every composite shares. Mixing the two in one table is the
        # exact confound this script's docstring warns about, and on the `depth_seen` stimulus it
        # was invisible because all four composites happened to share 394 programs anyway. On F2's
        # composites, whose coverage differs sharply, it moved `C_L1r_X1` from +2.67 to +1.48 and
        # would have printed per-composite rows that do not add up to the pooled row beneath them.
        c = bootstrap_delta(cells[(TREAT, cond)][cells[(TREAT, cond)]["snippet_id"].isin(progs)],
                            cells[(CONTROL, cond)][cells[(CONTROL, cond)]["snippet_id"].isin(progs)],
                            f"{TREAT} - {CONTROL} @ {cond}", n_resamples=N_BOOT, seed=SEED)
        out["per_composite"][cond] = c.to_dict()

    lo_i, hi_i = ci(draws_id)
    lo_s, hi_s = ci(draws_st)
    lo_d, hi_d = ci(draws_dd)
    out["pooled"] = {
        "with_identifier": {"value_pts": pt_id, "ci_lo": lo_i, "ci_hi": hi_i,
                            "excludes_zero": bool(lo_i > 0 or hi_i < 0)},
        "structural_only": {"value_pts": pt_st, "ci_lo": lo_s, "ci_hi": hi_s,
                            "excludes_zero": bool(lo_s > 0 or hi_s < 0)},
        "difference_of_differences": {"value_pts": pt_id - pt_st, "ci_lo": lo_d, "ci_hi": hi_d,
                                      "excludes_zero": bool(lo_d > 0 or hi_d < 0)},
    }

    dd = out["pooled"]["difference_of_differences"]
    # "The rule as opened" asked only that the structural-only stack show no breadth gain, and it
    # exists only for the stimulus it was written against. On the out-of-sample set there is no
    # single structural-only stack, so it is not evaluated there and the DIRECT contrast -- which
    # is the one the claim needs, and the reason this script exists -- carries the verdict alone.
    rule_as_opened = ("CONFIRMED" if not out["per_composite"]["C3_S1_S3_S4"]["excludes_zero"]
                      else "REFUTED") if "C3_S1_S3_S4" in out["per_composite"] else "N/A"
    direct = ("CONFIRMED" if dd["ci_lo"] > 0 else
              "REFUTED" if dd["ci_hi"] < 0 else "INCONCLUSIVE")
    out["hypotheses"] = [{
        "id": "H-stack-identifier",
        "rule_as_opened": "CONFIRM if structural-only stacks show no breadth gain at depth 3",
        "verdict_by_rule_as_opened": rule_as_opened,
        "rule_direct": ("CONFIRM iff [breadth gain on L1r-containing stacks] - [breadth gain on "
                        "structural-only] has ci_lo > 0"),
        "verdict_direct": direct,
        "note": ("The direct contrast is the one the claim needs. Where the two disagree, the "
                 "paper reports the direct verdict and says the rule as opened was weaker."),
    }]

    dst = (ROOT / "results" / "analysis" / "pipeline" /
           f"f3a_stack_identifier_{a.stimulus}_codellama7b.json")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))

    print(f"stimulus={a.stimulus}   programs common to every cell: {len(progs)}")
    for cond in WITH_ID + STRUCT_ONLY + BOTH:
        c = out["per_composite"][cond]
        star = "*" if c["excludes_zero"] else " "
        print(f"  {cond:18s} {c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{star}")
    p = out["pooled"]
    print(f"  {'pooled L1r stacks':18s} {p['with_identifier']['value_pts']:+6.2f} "
          f"[{p['with_identifier']['ci_lo']:+6.2f}, {p['with_identifier']['ci_hi']:+6.2f}]")
    print(f"  {'structural-only':18s} {p['structural_only']['value_pts']:+6.2f} "
          f"[{p['structural_only']['ci_lo']:+6.2f}, {p['structural_only']['ci_hi']:+6.2f}]")
    print(f"  {'DIFFERENCE':18s} {dd['value_pts']:+6.2f} [{dd['ci_lo']:+6.2f}, {dd['ci_hi']:+6.2f}]")
    print(f"\nH-stack-identifier: rule-as-opened={rule_as_opened}  direct={direct}")
    print(f"wrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
