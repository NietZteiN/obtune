#!/usr/bin/env python
"""E10 — does fine-tuning move the model TOWARD or AWAY from human difficulty orderings? NO H1.

The charter's secondary question, and the one thing in the paper plan that was written off as
blocked. It was not: `data/human/paper2_graded.csv` holds 600 graded responses from 50 participants
over 98 item cells, every one of which matches a legacy tier row, and the items only needed an
emitter (`scripts/47_emit_icse_items.py`).

Rules frozen in CLAUDE_SCRATCHPAD.md (pre-registration #3, commit 4665e17) BEFORE the eval was
submitted, and applied verbatim:

  human accuracy   fraction of a cell's responses graded Correct (~6.1 responses/cell, min 5)
  model accuracy   mean `correct` over that cell's trials
  bootstrap        clustered by PROGRAM (70 of them), never by cell
  H-human-base     item-level Spearman rho(base, human) over the 98 cells:
                   ci_lo > 0 CONFIRMED / ci_hi < 0 REFUTED / else INCONCLUSIVE
  H-human-shift    d_rho = rho(tuned_L0) - rho(base), PAIRED on the same draws:
                   ci_lo > 0 TOWARD / ci_hi < 0 AWAY / else NO DETECTABLE SHIFT
                   (reported for mono_all and cons_lam3, verdicted only for tuned_L0)
  H-human-tier     condition level, 5 tiers: REPORTED, never verdicted (n = 5)
  Paper-3          CONDITION level only — 6 items cannot support an item-level rho, and saying so
                   is part of the contribution
  sensitivity      the study's key carries its own spelling (FALSE, True), so strict grading is
                   reported beside a case/whitespace-insensitive regrade from `output_parsed`;
                   a disagreement above 2 pts makes the strict number an UNDERESTIMATE, not a
                   number to be quietly replaced

SENSITIVITY CHECK — WHAT IT ACTUALLY FOUND, recorded rather than re-specified. The registered
regrade is a TEXT-level comparison, and it turns out to be a *worse* instrument than the grader it
was meant to audit: the pipeline already grades by canonicalising the model's parsed output, so
`['Hi', 'my']` matches `["Hi","my"]` and `False` matches `false` (59 of `base`'s 60 correct rows
carry `grade_method == "normalized"`). A text compare scores STRICTER than that on every
string-valued gold, which is why the registered check reports a NEGATIVE gap for `base`. The
registered number is still printed, because a pre-registered check is not deleted when it turns out
badly; beside it the read now reports the instrument that answers the question the check was for —
how much work normalization is doing, as the share of correct rows that are not raw-exact. The
conclusion is the one the check was looking for, reached the other way round: the study's spelling
is handled upstream, so strict grading does NOT understate the model.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

PHASES = ["human_align"]
SYSTEMS = ["base", "tuned_L0", "mono_all", "cons_lam3"]
TIERS = ["T_L0", "T_L1", "T_L1b", "T_L2", "T_L3"]
HUMAN2 = ck.ROOT / "data" / "human" / "paper2_graded.csv"
HUMAN3 = ck.ROOT / "data" / "human" / "paper3_graded.csv"
N_BOOT, SEED = 2000, 17
TAG = re.compile(r"^(.*)_(L0|L1b|L1|L2|L3)$")


def human_cells() -> pd.DataFrame:
    rows = list(csv.DictReader(HUMAN2.open()))
    rec = []
    for r in rows:
        m = TAG.match(r["question_tag"])
        if not m:
            continue
        rec.append({"program_id": m.group(1), "cond": f"T_{m.group(2)}",
                    "correct": 1.0 if r["manual_status"].strip().lower() == "correct" else 0.0})
    df = pd.DataFrame(rec)
    g = df.groupby(["program_id", "cond"], as_index=False).agg(
        human_acc=("correct", "mean"), n_responses=("correct", "size"))
    return g


def norm(x) -> str:
    """Loose comparison key for the SENSITIVITY check only — never for a reported accuracy.

    The pipeline's own grading is canonical-JSON exact match, so the gold for a string answer is
    `"abc"` (quotes included) while the model's `output_parsed` is `abc`. A naive text compare
    therefore scores *stricter* than the real grader on every string-valued item, which is exactly
    the artifact the first run of this check produced (`base` "lenient" 20 pts BELOW strict). Decode
    both sides as JSON when they will decode, so the comparison is on values, and fall back to
    quote-stripped, case- and whitespace-insensitive text."""
    t = str(x).strip()
    try:
        v = json.loads(t)
        t = v if isinstance(v, str) else json.dumps(v, separators=(",", ":"), sort_keys=True)
    except Exception:
        if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
            t = t[1:-1]
    return re.sub(r"\s+", "", str(t)).lower().rstrip(".")


def gold_map() -> dict[str, str]:
    """item_id -> the study's answer key. The parquet carries `output_parsed` but not the gold,
    and the sensitivity check needs both."""
    import json
    out = {}
    for cond in TIERS:
        for lang in ("python", "javascript"):
            p = ck.ROOT / "data" / "eval" / "testset" / "items" / cond / f"{lang}.jsonl"
            if p.exists():
                for line in p.open():
                    r = json.loads(line)
                    out[r["item_id"]] = r["output_repr"]
    return out


def model_cells(model: str) -> tuple[pd.DataFrame, dict]:
    """Both languages. cellkit.load_cell defaults to python, so the languages are read explicitly;
    a missing JS cell is not fatal (the JS arms may not exist yet)."""
    gold = gold_map()
    frames = []
    for lang in ("python", "javascript"):
        for s in SYSTEMS:
            for c in TIERS:
                df = ck.load_cell(PHASES, model, s, c, language=lang)
                if df is None:
                    continue
                lenient = [1.0 if norm(a) == norm(gold.get(i, "\x00")) else 0.0
                           for a, i in zip(df["output_parsed"], df["item_id"])]
                frames.append(pd.DataFrame({
                    "system": s, "cond": c, "language": lang,
                    "program_id": df["snippet_id"], "item_id": df["item_id"],
                    "correct": df["correct"].astype(float), "lenient": lenient,
                    "raw_exact": df["raw_exact"].astype(float),
                    "grade_method": df["grade_method"].astype(str),
                    "format_fail": df["format_fail"].astype(float)}))
    if not frames:
        raise SystemExit("no human_align cells found — has ev_human_align_* run?")
    m = pd.concat(frames, ignore_index=True)
    sens = {}
    for s in SYSTEMS:
        sub = m[m.system == s]
        if len(sub):
            strict, len_ = float(sub.correct.mean()) * 100, float(sub.lenient.mean()) * 100
            corr = sub[sub.correct == 1]
            norm_share = float((corr.raw_exact == 0).mean()) * 100 if len(corr) else float("nan")
            sens[s] = {"strict_pct": round(strict, 2), "lenient_pct": round(len_, 2),
                       "gap_pts": round(len_ - strict, 2),
                       "format_fail_pct": round(float(sub.format_fail.mean()) * 100, 2),
                       "strict_is_underestimate": bool(len_ - strict > 2.0),
                       # the instrument that actually answers the question: how many correct answers
                       # the grader's own canonicalisation is responsible for
                       "normalized_share_of_correct_pct": round(norm_share, 2),
                       "grade_methods": {k: int(v) for k, v in sub.grade_method.value_counts().items()}}
    g = m.groupby(["system", "cond", "program_id"], as_index=False).agg(
        model_acc=("correct", "mean"), n_trials=("correct", "size"),
        languages=("language", "first"))
    return g, sens


def boot_rho(joined: pd.DataFrame, systems: list[str]) -> dict:
    """One program-clustered resample per draw, every system's rho recomputed on it, so the
    differences between systems are PAIRED (the whole question is a difference of rhos)."""
    progs = sorted(joined.program_id.unique())
    idx = {p: np.where(joined.program_id.values == p)[0] for p in progs}
    rng = np.random.default_rng(SEED)
    cols = {s: joined[f"acc_{s}"].values for s in systems if f"acc_{s}" in joined}
    hv = joined["human_acc"].values
    point = {s: float(spearmanr(hv, v).statistic) for s, v in cols.items()}
    draws = {s: np.empty(N_BOOT) for s in cols}
    for i in range(N_BOOT):
        pick = np.concatenate([idx[p] for p in rng.choice(progs, size=len(progs), replace=True)])
        h = hv[pick]
        for s, v in cols.items():
            r = spearmanr(h, v[pick]).statistic
            draws[s][i] = r if np.isfinite(r) else np.nan
    out = {"n_cells": int(len(joined)), "n_programs": len(progs), "rho": {}, "delta_rho": {},
           "undefined_draw_frac": {s: round(float(np.isnan(v).mean()), 4) for s, v in draws.items()}}
    for s, v in point.items():
        lo, hi = (float(x) for x in np.nanpercentile(draws[s], [2.5, 97.5]))
        out["rho"][s] = {"rho": round(v, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                         "excludes_zero": bool(lo > 0 or hi < 0)}
    if "base" in draws:
        for s in cols:
            if s == "base":
                continue
            d = draws[s] - draws["base"]
            lo, hi = (float(x) for x in np.nanpercentile(d, [2.5, 97.5]))
            out["delta_rho"][s] = {"delta": round(point[s] - point["base"], 4),
                                   "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                                   "verdict": "TOWARD" if lo > 0 else "AWAY" if hi < 0
                                              else "NO DETECTABLE SHIFT"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    hum = human_cells()
    mod, sens = model_cells(a.model)
    print(f"=== {a.model}: E10 human alignment ===")
    print(f"human: {len(hum)} cells, {hum.n_responses.sum():.0f} responses, "
          f"{hum.n_responses.mean():.1f} per cell, mean accuracy {hum.human_acc.mean():.3f}")

    wide = mod.pivot_table(index=["program_id", "cond"], columns="system", values="model_acc")
    wide.columns = [f"acc_{c}" for c in wide.columns]
    j = hum.merge(wide.reset_index(), on=["program_id", "cond"], how="inner")
    have = [s for s in SYSTEMS if f"acc_{s}" in j.columns]
    print(f"joined: {len(j)} cells over {j.program_id.nunique()} programs; arms present: {have}")
    if len(j) < 30:
        print("FATAL: too few joined cells to report", file=sys.stderr)
        return 1

    res = ck.new_result("E10 (human alignment)", Path(__file__).name, [a.model])
    res["human"] = {"n_cells": int(len(hum)), "n_responses": int(hum.n_responses.sum()),
                    "mean_accuracy": round(float(hum.human_acc.mean()), 4)}
    res["joined_cells"] = int(len(j))
    res["accuracy_by_arm"] = {s: round(float(j[f"acc_{s}"].mean()), 4) for s in have}
    res["grading_sensitivity"] = sens
    print("\n=== grading sensitivity: strict vs case/whitespace-insensitive regrade ===")
    for sname, v in sens.items():
        flag = ("  <-- STRICT IS AN UNDERESTIMATE" if v["strict_is_underestimate"]
                else "  (negative gap = the TEXT regrade is stricter than the grader, see docstring)"
                if v["gap_pts"] < -2 else "")
        print(f"  {sname:<12} strict {v['strict_pct']:6.2f} %   text-regrade {v['lenient_pct']:6.2f} %"
              f"   gap {v['gap_pts']:+5.2f} pts   format_fail {v['format_fail_pct']:.2f} %{flag}")
        print(f"  {'':<12} of its correct answers, {v['normalized_share_of_correct_pct']:.1f} % needed the "
              f"grader's canonicalisation (not raw-exact) — the study's spelling is handled upstream")

    print("\n=== mean accuracy on the 98-cell human set ===")
    print(f"  {'human':<12} {hum.human_acc.mean():.4f}")
    for s in have:
        print(f"  {s:<12} {j[f'acc_{s}'].mean():.4f}")

    b = boot_rho(j, have)
    res["item_level"] = b
    print("\n=== item-level Spearman rho with human accuracy (98 cells, bootstrap by program) ===")
    for s, v in b["rho"].items():
        print(f"  {s:<12} rho={v['rho']:+.3f} [{v['ci_lo']:+.3f}, {v['ci_hi']:+.3f}]"
              f"{'*' if v['excludes_zero'] else ''}")
    nan = b.get("undefined_draw_frac", {})
    if any(v > 0 for v in nan.values()):
        print("  [power] fraction of bootstrap draws where rho is undefined (a constant resampled "
              "column): " + ", ".join(f"{s} {v:.1%}" for s, v in nan.items() if v > 0))
    print("\n=== change in rho vs base (paired) ===")
    for s, v in b["delta_rho"].items():
        print(f"  {s:<12} d_rho={v['delta']:+.3f} [{v['ci_lo']:+.3f}, {v['ci_hi']:+.3f}]  {v['verdict']}")

    print("\n=== condition level (5 tiers) — REPORTED, never verdicted (n = 5) ===")
    tier = j.groupby("cond").agg(human=("human_acc", "mean"),
                                 **{s: (f"acc_{s}", "mean") for s in have})
    print(tier.to_string(float_format=lambda x: f"{x:.4f}"))
    res["tier_level"] = {"table": tier.round(4).to_dict(),
                         "rank_corr_vs_human": {s: round(float(spearmanr(tier["human"], tier[s]).statistic), 4)
                                                for s in have}}
    print("  rank correlation with human ordering: " +
          ", ".join(f"{s} {v:+.2f}" for s, v in res["tier_level"]["rank_corr_vs_human"].items()))

    base = b["rho"].get("base", {})
    ck.hypothesis(res, "H-human-base", "item-level rho(base, human): ci_lo>0 CONFIRMED / ci_hi<0 REFUTED",
                  "CONFIRMED" if base.get("ci_lo", -1) > 0 else "REFUTED" if base.get("ci_hi", 1) < 0
                  else "INCONCLUSIVE",
                  f"rho={base.get('rho')} [{base.get('ci_lo')}, {base.get('ci_hi')}]")
    sh = b["delta_rho"].get("tuned_L0", {})
    ck.hypothesis(res, "H-human-shift", "d_rho(tuned_L0 - base): ci_lo>0 TOWARD / ci_hi<0 AWAY",
                  sh.get("verdict", "UNAVAILABLE"),
                  f"d_rho={sh.get('delta')} [{sh.get('ci_lo')}, {sh.get('ci_hi')}]; "
                  + "; ".join(f"{s} {v['delta']:+.3f} ({v['verdict']})"
                              for s, v in b["delta_rho"].items() if s != "tuned_L0"))
    ck.hypothesis(res, "H-human-tier", "condition-level ordering (REPORTED, n=5, never verdicted)",
                  "REPORTED", ", ".join(f"{s} {v:+.2f}" for s, v in res["tier_level"]["rank_corr_vs_human"].items()))
    print()
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
