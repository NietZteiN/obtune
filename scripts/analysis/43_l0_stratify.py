#!/usr/bin/env python
"""E11b — WHERE on clean code does an arm's L0 cost land? 7B. NO H1.

E11 (`38_l0_cost.py`) said *which* arms pay an L0 cost. §22.6's open question is *where*: does the
cost concentrate on unusual answer formats, or on long programs? This answers it on existing cells —
no new evaluation — by joining the L0 item metadata (gold answer, program LOC) onto every L0 trial.

Rules frozen in CLAUDE_SCRATCHPAD.md (2026-09-08 pre-registration, commit e5d08ab) BEFORE this file
existed, and applied verbatim:

  strata   format class of the gold output_repr (common = a class holding >=10 % of items,
           everything else pooled as "unusual"); program-LOC terciles over the evaluated programs;
           answer-length terciles (exploratory).
  unit     primary = mono_all pooled over 3 seeds vs the pooled clean-code control
           {tuned_L0, tuned_L0_s42}. cons_lam3 (3 seeds), tuned_X1 and base reported, not verdicted.
  stat     Delta(stratum) = 100*(acc_arm - acc_ref) on that stratum. ONE program-clustered resample
           per bootstrap draw with every stratum recomputed on it, so between-stratum differences
           are paired and their intervals are valid (an unpaired difference of two independent CIs
           would be far too wide here — the same programs sit on both sides).
  H-L0-format  CONFIRMED iff Delta(unusual) - Delta(common) has ci_hi < 0
               REFUTED   iff that interval lies inside +/-1.0 (the E11 TOST margin)
               else INCONCLUSIVE
  H-L0-length  same, on Delta(T3_long) - Delta(T1_short)
  H-L0-answerlen  same statistic on answer-length terciles; REPORTED, not verdicted.

Gates nothing. A "both refuted" outcome is a finding — the cost is diffuse — not a failure.

--matched (E11c, pre-registration #2, commit 8da96b4) breaks the confound the first read could not:
"unusual format" and "easy item" are the SAME stratum on this item set (bool_none is 9.6 % of items
and the control scores 0.596 on the unusual group against 0.402 on the common one). It bins items by
the CONTROL's own per-item accuracy (0 / partial / 1 over the control's trials for that item),
compares common vs unusual WITHIN each bin, and pools the within-bin deltas weighted by the bin's
item count. The rule is TWO-SIDED this time:

  H-L0-format-matched  ci_hi < 0            CONFIRMED           (cost concentrates on unusual formats)
                       ci_lo > 0            CONFIRMED-REVERSED  (it concentrates on common formats)
                       inside +/-1.0        REFUTED             (no difference once difficulty is held)
                       otherwise            INCONCLUSIVE

E11b's rule had no branch for the reversal it found. That was a rule-design error, recorded in the
09-08 entry and corrected here rather than quietly patched into the old rule.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

ITEMS = ck.ROOT / "data" / "eval" / "heldout" / "items" / "L0" / "python.jsonl"
PHASES = ["objectives_teacher", "objectives_llama", "x1_split", "saturation",
          "objectives_generic", "x1_generic", "rq1_generic", "rq2_generic"]
CONTROL = ["tuned_L0", "tuned_L0_s42"]
UNITS = {                     # display name -> cells pooled (seed pooling per the pre-registration)
    "mono_all(3 seeds)": ["mono_all", "mono_all_s42", "mono_all_s101"],
    "cons_lam3(3 seeds)": ["cons_lam3", "cons_lam3_s42", "cons_lam3_s101"],
    "tuned_X1": ["tuned_X1"],
    "base": ["base"],
}
PRIMARY = "mono_all(3 seeds)"
COMMON_SHARE = 0.10           # a format class is "common" iff it holds >= this share of items
EQ_MARGIN = 1.0               # same TOST margin as E11
N_BOOT, SEED = 2000, 17

_INT = re.compile(r"^-?\d+$")
_FLOAT = re.compile(r"^-?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?$")


def format_class(s: str) -> str:
    """Deterministic classifier on the gold literal. Order matters and is frozen."""
    t = (s or "").strip()
    if not t:
        return "other"
    if t[0] == "[":
        return "list"
    if t[0] == "(":
        return "tuple"
    if t[0] == "{":
        return "dict_set"
    if t[0] in "\"'":
        return "str"
    if t in {"true", "false", "null", "True", "False", "None"}:
        return "bool_none"
    if _INT.match(t):
        return "int"
    if _FLOAT.match(t):
        return "float"
    return "other"


def terciles(values: pd.Series) -> pd.Series:
    """T1/T2/T3 by rank, so ties on a coarse integer scale (LOC) cannot empty a bin."""
    r = values.rank(method="first", pct=True)
    return pd.cut(r, [0, 1 / 3, 2 / 3, 1.0], labels=["T1", "T2", "T3"], include_lowest=True)


def load_items() -> pd.DataFrame:
    rows = [json.loads(line) for line in ITEMS.open()]
    df = pd.DataFrame({
        "item_id": [r["item_id"] for r in rows],
        "program_id": [r["program_id"] for r in rows],
        "fmt": [format_class(r["output_repr"]) for r in rows],
        "loc": [r.get("meta", {}).get("loc", np.nan) for r in rows],
        "answer_len": [len(r["output_repr"] or "") for r in rows],
    })
    return df


def pooled_cell(block, cells: list[str]) -> pd.DataFrame | None:
    parts = [block[c]["L0"] for c in cells if "L0" in block.get(c, {})]
    if not parts:
        return None
    got = [c for c in cells if "L0" in block.get(c, {})]
    if len(got) != len(cells):
        print(f"[warn] pooled over {got} — missing {sorted(set(cells) - set(got))}", file=sys.stderr)
    return pd.concat(parts, ignore_index=True)


def _matrix(df: pd.DataFrame, key: str, levels: list[str], progs: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """(n_programs x n_strata) sums and counts of `correct`, so a bootstrap draw is a gather+sum
    instead of 557 DataFrame concats. Pooling trials across programs, exactly as the concat form."""
    pi = {p: i for i, p in enumerate(progs)}
    li = {lv: k for k, lv in enumerate(levels)}
    S = np.zeros((len(progs), len(levels)))
    N = np.zeros((len(progs), len(levels)))
    sub = df[df["program_id"].isin(pi)]
    for (p, lv), g in sub.groupby(["program_id", key], observed=True):
        if lv in li:
            S[pi[p], li[lv]] = g["correct"].sum()
            N[pi[p], li[lv]] = len(g)
    return S, N


def analyse(arm: pd.DataFrame, ref: pd.DataFrame, key: str, levels: list[str]) -> dict:
    """Per-stratum deltas and every pairwise stratum difference, on ONE shared resample per draw."""
    progs = sorted(set(arm["program_id"]) & set(ref["program_id"]))
    aS, aN = _matrix(arm, key, levels, progs)
    bS, bN = _matrix(ref, key, levels, progs)
    rng = np.random.default_rng(SEED)

    def deltas(rows) -> np.ndarray:
        with np.errstate(invalid="ignore", divide="ignore"):
            return (aS[rows].sum(0) / aN[rows].sum(0) - bS[rows].sum(0) / bN[rows].sum(0)) * 100.0

    allrows = np.arange(len(progs))
    point = deltas(allrows)
    draws = np.empty((N_BOOT, len(levels)))
    for i in range(N_BOOT):
        draws[i] = deltas(rng.choice(allrows, size=len(progs), replace=True))
    lo, hi = np.nanpercentile(draws, [2.5, 97.5], axis=0)

    out = {"levels": levels, "n_programs": len(progs), "per_stratum": {}, "differences": {}}
    for k, lv in enumerate(levels):
        out["per_stratum"][lv] = {
            "delta_pts": round(float(point[k]), 3),
            "ci_lo": round(float(lo[k]), 3), "ci_hi": round(float(hi[k]), 3),
            "acc_arm": round(float(aS[:, k].sum() / aN[:, k].sum()), 4),
            "acc_ref": round(float(bS[:, k].sum() / bN[:, k].sum()), 4),
            "n_trials_arm": int(aN[:, k].sum())}
    for i in range(len(levels)):
        for j in range(len(levels)):
            if i >= j:
                continue
            d = draws[:, j] - draws[:, i]          # later stratum minus earlier
            dlo, dhi = (float(x) for x in np.nanpercentile(d, [2.5, 97.5]))
            out["differences"][f"{levels[j]} - {levels[i]}"] = {
                "delta_pts": round(float(point[j] - point[i]), 3),
                "ci_lo": round(dlo, 3), "ci_hi": round(dhi, 3),
                "excludes_zero": bool(dlo > 0 or dhi < 0),
                "equivalent": bool(dlo > -EQ_MARGIN and dhi < EQ_MARGIN)}
    return out


def matched_contrast(arm: pd.DataFrame, ref: pd.DataFrame) -> dict:
    """common-vs-unusual within difficulty bins, pooled. Difficulty is the CONTROL's per-item
    accuracy, so it is defined without reference to the arm being tested (using the arm's own
    accuracy would condition on the outcome and bias the contrast toward zero)."""
    diff = ref.groupby("item_id")["correct"].mean()
    bins = pd.cut(diff, [-0.01, 0.001, 0.999, 1.01], labels=["hard", "partial", "easy"])
    for df in (arm, ref):
        df["dbin"] = df["item_id"].map(bins).astype(str)
    progs = sorted(set(arm["program_id"]) & set(ref["program_id"]))
    levels = ["common", "unusual"]
    dbins = ["hard", "partial", "easy"]

    # one matrix per (difficulty bin x format group), all resampled together
    keys = [(d, f) for d in dbins for f in levels]
    def mat(df):
        pi = {p: i for i, p in enumerate(progs)}
        S = np.zeros((len(progs), len(keys))); N = np.zeros((len(progs), len(keys)))
        ki = {k: j for j, k in enumerate(keys)}
        sub = df[df["program_id"].isin(pi)]
        for (p, d, f), g in sub.groupby(["program_id", "dbin", "fmt_group"], observed=True):
            if (d, f) in ki:
                S[pi[p], ki[(d, f)]] = g["correct"].sum(); N[pi[p], ki[(d, f)]] = len(g)
        return S, N
    aS, aN = mat(arm); bS, bN = mat(ref)
    w = np.array([aN[:, j].sum() for j in range(len(keys))])

    def stat(rows) -> tuple[float, np.ndarray]:
        with np.errstate(invalid="ignore", divide="ignore"):
            d = (aS[rows].sum(0) / aN[rows].sum(0) - bS[rows].sum(0) / bN[rows].sum(0)) * 100.0
        per = {}
        num = den = 0.0
        for i, dbin in enumerate(dbins):
            c, u = d[2 * i], d[2 * i + 1]
            wt = w[2 * i] + w[2 * i + 1]
            per[dbin] = u - c
            if np.isfinite(u - c) and wt > 0:
                num += (u - c) * wt; den += wt
        return (num / den if den else np.nan), per

    allrows = np.arange(len(progs))
    point, per_point = stat(allrows)
    rng = np.random.default_rng(SEED)
    draws = np.empty(N_BOOT)
    per_draws = {b: np.empty(N_BOOT) for b in dbins}
    for i in range(N_BOOT):
        rows = rng.choice(allrows, size=len(progs), replace=True)
        draws[i], per = stat(rows)
        for b in dbins:
            per_draws[b][i] = per[b]
    lo, hi = (float(x) for x in np.nanpercentile(draws, [2.5, 97.5]))
    out = {"pooled": {"delta_pts": round(float(point), 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3),
                      "excludes_zero": bool(lo > 0 or hi < 0),
                      "equivalent": bool(lo > -EQ_MARGIN and hi < EQ_MARGIN)},
           "per_difficulty_bin": {}, "n_programs": len(progs)}
    for j, (d, f) in enumerate(keys):
        out.setdefault("cells", {})[f"{d}/{f}"] = {"n_trials_arm": int(aN[:, j].sum()),
                                                   "acc_ref": round(float(bS[:, j].sum() / bN[:, j].sum()), 4) if bN[:, j].sum() else None}
    for b in dbins:
        l2, h2 = (float(x) for x in np.nanpercentile(per_draws[b], [2.5, 97.5]))
        out["per_difficulty_bin"][b] = {"delta_pts": round(float(per_point[b]), 3),
                                        "ci_lo": round(l2, 3), "ci_hi": round(h2, 3)}
    return out


def matched_verdict(d: dict) -> str:
    if d["ci_hi"] < 0:
        return "CONFIRMED"
    if d["ci_lo"] > 0:
        return "CONFIRMED-REVERSED"
    if d["equivalent"]:
        return "REFUTED"
    return "INCONCLUSIVE"


def verdict(d: dict) -> str:
    if d["ci_hi"] < 0:
        return "CONFIRMED"
    if d["equivalent"]:
        return "REFUTED"
    return "INCONCLUSIVE"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--matched", action="store_true",
                    help="E11c: difficulty-matched format contrast (two-sided rule)")
    a = ap.parse_args()

    items = load_items()
    share = items["fmt"].value_counts(normalize=True)
    common = sorted(share[share >= COMMON_SHARE].index)
    items["fmt_group"] = np.where(items["fmt"].isin(common), "common", "unusual")
    prog_loc = items.groupby("program_id")["loc"].max()
    items["loc_bin"] = items["program_id"].map(terciles(prog_loc)).astype(str)
    items["alen_bin"] = terciles(items["answer_len"]).astype(str)

    print(f"=== {a.model}: WHERE the L0 cost lands ({len(items)} items / {items.program_id.nunique()} programs) ===")
    print("format classes: " + ", ".join(f"{k} {v:.1%}" for k, v in share.items()))
    print(f"common (>= {COMMON_SHARE:.0%}): {common}   unusual: {sorted(set(share.index) - set(common))}"
          f"   -> {(items.fmt_group == 'unusual').sum()} of {len(items)} items unusual")
    loc_edges = prog_loc.groupby(terciles(prog_loc), observed=True).agg(["min", "max", "size"])
    print(f"program LOC terciles:\n{loc_edges.to_string()}")

    cells = sorted({c for v in UNITS.values() for c in v} | set(CONTROL))
    block = ck.load_block(PHASES, a.model, cells, ["L0"], quiet=True)
    ref = pooled_cell(block, CONTROL)
    if ref is None:
        print("FATAL: no control cell", file=sys.stderr)
        return 1
    meta = items.set_index("item_id")[["program_id", "fmt", "fmt_group", "loc_bin", "alen_bin"]]

    def prep(df: pd.DataFrame) -> pd.DataFrame:
        j = df.join(meta, on="item_id", rsuffix="_m")
        miss = int(j["fmt_group"].isna().sum())
        if miss:
            print(f"[warn] {miss} trials had no item metadata and are dropped", file=sys.stderr)
        return j.dropna(subset=["fmt_group"])

    ref = prep(ref)
    res = ck.new_result("RQ1'/RQ4' (support)", Path(__file__).name, [a.model])
    res["strata"] = {"format_common": common, "format_share": {k: round(float(v), 4) for k, v in share.items()},
                     "n_items": int(len(items)), "n_unusual_items": int((items.fmt_group == "unusual").sum()),
                     "loc_terciles": {str(k): {"min": int(r["min"]), "max": int(r["max"]), "n_programs": int(r["size"])}
                                      for k, r in loc_edges.iterrows()}}
    res["units"] = {}
    KEYS = [("fmt_group", ["common", "unusual"], "answer-format"),
            ("loc_bin", ["T1", "T2", "T3"], "program LOC"),
            ("alen_bin", ["T1", "T2", "T3"], "answer length")]

    for unit, unit_cells in UNITS.items():
        arm = pooled_cell(block, unit_cells)
        if arm is None:
            print(f"[skip] {unit}: no cell", file=sys.stderr)
            continue
        arm = prep(arm)
        res["units"][unit] = {}
        print(f"\n--- {unit}  (vs pooled control {CONTROL})"
              f"  overall {(arm.correct.mean() - ref.correct.mean()) * 100:+.2f} pts")
        for key, levels, title in KEYS:
            r = analyse(arm, ref, key, levels)
            res["units"][unit][key] = r
            cells_txt = "  ".join(
                f"{lv}: {r['per_stratum'][lv]['delta_pts']:+6.2f} "
                f"[{r['per_stratum'][lv]['ci_lo']:+.2f},{r['per_stratum'][lv]['ci_hi']:+.2f}] "
                f"(ref {r['per_stratum'][lv]['acc_ref']:.3f})" for lv in levels)
            print(f"  {title:<14} {cells_txt}")
            for name, d in r["differences"].items():
                star = "*" if d["excludes_zero"] else ""
                eq = " (equiv)" if d["equivalent"] else ""
                print(f"      {name:<12} {d['delta_pts']:+6.2f} [{d['ci_lo']:+.2f}, {d['ci_hi']:+.2f}]{star}{eq}")

    if a.matched:
        print("\n=== E11c: format contrast MATCHED on the control's own per-item difficulty ===")
        for unit, unit_cells in UNITS.items():
            arm = pooled_cell(block, unit_cells)
            if arm is None:
                continue
            m = matched_contrast(prep(arm).copy(), ref.copy())
            res["units"].setdefault(unit, {})["matched_format"] = m
            pl = m["pooled"]
            star = "*" if pl["excludes_zero"] else ""
            eq = " (equiv)" if pl["equivalent"] else ""
            per = "  ".join(f"{b}: {v['delta_pts']:+.2f} [{v['ci_lo']:+.2f},{v['ci_hi']:+.2f}]"
                            for b, v in m["per_difficulty_bin"].items())
            print(f"  {unit:<20} unusual-common (pooled within difficulty) "
                  f"{pl['delta_pts']:+.2f} [{pl['ci_lo']:+.2f}, {pl['ci_hi']:+.2f}]{star}{eq}")
            print(f"  {'':<20} by bin: {per}")
        mp = res["units"][PRIMARY]["matched_format"]["pooled"]
        ck.hypothesis(res, "H-L0-format-matched",
                      "two-sided: ci_hi<0 CONFIRMED; ci_lo>0 CONFIRMED-REVERSED; inside +/-1.0 REFUTED",
                      matched_verdict(mp),
                      f"{PRIMARY}: {mp['delta_pts']:+.2f} [{mp['ci_lo']:+.2f}, {mp['ci_hi']:+.2f}]")

    p = res["units"][PRIMARY]
    fmt_d = p["fmt_group"]["differences"]["unusual - common"]
    len_d = p["loc_bin"]["differences"]["T3 - T1"]
    aln_d = p["alen_bin"]["differences"]["T3 - T1"]
    ck.hypothesis(res, "H-L0-format", "Delta(unusual)-Delta(common) ci_hi<0 CONFIRMED; inside +/-1.0 REFUTED",
                  verdict(fmt_d), f"{PRIMARY}: {fmt_d['delta_pts']:+.2f} [{fmt_d['ci_lo']:+.2f}, {fmt_d['ci_hi']:+.2f}]")
    ck.hypothesis(res, "H-L0-length", "Delta(T3_long)-Delta(T1_short) ci_hi<0 CONFIRMED; inside +/-1.0 REFUTED",
                  verdict(len_d), f"{PRIMARY}: {len_d['delta_pts']:+.2f} [{len_d['ci_lo']:+.2f}, {len_d['ci_hi']:+.2f}]")
    ck.hypothesis(res, "H-L0-answerlen", "same statistic on answer-length terciles (REPORTED, not verdicted)",
                  "REPORTED", f"{PRIMARY}: {aln_d['delta_pts']:+.2f} [{aln_d['ci_lo']:+.2f}, {aln_d['ci_hi']:+.2f}]")
    print()
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
