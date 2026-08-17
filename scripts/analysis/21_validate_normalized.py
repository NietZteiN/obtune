#!/usr/bin/env python
"""Soundness gate for the symbolic-normalization baseline.

WHAT THIS PROTECTS AGAINST
--------------------------
The normalization arm feeds the model a REWRITTEN program and scores the answer against
the ORIGINAL program's stored output. That is only valid if the rewrite preserves
behaviour. If a pass is subtly wrong, the arm does not fail loudly — it quietly scores a
different program and reports a number that looks like evidence. CLAUDE.md §4's
silent-failure list exists for exactly this shape of bug.

So: execute every normalized program against its item's stored `args_repr`, compare to the
item's stored `output_repr`, and refuse to let the arm run if any program's behaviour
changed. The comparison is `CaseResult.matches`, the same semantic-equivalence rule the
obfuscation gate uses (exceptions compare by TYPE — a rewrite may legitimately change a
traceback but never the exception raised).

A baseline item whose ORIGINAL already fails to reproduce its stored output is excluded
rather than counted against the normalizer: that is a corpus fact, not a rewrite fact.

H1 IS DELIBERATELY NOT VALIDATED HERE
-------------------------------------
Reading H1 costs a logged, budgeted quarantine access (CLAUDE.md §3.2 rule 3), and this
script is a development tool that gets re-run whenever a pass changes. Re-reading the
held-out family on every iteration is exactly the drip-feed the budget exists to stop —
and iterating on passes until H1 looked good would be tuning on H1, which rule 2 forbids
outright. The passes are condition-agnostic, so soundness measured across every trainable
condition is the evidence that carries over.

Usage:
    PYTHONPATH=src python scripts/analysis/21_validate_normalized.py --language python
    PYTHONPATH=src python scripts/analysis/21_validate_normalized.py --profile full --limit 50
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from obtune import data
from obtune.exec.pool import BatchItem, CaseResult, run_batch
from obtune.normalize import PROFILES, normalize

#: Trainable ladder only — see the module docstring on why H1 is absent.
# Composites added 2026-08-15. The normalization arm was only ever gated on the
# single-transform ladder, so `norm_*` numbers on STACKED conditions would have been
# ungated — a rewrite that is behaviour-preserving on `S1` alone is not thereby
# behaviour-preserving on `C_L1r_S1`. Filling those cells in §2.2 requires this gate to
# pass on them first; correctness before completeness.
CONDITIONS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4",
              "C_L1r_S1", "C_S1_L1r", "C_L1b_S1", "C_L2_S4", "C_L1r_S3", "C_S4_S3"]


def _case(pr) -> CaseResult:
    return pr.cases[0] if pr.cases else CaseResult(status=pr.child_status or "crash")


def validate(language: str, profile: str, limit: int | None, source: str) -> dict:
    items = []
    for cond in CONDITIONS:
        try:
            items.extend(data.load_eval_items([cond], language, source=source,
                                              script=Path(__file__).name))
        except FileNotFoundError:
            continue  # a condition with no eval variants in this source is not an error
    if limit:
        by_cond: dict[str, list] = defaultdict(list)
        for it in items:
            by_cond[it.condition].append(it)
        items = [it for c in sorted(by_cond) for it in by_cond[c][:limit]]
    if not items:
        raise SystemExit(f"no eval items for {language!r} in source {source!r}")

    norm = [normalize(it.code, it.language, entry_point=it.entry_point, profile=profile)
            for it in items]

    # Both sides are executed. The ORIGINAL run is the reference: an item whose original
    # does not reproduce its stored output is a pre-existing corpus issue and is excluded,
    # not blamed on the rewrite.
    orig = run_batch([BatchItem(it.item_id, it.language, it.code, it.entry_point, [it.args_repr])
                      for it in items])
    new = run_batch([BatchItem(it.item_id, it.language, n.code, it.entry_point, [it.args_repr])
                     for it, n in zip(items, norm)])

    unsound, excluded, ok = [], 0, 0
    changed = Counter()
    per_cond: dict[str, Counter] = defaultdict(Counter)
    applied_hist = Counter()
    for it, n, o, m in zip(items, norm, orig, new):
        co, cm = _case(o), _case(m)
        per_cond[it.condition]["n"] += 1
        applied_hist["+".join(n.applied) or "(none)"] += 1
        if n.changed:
            changed[it.condition] += 1
            per_cond[it.condition]["changed"] += 1
        if not (co.ok and co.output == it.output_repr):
            excluded += 1
            per_cond[it.condition]["excluded"] += 1
            continue
        if co.matches(cm):
            ok += 1
            continue
        unsound.append({
            "item_id": it.item_id, "condition": it.condition, "program_id": it.program_id,
            "passes": n.applied, "notes": n.notes,
            "orig": {"status": co.status, "output": co.output, "exc": co.exc_type},
            "norm": {"status": cm.status, "output": cm.output, "exc": cm.exc_type},
        })
        per_cond[it.condition]["unsound"] += 1

    return {
        "language": language, "profile": profile, "source": source,
        "passes": list(PROFILES[profile]),
        "conditions": CONDITIONS,
        "n_items": len(items), "n_validated": ok + len(unsound),
        "n_excluded_original_mismatch": excluded,
        "n_sound": ok, "n_unsound": len(unsound),
        "rewrite_rate": {c: {"changed": changed.get(c, 0), "n": per_cond[c]["n"]}
                         for c in sorted(per_cond)},
        "applied_combinations": dict(applied_hist.most_common()),
        "per_condition": {c: dict(v) for c, v in sorted(per_cond.items())},
        "unsound_examples": unsound[:25],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--language", default="python")
    ap.add_argument("--profile", default=None, help="default: every profile")
    ap.add_argument("--source", default="testset")
    ap.add_argument("--limit", type=int, default=None, help="items per condition")
    ap.add_argument("--out", default="results/analysis")
    args = ap.parse_args()

    profiles = [args.profile] if args.profile else sorted(PROFILES)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    failed = False
    print(f"{'profile':<10} {'items':>7} {'rewritten':>10} {'sound':>7} {'UNSOUND':>8} {'excl':>6}")
    for prof in profiles:
        rep = validate(args.language, prof, args.limit, args.source)
        rewritten = sum(v["changed"] for v in rep["rewrite_rate"].values())
        print(f"{prof:<10} {rep['n_items']:>7} {rewritten:>10} {rep['n_sound']:>7} "
              f"{rep['n_unsound']:>8} {rep['n_excluded_original_mismatch']:>6}")
        p = outdir / f"normalize_soundness_{args.language}_{prof}.json"
        p.write_text(json.dumps(rep, indent=2))
        if rep["n_unsound"]:
            failed = True
            print(f"  !! {rep['n_unsound']} program(s) changed behaviour — see {p}")
            for u in rep["unsound_examples"][:3]:
                print(f"     {u['item_id']} ({u['condition']}) passes={u['passes']} "
                      f"{u['orig']} -> {u['norm']}")

    if failed:
        # A hard failure on purpose: an unsound normalizer must not reach the eval queue,
        # where its damage would show up as a plausible-looking accuracy number.
        print("\nFAIL: normalization is not behaviour-preserving; the arm must not run.")
        return 1
    print("\nOK: every normalized program reproduced its original's behaviour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
