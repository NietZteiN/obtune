#!/usr/bin/env python
"""How much the one-shot demo moved the backward ladder, per arm and per model.

    python scripts/analysis/68_prompt_effect.py

The backward ladder was evaluated twice with the same adapters on the same items and only the prompt
different: `inverse_generic` holds the ZERO-SHOT read (`inverse_core.yaml`, prompt_id inverse_v1) and
`inverse_1shot` holds the repair (`inverse_ladder_1shot.yaml`, inverse_1shot_v1). That is an
unusually clean natural experiment and it is the reason the old cells were kept rather than
overwritten: the size of the confound can be measured instead of argued about.

WHY THE DIRECTION MATTERS MORE THAN THE SIZE. Every affected contrast put a ONE-SHOT arm (the merges,
which always had the demo) against a ZERO-SHOT baseline. If the demo flatters the untuned model, the
published merge gains were understated and the one reversal was overstated; if it flatters the tuned
arms, the opposite. `log/transfer/2026-09-14_two-prompts-one-phase.md` asserted the second without
measuring it. This script settles it.

Reports, per (model, arm), on the six ladder conditions plus X1, paired on the common program set:

    accuracy   zero-shot -> one-shot, and the difference
    format     zero-shot -> one-shot format-failure rate
    gate       whether the cell crosses the 0.25 gate in each reading

A cell missing from either phase is skipped, so this fills in as the repair lands.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from cellkit import allow_mixed_prompts  # noqa: E402

# This script's entire purpose is to compare the two prompts, so the registry's warning would fire
# on every arm and mean nothing here.
allow_mixed_prompts()

CELLS = ROOT / "results" / "cells"
OLD, NEW = "inverse_generic", "inverse_1shot"
LADDER = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1"]
ARMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]
MODELS = ["codellama-13b", "codellama-34b", "llama31-8b", "starcoder2-15b",
          "gemma3-12b", "codegemma-7b", "granite31-8b"]
FMT_GATE = 0.25
N_BOOT, SEED = 2000, 17


def load(phase, model, arm, cond):
    p = CELLS / phase / model / "python" / f"{arm}__{cond}" / "trials.parquet"
    if not p.exists():
        return None
    return pd.read_parquet(p, columns=["snippet_id", "correct", "format_fail"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    res = {"script": "68_prompt_effect.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "phases": {"zero_shot": OLD, "one_shot": NEW}, "conditions": LADDER,
           "n_resamples": N_BOOT, "seed": SEED, "models": {}}

    print("the one-shot demo's effect on the backward ladder: zero-shot -> one-shot, "
          "same adapters, same items\n")
    print(f"{'model':16s} {'arm':12s} {'n':>5s} {'acc0':>7s} {'acc1':>7s} {'delta':>17s} "
          f"{'fmt0':>6s} {'fmt1':>6s}  gate")
    any_row = False
    for m in MODELS:
        for arm in ARMS:
            pairs = []
            for c in LADDER:
                o, n = load(OLD, m, arm, c), load(NEW, m, arm, c)
                if o is None or n is None:
                    continue
                pairs.append((c, o, n))
            if not pairs:
                continue
            any_row = True
            progs = sorted(set.intersection(*[set(o["snippet_id"]) & set(n["snippet_id"])
                                              for _, o, n in pairs]))
            A, B = {}, {}
            for _, o, n in pairs:
                for src, dst in ((o, A), (n, B)):
                    src = src[src["snippet_id"].isin(progs)]
                    for p_, g in src.groupby("snippet_id"):
                        dst.setdefault(p_, []).append(g["correct"].to_numpy(dtype=float))
            A = {k: np.concatenate(v) for k, v in A.items()}
            B = {k: np.concatenate(v) for k, v in B.items()}
            a0 = np.concatenate([A[p_] for p_ in progs]).mean()
            a1 = np.concatenate([B[p_] for p_ in progs]).mean()
            rng = np.random.default_rng(SEED)
            idx = np.arange(len(progs))
            draws = np.empty(N_BOOT)
            for i in range(N_BOOT):
                pick = rng.choice(idx, size=len(progs), replace=True)
                draws[i] = (np.concatenate([B[progs[j]] for j in pick]).mean()
                            - np.concatenate([A[progs[j]] for j in pick]).mean()) * 100.0
            lo, hi = np.percentile(draws, [2.5, 97.5])
            f0 = float(pd.concat([o for _, o, _ in pairs])["format_fail"].mean())
            f1 = float(pd.concat([n for _, _, n in pairs])["format_fail"].mean())
            g0, g1 = f0 > FMT_GATE, f1 > FMT_GATE
            gate = {(True, True): "gated both", (True, False): "GATE LIFTED",
                    (False, True): "GATE IMPOSED", (False, False): "clean both"}[(g0, g1)]
            star = "*" if (lo > 0) == (hi > 0) else " "
            print(f"{m:16s} {arm:12s} {len(progs):5d} {a0:7.3f} {a1:7.3f} "
                  f"{(a1-a0)*100:+7.2f} [{lo:+6.2f},{hi:+6.2f}]{star} {f0:6.3f} {f1:6.3f}  {gate}")
            res["models"].setdefault(m, {})[arm] = {
                "n_programs": len(progs), "n_conditions": len(pairs),
                "acc_zero_shot": round(float(a0), 4), "acc_one_shot": round(float(a1), 4),
                "delta_pts": round(float((a1-a0)*100), 2),
                "ci": [round(float(lo), 2), round(float(hi), 2)],
                "significant": bool(star == "*"),
                "fmt_zero_shot": round(f0, 4), "fmt_one_shot": round(f1, 4), "gate": gate}
    if not any_row:
        print("  (no model has cells in both phases yet -- the repair is still running)")
    else:
        print("\n  A POSITIVE delta means the demo HELPED that arm. The published contrasts put "
              "one-shot merge\n  arms against zero-shot baselines, so if `base`'s delta is negative "
              "the merge gains were UNDERstated\n  and the one reversal OVERstated; if positive, the "
              "other way round.")

    p = Path(a.out) if a.out else ROOT / "results/analysis/pipeline/prompt_effect.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=2) + "\n")
    print(f"  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
