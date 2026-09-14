#!/usr/bin/env python
"""Every backward format failure on the panel, sorted into what would fix it.

    python scripts/analysis/71_backward_defects.py

67_backward_failure_modes.py showed, on one condition, that the single `format_fail` bit hides four
different failures. This runs the same decomposition over EVERY backward cell on all eight models
and sorts each failure by the remedy it needs, so the question "what should be fixed about input
prediction" is answered by counts rather than by the two cells someone happened to look at.

  stop_newline      a valid single POSITIONAL call on line 1, then more text. Fixed by a "\\n" stop
                    string, which the backward configs never carried (they inherit "\\n\\n"). Exactly
                    equivalent to re-grading on the first line, because that is what the stop would
                    have returned.
  keyword_args      a single call whose arguments are keyword=literal. The contract says "a single
                    call whose arguments are literals" and the parser rejects these on syntax alone.
                    Fixable only by reordering against the function signature.
  expression        call-shaped, single line, but an argument is an expression rather than a literal
                    (`2*3`, `-30829 + 30829`, `pi`). REJECTED BY DESIGN and stays rejected: a model
                    that copies an MBA constant instead of simplifying it has not found the input.
  truncated         hit the 128-token cap mid-call. Fixed by max_tokens; cannot be re-graded.
  answered_forward  the reply is the gold forward answer. A result, not a defect.
  malformed         nothing call-shaped anywhere. The failure the gate exists to catch.
"""
from __future__ import annotations

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
from obtune.inverse import _unwrap, extract_call  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from cellkit import trials_path  # noqa: E402  (v1 by default here: this script measures the defect v2 removes)

CELLS = ROOT / "results" / "cells"
PHASES = ["inverse_1shot", "inverse_generic"]
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1",
         "C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3",
         "C3_L1r_S3_S4", "C3_S1_S3_S4", "C3_L1r_S1_S4", "C4_L1r_S1_S3_S4",
         "C_L1r_X1", "C_X1_S1", "C_S2_X1", "C_L1r_X1m", "C_S1_X1s", "C3_L1r_S1_X1"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
ARMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "tuned_X1", "merge_dare_ties", "merge_ties"]
MAX_TOKENS = 128
KINDS = ["stop_newline", "keyword_args", "expression", "truncated", "answered_forward", "malformed"]


def _norm(x):
    return str(x).strip().strip('"').strip("'").replace(" ", "")


def _call_shape(line: str):
    """(is_call_shaped, has_keyword, literal_ok) for one line."""
    s = _unwrap(line)
    i = s.find("(")
    if i < 0 or not s.endswith(")"):
        return False, False, False
    try:
        node = ast.parse(s, mode="eval")
    except SyntaxError:
        return False, False, False
    if not isinstance(node.body, ast.Call):
        return False, False, False
    has_kw = bool(node.body.keywords)
    lit_ok = extract_call(line)[0]
    return True, has_kw, lit_ok


def classify(raw, ntok, gold_fwd):
    if _norm(raw) == gold_fwd:
        return "answered_forward"
    s = _unwrap(str(raw))
    lines = [l for l in s.splitlines() if l.strip()]
    first = lines[0] if lines else ""
    multiline = len(lines) > 1
    shaped, kw, lit = _call_shape(first)
    if shaped and lit and multiline:
        return "stop_newline"
    if shaped and kw:
        return "keyword_args"
    if shaped and not lit:
        return "expression"
    if ntok is not None and ntok >= MAX_TOKENS:
        return "truncated"
    return "malformed"


def main() -> int:
    gold = {c: {(i.program_id, i.item_id): _norm(i.output_repr)
                for i in load_eval_items([c], "python", source="heldout")} for c in CONDS}
    out = {"script": "71_backward_defects.py",
           "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "conditions": CONDS, "max_tokens": MAX_TOKENS, "by_model_arm": {}, "panel": {}}
    panel = Counter(); panel_n = panel_fail = 0
    print(f"{'model':15s} {'arm':16s} {'n':>6s} {'fail':>6s}  " + " ".join(f"{k[:9]:>9s}" for k in KINDS))
    for m in MODELS:
        for arm in ARMS:
            k = Counter(); n = nf = 0
            for c in CONDS:
                p = next((trials_path(CELLS/ph/m/"python"/f"{arm}__{c}") for ph in PHASES
                          if (CELLS/ph/m/"python"/f"{arm}__{c}"/"trials.parquet").exists()), None)
                if p is None:
                    continue
                d = pd.read_parquet(p, columns=["snippet_id", "item_id", "output_raw", "format_fail",
                                                "n_gen_tokens"])
                n += len(d)
                bad = d[d["format_fail"] == 1]
                nf += len(bad)
                g = gold[c]
                for sid, iid, raw, nt in zip(bad["snippet_id"], bad["item_id"], bad["output_raw"],
                                             bad["n_gen_tokens"]):
                    k[classify(raw, nt, g.get((sid, iid), "\x00"))] += 1
            if not n:
                continue
            panel.update(k); panel_n += n; panel_fail += nf
            out["by_model_arm"][f"{m}/{arm}"] = {"n": n, "n_fail": nf, **{x: k[x] for x in KINDS}}
            print(f"{m:15s} {arm:16s} {n:6d} {nf:6d}  " + " ".join(f"{k[x]:9d}" for x in KINDS))
    print(f"\n{'PANEL':15s} {'':16s} {panel_n:6d} {panel_fail:6d}  " + " ".join(f"{panel[x]:9d}" for x in KINDS))
    print(f"{'as % of trials':32s} {'':6s} {100*panel_fail/panel_n:5.1f}%  "
          + " ".join(f"{100*panel[x]/panel_n:8.2f}%" for x in KINDS))
    print(f"{'as % of failures':32s} {'':6s} {'':6s}  "
          + " ".join(f"{100*panel[x]/max(panel_fail,1):8.1f}%" for x in KINDS))
    out["panel"] = {"n": panel_n, "n_fail": panel_fail, **{x: panel[x] for x in KINDS}}
    p = ROOT / "results/analysis/pipeline/backward_defects.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
