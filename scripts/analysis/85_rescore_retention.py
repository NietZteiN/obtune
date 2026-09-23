#!/usr/bin/env python
"""Re-score every retention cell from its saved generations. No GPU.

    python scripts/analysis/85_rescore_retention.py [--model M] [--benchmark mbpp|humaneval]

WHY THIS EXISTS, and why it is the shape it is. Extraction failure on this task is
indistinguishable from catastrophic forgetting: an arm whose replies cannot be recovered
into runnable source scores 0, and the arms that frame answers unusually are exactly the
arms fine-tuned on output prediction. Two such faults were found on 2026-09-22 (a leading
space; a fence with a stray space in its info string), each of which read as a total
collapse on CodeLlama-34B and neither of which was a model result.

`results/forgetting/` could not be re-examined because it kept per-task booleans and
nothing else -- diagnosing it needed the model back on a GPU. `bench_retention` writes
every completion to `results/retention/raw/*.jsonl`, so a change to `extract_code` is a
re-scoring job that runs on a login-adjacent CPU in minutes. This is that job, and it is
the same relationship `72_regrade_inverse.py` has to the backward task.

Rewrites the per-arm JSON in place and prints the delta, so a change of extractor is
always visible as a before/after rather than as a silently different number.
"""
from __future__ import annotations
import sys, json, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))

RES = ROOT/"results"/"retention"
KEYS = ("pass@1_base", "pass@1_plus", "format_fail_rate", "raw_no_def_rate",
        "entry_point_mismatch_rate", "extraction_repaired_rate", "uncompilable_rate")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default=None)
    ap.add_argument("--benchmark", default=None, choices=["mbpp", "humaneval"])
    ap.add_argument("--dry-run", action="store_true",
                    help="print the deltas and write nothing")
    a = ap.parse_args()

    from obtune.bench_retention import score
    from evalplus.data import get_human_eval_plus, get_mbpp_plus

    problems = {}
    rows = []
    for raw_f in sorted((RES/"raw").glob("*.jsonl")):
        bench, rest = raw_f.stem.split("plus_", 1)
        bench = {"humaneval": "humaneval", "mbpp": "mbpp"}[bench]
        if a.benchmark and bench != a.benchmark:
            continue
        # <model>_<arm>: the arm is the last component, models carry hyphens
        for arm in ("base", "tuned_L0", "mono_all", "cons_lam3",
                    "merge_ties", "merge_dare_ties"):
            if rest.endswith("_" + arm):
                model = rest[: -len(arm) - 1]
                break
        else:
            print(f"  SKIP (unrecognised arm): {raw_f.name}"); continue
        if a.model and model != a.model:
            continue
        rows.append((raw_f, bench, model, arm))

    if not rows:
        print("no raw cells matched"); return 0

    for raw_f, bench, model, arm in rows:
        if bench not in problems:
            problems[bench] = get_mbpp_plus() if bench == "mbpp" else get_human_eval_plus()
        recs = [json.loads(l) for l in raw_f.open()]
        tids = [r["task_id"] for r in recs]
        raw = [r["raw"] for r in recs]
        rep = score(bench, problems[bench], tids, raw)
        rep.pop("_pairs", None)

        out = RES/f"{bench}plus_{model}_{arm}.json"
        prev = json.loads(out.read_text()) if out.exists() else {}
        old, new = prev.get("pass@1_plus"), rep["pass@1_plus"]
        d = "" if old is None else f"  ({old:.4f} -> {new:.4f}, {new-old:+.4f})"
        print(f"{model:16s} {bench:9s} {arm:16s} pass@1+ {new:.4f}{d}"
              f"  repaired {rep['extraction_repaired_rate']:.3f}"
              f"  uncompilable {rep['uncompilable_rate']:.3f}")
        if a.dry_run:
            continue
        prev.update({k: rep[k] for k in KEYS if k in rep})
        prev["per_task"] = rep["per_task"]
        prev["rescored_by"] = "scripts/analysis/85_rescore_retention.py"
        out.write_text(json.dumps(prev, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
