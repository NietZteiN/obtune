#!/usr/bin/env python
"""Build the CFT instance pools -> data/train/cft/<lang>/{gen,pos,neg}.jsonl

    python scripts/cft/10_build_cft_data.py --config cft/data_v1.yaml
    python scripts/cft/10_build_cft_data.py --config cft/data_v1.yaml --language python --limit 50

CPU only, and the expensive part is the executor: every negative is a mutation that has
been RUN against its parent's cases and kept only if an output genuinely differs
(src/obtune/cft/mutate.py). Expect a few minutes per language.

Writes a `pool_report.json` next to the pools with per-condition counts, the mutation
verification statistics, and the prompt-template hash. Re-run `make check` afterwards so
the new files enter the SHA manifest and the H1-marker content scan.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from obtune.cft import dataset as cft_data  # noqa: E402
from obtune.config import GLOBAL_SEED, load_config  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="cft/data_v1.yaml")
    ap.add_argument("--language", default=None, help="build one language instead of all")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap the number of source programs (smoke tests)")
    ap.add_argument("--negative-style", default=None, choices=cft_data.NEGATIVE_STYLES)
    ap.add_argument("--dry-run", action="store_true", help="build and report, write nothing")
    args = ap.parse_args()

    cfg = load_config(args.config)
    languages = [args.language] if args.language else list(cfg["languages"])
    mut = dict(cfg.get("mutation", {}) or {})

    for language in languages:
        print(f"[cft.data] building pools for {language} ...", flush=True)
        pools, report = cft_data.build_pools(
            language=language,
            conditions=list(cfg["conditions"]),
            splits=tuple(cfg.get("splits", ("train", "val"))),
            negative_style=args.negative_style or cfg.get("negative_style", "obfuscated_mutant"),
            n_per_task=cfg.get("n_per_task"),
            seed=int(cfg.get("seed", GLOBAL_SEED)),
            mutants_per_program=int(mut.get("mutants_per_program", 6)),
            keep_mutants_per_program=int(mut.get("keep_per_program", 1)),
            min_ok_fraction=float(mut.get("min_ok_fraction", 0.5)),
            max_cases=int(mut.get("max_cases", 12)),
            exec_timeout_s=float(mut.get("exec_timeout_s", 2.0)),
            exec_workers=int(mut.get("exec_workers", 32)),
            program_limit=args.limit,
        )
        print(json.dumps(report.model_dump(), indent=2, sort_keys=True))
        if args.dry_run:
            print("[cft.data] dry run — nothing written")
            continue
        written = cft_data.write_pools(language, pools, report)
        for task, path in sorted(written.items()):
            print(f"[cft.data] wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
