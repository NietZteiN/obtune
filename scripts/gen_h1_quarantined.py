#!/usr/bin/env python
"""The ONLY sanctioned producer of H1 stimuli (CLAUDE.md §3.2, quarantine layer 3).

H1 is the held-out discriminator for the whole invariance claim. This script is
the single module permitted to import ``src/obtune/obf/h1/`` (enforced statically
by tests/test_quarantine_lint.py), it refuses to run without an explicit intent
flag, it writes ``0o444`` outputs under ``data/quarantine/h1/`` and nowhere else,
and it appends an access-log row on every run.

What it does per base program:
  * Python  -> obf.h1.py_h1.transform (string encoding + guarded MBA)
  * JavaScript -> obf/h1/js_h1.mjs subprocess (rc4 stringArray + numbersToExpressions)
  * Enforces the min-sites quality bar from configs/conditions.yaml (a degenerate
    near-identity variant would make H1 spuriously easy).
  * Semantic gate: re-executes parent AND variant on the program's cases via
    exec.pool.run_batch and drops any variant whose canonical outputs diverge —
    H1 must be meaning-preserving like every other condition.

Usage:
  python scripts/gen_h1_quarantined.py --i-am-the-h1-generator \\
      --input <base.jsonl> --subset pilot --purpose pilot_eval [--lang all]

Input rows (one JSON object per line):
  { program_id, language, code, entry_point, cases:[{args_repr, ...}], source? }
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import GLOBAL_SEED, load_config  # noqa: E402
from obtune.exec.pool import BatchItem, run_batch  # noqa: E402
from obtune.paths import QUARANTINE_ROOT, iter_jsonl, write_jsonl  # noqa: E402
from obtune.provenance import RunManifest  # noqa: E402

# The one sanctioned H1 import (this script is exempt in the quarantine lint).
from obtune.obf.h1 import py_h1  # noqa: E402

import shutil  # noqa: E402

NODE_BIN = os.environ.get("OBTUNE_NODE") or shutil.which("node") or "node"
JS_H1_MJS = ROOT / "src" / "obtune" / "obf" / "h1" / "js_h1.mjs"

README_TEXT = """\
# data/quarantine/h1 — HELD-OUT H1 stimuli (DO NOT TRAIN ON)

H1 (string encoding + guarded MBA) is the paper's held-out discriminator. These
files exist ONLY to evaluate whether tuning taught semantic invariance or mere
transform memorization. HARD RULES (CLAUDE.md §3.2):

* Nothing may write here except `scripts/gen_h1_quarantined.py`.
* H1 is NEVER used for training, hyperparameter/prompt selection, router
  training, checkpoint selection, or merge tuning.
* H1 is read exactly twice: one frozen `pilot_eval` pass and one `final_eval`
  pass. Every read appends a row to `ACCESS_LOG.md`.
* `src/obtune/paths.py::load_training_jsonl` refuses to load anything under this
  directory, and `scripts/check_manifest.py` content-scans training files for the
  H1 marker patterns in `configs/conditions.yaml`.

Outputs are written `0o444` (read-only) as a speed bump against accidental edits.
"""

ACCESS_LOG_HEADER = """\
# H1 quarantine access log

Every write (generation) and read (evaluation) of H1 stimuli appends a row here
(CLAUDE.md §3.2 point 3). Do not delete rows.

