#!/usr/bin/env python
"""A1+A2: re-score the backward task under a uniform, arm-blind answer contract.

    python scripts/analysis/81_rescore_backward.py [--models m1 m2] [--conds c1 c2]

THE PROBLEM. `SYSTEM_PROMPT_INVERSE` rule 1 asks for `name(arg1, ...)`. Some arms reply with
the ARGUMENTS and no call wrapper -- CodeLlama-13B breadth answers " 3,2,1 ", CodeLlama-34B
answers ' "1+(2+3)" ' -- and `extract_call` rejects those, so the cell exceeds the 0.25 format
gate and leaves every mean. Three arms disappear from Table 5's reverse row that way.

Rerunning them does not help: the prompt already states the required form, and the 34B router
eval run on 2026-09-20 wrote all 16 cells and had all 16 gated. The models are ignoring the
contract, not being misprompted.

WHY THIS IS THE RIGHT FIX AND NOT SCORE INFLATION. The wrapper carries no information: the
entry point is GIVEN in the prompt, and `extract_call` discards the name it parses anyway --
grading executes the arguments. Refusing a correctly-formed argument list therefore measures
adherence to a convention, not reverse reasoning, which is precisely the conflation the
backward decomposition exists to separate.

HOW. Outputs that fail the strict parse but are a valid literal tuple are rewritten as
`entry_point(args)` and then graded by the UNCHANGED strict grader. Nothing in src/ is
modified and no grading rule is relaxed: the recovered reply is scored exactly as if the model
had written the wrapper. The rule is applied to EVERY arm and model, including the ones that
need it least, and the strict rate is reported beside the recovered one so the size of the
correction is visible per arm.
"""
from __future__ import annotations
import sys, ast, json, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts/analysis"))

BWD = ["inverse_1shot", "inverse_generic"]
ARMS = ["base", "tuned_L0", "mono_all", "cons_lam3", "mole_router", "merge_dare_ties"]
NICE = {"base": "Base", "tuned_L0": "Clean", "mono_all": "Breadth",
        "cons_lam3": "KL", "mole_router": "Router", "merge_dare_ties": "Merge"}
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "X1",
         "C_L1b_S1", "C_L1r_S1", "C_S1_L1r", "C_L2_S4", "C_L1r_S3", "C_S4_S3",
         "C_L1r_X1", "C_X1_S1", "C_S2_X1"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]

def repair(text: str, entry: str) -> tuple[str, bool]:
    """Return (possibly rewritten output, was_repaired). Strict-parsing replies are untouched."""
    from obtune.inverse import extract_call
    if extract_call(text)[0]:
        return text, False
    s = text.strip().strip("`").strip()
    if not s or "\n" in s:
        return text, False
    try:
        v = ast.literal_eval(f"({s.rstrip(',')},)")
    except Exception:
        return text, False
    if not isinstance(v, tuple):
        return text, False
    return f"{entry}({s.rstrip(',')})", True

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=MODELS)
    ap.add_argument("--conds", nargs="*", default=CONDS)
    a = ap.parse_args()
    from cellkit import load_cell
    from obtune.data import load_eval_items
    from obtune.inverse import grade_batch

    items_by_cond = {}
    for c in a.conds:
        try:
            items_by_cond[c] = {it.item_id: it for it in
                                load_eval_items([c], "python", script=__file__, source="heldout")}
        except FileNotFoundError:
            pass

    out = {}
    print(f"{'model':16s} {'arm':8s} {'strict fmt':>10s} {'rep fmt':>8s} "
          f"{'strict acc':>10s} {'rescored':>9s} {'delta':>7s}")
    for m in a.models:
        for arm in ARMS:
            its, outs, reps, n_rep, n = [], [], [], 0, 0
            strict_ok = 0
            for c in a.conds:
                d = load_cell(BWD, m, arm, c)
                if d is None or c not in items_by_cond: continue
                idx = items_by_cond[c]
                for iid, raw in zip(d.item_id, d.output_raw):
                    it = idx.get(iid)
                    if it is None: continue
                    n += 1
                    fixed, rep = repair(raw, it.entry_point)
                    if not rep: strict_ok += 1
                    n_rep += rep
                    # Track the flag HERE. Recomputing it later from `outs` is wrong: those
                    # strings are already repaired, so repair() returns False for every one and
                    # the strict column silently equals the rescored one -- which is exactly
                    # what the first run printed, +0.000 for all twelve arms.
                    reps.append(rep)
                    its.append(it); outs.append(fixed)
            if not n: continue
            g = grade_batch(its, outs)
            acc = sum(1 for x in g if x.correct)/len(g)
            # strict accuracy: a repaired reply was unparseable under the strict contract,
            # so it scored 0 there. Use the flags captured at collection time.
            sacc = sum(1 for x, r in zip(g, reps) if x.correct and not r)/len(g)
            rec = out.setdefault(m, {})[NICE[arm]] = dict(
                n=n, strict_format=round(strict_ok/n, 4), repaired=round(n_rep/n, 4),
                strict_acc=round(sacc, 4), rescored_acc=round(acc, 4))
            print(f"{m:16s} {NICE[arm]:8s} {rec['strict_format']:10.2f} {rec['repaired']:8.2f} "
                  f"{rec['strict_acc']:10.3f} {rec['rescored_acc']:9.3f} "
                  f"{rec['rescored_acc']-rec['strict_acc']:+7.3f}")
    f = ROOT/"results/analysis/pipeline/backward_rescored.json"
    f.write_text(json.dumps(out, indent=2)); print(f"\nwrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
