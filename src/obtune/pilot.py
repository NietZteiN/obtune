"""Week-1 kill-switch decision table (design doc §6).

Turns the pilot's cells into the go/no-go numbers that decide whether the full
grid launches and which branch the paper takes. Every quantity carries a
cluster-bootstrap CI over `program_id` — input cases within a program are
correlated, so bootstrapping items would understate the intervals.

    python -m obtune.pilot --model Qwen2.5-Coder-1.5B --language python
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from obtune.config import PROJECT_ROOT, load_config


def _cluster_bootstrap_delta(
    df_a: pd.DataFrame, df_b: pd.DataFrame, n_resamples: int, seed: int
) -> tuple[float, float, float]:
    """Bootstrap acc(a) - acc(b) in points, resampling PROGRAMS, not items."""
    programs = sorted(set(df_a["snippet_id"]) & set(df_b["snippet_id"]))
    a_by = {p: g["correct"].to_numpy() for p, g in df_a.groupby("snippet_id")}
    b_by = {p: g["correct"].to_numpy() for p, g in df_b.groupby("snippet_id")}
    rng = np.random.default_rng(seed)
    deltas = np.empty(n_resamples)
    idx = np.arange(len(programs))
    for i in range(n_resamples):
        pick = rng.choice(idx, size=len(programs), replace=True)
        a = np.concatenate([a_by[programs[j]] for j in pick])
        b = np.concatenate([b_by[programs[j]] for j in pick])
        deltas[i] = (a.mean() - b.mean()) * 100.0
    point = (df_a["correct"].mean() - df_b["correct"].mean()) * 100.0
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return float(point), float(lo), float(hi)


def _sel(df: pd.DataFrame, *, arch: str, cond: str, prompt_id: str | None = None) -> pd.DataFrame:
    out = df[(df["adapter_arch"] == arch) & (df["eval_cond"] == cond)]
    if prompt_id is not None:
        out = out[out["prompt_id"] == prompt_id]
    return out


def build(model: str, language: str, trials_path: Path, n_resamples: int, seed: int) -> dict[str, Any]:
    df = pd.read_parquet(trials_path)
    df = df[df["base_model"].str.contains(model, case=False, na=False)]
    df = df[(df["language"] == language) & (df["is_core"] == 1)]
    if df.empty:
        raise SystemExit(f"no trials for model~{model} language={language}")

    # Restrict to programs present in every cell, so no gate is decided on a
    # different program set than another (S1/H1 decline on different programs).
    per_cell = df.groupby(["adapter_arch", "prompt_id", "eval_cond"])["snippet_id"].apply(set)
    common = set.intersection(*per_cell.tolist())
    df = df[df["snippet_id"].isin(common)]

    cfg = load_config("eval/pilot_w1.yaml")
    gates = cfg["decision"]["gates"]
    train_cond = "L1b"

    base = lambda c: _sel(df, arch="none", cond=c)  # noqa: E731
    tuned = lambda c: _sel(df, arch="per_type", cond=c)  # noqa: E731
    oracle = lambda c, p: _sel(df, arch="oracle_prompt", cond=c, prompt_id=p)  # noqa: E731

    out: dict[str, Any] = {
        "model": model, "language": language, "phase": "pilot",
        "n_programs_common": len(common), "n_trials": int(len(df)),
        "n_resamples": n_resamples, "seed": seed,
        "train_cond": train_cond,
        "accuracy": {}, "gates": {}, "notes": [],
    }

    conds = [c for c in ["L0", "L1b", "L1r", "L2", "S1", "S2", "H1"] if c in set(df["eval_cond"])]
    for c in conds:
        row: dict[str, Any] = {}
        for name, sub in (("base", base(c)), ("tuned", tuned(c))):
            if len(sub):
                row[name] = {"n": int(len(sub)), "acc": round(float(sub["correct"].mean()), 4),
                             "format_fail": round(float(1 - sub["parse_ok"].mean()), 4)}
        for pid in sorted(set(_sel(df, arch="oracle_prompt", cond=c)["prompt_id"])):
            sub = oracle(c, pid)
            row[pid] = {"n": int(len(sub)), "acc": round(float(sub["correct"].mean()), 4),
                        "format_fail": round(float(1 - sub["parse_ok"].mean()), 4)}
        out["accuracy"][c] = row

    def gate(name: str, value: float, lo: float, hi: float, threshold: float,
             direction: str, note: str = "") -> None:
        passed = value >= threshold if direction == "min" else value <= threshold
        out["gates"][name] = {
            "value": round(value, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "threshold": threshold, "direction": direction,
            "pass": bool(passed), "note": note,
        }

    # 1. self gain — does training on L1b help on L1b at all?
    sg, sg_lo, sg_hi = _cluster_bootstrap_delta(tuned(train_cond), base(train_cond), n_resamples, seed)
    gate("self_gain_pts", sg, sg_lo, sg_hi, float(gates["self_gain_min_pts"]), "min",
         "acc_L1b(tuned) - acc_L1b(base)")

    # 2. output-format discipline of the TUNED model (the grid's grader assumption)
    ff = float(1 - tuned(train_cond)["parse_ok"].mean())
    gate("format_fail_rate", ff, ff, ff, float(gates["format_fail_max"]), "max",
         "tuned model, train condition")

    # 3. catastrophic forgetting on the clean condition
    fg, fg_lo, fg_hi = _cluster_bootstrap_delta(tuned("L0"), base("L0"), n_resamples, seed)
    gate("forget_L0_pts", fg, fg_lo, fg_hi, float(gates["forget_L0_min_pts"]), "min",
         "acc_L0(tuned) - acc_L0(base); negative = forgetting")

    # 4. conditioning vs capability — how much of the tuning gain does simply
    #    TELLING the model the obfuscation type recover?
    for pid in sorted(set(_sel(df, arch="oracle_prompt", cond=train_cond)["prompt_id"])):
        og, og_lo, og_hi = _cluster_bootstrap_delta(
            oracle(train_cond, pid), base(train_cond), n_resamples, seed)
        ratio = og / sg if sg > 0 else float("nan")
        branch = ("conditioning" if ratio >= float(gates["cond_recovery_conditioning"])
                  else "capability" if ratio <= float(gates["cond_recovery_capability"])
                  else "inconclusive")
        out["gates"][f"cond_recovery__{pid}"] = {
            "oracle_gain_pts": round(og, 4), "ci95": [round(og_lo, 4), round(og_hi, 4)],
            "ratio_to_self_gain": round(ratio, 4), "branch": branch,
            "note": ">=0.5 conditioning, <=0.2 capability, else run both arms",
        }

    # 5a. THE CONTROL CONTRAST — what did training on *obfuscated* code buy over
    #     training on clean code? Raw Δ-vs-base cannot answer this: the base model is
    #     weak at output prediction itself, so every adapter gains on every condition
    #     simply by learning the task. Only the gap to an L0-trained control isolates
    #     the obfuscation-specific effect, and it is the quantity H1c actually needs.
    if "L0" in set(df[df["adapter_arch"] == "per_type"]["train_cond"].dropna()):
        ctl = lambda c: df[(df["adapter_arch"] == "per_type") & (df["train_cond"] == "L0")  # noqa: E731
                           & (df["eval_cond"] == c)]
        tgt = lambda c: df[(df["adapter_arch"] == "per_type") & (df["train_cond"] == train_cond)  # noqa: E731
                           & (df["eval_cond"] == c)]
        vs_control: dict[str, Any] = {}
        for c in conds:
            if not len(ctl(c)) or not len(tgt(c)):
                continue
            pt, lo, hi = _cluster_bootstrap_delta(tgt(c), ctl(c), n_resamples, seed)
            vs_control[c] = {
                "value_pts": round(pt, 4), "ci95": [round(lo, 4), round(hi, 4)],
                "excludes_zero": bool(lo > 0 or hi < 0),
            }
        out["condition_specific_benefit"] = {
            "definition": f"acc(tuned_{train_cond}) - acc(tuned_L0), per eval condition",
            "control_train_cond": "L0",
            "per_condition": vs_control,
            "note": "The obfuscation-specific effect. A gain concentrated on the trained "
                    "condition and vanishing on the held-out one is the signature of "
                    "transform memorization; a gain that survives onto H1 is invariance.",
        }
        if "H1" in vs_control:
            v = vs_control["H1"]
            out["invariance_index_control_relative"] = {
                "value_pts": v["value_pts"], "ci95": v["ci95"],
                "excludes_zero": v["excludes_zero"],
                "verdict": ("invariance" if v["excludes_zero"] and v["value_pts"] > 0
                            else "memorization_or_null"),
                "note": "Supersedes the raw Δ-vs-base Invariance Index, which the L0 "
                        "control showed to be confounded with task acquisition.",
            }

    # 5b. the raw read — transfer onto the held-out obfuscator vs the untuned base.
    #     Kept because it is the design doc's original definition, but it is NOT the
    #     invariance measure: see 5a.
    if "H1" in conds:
        hd, hd_lo, hd_hi = _cluster_bootstrap_delta(tuned("H1"), base("H1"), n_resamples, seed)
        out["gates"]["h1_delta_pts"] = {
            "value": round(hd, 4), "ci95": [round(hd_lo, 4), round(hd_hi, 4)],
            "excludes_zero": bool(hd_lo > 0 or hd_hi < 0),
            "note": "Invariance Index (raw). >0 with CI excluding 0 supports H1c: "
                    "semantic invariance rather than transform memorization.",
        }
        # How much of the H1 gain is explained by the model merely learning the
        # OUTPUT FORMAT / task, which the one-shot oracle also teaches? Without this
        # the invariance claim is confounded with format learning.
        for pid in sorted(set(_sel(df, arch="oracle_prompt", cond="H1")["prompt_id"])):
            og, og_lo, og_hi = _cluster_bootstrap_delta(oracle("H1", pid), base("H1"), n_resamples, seed)
            out["gates"][f"h1_format_control__{pid}"] = {
                "oracle_gain_pts": round(og, 4), "ci95": [round(og_lo, 4), round(og_hi, 4)],
                "tuning_beyond_oracle_pts": round(hd - og, 4),
                "note": "tuning gain on H1 above what prompt-only conditioning achieves",
            }

    # 6. family sanity — a rename adapter should reach the identifier family more
    #    easily than the structural one.
    if {"L2", "S1"} <= set(conds):
        t_l2, l2_lo, l2_hi = _cluster_bootstrap_delta(tuned("L2"), base("L2"), n_resamples, seed)
        t_s1, s1_lo, s1_hi = _cluster_bootstrap_delta(tuned("S1"), base("S1"), n_resamples, seed)
        out["gates"]["family_sanity"] = {
            "transfer_L2_pts": round(t_l2, 4), "transfer_S1_pts": round(t_s1, 4),
            "L2_gt_S1": bool(t_l2 > t_s1),
            "note": "identifier-family transfer expected to exceed structural-family",
        }

    failed = [k for k, v in out["gates"].items() if isinstance(v, dict) and v.get("pass") is False]
    out["verdict"] = {
        "gates_failed": failed,
        "proceed_to_grid": not failed,
        "branch": out["gates"].get(f"cond_recovery__oracle_1shot_v1", {}).get("branch", "unknown"),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True)
    ap.add_argument("--language", default="python")
    ap.add_argument("--trials", default=str(PROJECT_ROOT / "results" / "trials.parquet"))
    ap.add_argument("--out", default=str(PROJECT_ROOT / "results" / "analysis" / "pilot_decision.json"))
    ap.add_argument("--n-resamples", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()

    rep = build(args.model, args.language, Path(args.trials), args.n_resamples, args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
