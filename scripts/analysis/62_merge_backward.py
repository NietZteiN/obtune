#!/usr/bin/env python
"""H-merge-backward — does weight-space merging pay the backward price every other forward-fitting
method pays?
    python scripts/analysis/62_merge_backward.py [model ...]

Applies the rule pre-registered in CLAUDE_SCRATCHPAD.md on 2026-09-13 BEFORE submission, restated verbatim:
  On CodeLlama-7B, pooled over L0-S2 and X1:
  - CONFIRMED ("merging pays the backward price too") iff the direction ratio of merge_dare_ties is
    negative AND merge_dare_ties - base backwards has ci_hi < 0.
  - REFUTED iff merge_dare_ties - base backwards has ci_lo > 0.
  - otherwise INCONCLUSIVE. The other three models are REPORTED, gate permitting.

Direction ratio = backward gain / forward gain, both against the untuned model, as in 58_direction_ratio.py.
Forward cells come from panel_core / merge_panel; backward from inverse_generic. Cells over the 0.25
format gate are excluded and named.

⚠️ PROMPT CONFOUND, FOUND 2026-09-14 AND NOT YET REPAIRED IN THIS SCRIPT'S OUTPUT.
This script reads the backward LADDER (L0-S2, X1), and on the seven non-CodeLlama-7B models those
cells were written by `inverse_core.yaml` with NO one-shot demo (`prompt_id: inverse_v1`), while the
merge arms it compares them against came from `inverse_merge.yaml` WITH one (`inverse_1shot_v1`).
The difference is large -- CodeGemma's `mono_all` sits at 0.882 format-failure zero-shot and 0.086
one-shot on a comparable condition -- so this script's format-gate exclusions and part of its merge
advantage are a prompt difference, not a method difference. The repair is queued as
`inverse_ladder_1shot.yaml` into phase `inverse_1shot`; once those cells land, change PHASES below
to ["inverse_1shot", "inverse_generic"] and re-read. The STACK-based reads
(65_backward_stacks.py, 66_three_methods.py) are unaffected: every arm there is one-shot.
"""
from __future__ import annotations
import datetime as dt, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis")); sys.path.insert(0, str(ROOT / "src"))
from cellkit import check_one_prompt, load_cell  # noqa: E402
MODELS = sys.argv[1:] or ["codellama-7b", "llama31-8b", "starcoder2-15b", "granite31-8b"]
LADDER = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1"]
ARMS = ["merge_dare_ties", "merge_ties"]
REF = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1"]
# inverse_1shot FIRST: it holds the ladder re-read with the one-shot prompt the merge arms always
# had. Until the repair lands for a model, that model still reads the zero-shot cells and the
# registry in cellkit warns -- which is the intended behaviour, not a bug to silence.
PH_B = ["inverse_1shot", "inverse_generic"]; PH_F = ["merge_panel", "panel_core", "rq2_generic"]
N_BOOT, SEED, FMT_MAX = 2000, 17, 0.25

def fmt_rate(df):
    if "format_ok" in df: return float(1.0 - df["format_ok"].mean())
    if "format_fail" in df: return float(df["format_fail"].mean())
    return 0.0

def _by(df, keep):
    return {p: g["correct"].to_numpy(dtype=float) for p, g in df.groupby("snippet_id") if p in keep}

def pooled(cells, treat, control, conds, progs):
    # This script has its OWN pooled(), so cellkit's guard never sees these frames. It has to be
    # called explicitly, and this is the contrast the 2026-09-14 prompt fault actually distorts:
    # the merge arms are one-shot and base/breadth/anchored are zero-shot on seven of eight models.
    check_one_prompt([cells[(treat, c)] for c in conds] + [cells[(control, c)] for c in conds],
                     label=f"{treat} - {control}")
    A = {c: _by(cells[(treat, c)], progs) for c in conds}; B = {c: _by(cells[(control, c)], progs) for c in conds}
    P = sorted(progs); rng = np.random.default_rng(SEED); idx = np.arange(len(P))
    def d(pick):
        a = np.concatenate([np.concatenate([A[c][P[j]] for j in pick]) for c in conds])
        b = np.concatenate([np.concatenate([B[c][P[j]] for j in pick]) for c in conds])
        return (a.mean() - b.mean()) * 100.0
    draws = np.array([d(rng.choice(idx, len(P), True)) for _ in range(N_BOOT)]); pt = d(np.arange(len(P)))
    lo, hi = (float(x) for x in np.percentile(draws, [2.5, 97.5]))
    return {"value_pts": float(pt), "ci_lo": lo, "ci_hi": hi, "n_programs": len(P), "excludes_zero": bool(lo > 0 or hi < 0)}

def s(c): return f"{c['value_pts']:+6.2f} [{c['ci_lo']:+6.2f}, {c['ci_hi']:+6.2f}]{'*' if c['excludes_zero'] else ' '}"

