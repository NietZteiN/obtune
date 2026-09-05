"""Download a Hugging Face model snapshot into HF_HOME — as a SLURM CPU job.

    python scripts/slurm/submit.py --name dl34b --partition normal --gres none \
        --time 03:00:00 --argv scripts/hf_snapshot.py <hf_id from configs/models.yaml>

Why a script and not a one-liner on the login node: the login node caps virtual memory
at 8 GB (`ulimit -v`), and `hf_transfer`'s multiplexed download of a 70 GB checkpoint
dies there with `memory allocation of 67021731 bytes failed` (2026-09-04, at file
8/15). Compute nodes have no such cap; /tmp is node-local, so the script has to live in
the repo rather than a scratch directory.
"""
from __future__ import annotations

import argparse
import os


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_id")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--allow", nargs="*",
                    default=["*.json", "*.safetensors", "tokenizer*", "*.model", "*.txt"],
                    help="glob patterns to fetch (default: safetensors weights + tokenizer)")
    a = ap.parse_args()
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
    from huggingface_hub import snapshot_download

    p = snapshot_download(a.repo_id, max_workers=a.workers, allow_patterns=a.allow)
    print("DONE", p, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
