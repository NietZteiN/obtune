#!/usr/bin/env python
"""Materialize SFT training pairs from gate-validated variants.

Reads data/train/base/<lang>.jsonl (BaseProgram: code + input cases) and
data/train/variants/<cond>/<lang>.jsonl (Variant: obfuscated code + entry point),
and emits data/train/pairs/<cond>/<lang>.jsonl (TrainPair: one row per
program x case, with the gold output literal).

Two things this step is responsible for getting right:

  * The gold output belongs to the PARENT program. A gate-validated variant is
    output-identical by construction, so the parent's canonical output is the
    label — we do not re-execute variants here (the gate already did, on these
    cases plus 20 fuzzed ones).
  * The prompt must reference the VARIANT's entry-point name. L1b/L1r/L2 rename
    the entry function; asking for `fibfib(...)` when the code defines
    `smoothArea(...)` would make the task unanswerable and silently destroy the
    adversarial-renaming condition.

H1 is structurally excluded: paths.TRAIN_ROOT contains no H1 variants, and
schema.TrainPair rejects the condition outright.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.paths import (  # noqa: E402
    LANGUAGES, TRAIN_ROOT, TRAINABLE_CONDITIONS, iter_jsonl, load_training_jsonl, write_jsonl,
)
from obtune.schema import TrainPair  # noqa: E402


def _split_of(program_id: str, splits: dict[str, str]) -> str:
    return splits.get(program_id, "train")


def emit_for(condition: str, language: str, n_cases: int, splits: dict[str, str],
             aug_tag: str | None = None) -> tuple[int, Counter]:
    base_path = TRAIN_ROOT / "base" / f"{language}.jsonl"
    var_path = TRAIN_ROOT / "variants" / condition / f"{language}.jsonl"
    if aug_tag:
        # Augmentation build (05_build_variants.py --aug-tag): same parents, same gold, a
        # re-seeded surface. Rows get a 4th item_id part so they can coexist with the
        # canonical rows in one training set without tripping validate_pairs' duplicate
        # check; the split is still the PARENT's, so no augmented row can cross into test.
        var_path = TRAIN_ROOT / "variants_aug" / aug_tag / condition / f"{language}.jsonl"
    if not base_path.exists() or not var_path.exists():
        return 0, Counter({"missing_input": 1})

    bases = {r["program_id"]: r for r in load_training_jsonl(base_path)}
    stats: Counter = Counter()
    rows: list[dict] = []

    for var in load_training_jsonl(var_path):
        parent = bases.get(var["program_id"])
        if parent is None:
            stats["orphan_variant"] += 1
            continue
        cases = parent.get("cases", [])[:n_cases]
        if not cases:
            stats["no_cases"] += 1
            continue
        for i, case in enumerate(cases):
            gold = case.get("output_canon")
            if gold is None:
                stats["no_gold"] += 1
                continue
            pair = TrainPair(
                item_id=f"{var['program_id']}::{condition}::{i}"
                        + (f"::aug-{aug_tag}" if aug_tag else ""),
                program_id=var["program_id"],
                program_group_id=var["program_id"],  # split unit — never split by row
                condition=condition,
                language=language,
                code=var["code"],
                entry_point=var["entry_point"],
                args_repr=case["args_repr"],
                output_repr=gold,
                split=_split_of(var["program_id"], splits),
                provenance=parent.get("provenance", "curated"),
            )
            rows.append(pair.model_dump())
            stats[f"split_{pair.split}"] += 1

    out = TRAIN_ROOT / "pairs" / condition / f"{language}.jsonl"
    if aug_tag:
        out = TRAIN_ROOT / "pairs_aug" / aug_tag / condition / f"{language}.jsonl"
    write_jsonl(out, rows)
    return len(rows), stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conditions", nargs="*", default=list(TRAINABLE_CONDITIONS))
    ap.add_argument("--languages", nargs="*", default=list(LANGUAGES))
    ap.add_argument("--aug-tag", default=None,
                    help="materialise data/train/variants_aug/<tag>/ into pairs_aug/<tag>/")
    args = ap.parse_args()

    if any(c == "H1" for c in args.conditions):
        print("refusing: H1 is never materialized as training pairs (CLAUDE.md §3.2)")
        return 2

    data_cfg = load_config("data.yaml")
    n_cases = int(data_cfg["cases"]["n_train_cases"])

    total = 0
    for language in args.languages:
        splits_file = TRAIN_ROOT.parent / "splits" / f"{language}.json"
        splits: dict[str, str] = {}
        if splits_file.exists():
            import json

            splits = json.loads(splits_file.read_text()).get("assignment", {})
        else:
            print(f"  note: no split file at {splits_file} — everything defaults to train")

        for condition in args.conditions:
            n, stats = emit_for(condition, language, n_cases, splits, aug_tag=args.aug_tag)
            total += n
            detail = ", ".join(f"{k}={v}" for k, v in sorted(stats.items())) or "-"
            print(f"  {language:<11} {condition:<4} {n:>7} pairs   {detail}")

    print(f"\ntotal pairs: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
