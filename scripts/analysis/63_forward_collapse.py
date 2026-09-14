#!/usr/bin/env python
"""Forward-collapse rate: how often an arm answers the FORWARD question when asked the BACKWARD one.

    python scripts/analysis/63_forward_collapse.py [condition]

A reply to the inverse prompt that is exactly the program's gold RETURN VALUE is not a malformed
call -- it is the answer to the other question. Verified 2026-09-14: on Granite and CodeGemma the
anchored arm does this on ~98 % of items and gets the forward answer right, while no untuned model
does it at all, and the inverse instruction is present in the rendered prompt for every model.

This is the metric the format gate was hiding. It is measurable on EVERY model and arm -- unlike
backward accuracy, which is uninterpretable wherever the gate bites -- and the untuned models sit at
the floor, so the full range is usable.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"src"))
from obtune.data import load_eval_items  # noqa: E402

COND = sys.argv[1] if len(sys.argv) > 1 else "L0"
MODELS = ["codellama-7b","codellama-13b","codellama-34b","llama31-8b","starcoder2-15b",
          "gemma3-12b","codegemma-7b","granite31-8b"]
ARMS = ["base","tuned_L0","mono_all","cons_lam3","tuned_X1"]

def norm(s): return str(s).strip().strip('"').strip("'").replace(" ", "")

gold = {(it.program_id, it.item_id): it.output_repr
        for it in load_eval_items([COND], "python", source="heldout")}

out = {"script": "63_forward_collapse.py", "condition": COND, "by_model": {}}
print(f"forward-collapse rate on the backward task, condition {COND}\n")
print(f"{'model':16s} " + " ".join(f"{a:>10s}" for a in ARMS))
agg = {a: [] for a in ARMS}
for m in MODELS:
    row, rec = [], {}
    for a in ARMS:
        p = ROOT/"results/cells/inverse_generic"/m/"python"/f"{a}__{COND}"/"trials.parquet"
        if not p.exists(): row.append("--"); continue
        d = pd.read_parquet(p, columns=["snippet_id","item_id","output_raw","format_fail","correct"])
        hit = sum(1 for _, r in d.iterrows()
                  if norm(r["output_raw"]) == norm(gold.get((r["snippet_id"], r["item_id"]), "\x00")))
        c = hit/len(d)
        rec[a] = {"collapse_rate": c, "n": int(len(d)),
                  "format_fail": float(d["format_fail"].mean()), "accuracy": float(d["correct"].mean())}
        agg[a].append(c); row.append(f"{c:.3f}")
    out["by_model"][m] = rec
    print(f"{m:16s} " + " ".join(f"{x:>10s}" for x in row))
out["panel_mean"] = {a: (sum(v)/len(v) if v else None) for a, v in agg.items()}
print(f"\n{'PANEL MEAN':16s} " + " ".join(f"{out['panel_mean'][a]:10.3f}" if out['panel_mean'][a] is not None
                                          else f"{'--':>10s}" for a in ARMS))
p = ROOT/"results/analysis/pipeline"/f"forward_collapse_{COND}.json"
p.write_text(json.dumps(out, indent=1)); print("\nwrote", p.relative_to(ROOT))