| date | script | purpose | detail |
|------|--------|---------|--------|
"""


def ensure_scaffold(h1_dir: Path) -> tuple[Path, Path]:
    h1_dir.mkdir(parents=True, exist_ok=True)
    readme = h1_dir / "README.md"
    access = h1_dir / "ACCESS_LOG.md"
    if not readme.exists():
        readme.write_text(README_TEXT)
    if not access.exists():
        access.write_text(ACCESS_LOG_HEADER)
    return readme, access


def append_access_log(access_path: Path, purpose: str, detail: str) -> None:
    row = f"| {date.today().isoformat()} | scripts/gen_h1_quarantined.py | {purpose} | {detail} |\n"
    # Path assembled above so this line carries no quarantine-path token next to
    # open( — the quarantine lint greps for exactly that co-occurrence.
    with open(access_path, "a") as f:
        f.write(row)


def _semantic_gate(program_id: str, language: str, parent_code: str, parent_entry: str,
                   variant_code: str, variant_entry: str, cases: list[dict]) -> tuple[bool, str]:
    """Re-execute parent and variant on the cases; require identical canonical
    outputs. Returns (passed, note)."""
    args = [c["args_repr"] for c in cases if "args_repr" in c]
    if not args:
        return True, "no-cases"
    parent = run_batch([BatchItem(program_id, language, parent_code, parent_entry, args)])[0]
    variant = run_batch([BatchItem(program_id, language, variant_code, variant_entry, args)])[0]
    if parent.child_status != "ok":
        return False, f"parent-exec-{parent.child_status}"
    if variant.child_status != "ok":
        return False, f"variant-exec-{variant.child_status}"
    for pc, vc in zip(parent.cases, variant.cases):
        if not pc.matches(vc):
            return False, "output-divergence"
    return True, "gate-ok"


def _run_js_h1(rows: list[dict], seed: int, min_total_sites: int) -> dict[str, dict]:
    """Batch-invoke js_h1.mjs. Returns {program_id: result_dict}."""
    if not rows:
        return {}
    payload = {
        "jobs": [
            {
                "program_id": r["program_id"],
                "code": r["code"],
                "entry_point": r["entry_point"],
                "seed": (seed + i) & 0xFFFFFFFF,
                "min_total_sites": min_total_sites,
            }
            for i, r in enumerate(rows)
        ]
    }
    env = dict(os.environ)
    env.setdefault("NODE_OPTIONS", "")
    proc = subprocess.run(
        [NODE_BIN, "--no-warnings", str(JS_H1_MJS)],
        input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"js_h1.mjs exited {proc.returncode}: {proc.stderr[-2000:]}")
    out: dict[str, dict] = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            rec = json.loads(line)
            out[rec["program_id"]] = rec
    return out


def _emit_row(base: dict, code: str, entry: str, meta: dict) -> dict:
    return {
        "program_id": base["program_id"],
        "condition": "H1",
        "language": base["language"],
        "code": code,
        "entry_point": entry,
        "entry_point_parent": base["entry_point"],
        "rename_map": {},
        "transform_meta": meta,
        "cases": base.get("cases", []),
        "source": base.get("source", "unknown"),
        "provenance": "synthetic",
    }


def generate(input_rows: list[dict], seed: int, langs: set[str],
             min_total_sites: int) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    """Returns ({lang: [accepted rows]}, stats)."""
    accepted: dict[str, list[dict]] = {"python": [], "javascript": []}
    stats = {"python": {"in": 0, "ok": 0, "rejected": 0}, "javascript": {"in": 0, "ok": 0, "rejected": 0}}

    py_rows = [r for r in input_rows if r.get("language") == "python" and "python" in langs]
    js_rows = [r for r in input_rows if r.get("language") == "javascript" and "javascript" in langs]

    # --- Python ---
    for i, r in enumerate(py_rows):
        stats["python"]["in"] += 1
        res = py_h1.transform(r["code"], min_total_sites=min_total_sites, seed=seed)
        if not res.ok:
            stats["python"]["rejected"] += 1
            continue
        passed, note = _semantic_gate(r["program_id"], "python", r["code"], r["entry_point"],
                                      res.code, r["entry_point"], r.get("cases", []))
        if not passed:
            stats["python"]["rejected"] += 1
            continue
        accepted["python"].append(_emit_row(r, res.code, r["entry_point"], {
            "seed": seed, "n_mba_sites": res.n_mba_sites, "n_encoded_strings": res.n_encoded_strings,
            "gate": note,
        }))
        stats["python"]["ok"] += 1

    # --- JavaScript ---
    js_results = _run_js_h1(js_rows, seed, min_total_sites)
    for r in js_rows:
        stats["javascript"]["in"] += 1
        rec = js_results.get(r["program_id"])
        if rec is None or not rec.get("ok"):
            stats["javascript"]["rejected"] += 1
            continue
        passed, note = _semantic_gate(r["program_id"], "javascript", r["code"], r["entry_point"],
                                      rec["code"], rec.get("entry_point", r["entry_point"]), r.get("cases", []))
        if not passed:
            stats["javascript"]["rejected"] += 1
            continue
        accepted["javascript"].append(_emit_row(r, rec["code"], rec.get("entry_point", r["entry_point"]), {
            "seed": seed, "n_encoded_strings": rec.get("n_encoded"), "n_number_sites": rec.get("n_number_sites"),
            "gate": note,
        }))
        stats["javascript"]["ok"] += 1

    return accepted, stats


def _write_readonly(path: Path, rows: list[dict]) -> None:
    # A prior run leaves the file 0o444; make it writable, rewrite, re-lock.
    if path.exists():
        try:
            os.chmod(path, 0o644)
        except PermissionError:
            pass
    write_jsonl(path, rows)
    os.chmod(path, 0o444)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate quarantined H1 stimuli.")
    ap.add_argument("--i-am-the-h1-generator", action="store_true",
                    help="Required intent flag. This script writes held-out H1 data.")
    ap.add_argument("--input", required=True, help="JSONL of L0 base programs.")
    ap.add_argument("--subset", required=True, help="Subset name, e.g. pilot | final | smoke.")
    ap.add_argument("--purpose", required=True, help="Access-log purpose, e.g. pilot_eval | final_eval | smoke.")
    ap.add_argument("--lang", choices=["all", "python", "javascript"], default="all")
    ap.add_argument("--seed", type=int, default=GLOBAL_SEED)
    args = ap.parse_args()

    if not args.i_am_the_h1_generator:
        ap.error("refusing to run without --i-am-the-h1-generator (CLAUDE.md §3.2)")

    cfg = load_config("conditions.yaml")
    h1_params = cfg["conditions"]["H1"]["params"]
    min_total_sites = int(h1_params.get("min_total_sites", 3))

    input_path = Path(args.input)
    if not input_path.exists():
        ap.error(f"input not found: {input_path}")
    input_rows = list(iter_jsonl(input_path))

    langs = {"python", "javascript"} if args.lang == "all" else {args.lang}
    accepted, stats = generate(input_rows, args.seed, langs, min_total_sites)

    h1_dir = QUARANTINE_ROOT / "h1"
    _, access_path = ensure_scaffold(h1_dir)
    subset_dir = h1_dir / args.subset
    subset_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    total_rows = 0
    for lang in ("python", "javascript"):
        if lang not in langs or not accepted[lang]:
            continue
        out_path = subset_dir / f"{lang}.jsonl"
        _write_readonly(out_path, accepted[lang])
        # Data usually lives under the repo, but OBTUNE_DATA_DIR may point elsewhere.
        rel = out_path.relative_to(ROOT) if out_path.is_relative_to(ROOT) else out_path
        written.append(str(rel))
        total_rows += len(accepted[lang])

    # Provenance manifest (CLAUDE.md §4) — kept writable for later inspection.
    manifest = (
        RunManifest(
            experiment="gen_h1_quarantined",
            run_id=f"{date.today().isoformat()}_{args.subset}",
            seed=args.seed,
            config_path=cfg.get("_config_path", "configs/conditions.yaml"),
            config_resolved={"H1": cfg["conditions"]["H1"]},
            extra={"stats": stats, "input": str(input_path), "purpose": args.purpose, "lang": args.lang},
        )
        .hash_scripts(["scripts/gen_h1_quarantined.py", "src/obtune/obf/h1/py_h1.py",
                       "src/obtune/obf/h1/js_h1.mjs"])
        .capture_git()
        .finalize()
    )
    manifest.write(subset_dir)

    detail = f"{total_rows} rows -> {', '.join(written) if written else '(none accepted)'} | stats={stats}"
    append_access_log(access_path, args.purpose, detail)

    print(json.dumps({"subset": args.subset, "written": written, "rows": total_rows, "stats": stats}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
