#!/usr/bin/env python3
"""Audit results/cells for vLLM prefix-cache contamination between same-named adapters.

vLLM hashes prefix-cache blocks on `LoRARequest.lora_name`. Until 2026-09-03 eval_vllm named
adapters `<parent>/<leaf>`, so `runs/adapters/.../L0_r32_s17/best` and
`runs/adapters_formatonly/.../L0_r32_s17/best` shared a name, and whichever was evaluated
second in an engine decoded on top of the first one's cached prefill. Symptoms: elapsed_s
roughly halved, ~60 % output agreement with the same adapter evaluated elsewhere, 3-6 pts
lower accuracy. 28 cells were affected, one of them the CodeLlama H1 pilot's tuned_L0 row.

A cell is flagged when, within one job (cells sharing `run_ts`, written in mtime order), an
adapter with the same legacy name but a different path was loaded earlier. Cells produced
after the fix cannot collide (names are full paths) but are scanned anyway.

    python scripts/audit_prefix_collisions.py            # report
    python scripts/audit_prefix_collisions.py --move DIR # quarantine them under DIR
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def legacy_name(p: str) -> str:
    q = Path(p)
    return q.parent.name + "/" + q.name


def scan(cells_root: Path):
    cells = []
    for m in glob.glob(str(cells_root / "*/*/*/*/cell_meta.json")):
        if "/_contaminated" in m:
            continue
        d = json.load(open(m))
        if not str(d.get("engine", "")).startswith("vllm"):
            continue
        rel = Path(m).relative_to(cells_root).parts
        cells.append((rel[0], rel[1], rel[2], d["run_ts"], os.path.getmtime(m), rel[3],
                      tuple(sorted(set(d.get("adapter_paths") or []))), os.path.dirname(m)))
    cells.sort(key=lambda r: (r[0], r[1], r[2], r[3], r[4]))
    groups = collections.defaultdict(list)
    for r in cells:
        groups[r[:4]].append(r)
    bad = []
    for rows in groups.values():
        seen: dict[str, str] = {}
        for r in rows:
            hits = [(legacy_name(p), seen[legacy_name(p)]) for p in r[6]
                    if legacy_name(p) in seen and seen[legacy_name(p)] != p]
            if hits:
                bad.append((r[7], hits[0][1]))
            for p in r[6]:
                seen.setdefault(legacy_name(p), p)
    return len(cells), bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", default=str(ROOT / "results" / "cells"))
    ap.add_argument("--move", default=None, help="move flagged cells under this dir")
    a = ap.parse_args()
    n, bad = scan(Path(a.cells))
    print(f"{n} vLLM cells scanned; {len(bad)} contaminated")
    for cell, src in bad:
        print(f"  {os.path.relpath(cell, a.cells)}   prefill from {src}")
    if a.move and bad:
        dst = Path(a.move)
        for cell, _ in bad:
            tgt = dst / Path(cell).relative_to(a.cells)
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(cell, tgt)
        print(f"moved {len(bad)} cell(s) under {dst}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
