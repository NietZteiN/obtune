#!/usr/bin/env python
"""Generate the six trainable conditions for a set of base programs.

    python scripts/05_build_variants.py --target testset      # data/eval/testset/
    python scripts/05_build_variants.py --target train        # data/train/

H1 is NOT produced here — it is quarantined and comes only from
scripts/gen_h1_quarantined.py (CLAUDE.md §3.2).

Reports per-condition coverage and the all-conditions-succeeded common subset, which
is the program set headline transfer numbers must be computed on: S1/S2 decline on
different programs than the identifier conditions, so a per-condition full set would
confound the family contrast with differing program sets.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.obf import builder  # noqa: E402
from obtune.paths import (  # noqa: E402
    EVAL_ROOT, LANGUAGES, MANIFESTS_ROOT, TRAIN_ROOT, TRAINABLE_CONDITIONS,
    iter_jsonl, write_jsonl,
)
from obtune.schema import BaseProgram  # noqa: E402


def _load_targets(target: str) -> dict[str, list[BaseProgram]]:
    root = (EVAL_ROOT / "testset" / "base") if target == "testset" else (TRAIN_ROOT / "base")
    by_lang: dict[str, list[BaseProgram]] = {lang: [] for lang in LANGUAGES}
    if not root.exists():
        raise SystemExit(f"no base programs at {root} — run the ingest/corpus step first")
    for path in sorted(root.glob("*.jsonl")):
        for row in iter_jsonl(path):
            program = BaseProgram.model_validate(row)
            by_lang[program.language].append(program)
    return {k: v for k, v in by_lang.items() if v}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=["testset", "train"], default="testset")
    ap.add_argument("--conditions", nargs="*", default=list(TRAINABLE_CONDITIONS))
    # Composites live in their own ladder file and are deliberately OUTSIDE
    # TRAINABLE_CONDITIONS, so they can never be swept into the RQ1 matrix by a default.
    # `builder.build_variants` already accepts a cfg; it just was never given one here, so
    # it fell back to conditions.yaml and no composite code could ever resolve.
    ap.add_argument("--conditions-config", default="conditions.yaml",
                    help="ladder file; use conditions_composite.yaml for the C_ codes")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if "H1" in args.conditions:
        print("refusing: H1 is quarantined — use scripts/gen_h1_quarantined.py")
        return 2

    cfg = load_config(args.conditions_config)
    # Per-condition variant files are namespaced by condition code already, but the coverage
    # matrix and the reject dump are written to FIXED paths — so a second-ladder run would
    # silently overwrite the RQ1 coverage matrix with a one-condition composite summary.
    # Suffix both by the ladder file whenever it is not the canonical one.
    stem = Path(args.conditions_config).stem
    tag = "" if stem == "conditions" else "_" + stem.replace("conditions_", "")
    out_root = (EVAL_ROOT / "testset" / "variants") if args.target == "testset" else (TRAIN_ROOT / "variants")
    summary: dict[str, dict] = {}

    for language, programs in _load_targets(args.target).items():
        report = builder.build_variants(
            programs, args.conditions, language, workers=args.workers,
            seed=int(cfg.get("global_seed", 17)), write=False, cfg=cfg,
        )
        counts = {c: 0 for c in args.conditions}
        for v in report.variants:
            counts[v.condition] += 1
        common = report.common_subset()
        n = len(programs)
        print(f"{language}: {n} programs — " + "  ".join(f"{c}={counts[c]}/{n}" for c in args.conditions))
        print(f"  common subset (all {len(args.conditions)} conditions): {len(common)}/{n}")

        declines: dict[str, list[str]] = {}
        for key, rec in report.entries.items():
            if rec["status"] == "ok":
                continue
            pid, cond = key.rsplit("::", 1)
            gate = rec.get("gate") or {}
            failed = [c for c, v in (gate.get("checks") or {}).items() if v is False]
            declines.setdefault(cond, []).append(f"{pid}: {failed or rec.get('skipped_constructs') or 'declined'}")
        for cond, items in sorted(declines.items()):
            print(f"  {cond} declined {len(items)}: {items[0][:90]}" + (" ..." if len(items) > 1 else ""))

        if not args.dry_run:
            for cond in args.conditions:
                rows = [v.model_dump() for v in report.variants if v.condition == cond]
                write_jsonl(out_root / cond / f"{language}.jsonl", rows)
            write_jsonl(Path(f"data/rejects/{language}/{args.target}{tag}.jsonl"), report.rejects)

        summary[language] = {"n_programs": n, "coverage": counts,
                             "common_subset": common, "n_common": len(common)}

    if not args.dry_run:
        MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)
        path = MANIFESTS_ROOT / f"coverage_matrix_{args.target}{tag}.json"
        path.write_text(json.dumps(summary, indent=2))
        print(f"\nwrote {out_root} and {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
