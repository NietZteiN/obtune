#!/usr/bin/env python
"""Populate the HF cache with the raw datasets the corpus is BUILT from.

    python scripts/fetch_corpus_datasets.py [--language python] [--tiers tier1 tier2 tier3]

Not needed to run anything: `data/train/base/python.jsonl` and the whole variant tree
transferred with the project and are what every job reads. This closes a *reproducibility*
gap instead — the tier-1 sources (APPS, CRUXEval, HumanEval) that produced the 2,231-program
corpus were downloaded on the old cluster and were never in juno's cache, so
`scripts/02_build_corpus.py` could not be re-run here to reproduce the corpus from scratch.
For an artifact-track submission that is the difference between "the corpus is included" and
"the corpus can be rebuilt".

Reads configs/sources.yaml, so it follows the source list rather than duplicating it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import load_config  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--language", default="python")
    ap.add_argument("--tiers", nargs="*", default=["tier1"])
    a = ap.parse_args()

    from datasets import load_dataset

    src = load_config("sources.yaml")[a.language]
    rc = 0
    for tier in a.tiers:
        for entry in src.get(tier, []):
            hf_id = entry.get("hf_id")
            if not hf_id:
                print(f"[skip] {entry.get('name')}: local path, not a hub dataset", flush=True)
                continue
            kw = {}
            if entry.get("config"):
                kw["name"] = entry["config"]
            if entry.get("data_file"):
                kw["data_files"] = entry["data_file"]
            try:
                # The split string in sources.yaml can be "train+validation+test"; fetching
                # the whole repo is simpler and is what the loaders will read anyway.
                ds = load_dataset(hf_id, **kw)
                sizes = {k: len(v) for k, v in ds.items()} if hasattr(ds, "items") else len(ds)
                print(f"[ok]   {entry['name']:12s} {hf_id} -> {sizes}", flush=True)
            except Exception as exc:
                print(f"[FAIL] {entry['name']:12s} {hf_id}: {type(exc).__name__}: {exc}", flush=True)
                rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
