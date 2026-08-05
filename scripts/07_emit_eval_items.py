#!/usr/bin/env python
"""Materialize test-set EvalItems from gate-validated variants.

`05_build_variants.py` writes `Variant` rows (the gate's output: obfuscated code
plus its rename map and verdict). Evaluation needs one row per variant x input
case, carrying the gold output — the same expansion `06_emit_pairs.py` does for
training. Keeping the two artifacts in separate directories means re-running the
builder never clobbers the eval inputs, and vice versa:

    data/eval/testset/variants/<cond>/<lang>.jsonl   Variant  (gate output)
    data/eval/testset/items/<cond>/<lang>.jsonl      EvalItem (eval input)

As in training, the gold output belongs to the PARENT program: a gate-validated
variant is output-identical by construction, so we do not re-execute it here. The
prompt must use the VARIANT's entry-point name, since L1b/L1r/L2 rename it.

`rename_map` and `entry_point_parent` are carried into `meta` because the RQ3
decoy-capture analysis needs the L1b decoy->true pairing at eval time.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.paths import EVAL_ROOT, LANGUAGES, iter_jsonl, write_jsonl  # noqa: E402
from obtune.schema import EvalItem  # noqa: E402

TESTSET = EVAL_ROOT / "testset"


def _base_programs() -> dict[str, dict]:
    """program_id -> BaseProgram row, across both datasets."""
    out: dict[str, dict] = {}
    for f in sorted((TESTSET / "base").glob("*.jsonl")):
        for row in iter_jsonl(f):
            out[row["program_id"]] = row
    return out


def _dataset_of(program_id: str, row: dict) -> str:
    ds = (row.get("meta") or {}).get("dataset")
    if ds in ("A", "B"):
        return ds
    # Ingest names programs "A:Python/36" / "B:cruxeval-x-python/0".
    head = program_id.split(":", 1)[0]
    return head if head in ("A", "B") else "B"


def emit_for(condition: str, language: str, bases: dict[str, dict],
             n_cases: int, include_h1: bool) -> tuple[int, Counter]:
    src = TESTSET / "variants" / condition / f"{language}.jsonl"
    if condition == "H1":
        # H1 lives in the quarantine tree and is materialized only when an
        # evaluation pass has an explicit purpose (CLAUDE.md §3.2).
        src = ROOT / "data" / "quarantine" / "h1" / "testset" / f"{language}.jsonl"
    stats: Counter = Counter()
    if not src.exists():
        return 0, Counter({"missing_variants": 1})

    rows: list[dict] = []
    for var in iter_jsonl(src):
        parent = bases.get(var["program_id"])
        if parent is None:
            stats["orphan_variant"] += 1
            continue
        cases = (parent.get("cases") or [])[:n_cases]
        if not cases:
            stats["no_cases"] += 1
            continue
        for i, case in enumerate(cases):
            gold = case.get("output_canon")
            if gold is None:
                stats["no_gold"] += 1
                continue
            item = EvalItem(
                item_id=f"{var['program_id']}::{condition}::{i}",
                program_id=var["program_id"],
                dataset=_dataset_of(var["program_id"], parent),
                condition=condition,
                language=language,
                code=var["code"],
                entry_point=var["entry_point"],
                args_repr=case["args_repr"],
                output_repr=gold,
                case_role=case.get("case_role", "generated"),
                meta={
                    "entry_point_parent": var.get("entry_point_parent", parent["entry_point"]),
                    "rename_map": var.get("rename_map") or {},
                    "source": parent.get("source"),
                    "loc": parent.get("loc"),
                },
            )
            rows.append(item.model_dump())
            stats["items"] += 1

    if condition == "H1":
        if not include_h1:
            return 0, Counter({"h1_skipped": 1})
        # H1 items stay inside the quarantine tree — the loader reads them only
        # through load_h1_items(), which demands a purpose and writes ACCESS_LOG.
        out = ROOT / "data" / "quarantine" / "h1" / "testset" / "items" / f"{language}.jsonl"
    else:
        out = TESTSET / "items" / condition / f"{language}.jsonl"
    write_jsonl(out, rows)
    return len(rows), stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--conditions", nargs="*",
                    default=["L0", "L1b", "L1r", "L2", "S1", "S2", "H1"])
    ap.add_argument("--languages", nargs="*", default=list(LANGUAGES))
    ap.add_argument("--include-h1", action="store_true", default=True,
                    help="materialize H1 eval items (the eval pass still records its purpose)")
    args = ap.parse_args()

    n_cases = int(load_config("data.yaml")["cases"]["n_eval_cases"])
    bases = _base_programs()
    print(f"  {len(bases)} test-set base programs, up to {n_cases} cases each")

    total = 0
    for language in args.languages:
        for condition in args.conditions:
            n, stats = emit_for(condition, language, bases, n_cases, args.include_h1)
            total += n
            detail = ", ".join(f"{k}={v}" for k, v in sorted(stats.items())) or "-"
            print(f"  {language:<11} {condition:<4} {n:>6} items   {detail}")

    print(f"\ntotal eval items: {total}")
    return 0 if total else 1


if __name__ == "__main__":
    sys.exit(main())
