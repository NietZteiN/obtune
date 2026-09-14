#!/usr/bin/env python
"""Which method is best on stacked obfuscation — asked separately for the three kinds of stack.

    python scripts/analysis/69_stack_leaderboard.py

"Best on stacks" has three different answers and collapsing them loses the paper's point:

  SEEN depth-2 (6)    two transforms the training set contains
  depth-3/4 (4)       three or four transforms, all seen
  UNSEEN-containing   a stack one of whose transforms is the held-out family (X1)

Raw forward accuracy, pooled per group, every method including the merge and the router. No deltas
and no ratios: the question is which arm is highest, and a ratio against a format-gated untuned
model is not an answer. `g` marks a cell over the 0.25 format gate.

READ IT WITH THE BACKWARD TABLES. The arm that wins the first two groups is also the arm that
forward-locks hardest (67_backward_failure_modes.py) and is furthest below the untuned model
backwards (65_backward_stacks.py). Forward accuracy on seen stacks and bidirectional competence are
different axes and the panel separates them cleanly.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from cellkit import allow_mixed_prompts, load_cell  # noqa: E402

# Forward cells only, and a forward arm's prompt is the same everywhere; the registry would compare
# it against the BACKWARD prompt for the same arm, which is not a fault.
allow_mixed_prompts()

SEEN = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]
DEEP = ["C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4"]
UNSEEN = ["C_L1r_X1", "C_X1_S1", "C_S2_X1"]
PH = ["panel_core", "composite_generic", "composite_depth", "f2_divergence"]
MPH = ["merge_panel", "rq2_generic", "composite_generic", "composite_depth", "f2_divergence"]
ARMS = [("base", "base", PH), ("clean", "tuned_L0", PH), ("breadth", "mono_all", PH),
        ("anchored", "cons_lam3", PH), ("family", "tuned_X1", PH),
        ("merge", "merge_dare_ties", MPH), ("router", "mole_router", ["mole_generic"])]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
GROUPS = [("SEEN depth-2 stacks (6)", SEEN), ("depth-3/4 stacks, all seen (4)", DEEP),
          ("stacks containing the UNSEEN family (3)", UNSEEN)]
FMT_GATE = 0.25


def main() -> int:
    out = {"script": "69_stack_leaderboard.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "metric": "forward accuracy (execution-graded output prediction)",
           "format_gate": FMT_GATE, "groups": {}}
    for gname, conds in GROUPS:
        print(f"\n=== forward accuracy, {gname} ===")
        print(f"{'model':16s} " + " ".join(f"{n:>10s}" for n, _, _ in ARMS) + "   winner")
        wins = {}
        for m in MODELS:
            row, vals = [], {}
            for n, sy, ph in ARMS:
                fr = [load_cell(ph, m, sy, c) for c in conds]
                if any(f is None for f in fr):
                    row.append(f"{'--':>10s}")
                    continue
                d = pd.concat(fr)
                ff = float(d["format_fail"].mean()) if "format_fail" in d else 0.0
                acc = float(d["correct"].mean())
                gated = ff > FMT_GATE
                if not gated and n != "base":
                    vals[n] = acc
                row.append(f"{acc:9.3f}" + ("g" if gated else " "))
                out["groups"].setdefault(gname, {}).setdefault(m, {})[n] = {
                    "accuracy": round(acc, 4), "format_fail": round(ff, 4), "gated": gated}
            win = max(vals, key=vals.get) if vals else "--"
            wins[win] = wins.get(win, 0) + 1
            print(f"{m:16s} " + " ".join(row) + f"   {win}")
        tally = ", ".join(f"{k} {v}/{len(MODELS)}" for k, v in
                          sorted(wins.items(), key=lambda kv: -kv[1]))
        print(f"{'':16s} winners: {tally}")
        out["groups"][gname]["_winners"] = wins
    print("\n  g = over the 0.25 format gate; a gated cell cannot win. `base` is shown for scale "
          "and is excluded from the\n  winner column. Forward accuracy only — see "
          "65_backward_stacks.py and 67_backward_failure_modes.py for the\n  other direction, where "
          "the ordering is different.")
    p = ROOT / "results/analysis/pipeline/stack_leaderboard.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
