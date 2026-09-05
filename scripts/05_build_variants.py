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


def _load_targets(target: str, base_root: Path | None = None) -> dict[str, list[BaseProgram]]:
    root = (EVAL_ROOT / "testset" / "base") if target == "testset" else (TRAIN_ROOT / "base")
    if base_root is not None:
        root = base_root
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
    # VARIANT AUGMENTATION (2026-09-03). The canonical build gives every program exactly ONE
    # variant per condition, drawn at `global_seed`. For the randomised transforms (L1b's
    # name pool, L1r's hex names, S1's state ids and case order, S2's predicates) a second
    # seed is a genuinely different surface over the same semantics -- the textbook
    # augmentation for invariance, and untried here. `--aug-tag` writes such a build to
    # data/train/variants_aug/<tag>/ so it can never overwrite the canonical variants, the
    # coverage matrix or the reject dump; `06_emit_pairs.py --aug-tag` materialises it.
    ap.add_argument("--seed", type=int, default=None,
                    help="override conditions.yaml global_seed (use with --aug-tag)")
    ap.add_argument("--aug-tag", default=None,
                    help="write to data/train/variants_aug/<tag>/ instead of variants/")
    # DATA-SCALE EXTENSION (2026-09-03): `02_build_corpus.py --extend-frozen <tag>` writes
    # NEW train-only programs to data/train/base_<tag>/. Their variants go through the same
    # aug-tag route (so 06_emit_pairs / data.load_pairs pick them up via augment_tags)
    # but at the canonical seed — these are different programs, not re-seeds.
    ap.add_argument("--base-root", default=None,
                    help="read base programs from this directory instead of data/train/base/ "
                         "(requires --aug-tag; --seed optional)")
    args = ap.parse_args()
    if args.aug_tag and args.target != "train":
        print("refusing: --aug-tag is a TRAINING-side augmentation; the eval variants are frozen")
        return 2
    if args.base_root and not args.aug_tag:
        print("refusing: --base-root output must be tagged (--aug-tag) so it cannot land on "
              "the canonical variants/")
        return 2
    if not args.base_root and (args.seed is not None) != (args.aug_tag is not None):
        print("refusing: --seed and --aug-tag go together (a re-seeded build must not land "
              "on the canonical paths, and a tagged build at the canonical seed is a duplicate)")
        return 2

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
    if args.aug_tag:
        tag += f"_aug_{args.aug_tag}"
    # A partial `--conditions` build must not overwrite the full ladder's coverage matrix
    # and reject dump with a one-condition summary. That is exactly what the S3/S4 build
    # did to coverage_matrix_{train,testset}.json (found 2026-09-04 while adding X1), so a
    # strict subset now gets its own suffix; a full-ladder build keeps the canonical path.
    if set(args.conditions) != set(TRAINABLE_CONDITIONS):
        tag += "_" + "-".join(args.conditions)
    out_root = (EVAL_ROOT / "testset" / "variants") if args.target == "testset" else (TRAIN_ROOT / "variants")
    if args.aug_tag:
        out_root = TRAIN_ROOT / "variants_aug" / args.aug_tag
    build_seed = int(cfg.get("global_seed", 17)) if args.seed is None else int(args.seed)
    summary: dict[str, dict] = {}

    base_root = Path(args.base_root) if args.base_root else None
    for language, programs in _load_targets(args.target, base_root).items():
        report = builder.build_variants(
            programs, args.conditions, language, workers=args.workers,
            seed=build_seed, write=False, cfg=cfg,
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
                             "common_subset": common, "n_common": len(common),
                             "seed": build_seed, "aug_tag": args.aug_tag, "base_root": args.base_root}

    if not args.dry_run:
        MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)
        path = MANIFESTS_ROOT / f"coverage_matrix_{args.target}{tag}.json"
        path.write_text(json.dumps(summary, indent=2))
        print(f"\nwrote {out_root} and {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
