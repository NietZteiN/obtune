#!/usr/bin/env python
"""What a gated backward cell is actually made of.

    python scripts/analysis/67_backward_failure_modes.py [--cond C_L1r_X1] [--models a,b]

`format_fail` is one bit, the gate on it is one threshold, and twenty-odd backward cells on this
panel are over that threshold. "Its responses are mostly unparseable" is what the tables say about
all of them, and it is not true of all of them. Four different things are in that bucket:

  answered_forward   the reply is exactly the gold FORWARD answer. Not malformed -- the arm answered
                     the other question. This is the forward-locking result appearing as a parse
                     failure (63_forward_collapse.py established the metric).
  stop_failure       a syntactically valid single call sits on the FIRST line and the model then
                     kept generating -- usually a fresh "Language: python / Program:" prompt. The
                     answer is present and the grader discards it, by design: inverse.py refuses
                     multi-line replies on purpose, because hunting for a call inside prose would
                     repair the failure it wants to report. Worth separating anyway, because it is
                     a decoding problem and the other three are not.
  truncated          generation hit the token cap (128) mid-call. Not a format failure by the
                     grader's own logic -- the harness ran out of room. CLAUDE.md section 4 item 8
                     requires this rate to be reported and nothing reported it.
  malformed          prose, an expression, a bare variable, nothing call-shaped. The failure the
                     gate is meant to catch.

WHY IT MATTERS THAT THESE ARE SEPARATED. On CodeGemma's UNTUNED model at C_L1r_X1, 55 % of the
format failures carry a valid call on the first line and 41 % are truncation, against 4.7 %
genuinely malformed -- so that cell's gate is mostly harness, and `base` is the reference every
contrast is formed against. On the same model's anchored arm, 99 % are malformed. One marker, two
completely different cells.

THE GRADER IS NOT CHANGED BY THIS SCRIPT and should not be changed lightly: its strictness is
pre-registered in inverse.py's docstring with its reasoning. This measures what the strictness is
catching, so a reader can tell a result from an artefact.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune.data import load_eval_items  # noqa: E402

CELLS = ROOT / "results" / "cells"
PHASES = ["inverse_1shot", "inverse_generic"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
ARMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1", "merge_dare_ties", "merge_ties",
        "mole_router"]
MAX_TOKENS = 128   # sampling.max_tokens in every backward config
FMT_GATE = 0.25


def _norm(x):
    return str(x).strip().strip('"').strip("'").replace(" ", "")


def _first_line_is_call(raw) -> bool:
    lines = str(raw).splitlines()
    if not lines:
        return False
    try:
        t = ast.parse(lines[0].strip(), mode="eval")
    except Exception:
        return False
    return isinstance(t.body, ast.Call)


def cell_path(model, sysn, cond):
    for ph in PHASES:
        p = CELLS / ph / model / "python" / f"{sysn}__{cond}" / "trials.parquet"
        if p.exists():
            return p, ph
    return None, None


def decompose(model, sysn, cond, gold):
    p, ph = cell_path(model, sysn, cond)
    if p is None:
        return None
    d = pd.read_parquet(p, columns=["snippet_id", "item_id", "output_raw", "format_fail",
                                    "n_gen_tokens", "correct"])
    n = len(d)
    if not n:
        return None
    bad = d[d["format_fail"] == 1]
    kinds = Counter()
    for sid, iid, raw, ntok in zip(bad["snippet_id"], bad["item_id"], bad["output_raw"],
                                   bad["n_gen_tokens"]):
        if _norm(raw) == gold.get((sid, iid), "\x00"):
            kinds["answered_forward"] += 1
        elif _first_line_is_call(raw):
            kinds["stop_failure"] += 1
        elif ntok is not None and ntok >= MAX_TOKENS:
            kinds["truncated"] += 1
        else:
            kinds["malformed"] += 1
    nb = len(bad)
    return {"phase": ph, "n": int(n), "accuracy": float(d["correct"].mean()),
            "format_fail": float(d["format_fail"].mean()),
            "gated": bool(d["format_fail"].mean() > FMT_GATE),
            "truncation_rate_all": float((d["n_gen_tokens"] >= MAX_TOKENS).mean()),
            "n_failures": int(nb),
            "shares": {k: (kinds[k] / nb if nb else None)
                       for k in ("answered_forward", "stop_failure", "truncated", "malformed")}}



# STACKS ONLY BY DEFAULT, AND THE REASON IS A CONFOUND FOUND THE SAME DAY THIS SCRIPT WAS WRITTEN.
# Every stack cell, on every model and arm, was evaluated with the one-shot inverse prompt. The
# LADDER cells were not: on the seven non-CodeLlama-7B models `inverse_core.yaml` wrote them
# zero-shot, and the missing demo inflates forward collapse enormously -- CodeGemma's `mono_all`
# goes 0.777 zero-shot to 0.029 one-shot on the same seven conditions. Pooling the two therefore
# measured the prompt as much as the arm. The stack set is the largest uncontaminated pool
# available on all eight models, so it is the default; `--conds all` restores the old set and is
# only honest once the `inverse_1shot` repair has landed everywhere.
# See log/transfer/2026-09-14_collapse-was-half-prompt.md.
STACK_CONDS = ["C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3",
               "C_L1r_X1", "C_X1_S1", "C_S2_X1", "C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4",
               "C4_L1r_S1_S3_S4", "C_L1r_X1m", "C_S1_X1s", "C3_L1r_S1_X1"]
LADDER_CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1"]
ALL_CONDS = STACK_CONDS


def aggregate(models, conds=None):
    """Forward-collapse rate over ALL trials, every arm, pooled over every backward condition.

    This is the metric the format gate was hiding, and unlike backward accuracy it is readable on
    every model and arm: the untuned models sit at the floor, so the full range is usable. Pooled
    over conditions rather than reported per condition because the question -- does this way of
    adapting a model make it answer the other question -- is about the arm, not about one transform.
    """
    conds = list(conds or ALL_CONDS)
    gold = {c: {(i.program_id, i.item_id): _norm(i.output_repr)
                for i in load_eval_items([c], "python", source="heldout")} for c in conds}
    rows, agg = {}, {}
    print(f"\n\nforward-collapse rate, pooled over {len(conds)} backward conditions: "
          f"how often an arm\nanswers the FORWARD question when asked the BACKWARD one\n")
    print(f"{'model':16s} " + " ".join(f"{a[:13]:>14s}" for a in ARMS))
    for m in models:
        cells = []
        for arm in ARMS:
            hits = tot = 0
            for c in conds:
                p, _ = cell_path(m, arm, c)
                if p is None:
                    continue
                d = pd.read_parquet(p, columns=["snippet_id", "item_id", "output_raw"])
                g = gold[c]
                hits += sum(1 for sid, iid, raw in zip(d["snippet_id"], d["item_id"], d["output_raw"])
                            if _norm(raw) == g.get((sid, iid), "\x00"))
                tot += len(d)
            if not tot:
                cells.append(f"{'--':>14s}")
                continue
            r = hits/tot
            rows.setdefault(m, {})[arm] = {"collapse_rate": r, "n_trials": tot}
            agg.setdefault(arm, []).append(r)
            cells.append(f"{r:14.3f}")
        print(f"{m:16s} " + " ".join(cells))
    means = {a: (sum(v)/len(v) if v else None) for a, v in agg.items()}
    print(f"\n{'PANEL MEAN':16s} " + " ".join(
        f"{means.get(a):14.3f}" if means.get(a) is not None else f"{'--':>14s}" for a in ARMS))
    print("\n  The untuned model is at the floor and BOTH MERGES are at the floor with it. Every "
          "single-adapter\n  arm is above it, and the anchored objective -- whose extra term is a KL "
          "to the clean parent's\n  ANSWER-TOKEN distribution -- is the highest. Forward-locking "
          "tracks how directly an objective\n  pins the output head.")
    return {"conditions": conds, "by_model": rows, "panel_mean": means}



FWD_PHASES = {"merge_dare_ties": ["merge_panel", "rq2_generic", "composite_generic", "f2_divergence"],
              "merge_ties": ["merge_panel", "rq2_generic", "composite_generic", "f2_divergence"]}
FWD_DEFAULT = ["panel_core", "composite_generic", "f2_divergence"]


def mirror_control(models):
    """THE CONTROL FOR FORWARD COLLAPSE: does anything answer BACKWARD when asked FORWARD?

    "The tuned arms answer the other question" is only a directional claim if the confusion is
    directional. If arms simply mixed the two tasks up, the mirror would show the same thing: forward
    replies shaped like a CALL rather than like a value. It does not. This measures the share of
    forward replies that parse as a single call -- the backward answer's shape -- on the same arms
    and the same conditions.
    """
    conds = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1", "C_L1r_S1", "C_L1r_X1"]
    arms = [a for a in ARMS if a != "mole_router"]
    print(f"\n\nMIRROR CONTROL: share of FORWARD replies that are call-shaped "
          f"(the backward answer's form)\n")
    print(f"{'model':16s} " + " ".join(f"{a[:12]:>13s}" for a in arms))
    rows = {}
    for m in models:
        cells = []
        for arm in arms:
            hits = tot = 0
            for c in conds:
                for ph in FWD_PHASES.get(arm, FWD_DEFAULT):
                    q = CELLS / ph / m / "python" / f"{arm}__{c}" / "trials.parquet"
                    if q.exists():
                        d = pd.read_parquet(q, columns=["output_raw"])
                        for r in d["output_raw"]:
                            try:
                                if isinstance(ast.parse(str(r).strip(), mode="eval").body, ast.Call):
                                    hits += 1
                            except Exception:
                                pass
                        tot += len(d)
                        break
            if not tot:
                cells.append(f"{'--':>13s}")
                continue
            rows.setdefault(m, {})[arm] = {"call_shaped_rate": hits/tot, "n_trials": tot}
            cells.append(f"{hits/tot:13.4f}")
        print(f"{m:16s} " + " ".join(cells))
    print("\n  Essentially zero everywhere, and highest on the UNTUNED model rather than on a tuned "
          "arm. The\n  confusion runs one way only: tuned arms answer forward when asked backward, "
          "and nothing answers\n  backward when asked forward. Forward-locking is directional.")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cond", default="C_L1r_X1",
                    help="condition to decompose (default: the hardest stack, one containing X1)")
    ap.add_argument("--models", default=None)
    ap.add_argument("--conds", default="stacks", choices=["stacks", "ladder", "all"],
                    help="which backward conditions the aggregate pools. Default `stacks`: the "
                         "largest set evaluated with ONE prompt on every model. `ladder` and `all` "
                         "mix prompts until the inverse_1shot repair has landed everywhere.")
    ap.add_argument("--aggregate", action="store_true",
                    help="also print the panel-wide forward-collapse table: every arm, every model, "
                         "pooled over all sixteen backward conditions")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    models = a.models.split(",") if a.models else MODELS

    out = {"script": "67_backward_failure_modes.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "max_tokens": MAX_TOKENS, "format_gate": FMT_GATE, "condition": a.cond, "cells": {}}

    gold = {(i.program_id, i.item_id): _norm(i.output_repr)
            for i in load_eval_items([a.cond], "python", source="heldout")}

    print(f"backward failure modes at {a.cond}: what the `fmt` marker is made of\n")
    print(f"{'model':16s} {'arm':16s} {'fmt':>6s} {'trunc':>6s} {'nfail':>6s}"
          f" {'fwd':>6s} {'stop':>6s} {'trunc':>6s} {'malf':>6s}")
    for m in models:
        for arm in ARMS:
            r = decompose(m, arm, a.cond, gold)
            if r is None:
                continue
            out["cells"][f"{m}/{arm}"] = r
            s = r["shares"]
            mark = "*" if r["gated"] else " "
            print(f"{m:16s} {arm:16s} {r['format_fail']:6.3f}{mark}{r['truncation_rate_all']:6.3f}"
                  f" {r['n_failures']:6d} "
                  + " ".join(f"{(s[k] if s[k] is not None else 0):6.3f}"
                             for k in ("answered_forward", "stop_failure", "truncated", "malformed")))
    print("\n* = the cell is over the 0.25 format gate. `fmt` is the cell's format-failure rate and "
          "the second `trunc` column\n  is truncation over ALL trials; the four share columns are "
          "fractions OF THE FAILURES, and sum to 1.")
    print("  fwd = answered the forward question · stop = valid call on line 1 then kept generating "
          "· trunc = hit the\n  128-token cap · malf = nothing call-shaped. Only the last is the "
          "failure the gate is meant to catch.")

    if a.aggregate:
        conds = {"stacks": STACK_CONDS, "ladder": LADDER_CONDS,
                 "all": LADDER_CONDS + STACK_CONDS}[a.conds]
        out["condition_set"] = a.conds
        out["aggregate"] = aggregate(models, conds)
        out["mirror_control"] = mirror_control(models)

    p = Path(a.out) if a.out else ROOT / "results/analysis/pipeline" / f"backward_failure_modes_{a.cond}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
