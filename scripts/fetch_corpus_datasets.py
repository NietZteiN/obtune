#!/usr/bin/env python
"""Populate the HF cache with the raw files the corpus loaders read, then PROVE they read them.

    python scripts/fetch_corpus_datasets.py            # fetch + verify
    python scripts/fetch_corpus_datasets.py --verify   # verify only

Not needed to run anything: `data/train/base/python.jsonl` and the whole variant tree transferred
with the project and are what every job reads. This closes a *reproducibility* gap — the tier-1
sources that produced the 2,231-program corpus were downloaded on the old cluster and were never in
juno's cache, so `scripts/02_build_corpus.py` could not be re-run here.

WHY snapshot_download AND NOT load_dataset. The first version of this script called
`load_dataset`, which reported success for all three sources while leaving the corpus **still
unbuildable**: the loaders in `obtune/corpus/sources/` do not use `datasets` at all — they read
raw files out of the hub cache via `find_cached(REPO_ID, pattern)`. `load_dataset` on
`codeparrot/apps` yields an arrow cache and, under `datasets` 4.x, only through the
`refs/convert/parquet` branch (script loaders are refused) — so no `train.jsonl` ever lands, which
is the one file `apps.dataset_path()` looks for. Fetching the raw files the loaders name is the
only thing that actually helps, and the verify pass below is what caught the difference.

Two hub-side changes since the corpus was first built, both hit on 2026-09-09:
  * `datasets` 4.x refuses script-based loaders ("Dataset scripts are no longer supported, but
    found apps.py"). Irrelevant once we fetch raw files.
  * `openai_humaneval` is now `openai/openai_humaneval`; the bare id no longer resolves.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# repo id -> the glob patterns the corresponding loader's dataset_path() looks for.
# Keep this in step with obtune/corpus/sources/*.py; the verify pass fails loudly if it drifts.
SPECS = {
    "codeparrot/apps": ["*.jsonl"],                 # apps.py: find_cached(REPO_ID, "train.jsonl")
    "cruxeval-org/cruxeval": ["*.jsonl"],           # cruxeval.py
    "openai/openai_humaneval": ["*.parquet"],       # humaneval.py: find_cached(REPO_ID, "*.parquet")
}


def verify() -> int:
    from obtune.corpus.sources import apps, cruxeval, humaneval
    rc = 0
    for name, mod in (("apps", apps), ("cruxeval", cruxeval), ("humaneval", humaneval)):
        try:
            print(f"  [ok]   {name:10s} loader resolves -> {mod.dataset_path()}", flush=True)
        except Exception as exc:
            print(f"  [FAIL] {name:10s} {type(exc).__name__}: {str(exc)[:180]}", flush=True)
            rc = 1
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true", help="skip the download, just check the loaders")
    a = ap.parse_args()

    if not a.verify:
        from huggingface_hub import snapshot_download
        for repo, patterns in SPECS.items():
            try:
                p = snapshot_download(repo, repo_type="dataset", allow_patterns=patterns,
                                      max_workers=4)
                print(f"  [ok]   {repo} -> {p}", flush=True)
            except Exception as exc:
                print(f"  [FAIL] {repo}: {type(exc).__name__}: {str(exc)[:200]}", flush=True)

    print("\nverifying the loaders can actually read what is cached:")
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
