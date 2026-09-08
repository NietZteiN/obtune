#!/usr/bin/env python
"""E11 — what does each arm cost on CLEAN code? (§4 item 7, forgetting), 7B. NO H1.

Every system that has an L0 cell in any of the listed phases is contrasted against tuned_L0
on L0 with a TOST margin of ±1.0 pt. Rule (pre-registered 2026-09-07): an arm is
"L0-free" iff equivalent at ±1.0; "pays an L0 cost" iff ci_hi < 0; "underpowered" otherwise.
Reported per arm; gates nothing. The headline use is the RQ1' cost column: an arm that buys
unseen-family robustness by giving up clean-code accuracy has not learned invariance.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

PHASES = ["objectives_teacher", "objectives_llama", "x1_split", "saturation",
          "objectives_generic", "x1_generic", "rq1_generic", "rq2_generic"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ4' (support)", Path(__file__).name, [a.model])
    systems = set()
    for ph in PHASES:
        d = ck.CELLS / ph / a.model / "python"
        if d.exists():
            systems |= {p.name[:-4] for p in d.iterdir() if p.name.endswith("__L0")}
    systems = sorted(systems - {"tuned_L0"})
    b = ck.load_block(PHASES, a.model, systems + ["tuned_L0"], ["L0"], quiet=True)
    res["accuracy"][a.model], res["format_fail"][a.model] = ck.acc_table(b)
    C = res["contrasts"].setdefault(a.model, {})
    rows = []
    for s in systems:
        r = ck.contrast(b, s, "tuned_L0", ["L0"], label=f"{s} - tuned_L0 @ L0", eq_margin=1.0)
        if r:
            C[f"{s} - tuned_L0 @ L0"] = r
            cls = "L0-free" if r.get("equivalent") else "pays L0 cost" if r["ci_hi"] < 0 else \
                  "gains on L0" if r["ci_lo"] > 0 else "underpowered"
            rows.append((s, r, cls))
    rows.sort(key=lambda x: x[1]["value_pts"], reverse=True)
    print(f"=== {a.model}: L0 cost vs tuned_L0 ({len(rows)} arms) ===")
    for s, r, cls in rows:
        print(f"  {s:<28} {ck.fmt(r):<42} {cls}")
    res["classes"] = {s: cls for s, _, cls in rows}
    n_cost = sum(cls == "pays L0 cost" for _, _, cls in rows)
    ck.hypothesis(res, "L0-cost", "per arm: equivalent at ±1.0 = free; ci_hi<0 = cost (reported)", "REPORTED",
                  f"{n_cost}/{len(rows)} arms pay an L0 cost; " +
                  ", ".join(f"{s}={cls}" for s, _, cls in rows if s in {"mono_all", "cons_lam3", "tuned_X1", "cons_tbase", "cons_tmono"}))
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
