#!/usr/bin/env python
"""E9 / RQ4' — does the identifier-knockout signature track unseen-family robustness? NO H1.

Reads results/attn/knockout/<model>/X1/<system>.json (score mode: teacher-forced log P(gold)
clean vs identifier-keys knocked out; NEGATIVE delta = the knockout hurt). Per-item deltas are
paired across systems on the same items and bootstrapped by program (snippet_id).

Rules (CLAUDE_SCRATCHPAD.md 2026-09-07, verbatim):
  H-attn-cons   "cons_lam3 depends less on identifier keys on X1 than mono_all does":
                CONFIRMED iff mean(delta_cons − delta_mono) has ci_lo > 0 (cons loses LESS logp).
  H-attn-breadth "breadth makes the model MORE identifier-dependent on the unseen family":
                CONFIRMED iff mean(delta_mono − delta_L0) has ci_hi < 0.
  H-attn-order  reported: Spearman between per-system mean knockout damage and per-system X1
                accuracy across the five arms (n=5 — descriptive only, never a test).
Support for RQ4', not a causal claim about transfer; that would need the intervention on the
transfer itself (log/attention/README.md).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cellkit as ck  # noqa: E402

SYSTEMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]


def load(model: str, system: str, cond: str):
    p = ck.ROOT / "results" / "attn" / "knockout" / model / cond / f"{system}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    rows = {r["item_id"]: r for r in d["rows"]}
    return d["summary"], rows


def paired(rows_a, rows_b, key="delta_logp", n=2000, seed=17):
    ids = sorted(set(rows_a) & set(rows_b))
    prog = {}
    for i in ids:
        prog.setdefault(i.split("::")[0], []).append(rows_a[i][key] - rows_b[i][key])
    progs = sorted(prog)
    vals = [np.asarray(prog[p]) for p in progs]
    rng = np.random.default_rng(seed)
    draws = np.empty(n)
    for k in range(n):
        pick = rng.choice(len(progs), size=len(progs), replace=True)
        draws[k] = np.concatenate([vals[j] for j in pick]).mean()
    point = float(np.concatenate(vals).mean())
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    return {"value": round(point, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
            "n_items": len(ids), "n_programs": len(progs), "excludes_zero": bool(lo > 0 or hi < 0)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--condition", default="X1")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = ck.new_result("RQ4'", Path(__file__).name, [a.model])
    ko = {s: load(a.model, s, a.condition) for s in SYSTEMS}
    ko = {s: v for s, v in ko.items() if v}
    res["knockout"] = {s: v[0] for s, v in ko.items()}
    print(f"=== {a.model} knockout on {a.condition} ===")
    for s, (summ, _) in ko.items():
        print(f"  {s:<12} mean Δlogp {summ['mean_delta_logp']:+.4f}  (n={summ['n_items']}, keys {summ['mean_keys_knocked']:.1f})")
    P = res.setdefault("paired", {})
    for x, y in [("cons_lam3", "mono_all"), ("mono_all", "tuned_L0"), ("cons_lam3", "tuned_L0"),
                 ("tuned_X1", "tuned_L0"), ("tuned_L0", "base")]:
        if x in ko and y in ko:
            P[f"{x} - {y}"] = paired(ko[x][1], ko[y][1])
            r = P[f"{x} - {y}"]
            print(f"  Δ({x}) − Δ({y}) = {r['value']:+.4f} [{r['ci_lo']:+.4f}, {r['ci_hi']:+.4f}]{'*' if r['excludes_zero'] else ''}")
    r = P.get("cons_lam3 - mono_all")
    ck.hypothesis(res, "H-attn-cons", "Δ(cons) − Δ(mono) ci_lo>0 on X1",
                  "PENDING" if not r else "CONFIRMED" if r["ci_lo"] > 0 else "REFUTED",
                  f"{r}" if r else "cells missing")
    r = P.get("mono_all - tuned_L0")
    ck.hypothesis(res, "H-attn-breadth", "Δ(mono) − Δ(L0) ci_hi<0 on X1",
                  "PENDING" if not r else "CONFIRMED" if r["ci_hi"] < 0 else "REFUTED",
                  f"{r}" if r else "cells missing")
    # descriptive ordering against X1 accuracy (never a test at n=5)
    b = ck.load_block(["x1_split", "objectives_generic", "x1_generic"], a.model, list(ko), [a.condition], quiet=True)
    acc = {s: float(b[s][a.condition]["correct"].mean()) for s in ko if s in b}
    if len(acc) >= 4:
        from scipy.stats import spearmanr
        ss = sorted(acc)
        rho = spearmanr([res["knockout"][s]["mean_delta_logp"] for s in ss], [acc[s] for s in ss]).correlation
        res["order"] = {"systems": ss, "x1_acc": acc, "spearman": None if rho != rho else round(float(rho), 3)}
        ck.hypothesis(res, "H-attn-order", "descriptive only (n≤5)", "REPORTED",
                      f"Spearman(knockout damage, X1 acc) = {res['order']['spearman']} over {ss}")
    ck.print_hyps(res)
    ck.write(res, a.out)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
