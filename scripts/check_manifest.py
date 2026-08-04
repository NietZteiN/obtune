#!/usr/bin/env python
"""Data-tree integrity check — run by `make check` and the pre-commit hook.

Verifies SHA manifests, then runs the two content-level H1 leak checks that labels
alone cannot catch (see src/obtune/manifest.py). Exits nonzero on any violation.

    python scripts/check_manifest.py            # verify
    python scripts/check_manifest.py --rebuild  # regenerate the manifests
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune import manifest  # noqa: E402
from obtune.paths import EVAL_ROOT, QUARANTINE_ROOT, TRAIN_ROOT  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true",
                    help="regenerate manifests from the current tree instead of verifying")
    args = ap.parse_args()

    if args.rebuild:
        for root, name in ((TRAIN_ROOT, "train"), (EVAL_ROOT, "eval"), (QUARANTINE_ROOT, "quarantine")):
            if root.exists():
                out = manifest.write(root, name)
                print(f"wrote {out}")
            else:
                print(f"skip {name}: {root} does not exist yet")
        return 0

    if not TRAIN_ROOT.exists():
        print("check_manifest: no data/train/ yet — nothing to verify")
        return 0

    rep = manifest.verify()
    print(rep.summary())
    for path in rep.changed:
        print(f"  CHANGED  {path}")
    for path in rep.missing:
        print(f"  MISSING  {path}")
    for path in rep.shared_with_quarantine:
        print(f"  QUARANTINE BYTES IN TRAINING TREE  {path}")
    for path in rep.h1_labeled_in_train:
        print(f"  H1-LABELED ROWS IN TRAINING TREE   {path}")
    for hit in rep.h1_marker_hits[:20]:
        print(f"  H1 MARKER  {hit['file']}:{hit['line']} "
              f"program={hit['program_id']} condition={hit['condition']} pattern={hit['pattern']}")
    if len(rep.h1_marker_hits) > 20:
        print(f"  ... and {len(rep.h1_marker_hits) - 20} more marker hits")

    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
