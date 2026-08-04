#!/usr/bin/env python
"""Ingest the ICSE stimuli: 350 byte-identical legacy rows + the L0 parents.

    python scripts/01_ingest_testset.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.testset import ingest  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report without writing files")
    args = ap.parse_args()

    report = ingest.run(write=not args.dry_run)

    for dataset, d in report["datasets"].items():
        langs = ", ".join(f"{k}={v}" for k, v in sorted(d["per_language"].items()))
        print(f"Dataset {dataset}: {d['legacy_rows']} legacy rows | {d['parents']} L0 parents ({langs})")
        print(f"  executed ok {d['executed_ok']} | answer key agrees {d['answer_agreements']}"
              f" | disagrees {len(d['answer_disagreements'])}"
              f" | whitespace-normalized {d['whitespace_normalized']}")
        for u in d["unparsed"]:
            print(f"  UNPARSED  {u['task_id']} ({u['language']}): {u['reason']} — {str(u['raw_input'])[:60]!r}")
        for f in d["exec_failures"]:
            print(f"  EXEC FAIL {f['task_id']} ({f['language']}): {f['status']}/{f['exc_type']}"
                  f" entry={f['entry_point']} args={f['args'][:40]}")
        for m in d["answer_disagreements"]:
            print(f"  ANSWER    {m['task_id']} ({m['language']}): executed {m['executed']!r}"
                  f" vs key {m['human_key']!r}")

    print(f"\ntotal: {report['total_parents']} L0 parents, {report['total_legacy_rows']} legacy rows")
    if not args.dry_run:
        print("wrote data/eval/testset/{base,legacy_icse}/ and data/manifests/testset_ingest_report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
