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


def _extra_cases(parent: dict, n_cases: int, k: int) -> list[dict]:
    """Promote up to `k` of the parent's gate inputs to training cases (lever 5, 2026-09-05).

    Gate inputs are already execution-gated in the strongest sense the project has: they
    ran on the parent (output 1..200 chars), passed the determinism check across hash
    seeds, and every kept variant of this program was verified output-identical on them
    by the semantic gate. So they are free labelled cases. What they are NOT is
    output-diverse -- fuzzing hits degenerate paths often (three gate inputs returning
    `0` for the same program is typical), so a naive "take the first k" would teach the
    modal answer. Preference order: outputs not already among the training cases, one
    per distinct output; then anything left, still one per distinct output; duplicates
    only if the program cannot supply k distinct answers at all.
    """
    seen = {c.get("output_canon") for c in (parent.get("cases") or [])[:n_cases]}
    pool = [g for g in (parent.get("gate_inputs") or []) if g.get("output_canon") is not None]
    chosen: list[dict] = []
    for pass_no in (0, 1, 2):
        for g in pool:
            if len(chosen) >= k:
                return chosen
            if g in chosen:
                continue
            o = g["output_canon"]
            if pass_no == 0 and o in seen:
                continue
            if pass_no < 2 and o in {c["output_canon"] for c in chosen}:
                continue
            chosen.append(g)
    return chosen


def emit_for(condition: str, language: str, n_cases: int, splits: dict[str, str],
             aug_tag: str | None = None, extra_cases: int = 0) -> tuple[int, Counter]:
    base_path = TRAIN_ROOT / "base" / f"{language}.jsonl"
    var_path = TRAIN_ROOT / "variants" / condition / f"{language}.jsonl"
    if extra_cases:
        # Lever 5: SAME variants, SAME parents, MORE cases. Rows carry indices >= n_cases
        # and the `::aug-<tag>` suffix so they coexist with the canonical rows in one
        # training set; the split is the parent's, so nothing crosses into test. The
        # canonical eval items read `cases[:n_train_cases]` from the base file, which this
        # does not touch -- the evaluation inputs are unchanged.
        if not aug_tag:
            raise SystemExit("--extra-cases needs --aug-tag to name the pairs_aug/<tag>/ output")
    elif aug_tag:
        # Augmentation build (05_build_variants.py --aug-tag): same parents, same gold, a
        # re-seeded surface. Rows get a 4th item_id part so they can coexist with the
        # canonical rows in one training set without tripping validate_pairs' duplicate
        # check; the split is still the PARENT's, so no augmented row can cross into test.
        var_path = TRAIN_ROOT / "variants_aug" / aug_tag / condition / f"{language}.jsonl"
    if not base_path.exists() or not var_path.exists():
        return 0, Counter({"missing_input": 1})

    bases = {r["program_id"]: r for r in load_training_jsonl(base_path)}
    if aug_tag:
        # Split-frozen extension corpora (02_build_corpus.py --extend-frozen <tag>) put
        # NEW parents under data/train/base_<tag>/; a re-seed build has none and every
        # variant resolves to the canonical parent above. Still under TRAIN_ROOT.
        ext = TRAIN_ROOT / f"base_{aug_tag}" / f"{language}.jsonl"
        if ext.exists():
            for r in load_training_jsonl(ext):
                bases.setdefault(r["program_id"], r)
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
        if extra_cases:
            extra = _extra_cases(parent, n_cases, extra_cases)
            stats[f"extra_{len(extra)}"] += 1
            cases = [(n_cases + j, c) for j, c in enumerate(extra)]
        else:
            cases = list(enumerate(cases))
        for i, case in cases:
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
    ap.add_argument("--extra-cases", type=int, default=0,
                    help="lever 5: emit up to K additional cases per program from the parent's "
                         "execution-gated gate_inputs (canonical variants) into pairs_aug/<tag>/")
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
            n, stats = emit_for(condition, language, n_cases, splits, aug_tag=args.aug_tag,
                                extra_cases=args.extra_cases)
            total += n
            detail = ", ".join(f"{k}={v}" for k, v in sorted(stats.items())) or "-"
            print(f"  {language:<11} {condition:<4} {n:>7} pairs   {detail}")

    print(f"\ntotal pairs: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
