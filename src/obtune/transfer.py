"""RQ1 — the transfer matrix, the Transfer Ratio, and the Invariance Index.

    python -m obtune.transfer --model qwen25c-1.5b --language python

Definitions (CLAUDE.md §3, RQ1)
-------------------------------
    TR(i -> j) = (acc_j(tuned_i) - acc_j(base)) / (acc_j(tuned_j) - acc_j(base))
    Invariance Index = mean_i TR(i -> H1)

The whole result rests on three statistical decisions, each of which has a cheap wrong
answer that would inflate the headline:

1. **Denominator guard.** TR is a ratio whose denominator is itself an estimate. If
   condition j is one the base model already handles (or one nothing helps), the
   denominator is near zero and TR explodes — a 0.4-point numerator over a 0.2-point
   denominator is "TR = 2.0, transfer exceeds self-training", which is noise wearing a
   headline. So a cell is DEFINED only when the self-training gain is at least
   `min_denominator_pts` (3 points) AND its cluster-bootstrap CI excludes zero.
   Undefined cells are excluded from every average and reported as undefined, never
   silently dropped or imputed to 0.

2. **Cluster bootstrap by program_id, not by item.** Each program contributes 3-5 input
   cases whose outcomes are strongly correlated (get the program wrong, get all its
   cases wrong). Resampling items would treat them as independent and understate the
   CIs by roughly sqrt(cases-per-program). Programs are the independent unit.
   Numerator and denominator are computed on the SAME resample so their correlation is
   preserved — resampling them independently would widen the TR CI spuriously.

3. **Invariance Index is reported in raw points first.** `mean_i (acc_H1(tuned_i) -
   acc_H1(base))` is the primary number because it survives a near-zero H1 gain from
   the monolithic adapter; the normalized version (divided by the monolithic H1 gain,
   since no `tuned_H1` exists — H1 is never trained) is secondary and is emitted as
   undefined when that denominator fails the guard.

Paired McNemar (exact) compares tuned vs base on the same items; p-values across the
matrix are BH-adjusted as ONE family (CLAUDE.md §4).
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RESULTS_DIR, load_config

N_BOOTSTRAP = 2000
MIN_DENOMINATOR_PTS = 3.0
Z95 = 1.959963984540054
STUB_MARKER = "STUB_DO_NOT_USE"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_trials(
    source: Optional[Path] = None,
    model: Optional[str] = None,
    language: Optional[str] = None,
    phase: Optional[str] = None,
) -> pd.DataFrame:
    """Load trials from results/trials.parquet if present, else from cell parquets."""
    source = Path(source) if source else RESULTS_DIR
    if source.is_file():
        df = pd.read_parquet(source)
    else:
        cells_root = source / "cells" if (source / "cells").exists() else source
        parts = []
        for p in sorted(cells_root.rglob("trials.parquet")):
            if (p.parent / STUB_MARKER).exists():
                continue
            parts.append(pd.read_parquet(p))
        if not parts:
            raise FileNotFoundError(f"no cell parquets under {cells_root}")
        df = pd.concat(parts, ignore_index=True)
    if model:
        # `base_model` stores the HF id ("Qwen/Qwen2.5-Coder-1.5B-Instruct"), but every
        # other entry point in this project addresses models by their config KEY
        # ("qwen25c-1.5b"). The key is not a substring of the id, so passing the key —
        # which is what scripts/pipeline.sh did, and what this CLI's own --help offered as
        # its first example — matched zero rows and printed "no trials". The analysis stage
        # then exited 0 with no transfer matrix: RQ1's headline artifact, silently absent.
        # Resolve the key to its id first, and accept either spelling.
        needle = model
        try:
            models_cfg = load_config("models.yaml")
            entry = (models_cfg.get("models") or models_cfg).get(model)
            if isinstance(entry, dict) and entry.get("hf_id"):
                needle = entry["hf_id"]
        except Exception:  # noqa: BLE001 — an unresolvable key just falls back to substring
            pass
        df = df[df["base_model"].str.contains(needle, case=False, regex=False)
                | (df["base_model"] == needle)]
    if language:
        df = df[df["language"] == language]
    if phase:
        df = df[df["phase"] == phase]
    return df.reset_index(drop=True)


def system_label(df: pd.DataFrame) -> pd.Series:
    """Stable per-system key: the run_id's system field is not in TrialRow, so systems
    are identified by (adapter_arch, train_cond, adapter_id) as the schema intends."""
    return (
        df["adapter_arch"].astype(str)
        + "|" + df["train_cond"].fillna("-").astype(str)
        + "|" + df["adapter_id"].fillna("-").astype(str)
    )


def core_subset(df: pd.DataFrame) -> pd.DataFrame:
    """The all-conditions-succeeded common subset (CLAUDE.md §4, coverage honesty).

    S1/S2 bail on some programs by design. Comparing a cell built on 900 programs with
    one built on 700 confounds the transform effect with the program set, so the
    headline matrix uses only programs present in EVERY eval condition.

    The intersection is taken WITHIN an experiment, not across everything on disk. Without
    that scoping the subset is hostage to the sparsest grid present: on 2026-08-10 the S3/S4
    expansion (40 programs, a testset-sourced grid) landed alongside the main heldout grid
    (597) and silently cut the common subset from 340 programs to 23 — a 93 % loss that
    reached the published transfer matrix as `n_programs: 23` and inflated every CI in it.
    Nothing failed; the matrix simply described a different, much smaller corpus.

    Grouping by `experiment_id` restores the docstring's own words — "present in EVERY eval
    condition" of *its own grid* — and keeps a sparse supplementary grid from redefining the
    headline's denominator.
    """
    if "experiment_id" in df.columns and df["experiment_id"].notna().any():
        keep = []
        for _, sub in df.groupby("experiment_id", dropna=False):
            per_cond = sub.groupby("eval_cond")["snippet_id"].apply(set)
            if per_cond.empty:
                continue
            common = set.intersection(*per_cond.tolist())
            keep.append(sub[sub["snippet_id"].isin(common)])
        if keep:
            out = pd.concat(keep, ignore_index=False).copy()
            out["is_core"] = 1
            return out

    per_cond = df.groupby("eval_cond")["snippet_id"].apply(set)
    if per_cond.empty:
        return df
    common = set.intersection(*per_cond.tolist())
    out = df[df["snippet_id"].isin(common)].copy()
    out["is_core"] = 1
    return out


# --------------------------------------------------------------------------- #
# Interval estimates
# --------------------------------------------------------------------------- #

def wilson_ci(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval — the CI for a proportion that stays inside [0,1] and does
    not collapse at k=0 or k=n (where Wald would report a zero-width interval)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar on the discordant pairs. b = tuned right / base wrong."""
    n = b + c
    if n == 0:
        return 1.0
    from scipy.stats import binomtest

    return float(binomtest(min(b, c), n, 0.5, alternative="two-sided").pvalue)


