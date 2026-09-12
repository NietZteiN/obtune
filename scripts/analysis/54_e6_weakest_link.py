#!/usr/bin/env python
"""E6 — is X1's half-adapter gain a WEAKEST-LINK effect or adaptation to the family's SURFACE?

    python scripts/analysis/54_e6_weakest_link.py

THE OPEN QUESTION (log/transfer/2026-09-08_x1-split-mechanism-not-family.md). Either half of X1
recovers ~90 % of the whole adapter's gain on stacked X1 (+4.12 / +4.20 of +4.61) while
transferring almost nothing to the other half's condition. That is not additive, and two readings
fit it: (i) WEAKEST-LINK -- an X1 item fails on whichever mechanism the model meets first, so
relieving either unlocks most items; (ii) SURFACE -- the gain is adaptation to the family's
scaffolding (helper preamble, longer code, the X1 prompt distribution), which either half's
training data carries.

THE DISCRIMINATOR IS PROGRAMS WITH ONLY ONE MECHANISM. X1's site bar is on the TOTAL, so many
programs carry arithmetic sites and no strings, or the reverse. A half-adapter evaluated on a
program containing none of the mechanism it was trained on can only gain through surface. That is
a sharper test than the item-ordering one registered on 09-08, which needs both mechanisms present
and leaves only 156 programs; both are computed here and the ordering test is reported beside it.

Rules and their limits were pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-11 before any
accuracy below was computed. No H1: every cell is X1-family (CLAUDE.md 3.2).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from cellkit import load_cell  # noqa: E402

MODEL = "codellama-7b"
PHASES = ["x1_split", "x1_generic", "rq2_generic"]
N_BOOT, SEED, EQ_MARGIN = 2000, 17, 1.5

# The helper preamble is emitted verbatim at the top of EVERY X1 variant, so the definitions of
# `_rs` and `_ar_*` are always present and must not be mistaken for uses. `_ar_x` is the last
# helper defined, so everything after its body is the program itself.
PREAMBLE_END = "def _ar_x(a, b):"
RE_MBA = re.compile(r"_ar_[pmx]\(")
RE_STR = re.compile(r"_rs\(")


def classify(code: str) -> str:
    body = code.split(PREAMBLE_END)[-1]
    m, s = RE_MBA.search(body), RE_STR.search(body)
    if m and s:
        return "mba_first" if m.start() < s.start() else "str_first"
    if m:
        return "mba_only"
    if s:
        return "str_only"
    # No helper CALL at all: X1's third mechanism, int-literal expansion (0 -> -39174 + 39174),
    # applied on its own. These programs carry the full scaffolding and no helper use, which makes
    # them the purest surface cell in the set -- and the smallest.
    return "expansion_only"


def _by_program(df, keep):
    return {pid: g["correct"].to_numpy(dtype=float)
            for pid, g in df.groupby("snippet_id") if pid in keep}


def contrast(treat, control, progs, label):
    A, B = _by_program(treat, progs), _by_program(control, progs)
    P = sorted(set(A) & set(B))
    if len(P) < 2:
        return {"label": label, "n_programs": len(P), "value_pts": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan"),
                "excludes_zero": False, "equivalent": None}
    rng = np.random.default_rng(SEED)
    idx = np.arange(len(P))

    def d(pick):
        a = np.concatenate([A[P[j]] for j in pick])
        b = np.concatenate([B[P[j]] for j in pick])
        return (a.mean() - b.mean()) * 100.0

    draws = np.array([d(rng.choice(idx, size=len(P), replace=True)) for _ in range(N_BOOT)])
    pt = d(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    elo, ehi = (float(x) for x in np.percentile(draws, [5.0, 95.0]))
    return {"label": label, "n_programs": len(P),
            "n_items": int(sum(len(A[p]) for p in P)),
            "value_pts": pt, "ci_lo": lo, "ci_hi": hi,
            "excludes_zero": bool(lo > 0 or hi < 0),
            "equivalent": bool(elo > -EQ_MARGIN and ehi < EQ_MARGIN),
            "eq_margin_pts": EQ_MARGIN}


def main() -> int:
    items = [json.loads(l) for l in (ROOT / "data/eval/heldout/items/X1/python.jsonl").open()]
    code_by_prog = {}
    for r in items:
        code_by_prog.setdefault(r["program_id"], r["code"])
    groups: dict[str, set[str]] = {}
    for pid, code in code_by_prog.items():
        groups.setdefault(classify(code), set()).add(pid)

    cells = {}
    for s in ["tuned_L0", "tuned_X1", "tuned_X1m", "tuned_X1s", "mono_all", "base"]:
        df = load_cell(PHASES, MODEL, s, "X1")
        if df is None:
            print(f"MISSING cell {s}__X1", file=sys.stderr)
            return 1
        cells[s] = df

    out = {
        "script": "54_e6_weakest_link.py",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "model": MODEL, "eval_condition": "X1",
        "n_resamples": N_BOOT, "seed": SEED, "eq_margin_pts": EQ_MARGIN,
        "group_sizes": {k: len(v) for k, v in sorted(groups.items())},
        "by_group": {},
    }
    print("program groups:", out["group_sizes"], "\n")

    arms = ["tuned_X1", "tuned_X1m", "tuned_X1s", "mono_all"]
    for g, progs in sorted(groups.items()):
        out["by_group"][g] = {}
        print(f"--- {g} (n={len(progs)}) ---")
        for arm in arms:
            c = contrast(cells[arm], cells["tuned_L0"], progs, f"{arm} - tuned_L0")
            out["by_group"][g][c["label"]] = c
            star = "*" if c["excludes_zero"] else ("=" if c["equivalent"] else " ")
            print(f"   {c['label']:26s} {c['value_pts']:+6.2f} "
                  f"[{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{star}")
        print()

    # --- the order test, among programs carrying BOTH mechanisms -------------------------
    both = groups.get("mba_first", set()) | groups.get("str_first", set())
    A = _by_program(cells["tuned_X1m"], both)
    B = _by_program(cells["tuned_L0"], both)
    mf = sorted(groups.get("mba_first", set()) & set(A) & set(B))
    sf = sorted(groups.get("str_first", set()) & set(A) & set(B))
    rng = np.random.default_rng(SEED)

    def half(pick, P):
        a = np.concatenate([A[P[j]] for j in pick])
        b = np.concatenate([B[P[j]] for j in pick])
        return (a.mean() - b.mean()) * 100.0

    draws = np.empty(N_BOOT)
    for i in range(N_BOOT):
        draws[i] = (half(rng.choice(np.arange(len(mf)), len(mf), True), mf)
                    - half(rng.choice(np.arange(len(sf)), len(sf), True), sf))
    pt = half(np.arange(len(mf)), mf) - half(np.arange(len(sf)), sf)
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    order = {"label": "tuned_X1m gain: mba_first - str_first",
             "n_mba_first": len(mf), "n_str_first": len(sf),
             "value_pts": pt, "ci_lo": lo, "ci_hi": hi,
             "excludes_zero": bool(lo > 0 or hi < 0)}
    out["order_test"] = order
    print(f"--- order test (both-mechanism programs) ---\n   {order['label']}: "
          f"{pt:+6.2f} [{lo:+6.2f}, {hi:+6.2f}]"
          f"{'*' if order['excludes_zero'] else ''}   "
          f"(n {len(mf)} mba-first vs {len(sf)} str-first)\n")

    a = out["by_group"].get("mba_only", {}).get("tuned_X1s - tuned_L0")
    b = out["by_group"].get("str_only", {}).get("tuned_X1m - tuned_L0")

    def rule(c):
        if c is None:
            return "NO DATA"
        if c["ci_lo"] > 0:
            return "SURFACE"
        if c["equivalent"]:
            return "MECHANISM"
        return "INCONCLUSIVE"

    va, vb = rule(a), rule(b)
    verdict = ("surface" if va == "SURFACE" and vb == "SURFACE" else
               "weakest-link" if va == "MECHANISM" and vb == "MECHANISM"
               and order["ci_lo"] > 0 else "undecided")
    out["hypotheses"] = [
        {"id": "H-E6-surface-a", "rule": "tuned_X1s - tuned_L0 on mba_only: SURFACE iff ci_lo>0, "
                                         "MECHANISM iff TOST-equivalent at +/-1.5",
         "verdict": va, "evidence": a,
         "limit": ("tuned_X1s pays the campaign's largest L0 cost (-4.37) and is the only arm "
                   "trained at a 4,096-token window; that global deficit biases this test toward "
                   "zero, so a null here is weak evidence and a positive is strong.")},
        {"id": "H-E6-surface-b", "rule": "tuned_X1m - tuned_L0 on str_only: same rule",
         "verdict": vb, "evidence": b,
         "limit": "str_only has 51 programs; underpowered, so a null here means little."},
        {"id": "H-E6-order", "rule": "tuned_X1m gain larger on mba_first than str_first: "
                                     "WEAKEST-LINK iff ci_lo>0",
         "verdict": "WEAKEST-LINK" if order["ci_lo"] > 0 else
                    ("AGAINST" if order["ci_hi"] < 0 else "INCONCLUSIVE"),
         "evidence": order},
    ]
    out["verdict"] = verdict
    for h in out["hypotheses"]:
        print(f"{h['id']:20s} {h['verdict']}")
    print(f"\nE6 reading: {verdict}")

    dst = ROOT / "results/analysis/pipeline/e6_weakest_link_codellama7b.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(f"wrote {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
