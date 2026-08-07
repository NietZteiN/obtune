#!/usr/bin/env python
"""Refuse to train if the corpus is contaminated. Quarantine layer 4b (CLAUDE.md §3.2).

Three independent checks, because each catches something the others cannot:

  1. no row under data/train/ is labelled `condition: H1`
  2. no training file's *content* matches an H1 marker regex — labels can be wrong,
     content cannot (this is what catches an obfuscator leaking string-array or MBA
     artifacts into a condition that claims to be S1)
  3. splits actually partition: a program_id may appear in exactly one of
     train/val/test, and no `test` program may appear in any training pair. A
     program that is both trained on and evaluated on inflates every cell of the
     transfer matrix, and nothing downstream can detect it.

    python scripts/check_no_h1_in_train.py     # exits nonzero on any violation
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.manifest import h1_marker_patterns, scan_for_h1_markers  # noqa: E402
from obtune.paths import SPLITS_ROOT, TRAIN_ROOT, iter_jsonl  # noqa: E402


def main() -> int:
    problems: list[str] = []

    if not TRAIN_ROOT.exists():
        print("check_no_h1_in_train: no data/train/ yet — nothing to check")
        return 0

    patterns = h1_marker_patterns()
    n_files = n_rows = 0
    for f in sorted(TRAIN_ROOT.rglob("*.jsonl")):
        n_files += 1
        h1_rows = 0
        for row in iter_jsonl(f):
            n_rows += 1
            if row.get("condition") == "H1":
                h1_rows += 1
        if h1_rows:
            problems.append(f"{f.relative_to(ROOT)}: {h1_rows} rows labelled condition=H1")
        hits = scan_for_h1_markers(f, patterns)
        if hits:
            ex = hits[0]
            problems.append(
                f"{f.relative_to(ROOT)}: {len(hits)} row(s) contain H1 markers "
                f"(first: line {ex['line']} program={ex['program_id']} pattern={ex['pattern']})"
            )

    # Split integrity.
    for split_file in sorted(SPLITS_ROOT.glob("*.json")) if SPLITS_ROOT.exists() else []:
        lang = split_file.stem
        assignment = json.loads(split_file.read_text()).get("assignment", {})
        by_split = defaultdict(set)
        for pid, split in assignment.items():
            by_split[split].add(pid)
        names = sorted(by_split)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                overlap = by_split[a] & by_split[b]
                if overlap:
                    problems.append(
                        f"{lang}: {len(overlap)} program(s) in both '{a}' and '{b}' "
                        f"(e.g. {sorted(overlap)[:3]})"
                    )
        test_ids = by_split.get("test", set())
        if test_ids:
            pairs_dir = TRAIN_ROOT / "pairs"
            for f in sorted(pairs_dir.rglob(f"{lang}.jsonl")) if pairs_dir.exists() else []:
                leaked = {r["program_id"] for r in iter_jsonl(f)
                          if r.get("program_id") in test_ids and r.get("split") != "test"}
                if leaked:
                    problems.append(
                        f"{f.relative_to(ROOT)}: {len(leaked)} held-out 'test' program(s) "
                        f"appear as training pairs (e.g. {sorted(leaked)[:3]})"
                    )

    if problems:
        print(f"TRAIN CORPUS CHECK FAILED — {len(problems)} problem(s):")
        for p in problems[:20]:
            print(f"  {p}")
        if len(problems) > 20:
            print(f"  ... and {len(problems) - 20} more")
        return 1

    print(f"train corpus check OK — {n_files} files, {n_rows} rows, no H1 labels, "
          "no H1 markers, splits disjoint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