def run(model):
    fwd, bwd, gated, missing = {}, {}, [], []
    for sy in ARMS + REF:
        for c in LADDER:
            b = load_cell(PH_B, model, sy, c); f = load_cell(PH_F, model, sy, c)
            if b is None or f is None:
                if sy in ARMS or sy in ("base",): missing.append(f"{sy}__{c}({'bwd' if b is None else 'fwd'})")
                continue
            if fmt_rate(b) > FMT_MAX: gated.append(f"{sy}__{c}"); continue
            bwd[(sy, c)] = b; fwd[(sy, c)] = f
    if missing:
        print(f"{model}: incomplete, refusing to read: {missing[:8]}", file=sys.stderr); return None
    arms = [a for a in ARMS if all((a, c) in bwd for c in LADDER)]
    if not arms:
        print(f"{model}: every merge arm has a format-gated backward cell ({gated[:6]}) -- not read", file=sys.stderr); return None
    conds = [c for c in LADDER if all((sy, c) in bwd for sy in arms + ["base"])]
    # THE UNTUNED MODEL CAN BE ABSENT. StarCoder2's backward `base` cells are format-failure 1.00 on
    # every condition -- the untuned model emits nothing parseable in this direction -- so every
    # contrast against it, and the direction ratio with it in the denominator, is undefined. Report
    # the merge arms' absolute accuracy and say so, rather than dividing by a zero that is a prompt
    # contract failure and not a capability (CLAUDE.md 4, item 6).
    if not conds:
        out = {"script": "62_merge_backward.py", "model": model,
               "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "no_untuned_reference": "every backward `base` cell exceeds the format gate; no contrast or "
                                       "direction ratio is defined on this model",
               "format_gated_cells": gated,
               "absolute_backward_accuracy": {f"{sy}__{c}": float(df["correct"].mean())
                                              for (sy, c), df in bwd.items() if sy in arms}}
        print(f"\n=== {model} ===\n  no untuned backward reference: every `base` cell is format-gated.")
        for k, v in sorted(out["absolute_backward_accuracy"].items()): print(f"    {k:28s} {v:.3f}")
        p = ROOT / "results/analysis/pipeline" / f"merge_backward_{model.replace('-', '')}.json"
        p.write_text(json.dumps(out, indent=1)); print("  wrote", p.relative_to(ROOT)); return out
    progs = None
    for sy in arms + ["base"]:
        for c in conds:
            for d0 in (bwd, fwd):
                ss = set(d0[(sy, c)]["snippet_id"]); progs = ss if progs is None else progs & ss
    out = {"script": "62_merge_backward.py", "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "model": model, "conditions_read": conds, "format_gated_cells": gated, "n_resamples": N_BOOT, "seed": SEED, "arms": {}}
    print(f"\n=== {model} ({len(progs)} programs, conditions {conds}) ===")
    if gated: print("  format-gated, excluded:", gated)
    for sy in arms + [r for r in REF if r != "base" and all((r, c) in bwd for c in conds)]:
        b = pooled(bwd, sy, "base", conds, progs); f = pooled(fwd, sy, "base", conds, progs)
        dr = (b["value_pts"] / f["value_pts"]) if abs(f["value_pts"]) > 1e-9 else None
        out["arms"][sy] = {"backward_vs_base": b, "forward_vs_base": f, "direction_ratio": dr}
        print(f"  {sy:18s} fwd {s(f)}   bwd {s(b)}   DR {dr:+.2f}" if dr is not None else f"  {sy:18s} fwd {s(f)}   bwd {s(b)}")
    if model == "codellama-7b" and "merge_dare_ties" in out["arms"]:
        a = out["arms"]["merge_dare_ties"]; b = a["backward_vs_base"]; dr = a["direction_ratio"]
        verdict = ("REFUTED" if b["ci_lo"] > 0 else
                   "CONFIRMED" if (dr is not None and dr < 0 and b["ci_hi"] < 0) else "INCONCLUSIVE")
        out["hypotheses"] = [{"id": "H-merge-backward",
            "rule": "CONFIRMED iff merge_dare_ties direction ratio < 0 AND merge_dare_ties - base backwards ci_hi < 0; "
                    "REFUTED iff that ci_lo > 0; else INCONCLUSIVE",
            "verdict": verdict, "evidence": {"direction_ratio": dr, "backward_vs_base": b}}]
        print(f"  H-merge-backward  {verdict}  (DR {dr:+.2f}, bwd {s(b)})")
    p = ROOT / "results/analysis/pipeline" / f"merge_backward_{model.replace('-', '')}.json"
    p.write_text(json.dumps(out, indent=1)); print("  wrote", p.relative_to(ROOT)); return out

if __name__ == "__main__":
    for m in MODELS: run(m)