def bh_fdr(pvals: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values. The transfer matrix is ONE family."""
    p = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(p)
    out = np.full(p.shape, np.nan)
    if ok.sum() == 0:
        return out.tolist()
    q = p[ok]
    m = q.size
    order = np.argsort(q)
    ranked = q[order] * m / (np.arange(m) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(m)
    adj[order] = np.clip(ranked, 0, 1)
    out[ok] = adj
    return out.tolist()


# --------------------------------------------------------------------------- #
# Cluster bootstrap
# --------------------------------------------------------------------------- #

@dataclass
class PairedCells:
    """Two systems' outcomes on the SAME items, grouped by program for clustering."""

    programs: np.ndarray  # (P,) program ids
    n_items: np.ndarray  # (P,) items per program
    sum_a: np.ndarray  # (P,) correct count, system A
    sum_b: np.ndarray  # (P,) correct count, system B

    @property
    def n(self) -> int:
        return int(self.n_items.sum())

    def delta(self) -> float:
        tot = self.n_items.sum()
        return float((self.sum_a.sum() - self.sum_b.sum()) / tot) if tot else float("nan")


def pair_items(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    """Inner-join two cells on item_id. An explicit merge, not index alignment: a cell
    that is missing items (a crashed shard) must shrink the comparison, not silently
    produce NaNs that count as zeros."""
    a = df_a[["item_id", "snippet_id", "correct"]].drop_duplicates("item_id")
    b = df_b[["item_id", "correct"]].drop_duplicates("item_id")
    return a.merge(b, on="item_id", suffixes=("_a", "_b"))


def pair_cells(df_a: pd.DataFrame, df_b: pd.DataFrame) -> PairedCells:
    """Inner-join two cells on item_id and aggregate by program."""
    m = pair_items(df_a, df_b)
    if m.empty:
        return PairedCells(np.array([]), np.array([]), np.array([]), np.array([]))
    g = m.groupby("snippet_id").agg(
        n_items=("item_id", "size"), sum_a=("correct_a", "sum"), sum_b=("correct_b", "sum")
    )
    return PairedCells(
        g.index.to_numpy(), g["n_items"].to_numpy(float),
        g["sum_a"].to_numpy(float), g["sum_b"].to_numpy(float),
    )


def bootstrap_program_indices(n_programs: int, n_resamples: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_programs, size=(n_resamples, n_programs))


def bootstrap_delta(
    pc: PairedCells, n_resamples: int = N_BOOTSTRAP, seed: int = GLOBAL_SEED,
    idx: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Cluster-bootstrap distribution of acc_A - acc_B. Resamples PROGRAMS."""
    if pc.programs.size == 0:
        return np.array([])
    if idx is None:
        idx = bootstrap_program_indices(pc.programs.size, n_resamples, seed)
    n = pc.n_items[idx].sum(axis=1)
    da = pc.sum_a[idx].sum(axis=1)
    db = pc.sum_b[idx].sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (da - db) / n


def ci_from_draws(draws: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    d = draws[np.isfinite(draws)]
    if d.size == 0:
        return (float("nan"), float("nan"))
    return (float(np.quantile(d, alpha / 2)), float(np.quantile(d, 1 - alpha / 2)))


# --------------------------------------------------------------------------- #
# The matrix
# --------------------------------------------------------------------------- #

def accuracy_table(df: pd.DataFrame) -> pd.DataFrame:
    # prompt_id is part of the system identity: oracle_prompt and oracle_prompt_1shot
    # share adapter_arch and have no adapter, and differ ONLY by prompt (RQ2).
    g = df.groupby(
        ["adapter_arch", "train_cond", "adapter_id", "prompt_id", "eval_cond"], dropna=False
    )
    rows = []
    for (arch, tc, aid, pid, ec), sub in g:
        k, n = int(sub["correct"].sum()), int(len(sub))
        lo, hi = wilson_ci(k, n)
        rows.append(
            {
                "adapter_arch": arch, "train_cond": tc, "adapter_id": aid,
                "prompt_id": pid, "eval_cond": ec,
                "n": n, "n_programs": sub["snippet_id"].nunique(), "k": k, "acc": k / n,
                "wilson_lo": lo, "wilson_hi": hi,
                "format_fail_rate": float(sub["format_fail"].mean()) if "format_fail" in sub else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def _select(df: pd.DataFrame, arch: str, train_cond: Optional[str], eval_cond: str) -> pd.DataFrame:
    m = (df["adapter_arch"] == arch) & (df["eval_cond"] == eval_cond)
    m &= df["train_cond"].isna() if train_cond is None else (df["train_cond"] == train_cond)
    return df[m]


def transfer_matrix(
    df: pd.DataFrame,
    train_conditions: Sequence[str],
    eval_conditions: Sequence[str],
    tuned_arch: str = "per_type",
    base_arch: str = "none",
    mono_arch: str = "mono",
    n_resamples: int = N_BOOTSTRAP,
    seed: int = GLOBAL_SEED,
    min_denominator_pts: float = MIN_DENOMINATOR_PTS,
) -> pd.DataFrame:
    """One row per (train_cond i, eval_cond j) with acc, delta, TR and the guard verdict."""
    base_cells = {j: _select(df, base_arch, None, j) for j in eval_conditions}

    # The denominator for column j is the self-trained adapter on j. H1 has no
    # tuned_H1 by construction (CLAUDE.md §3.2), so its denominator is the monolithic
    # adapter's H1 gain — which is exactly the quantity the normalized Invariance
    # Index is expressed in.
    den_cells: dict[str, pd.DataFrame] = {}
    den_source: dict[str, str] = {}
    for j in eval_conditions:
        self_tuned = _select(df, tuned_arch, j, j)
        if not self_tuned.empty:
            den_cells[j], den_source[j] = self_tuned, f"{tuned_arch}[{j}]"
        else:
            mono = _select(df, mono_arch, None, j)
            if mono.empty:
                mono = df[(df["adapter_arch"] == mono_arch) & (df["eval_cond"] == j)]
            den_cells[j], den_source[j] = mono, mono_arch

    rows = []
    for j in eval_conditions:
        base = base_cells[j]
        den_cell = den_cells[j]
        den_pc = pair_cells(den_cell, base)
        idx = (
            bootstrap_program_indices(den_pc.programs.size, n_resamples, seed)
            if den_pc.programs.size
            else None
        )
        den_draws = bootstrap_delta(den_pc, n_resamples, seed, idx=idx)
        den = den_pc.delta()
        den_lo, den_hi = ci_from_draws(den_draws)
        den_ok = (
            den_pc.programs.size > 0
            and np.isfinite(den)
            and den * 100 >= min_denominator_pts
            and np.isfinite(den_lo)
            and (den_lo > 0)
        )

        for i in train_conditions:
            tuned = _select(df, tuned_arch, i, j)
            if tuned.empty or base.empty:
                continue
            pc = pair_cells(tuned, base)
            num = pc.delta()
            # Numerator and denominator share the resample so their correlation
            # (same programs, same base cell) is preserved in the TR CI.
            num_idx = (
                idx if (idx is not None and pc.programs.size == den_pc.programs.size
                        and np.array_equal(pc.programs, den_pc.programs))
                else bootstrap_program_indices(pc.programs.size, n_resamples, seed)
            )
            num_draws = bootstrap_delta(pc, n_resamples, seed, idx=num_idx)
            num_lo, num_hi = ci_from_draws(num_draws)

            paired = pair_items(tuned, base)
            b = int(((paired["correct_a"] == 1) & (paired["correct_b"] == 0)).sum())
            c = int(((paired["correct_a"] == 0) & (paired["correct_b"] == 1)).sum())

            if den_ok:
                tr = num / den
                if num_draws.size == den_draws.size and num_draws.size:
                    with np.errstate(invalid="ignore", divide="ignore"):
                        tr_draws = np.where(den_draws != 0, num_draws / den_draws, np.nan)
                    tr_lo, tr_hi = ci_from_draws(tr_draws)
                else:
                    tr_lo = tr_hi = float("nan")
            else:
                tr = tr_lo = tr_hi = float("nan")

            rows.append(
                {
                    "train_cond": i, "eval_cond": j,
                    "n_items": pc.n, "n_programs": int(pc.programs.size),
                    "acc_tuned": float(tuned["correct"].mean()),
                    "acc_base": float(base["correct"].mean()),
                    "delta_pts": num * 100,
                    "delta_ci_lo_pts": num_lo * 100, "delta_ci_hi_pts": num_hi * 100,
                    "den_source": den_source[j],
                    "den_pts": den * 100,
                    "den_ci_lo_pts": den_lo * 100, "den_ci_hi_pts": den_hi * 100,
                    "tr_defined": bool(den_ok),
                    "tr": tr, "tr_ci_lo": tr_lo, "tr_ci_hi": tr_hi,
                    "mcnemar_b": b, "mcnemar_c": c, "mcnemar_p": mcnemar_exact(b, c),
                    "is_self": i == j,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out["mcnemar_p_bh"] = bh_fdr(out["mcnemar_p"].tolist())
    return out


def invariance_index(
    matrix: pd.DataFrame, held_out: str = "H1", exclude_self: bool = True
) -> dict[str, Any]:
    """mean_i TR(i -> H1), in raw points (primary) and normalized (secondary)."""
    col = matrix[matrix["eval_cond"] == held_out]
    if exclude_self:
        col = col[~col["is_self"]]
    if col.empty:
        return {"held_out": held_out, "n_train_conditions": 0, "raw_delta_pts": float("nan")}
    defined = col[col["tr_defined"] & col["tr"].notna()]
    return {
        "held_out": held_out,
        "n_train_conditions": int(len(col)),
        # PRIMARY: raw delta-H1 points, defined regardless of the denominator guard.
        "raw_delta_pts": float(col["delta_pts"].mean()),
        "raw_delta_pts_min": float(col["delta_pts"].min()),
        "raw_delta_pts_max": float(col["delta_pts"].max()),
        "per_condition_delta_pts": dict(zip(col["train_cond"], col["delta_pts"].round(4))),
        # SECONDARY: normalized by the monolithic H1 gain; undefined if it fails the guard.
        "normalized_defined": bool(len(defined) > 0),
        "n_defined": int(len(defined)),
        "normalized": float(defined["tr"].mean()) if len(defined) else float("nan"),
        "normalizer": col["den_source"].iloc[0],
        "normalizer_pts": float(col["den_pts"].iloc[0]),
    }


def summarize(matrix: pd.DataFrame) -> dict[str, Any]:
    if matrix.empty:
        return {"n_cells": 0}
    off = matrix[~matrix["is_self"]]
    defined = off[off["tr_defined"] & off["tr"].notna()]
    return {
        "n_cells": int(len(matrix)),
        "n_offdiagonal": int(len(off)),
        "n_tr_defined": int(len(defined)),
        "n_tr_undefined": int(len(off) - len(defined)),
        "mean_tr_offdiagonal": float(defined["tr"].mean()) if len(defined) else float("nan"),
        "mean_self_delta_pts": float(matrix[matrix["is_self"]]["delta_pts"].mean())
        if (matrix["is_self"]).any() else float("nan"),
        "n_significant_bh05": int((matrix["mcnemar_p_bh"] < 0.05).sum())
        if "mcnemar_p_bh" in matrix else 0,
    }


# --------------------------------------------------------------------------- #

def run(
    model: str,
    language: str,
    source: Optional[Path] = None,
    train_conditions: Optional[Sequence[str]] = None,
    eval_conditions: Optional[Sequence[str]] = None,
    core_only: bool = True,
    out_dir: Optional[Path] = None,
    n_resamples: int = N_BOOTSTRAP,
    seed: int = GLOBAL_SEED,
) -> dict[str, Any]:
    from obtune.paths import ALL_CONDITIONS, TRAINABLE_CONDITIONS

    df = load_trials(source, model=model, language=language)
    if df.empty:
        raise SystemExit(f"no trials for model={model} language={language}")
    if core_only:
        df = core_subset(df)

    train_conditions = list(train_conditions or TRAINABLE_CONDITIONS)
    eval_conditions = list(eval_conditions or ALL_CONDITIONS)
    eval_conditions = [c for c in eval_conditions if c in set(df["eval_cond"])]

    acc = accuracy_table(df)
    matrix = transfer_matrix(
        df, train_conditions, eval_conditions, n_resamples=n_resamples, seed=seed
    )
    ii = invariance_index(matrix) if "H1" in eval_conditions else {"held_out": "H1", "raw_delta_pts": float("nan")}

    out_dir = Path(out_dir) if out_dir else RESULTS_DIR / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_model = model.replace("/", "-")
    mpath = out_dir / f"transfer_{safe_model}_{language}.parquet"
    matrix.to_parquet(mpath, index=False)
    apath = out_dir / f"accuracy_{safe_model}_{language}.parquet"
    acc.to_parquet(apath, index=False)

    report = {
        "model": model, "language": language,
        "core_only": core_only, "n_trials": int(len(df)),
        "n_programs": int(df["snippet_id"].nunique()),
        "n_resamples": n_resamples, "seed": seed,
        "min_denominator_pts": MIN_DENOMINATOR_PTS,
        "summary": summarize(matrix),
        "invariance_index": ii,
        "matrix_parquet": str(mpath), "accuracy_parquet": str(apath),
    }
    (out_dir / f"transfer_{safe_model}_{language}.json").write_text(json.dumps(report, indent=2, default=float))
    return report


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="RQ1 transfer matrix")
    ap.add_argument("--model", required=True,
                    help="model config key (qwen25c-1.5b) or any substring of the HF id "
                         "(Qwen2.5-Coder-1.5B); the key is resolved via models.yaml")
    ap.add_argument("--language", default="python")
    ap.add_argument("--source", default=None, help="results/ root, a cells dir, or a trials.parquet")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--all-programs", action="store_true", help="disable the common-subset filter")
    ap.add_argument("--n-resamples", type=int, default=N_BOOTSTRAP)
    ap.add_argument("--seed", type=int, default=GLOBAL_SEED)
    args = ap.parse_args(argv)

    report = run(
        model=args.model, language=args.language,
        source=Path(args.source) if args.source else None,
        core_only=not args.all_programs,
        out_dir=Path(args.out_dir) if args.out_dir else None,
        n_resamples=args.n_resamples, seed=args.seed,
    )
    print(json.dumps(report, indent=2, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
