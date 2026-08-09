"""Control-relative transfer matrix — the memorization test (RQ1).

`transfer.py` measures each adapter against the **untuned base**. That answers "did
tuning help?" but not "did tuning on *obfuscated* code help?", because the base model
is weak at output prediction itself: any adapter gains on every condition simply by
learning the task and its answer format. The pilot made the difference concrete — an
adapter trained on clean L0 code reached the held-out obfuscator *better* (+30.3 pts)
than one trained on adversarial renaming (+27.3), so the raw gain measured task
acquisition, not invariance.

This module measures every adapter against the **L0-trained control** instead:

    Delta_ij = acc_j(tuned_i) - acc_j(tuned_L0)

and classifies each cell by its relation, because the *shape* across relations is the
hypothesis, not any single cell:

    self         i == j            the condition the adapter was trained on
    same_family  identifier {L1b,L1r,L2} or structural {S1,S2}
    cross_family different families
    held_out     j == H1           never trained on by anyone
    clean        j == L0           the control's own condition

Memorization predicts self >> same_family > cross_family ~= held_out ~= 0.
Invariance predicts Delta stays positive off-diagonal, especially onto H1.

Because "~= 0" is an acceptance of the null, each pooled class also gets a **TOST
equivalence test** against a margin derived from the control's own seed-to-seed
noise: a difference smaller than the control varies by cannot be called transfer.
Point estimates and CIs come from a cluster bootstrap over `snippet_id`, matching
transfer.py — items within a program are correlated, so resampling items would
understate the intervals.

    python -m obtune.control_relative --model Qwen2.5-Coder-1.5B --language python
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np
import pandas as pd

from obtune.config import GLOBAL_SEED, RESULTS_DIR
from obtune.transfer import load_trials

CONTROL_TRAIN_COND = "L0"
IDENTIFIER_FAMILY = ("L1b", "L1r", "L2")
STRUCTURAL_FAMILY = ("S1", "S2")
HELD_OUT = "H1"

#: Floor on the equivalence margin, in accuracy points. The margin is
#: max(MIN_EQ_MARGIN_PTS, 2 * seed-to-seed SD of the control) so it can never shrink
#: below a difference nobody would call meaningful, however quiet the seeds happen
#: to be. `held_out` uses a wider margin: its program coverage is lower (H1 applies
#: to ~73% of programs), so its interval is correspondingly wider.
MIN_EQ_MARGIN_PTS = 3.0
HELD_OUT_EQ_MARGIN_PTS = 4.0
N_BOOTSTRAP = 4000


def family_of(cond: str) -> str:
    if cond in IDENTIFIER_FAMILY:
        return "identifier"
    if cond in STRUCTURAL_FAMILY:
        return "structural"
    return cond  # L0 / H1 are their own


def relation_of(train_cond: str, eval_cond: str) -> str:
    """Relation class of a matrix cell. Order matters: held_out and clean are about
    the EVAL condition and take precedence over the family comparison."""
    if eval_cond == HELD_OUT:
        return "held_out"
    if eval_cond == CONTROL_TRAIN_COND:
        return "clean"
    if train_cond == eval_cond:
        return "self"
    return "same_family" if family_of(train_cond) == family_of(eval_cond) else "cross_family"


@dataclass
class Contrast:
    """A bootstrapped difference in accuracy points."""

    label: str
    value_pts: float
    ci_lo: float
    ci_hi: float
    n_programs: int
    n_items: int
    acc_treatment: float = 0.0
    acc_control: float = 0.0
    excludes_zero: bool = False
    equivalent: Optional[bool] = None
    eq_margin_pts: Optional[float] = None
    verdict: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in asdict(self).items()}


def _by_program(df: pd.DataFrame) -> dict[str, np.ndarray]:
    return {p: g["correct"].to_numpy() for p, g in df.groupby("snippet_id")}


def bootstrap_delta(
    treat: pd.DataFrame, control: pd.DataFrame, label: str,
    n_resamples: int = N_BOOTSTRAP, seed: int = GLOBAL_SEED,
    eq_margin: Optional[float] = None,
) -> Contrast:
    """acc(treat) - acc(control) in points, resampling PROGRAMS.

    Programs are the unit of resampling because a program contributes several
    correlated items; resampling items would produce intervals that are too narrow
    and would make an equivalence verdict unearned.
    """
    progs = sorted(set(treat["snippet_id"]) & set(control["snippet_id"]))
    if not progs:
        return Contrast(label, float("nan"), float("nan"), float("nan"), 0, 0)
    A, B = _by_program(treat), _by_program(control)
    rng = np.random.default_rng(seed)
    idx = np.arange(len(progs))
    draws = np.empty(n_resamples)
    for i in range(n_resamples):
        pick = rng.choice(idx, size=len(progs), replace=True)
        a = np.concatenate([A[progs[j]] for j in pick])
        b = np.concatenate([B[progs[j]] for j in pick])
        draws[i] = (a.mean() - b.mean()) * 100.0

    acc_t = float(np.concatenate([A[p] for p in progs]).mean())
    acc_c = float(np.concatenate([B[p] for p in progs]).mean())
    point = (acc_t - acc_c) * 100.0
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    n_items = int(sum(len(A[p]) for p in progs))

    c = Contrast(label, point, lo, hi, len(progs), n_items, acc_t, acc_c,
                 excludes_zero=bool(lo > 0 or hi < 0))
    if eq_margin is not None:
        # TOST: equivalent when the 90% interval lies inside +/- margin. The 90%
        # interval is the two-one-sided-tests interval at alpha=.05 per side.
        elo, ehi = (float(x) for x in np.percentile(draws, [5.0, 95.0]))
        c.eq_margin_pts = eq_margin
        c.equivalent = bool(elo > -eq_margin and ehi < eq_margin)
        c.verdict = _verdict(c.excludes_zero, c.equivalent, c.value_pts)
    return c


def _verdict(sig: bool, equiv: Optional[bool], value_pts: float = 0.0) -> str:
    """The 2x2 that keeps 'no effect' honest, with the SIGN carried through.

    A non-significant result is only evidence of absence when it is ALSO
    equivalent; otherwise the study was simply underpowered on that cell.

    Sign matters and was originally omitted: a significant NEGATIVE delta was
    labelled "generalizes", which reads as positive transfer when it is the
    opposite — training on obfuscated code doing measurably WORSE than the
    clean-code control.
    """
    if equiv is None:
        return "significant" if sig else "not_significant"
    if sig and not equiv:
        return "generalizes" if value_pts > 0 else "hurts"
    if not sig and equiv:
        return "null_accepted"
    if sig and equiv:
        return "trivial"
    return "inconclusive"


def control_seed_sd(df: pd.DataFrame, eval_conditions: Sequence[str]) -> float:
    """Seed-to-seed SD of the control adapter's accuracy, in points.

    This is the noise floor the equivalence margin is built from: a difference
    smaller than the control's own run-to-run variation cannot be called transfer.
    Returns 0.0 when only one control seed exists, in which case the margin falls
    back to MIN_EQ_MARGIN_PTS.
    """
    ctl = df[(df["adapter_arch"] == "per_type") & (df["train_cond"] == CONTROL_TRAIN_COND)]
    if ctl.empty or "seed" not in ctl.columns:
        return 0.0
    per = ctl.groupby(["seed", "eval_cond"])["correct"].mean().unstack()
    if per.shape[0] < 2:
        return 0.0
    cols = [c for c in eval_conditions if c in per.columns]
    return float(np.nanmean([per[c].std(ddof=1) * 100.0 for c in cols])) if cols else 0.0


def build(
    df: pd.DataFrame,
    train_conditions: Sequence[str],
    eval_conditions: Sequence[str],
    n_resamples: int = N_BOOTSTRAP,
    seed: int = GLOBAL_SEED,
) -> dict[str, Any]:
    tuned = df[df["adapter_arch"] == "per_type"]
    control_all = tuned[tuned["train_cond"] == CONTROL_TRAIN_COND]
    if control_all.empty:
        raise SystemExit(
            f"no adapter trained on {CONTROL_TRAIN_COND!r} — the control-relative matrix "
            "needs one; every Delta is measured against it"
        )

    sd_seed = control_seed_sd(df, eval_conditions)
    margin = max(MIN_EQ_MARGIN_PTS, 2.0 * sd_seed)

    # --- per-cell Delta_ij (descriptive: seed variance dominates at 2 seeds) ---- #
    cells: list[dict[str, Any]] = []
    for i in train_conditions:
        if i == CONTROL_TRAIN_COND:
            continue
        for j in eval_conditions:
            t = tuned[(tuned["train_cond"] == i) & (tuned["eval_cond"] == j)]
            c = control_all[control_all["eval_cond"] == j]
            if t.empty or c.empty:
                continue
            con = bootstrap_delta(t, c, f"{i}->{j}", n_resamples, seed)
            row = con.to_dict()
            row.update({"train_cond": i, "eval_cond": j, "relation": relation_of(i, j)})
            cells.append(row)

    # --- pooled relation classes (confirmatory: this is where the power is) ----- #
    classes: list[dict[str, Any]] = []
    for rel in ("self", "same_family", "cross_family", "held_out", "clean"):
        members = [(c["train_cond"], c["eval_cond"]) for c in cells if c["relation"] == rel]
        if not members:
            continue
        t = pd.concat([tuned[(tuned["train_cond"] == i) & (tuned["eval_cond"] == j)]
                       for i, j in members])
        # The control contributes the same eval conditions, so the comparison is
        # like-for-like on program and condition mix.
        c = pd.concat([control_all[control_all["eval_cond"] == j] for _, j in members])
        eq = HELD_OUT_EQ_MARGIN_PTS if rel == "held_out" else margin
        con = bootstrap_delta(t, c, rel, n_resamples, seed, eq_margin=eq)
        row = con.to_dict()
        row.update({"relation": rel, "n_cells": len(members)})
        classes.append(row)

    by_rel = {c["relation"]: c for c in classes}
    ordered = [by_rel[r]["value_pts"] for r in ("self", "same_family", "cross_family", "held_out")
               if r in by_rel]
    monotone = all(ordered[k] >= ordered[k + 1] for k in range(len(ordered) - 1)) if len(ordered) > 1 else None

    return {
        "control_train_cond": CONTROL_TRAIN_COND,
        "n_resamples": n_resamples,
        "seed": seed,
        "control_seed_sd_pts": round(sd_seed, 4),
        "eq_margin_pts": round(margin, 4),
        "eq_margin_held_out_pts": HELD_OUT_EQ_MARGIN_PTS,
        "relation_classes": classes,
        "cells": cells,
        "gradient_monotone": monotone,
        "invariance_index_control_relative": by_rel.get("held_out"),
        "interpretation": _interpret(by_rel, monotone),
    }


def _interpret(by_rel: dict[str, dict[str, Any]], monotone: Optional[bool]) -> str:
    ho = by_rel.get("held_out")
    self_c = by_rel.get("self")
    if not ho or not self_c:
        return "incomplete: need both a self and a held_out class"
    if ho.get("verdict") == "generalizes" and ho["value_pts"] > 0:
        return ("INVARIANCE: training on obfuscated code helps on the held-out obfuscator "
                "beyond what clean-code training gives.")
    if ho.get("verdict") == "null_accepted" and self_c.get("excludes_zero"):
        return ("MEMORIZATION: obfuscation-specific benefit is real on the trained condition "
                "but statistically equivalent to zero on the held-out obfuscator."
                + (" The gradient is monotone." if monotone else ""))
    if ho.get("verdict") == "inconclusive":
        return ("INCONCLUSIVE on the held-out condition: neither significant nor equivalent — "
                "underpowered, do not claim a null.")
    return f"held_out verdict={ho.get('verdict')}, self excludes_zero={self_c.get('excludes_zero')}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="substring of base_model")
    ap.add_argument("--language", default="python")
    ap.add_argument("--source", default=None, help="results root or trials.parquet")
    ap.add_argument("--phase", default=None)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--n-resamples", type=int, default=N_BOOTSTRAP)
    ap.add_argument("--seed", type=int, default=GLOBAL_SEED)
    ap.add_argument("--all-programs", action="store_true",
                    help="skip the all-conditions common-subset filter")
    args = ap.parse_args()

    df = load_trials(args.source, model=args.model, language=args.language, phase=args.phase)
    if df.empty:
        raise SystemExit(f"no trials for model~{args.model} language={args.language}")
    if not args.all_programs:
        # Cells must share a program set, or a class mean mixes different programs.
        per_cell = df.groupby(["adapter_arch", "train_cond", "eval_cond"], dropna=False)["snippet_id"].apply(set)
        common = set.intersection(*per_cell.tolist())
        df = df[df["snippet_id"].isin(common)]

    train_conditions = sorted(x for x in df["train_cond"].dropna().unique())
    eval_conditions = [c for c in ("L0", "L1b", "L1r", "L2", "S1", "S2", "H1")
                       if c in set(df["eval_cond"])]
    rep = build(df, train_conditions, eval_conditions, args.n_resamples, args.seed)
    rep.update({"model": args.model, "language": args.language,
                "n_trials": int(len(df)), "n_programs": int(df["snippet_id"].nunique())})

    out_dir = Path(args.out_dir) if args.out_dir else RESULTS_DIR / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"control_relative_{args.model}_{args.language}"
    (out_dir / f"{stem}.json").write_text(json.dumps(rep, indent=2))
    pd.DataFrame(rep["cells"]).to_parquet(out_dir / f"{stem}.parquet", index=False)

    print(f"model={args.model} language={args.language} "
          f"programs={rep['n_programs']} trials={rep['n_trials']}")
    print(f"control seed SD {rep['control_seed_sd_pts']} pts -> equivalence margin "
          f"{rep['eq_margin_pts']} pts ({rep['eq_margin_held_out_pts']} for held_out)\n")
    # Per-condition deltas against the L0-only control. The relation-class summary
    # below pools cells and is the confirmatory family, but pooling hides which single
    # condition carries an effect — in this project exactly one does (L1b).
    if rep.get("cells"):
        conds = [c for c in ("L0", "L1b", "L1r", "L2", "S1", "S2", "H1")
                 if any(x["eval_cond"] == c for x in rep["cells"])]
        trains = sorted({x["train_cond"] for x in rep["cells"]})
        print(f"\nDelta vs the {CONTROL_TRAIN_COND}-only control, per condition"
              " (accuracy points; * = CI excludes 0)")
        print(f"{'trained on':14}" + "".join(f"{c:>10}" for c in conds))
        for t in trains:
            row = []
            for c in conds:
                cell = next((x for x in rep["cells"]
                             if x["train_cond"] == t and x["eval_cond"] == c), None)
                row.append(
                    f"{cell['value_pts']:>9.1f}{'*' if cell['excludes_zero'] else ' '}"
                    if cell else f"{'--':>10}")
            print(f"{t:14}" + "".join(row))
        print()

    print(f"{'relation':14}{'cells':>6}{'delta':>9}{'CI95':>20}{'verdict':>16}")
    for c in rep["relation_classes"]:
        ci = f"[{c['ci_lo']:+.1f},{c['ci_hi']:+.1f}]"
        print(f"{c['relation']:14}{c['n_cells']:>6}{c['value_pts']:>+9.1f}{ci:>20}{c['verdict']:>16}")
    print(f"\nmonotone gradient: {rep['gradient_monotone']}")
    print(rep["interpretation"])
    print(f"\nwrote {out_dir / (stem + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
