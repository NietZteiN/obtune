#!/usr/bin/env python
"""Archive post-selection training checkpoints to scratch and leave symlinks behind.

    python scripts/ops/archive_checkpoints.py [--dry-run] [--limit N]

WHAT MOVES. Under every adapter that already has `best/adapter_model.safetensors`, the intermediate
`checkpoint-*/` directories and `final/`. Every evaluation in the project reads `best/` only;
checkpoint selection reads `checkpoint-*` only for adapters that do NOT yet have `best/`, which are
excluded here by construction. So nothing running or queued depends on what moves.

WHY. /work hit the per-user quota on 2026-09-14 with 357 GB in these directories across 152
adapters. They are the raw training record and are kept, not deleted: each is copied to
/scratch/juno/$USER/obtune_ckpt_archive/<same relative path>, verified by file count and apparent
bytes, and only then removed from /work and replaced by a SYMLINK to the archive, so every path
anyone has written down still resolves. Authorised by the user ("archive and change the links to
scratch"). Per-directory: a directory whose verification fails is left in place and reported.

CAVEAT. /scratch carries an unconfirmed purge policy (scripts/env.sh). best/ stays on /work; only
the record moves. If scratch is purged, the symlinks dangle and the record is gone -- which is the
trade the user chose over deleting it outright.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path(f"/scratch/juno/{os.environ['USER']}/obtune_ckpt_archive")
ROOTS = [ROOT / "runs/adapters", ROOT / "runs/adapters_objectives"]


def inventory(d: Path):
    n = b = 0
    for f in d.rglob("*"):
        if f.is_symlink():
            n += 1; b += f.lstat().st_size
        elif f.is_file():
            n += 1; b += f.stat().st_size
    return n, b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after N directories (0 = all)")
    a = ap.parse_args()

    targets = []
    for root in ROOTS:
        for best in sorted(root.glob("*/python/*/best/adapter_model.safetensors")):
            adir = best.parent.parent
            for d in sorted(adir.glob("checkpoint-*")) + ([adir / "final"] if (adir / "final").exists() else []):
                if d.is_symlink():
                    continue  # already archived
                targets.append(d)
    print(f"{len(targets)} directories to archive", flush=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "README.md").write_text(
        "# obtune checkpoint archive\n\nIntermediate `checkpoint-*/` and `final/` directories moved here from\n"
        f"{ROOT}/runs/adapters and runs/adapters_objectives on {dt.date.today()} because /work hit its quota.\n"
        "Each original path is now a symlink to its twin here. `best/` never moved. Regenerable from the\n"
        "configs and seeds in the repo, at ~20-45 GPU-min per adapter.\n")
    done = failed = 0; moved_bytes = 0
    log = ROOT / "results/analysis/pipeline/ckpt_archive.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as lf:
        for i, src in enumerate(targets):
            if a.limit and i >= a.limit:
                break
            rel = src.relative_to(ROOT)
            dst = ARCHIVE / rel
            n_src, b_src = inventory(src)
            if a.dry_run:
                print(f"would move {rel} ({b_src/2**30:.2f} GB, {n_src} files)")
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(["rsync", "-a", str(src) + "/", str(dst) + "/"], capture_output=True, text=True)
            n_dst, b_dst = inventory(dst) if dst.exists() else (0, 0)
            ok = r.returncode == 0 and (n_src, b_src) == (n_dst, b_dst) and n_src > 0
            rec = {"src": str(rel), "files": n_src, "bytes": b_src, "rsync_rc": r.returncode,
                   "verified": ok, "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            if ok:
                shutil.rmtree(src)
                os.symlink(dst, src)
                done += 1; moved_bytes += b_src
                rec["symlink"] = True
            else:
                failed += 1
                rec["stderr"] = (r.stderr or "")[-300:]
                print(f"NOT VERIFIED, left in place: {rel}  rc={r.returncode} src={n_src}/{b_src} dst={n_dst}/{b_dst}", flush=True)
            lf.write(json.dumps(rec) + "\n"); lf.flush()
            if (i + 1) % 25 == 0 or ok and i < 3:
                print(f"[{i+1}/{len(targets)}] {rel}  moved so far {moved_bytes/2**30:.0f} GB, failed {failed}", flush=True)
    print(f"done: {done} archived ({moved_bytes/2**30:.0f} GB), {failed} left in place", flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
