#!/usr/bin/env python
"""Aggregate every finished eval cell into the master-report numbers.

Writes `results/analysis/master_report.json`, the single artifact behind
`docs/MASTER_REPORT_2026-08-10.md`. Run from the project root:

    python scripts/make_master_report.py

Two evaluation grids exist and must never be pooled — they are disjoint in
programs, and pooling them silently averages different populations:

  Grid A ("corpus")  base, tuned_<c>_s17/s42, mono_all/r64/r128/r192, ctl_r64,
                     oracle_prompt_1shot — on the held-out corpus split
                     (`apps_*`, `cruxeval_sample_*`): 557 py / 168 js programs,
                     all 7 conditions including H1.
  Grid B ("testset") router, the three merges, tuned_<c> (no seed suffix),
                     tuned_S3/S4 — on the ICSE test-set programs
                     (`A:…`, `B:…`): 40 py / 30 js, L0..S2 (+S3/S4, +H1 for merges).

Why the project's own `is_core` flag is not used here: it intersects over *every*
eval condition present for a (phase, model, language) group, which since the S3/S4
cells landed includes conditions covering only 40 programs — collapsing the common
subset to ~23 programs and quietly changing what earlier numbers meant. The common
subset is recomputed explicitly per grid instead, from the `base` row's coverage.

Metric: control-relative deltas (vs the L0-only adapter of the same seed and grid),
which is the corrected metric the pilot's L0 control forced (design doc §5.1).
CIs: cluster bootstrap by program (not by item — several items per program are
correlated), 2000 resamples, seed 17. BH-FDR within each delta family.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

CELLS = PROJECT_ROOT / "results" / "cells"
OUT = PROJECT_ROOT / "results" / "analysis" / "master_report.json"

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "H1"]
TRAIN = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
CONDS6 = ["L0", "L1b", "L1r", "L2", "S1", "S2"]
NBOOT, SEED = 2000, 17
MIN_DENOM_PTS = 3.0  # TR denominator guard: below this the ratio is noise/noise


def load_cells() -> pd.DataFrame:
    """One row per graded trial, labelled by the cell it came from.

    Deliberately does NOT go through `obtune.trial_table`: that collapses on a
    TRIAL_KEY without the system label, and the system label is what separates
    e.g. `tuned_L0` (Grid B) from `tuned_L0_s17` (Grid A).
    """
    frames = []
    for p in sorted(CELLS.glob("*/*/*/*/trials.parquet")):
        d = pd.read_parquet(p)
        parts = p.parts
        d["phase"] = parts[-5]
        d["system"] = parts[-2].split("__")[0]
        d["cell_path"] = str(p.parent)
        frames.append(d)
    if not frames:
        raise FileNotFoundError(f"no cell parquets under {CELLS}")
    df = pd.concat(frames, ignore_index=True)
    # ICSE test-set snippet ids are namespaced ("A:Python/101"); corpus ids are not.
    df["grid"] = np.where(df.snippet_id.str.contains(":"), "testset", "corpus")
    return df


def common(d: pd.DataFrame, conds) -> set:
    """Programs that survived every condition in `conds` — the coverage-matched subset."""
    sets = [set(d.loc[d.eval_cond == c, "snippet_id"]) for c in conds]
    return set.intersection(*sets) if sets else set()


def _by_prog(d: pd.DataFrame, progs) -> pd.DataFrame:
    return d.groupby("snippet_id")["correct"].agg(["sum", "count"]).reindex(progs).fillna(0)


def boot(d_t: pd.DataFrame, d_c: pd.DataFrame, progs) -> tuple:
    """Paired accuracy difference in points, with a cluster bootstrap CI and p."""
    progs = sorted(progs)
    t, c = _by_prog(d_t, progs), _by_prog(d_c, progs)
    if t["count"].sum() == 0 or c["count"].sum() == 0:
        return (np.nan,) * 4
    point = (t["sum"].sum() / t["count"].sum() - c["sum"].sum() / c["count"].sum()) * 100
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(progs), size=(NBOOT, len(progs)))
    ts, tn = t["sum"].to_numpy(), t["count"].to_numpy()
    cs, cn = c["sum"].to_numpy(), c["count"].to_numpy()
    draws = (ts[idx].sum(1) / np.maximum(tn[idx].sum(1), 1)
             - cs[idx].sum(1) / np.maximum(cn[idx].sum(1), 1)) * 100
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = max(2 * min((draws <= 0).mean(), (draws >= 0).mean()), 1.0 / NBOOT)
    return point, lo, hi, p


def bh(pvals) -> np.ndarray:
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.minimum.accumulate((p[order] * n / np.arange(n, 0, -1))[::-1])[::-1]
    q = np.empty(n)
    q[order] = np.minimum(adj, 1.0)
    return q


def family(sub: pd.DataFrame, systems, conds, progs, control) -> tuple[dict, pd.DataFrame]:
    """Accuracy table + control-relative deltas for one family of systems."""
    acc = {}
    for s in systems:
        acc[s] = {}
        for c in conds:
            cell = sub[(sub.system == s) & (sub.eval_cond == c)]
            acc[s][c] = round(float(cell["correct"].mean()), 4) if len(cell) else None
    rows, pv = [], []
    for s in systems:
        if s == control:
            continue
        for c in conds:
            t = sub[(sub.system == s) & (sub.eval_cond == c)]
            k = sub[(sub.system == control) & (sub.eval_cond == c)]
            if not len(t) or not len(k):
                continue
            point, lo, hi, p = boot(t, k, progs)
            rows.append(dict(system=s, eval=c, delta_pts=point, lo=lo, hi=hi, p=p))
            pv.append(p)
    d = pd.DataFrame(rows)
    if len(d):
        d["q"] = bh(pv)
        # "real" = FDR-significant AND the bootstrap interval does not straddle zero
        d["sig"] = (d.q < 0.05) & (np.sign(d.lo) == np.sign(d.hi))
    return acc, d


def main() -> int:
    df = load_cells()
    main_df = df[df.phase == "main"]
    out: dict = {}

    # ---------------------------------------------------- Grid A: RQ1 + mono + oracle
    for lang in ["python", "javascript"]:
        L = main_df[(main_df.language == lang) & (main_df.grid == "corpus")]
        progs = common(L[L.system == "base"], CONDS)
        A = L[L.snippet_id.isin(progs)]
        for tag in ["s17", "s42"]:
            systems = ["base"] + [f"tuned_{c}_{tag}" for c in TRAIN]
            # the rank sweep and the oracle-prompt arm exist at one seed only
            extras = [s for s in ["mono_all", "mono_r64", "mono_r128", "mono_r192",
                                  "ctl_r64", "oracle_prompt_1shot"] if s in set(A.system)]
            syss = systems + (extras if tag == "s17" else [])
            acc, d = family(A, syss, CONDS, progs, f"tuned_L0_{tag}")
            out[f"gridA_{lang}_{tag}"] = dict(
                n_programs=len(progs), n_trials=int(len(A[A.system.isin(syss)])),
                control=f"tuned_L0_{tag}", accuracy=acc,
                deltas=d.round(4).to_dict("records") if len(d) else [])
            if len(d):
                dd = d.set_index(["system", "eval"])["delta_pts"]
                tr = {}
                for j in CONDS:
                    den = (dd.get((f"tuned_{j}_{tag}", j), np.nan)
                           if j in TRAIN and j != "L0" else np.nan)
                    for i in TRAIN:
                        if i in ("L0", j):
                            continue
                        num = dd.get((f"tuned_{i}_{tag}", j), np.nan)
                        ok = den == den and abs(den) >= MIN_DENOM_PTS and num == num
                        tr[f"{i}->{j}"] = round(float(num / den), 3) if ok else None
                out[f"gridA_TR_{lang}_{tag}"] = tr

    # ------------------------------------------------------------- seed stability
    rows = []
    for lang in ["python", "javascript"]:
        L = main_df[(main_df.language == lang) & (main_df.grid == "corpus")]
        progs = common(L[L.system == "base"], CONDS)
        A = L[L.snippet_id.isin(progs)]
        for c in TRAIN:
            for e in CONDS:
                x = A[(A.system == f"tuned_{c}_s17") & (A.eval_cond == e)]["correct"]
                y = A[(A.system == f"tuned_{c}_s42") & (A.eval_cond == e)]["correct"]
                if len(x) and len(y):
                    rows.append(dict(language=lang, train=c, eval=e,
                                     s17=round(float(x.mean()), 4), s42=round(float(y.mean()), 4),
                                     diff_pts=round(float(y.mean() - x.mean()) * 100, 2)))
    out["seed_stability"] = rows
    ad = np.abs([r["diff_pts"] for r in rows])
    out["seed_noise"] = dict(mean_abs_pts=round(float(ad.mean()), 2),
                             median_abs_pts=round(float(np.median(ad)), 2),
                             p95_abs_pts=round(float(np.percentile(ad, 95)), 2))

    # ----------------------------------------------------------- Grid B: RQ2 + S3/S4
    for lang in ["python", "javascript"]:
        L = main_df[(main_df.language == lang) & (main_df.grid == "testset")]
        arms = [s for s in ["router", "merge_ties", "merge_dare_ties", "merge_dare_linear"]
                if s in set(L.system)]
        if not arms:
            continue
        progs = set.intersection(*[common(L[L.system == s], CONDS6) for s in arms])
        B = L[L.snippet_id.isin(progs)]
        syss = [s for s in (["base", "tuned_L0"] + [f"tuned_{c}" for c in TRAIN[1:]]
                            + ["tuned_S3", "tuned_S4"] + arms) if s in set(B.system)]
        acc, d = family(B, syss, CONDS6 + ["H1", "S3", "S4"], progs, "tuned_L0")
        out[f"gridB_{lang}"] = dict(n_programs=len(progs), control="tuned_L0", accuracy=acc,
                                    deltas=d.round(4).to_dict("records") if len(d) else [])

    # ------------------------------------------- perfect-routing ceiling (Grid A, s17)
    for lang in ["python", "javascript"]:
        L = main_df[(main_df.language == lang) & (main_df.grid == "corpus")]
        progs = common(L[L.system == "base"], CONDS)
        A = L[L.snippet_id.isin(progs)]
        ceiling = {}
        for e in CONDS6:
            t = A[(A.system == f"tuned_{e}_s17") & (A.eval_cond == e)]
            k = A[(A.system == "tuned_L0_s17") & (A.eval_cond == e)]
            if len(t) and len(k):
                point, lo, hi, _ = boot(t, k, progs)
                ceiling[e] = dict(acc=round(float(t.correct.mean()), 4),
                                  delta_pts=round(point, 2), lo=round(lo, 2), hi=round(hi, 2))
        out[f"routing_ceiling_{lang}"] = ceiling

    # --------------------------------------------------------- hygiene / provenance
    out["hygiene"] = (main_df.groupby(["language", "system"])
                      .agg(format_fail=("format_fail", "mean"), parse_ok=("parse_ok", "mean"),
                           n_trials=("correct", "size")).round(4).reset_index()
                      .to_dict("records"))
    out["h1_access"] = {f"{a}|{b}": int(v) for (a, b), v in
                        main_df[main_df.eval_cond == "H1"]
                        .groupby(["language", "h1_access_purpose"]).size().items()}
    out["inventory"] = dict(
        n_cells=int(df.cell_path.nunique()), n_trials=int(len(df)),
        phases=sorted(df.phase.unique().tolist()),
        languages=sorted(df.language.unique().tolist()),
        coverage={f"{lang}/{grid}": int(g.snippet_id.nunique())
                  for (lang, grid), g in main_df.groupby(["language", "grid"])},
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, default=str))
    print(f"wrote {OUT}  ({out['inventory']['n_cells']} cells, {out['inventory']['n_trials']} trials)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
