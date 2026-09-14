#!/usr/bin/env python
"""Re-grade every backward cell as if the harness had carried the newline stop it should have.

    python scripts/analysis/72_regrade_inverse.py [--models a,b] [--dry-run]

THE DEFECT. The backward prompt asks for ONE call on ONE line, and the backward configs inherited
the forward stop list ("\\n\\n", fences, <end_of_turn>) without adding "\\n". A model that writes the
call and then starts a fresh "Language: python / Program:" block produces a multi-line reply, and
`inverse.extract_call` refuses multi-line replies by design. 71_backward_defects.py counted 22,893
such replies on the panel -- 21,140 of them in one arm, CodeGemma's TIES merge, where they are 65 %
of ALL its trials and the reason that arm was declared unreadable.

WHY THIS IS A RE-GRADE AND NOT A LOOSENING. A "\\n" stop string makes vLLM return exactly the text
before the first newline. Taking the first line of what was generated is therefore the same
measurement the corrected harness would have made, not a search for a call inside prose: a first
line that is prose still fails, an expression still fails, a keyword call still fails. Verified
safe: 0 of 68,310 sampled replies begin with a newline, so the stop cannot truncate to empty.

WHAT IT WRITES. Beside every `trials.parquet` a `trials_v2.parquet` with the same columns plus
`regrade_v2` ("first_line" on the rows this touched, "" elsewhere), and a `cell_meta_v2.json`. The
originals are NEVER modified, so v1 and v2 stay comparable forever. Readers prefer v2 where it exists
(cellkit, 59_master_tables) and fall back to v1 where it does not, which is any cell with nothing to
re-grade.

WHAT IT DOES NOT TOUCH, with the numbers that say why:
  truncation      3.05 % of trials. Gold calls have p99 = 64 tokens and 0.21 % exceed 128, so the
                  cap already covers every answer that can be right; 38 % of truncations are loops.
  keyword args    0.10 % of trials. Needs signature reordering; not worth the code.
  expressions     0.74 % of trials. Rejected by design in inverse.py and still are.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from obtune import inverse  # noqa: E402
from obtune.data import load_eval_items  # noqa: E402
from obtune.inverse import _unwrap, extract_call  # noqa: E402

CELLS = ROOT / "results" / "cells"
PHASES = ["inverse_1shot", "inverse_generic"]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]


def first_line(raw: str) -> str:
    s = _unwrap(str(raw))
    lines = [l for l in s.splitlines() if l.strip()]
    return lines[0] if lines else ""


def regrade_cell(cell: Path, items_by_key: dict, dry: bool) -> dict:
    df = pd.read_parquet(cell / "trials.parquet")
    bad = df.index[df["format_fail"] == 1]
    cand, texts, items = [], [], []
    for i in bad:
        raw = df.at[i, "output_raw"]
        s = _unwrap(str(raw))
        if len([l for l in s.splitlines() if l.strip()]) < 2:
            continue                      # single-line failures are not this defect
        fl = first_line(raw)
        if not extract_call(fl)[0]:
            continue
        it = items_by_key.get((df.at[i, "snippet_id"], df.at[i, "item_id"]))
        if it is None:
            continue
        cand.append(i); texts.append(fl); items.append(it)
    rec = {"n": int(len(df)), "n_fail_v1": int(len(bad)), "n_regraded": len(cand),
           "acc_v1": float(df["correct"].mean()), "fmt_v1": float(df["format_fail"].mean())}
    if not cand or dry:
        rec.update({"acc_v2": rec["acc_v1"], "fmt_v2": rec["fmt_v1"], "written": False})
        return rec
    grades = inverse.grade_batch(items, texts, workers=8)
    v2 = df.copy()
    v2["regrade_v2"] = ""
    # The trial columns are stored as int64 flags, not bools; pandas refuses a bool into an int
    # column at .at[] assignment (TypeError: Invalid value 'True' for dtype 'int64').
    for i, g in zip(cand, grades):
        v2.at[i, "correct"] = int(g.correct)
        v2.at[i, "parse_ok"] = int(g.parse_ok)
        v2.at[i, "format_fail"] = int(g.format_fail)
        v2.at[i, "raw_exact"] = int(g.raw_exact)
        v2.at[i, "args_exact"] = int(g.raw_exact)
        v2.at[i, "exec_status"] = g.exec_status
        v2.at[i, "exec_output"] = g.exec_output
        v2.at[i, "called_name"] = g.called_name
        v2.at[i, "output_parsed"] = g.pred_norm
        v2.at[i, "grade_method"] = g.method
        v2.at[i, "error_category"] = inverse.error_category(g)
        v2.at[i, "regrade_v2"] = "first_line"
    v2.to_parquet(cell / "trials_v2.parquet", index=False)
    meta = json.loads((cell / "cell_meta.json").read_text())
    meta.update({"grade_version": "v2", "regraded_rows": len(cand),
                 "regrade_rule": "first line of a multi-line reply, == a '\\n' stop string",
                 "accuracy_v1": meta.get("accuracy"), "format_fail_rate_v1": meta.get("format_fail_rate"),
                 "accuracy": float(v2["correct"].mean()),
                 "format_fail_rate": float(v2["format_fail"].mean()),
                 "regraded_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    (cell / "cell_meta_v2.json").write_text(json.dumps(meta, indent=2) + "\n")
    rec.update({"acc_v2": meta["accuracy"], "fmt_v2": meta["format_fail_rate"], "written": True})
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    models = a.models.split(",") if a.models else MODELS
    item_cache: dict[str, dict] = {}
    summary = {}
    print(f"{'cell':52s} {'n':>5s} {'regr':>5s} {'acc v1':>7s} {'acc v2':>7s} {'fmt v1':>7s} {'fmt v2':>7s}")
    for m in models:
        for ph in PHASES:
            base = CELLS / ph / m / "python"
            if not base.exists():
                continue
            for cell in sorted(base.iterdir()):
                if not (cell / "trials.parquet").exists():
                    continue
                meta = json.loads((cell / "cell_meta.json").read_text()) if (cell / "cell_meta.json").exists() else {}
                if meta.get("task") != "input":
                    continue
                cond = cell.name.split("__", 1)[1]
                if cond not in item_cache:
                    item_cache[cond] = {(i.program_id, i.item_id): i
                                        for i in load_eval_items([cond], "python", source="heldout")}
                rec = regrade_cell(cell, item_cache[cond], a.dry_run)
                key = f"{ph}/{m}/{cell.name}"
                summary[key] = rec
                if rec["n_regraded"]:
                    print(f"{key[-52:]:52s} {rec['n']:5d} {rec['n_regraded']:5d} {rec['acc_v1']:7.3f} "
                          f"{rec['acc_v2']:7.3f} {rec['fmt_v1']:7.3f} {rec['fmt_v2']:7.3f}")
    n_cells = len(summary); n_written = sum(1 for r in summary.values() if r["written"])
    n_rows = sum(r["n_regraded"] for r in summary.values())
    print(f"\n{n_cells} backward cells scanned, {n_written} got a v2 ({n_rows} rows re-graded)")
    p = ROOT / "results/analysis/pipeline/regrade_inverse_v2.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                             "dry_run": a.dry_run, "cells": summary}, indent=2) + "\n")
    print(f"  wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
