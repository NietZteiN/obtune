#!/usr/bin/env python
"""Re-derive the experiment checklist's coverage matrix FROM DISK.

    python scripts/paper/coverage_matrix.py --write   # update docs/EXPERIMENT_CHECKLIST.md

A hand-maintained coverage table drifts the moment a job lands, and a drifted one is worse than
none: it is the document used to decide what to run next. This reads `results/cells/` and
`runs/adapters/` and rewrites the table between its two anchors, so the checklist cannot disagree
with the filesystem.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = ["codellama-7b", "codellama-13b", "codellama-34b", "llama31-8b",
          "starcoder2-15b", "gemma3-12b", "codegemma-7b", "granite31-8b"]
NICE = {"codellama-7b": "CodeLlama-7B", "codellama-13b": "CodeLlama-13B",
        "codellama-34b": "CodeLlama-34B", "llama31-8b": "Llama-3.1-8B",
        "starcoder2-15b": "StarCoder2-15B", "gemma3-12b": "Gemma-3-12B",
        "codegemma-7b": "CodeGemma-7B", "granite31-8b": "Granite-3.1-8B"}
SPEC = ["L1b", "L1r", "L2", "S1", "S2"]
START, END = "## What exists today", "**Routing, merging and ICL exist on one model of eight.**"


def n_cells(phase: str, model: str) -> int:
    p = ROOT / "results/cells" / phase / model / "python"
    return len(list(p.iterdir())) if p.is_dir() else 0


def build() -> str:
    y = lambda b: "✅" if b else "❌"
    rows = []
    for m in MODELS:
        specs = sum((ROOT / f"runs/adapters/{m}/python/{c}_r32_s17/best/adapter_model.safetensors").exists()
                    for c in SPEC)
        merges = len(list((ROOT / f"runs/adapters/{m}/python").glob("*merge*_r32_s17"))) \
            if (ROOT / f"runs/adapters/{m}/python").is_dir() else 0
        rows.append(
            f"| {NICE[m]} | {y(n_cells('panel_core', m) >= 35)} | "
            f"{y(n_cells('composite_generic', m) >= 30)} | {y(n_cells('f2_divergence', m) >= 30)} | "
            f"{y(n_cells('basecheck_1shot', m) > 0)} | {y(n_cells('inverse_generic', m) > 0)} | "
            f"{specs}/5 | {y(merges > 0)} | {y((ROOT / f'runs/mole/{m}/python').is_dir())} |")
    return ("| model | ladder+family | seen stacks | unseen stacks | ICL | reverse | "
            "specialists | merges | router |\n|---|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    table = build()
    print(table)
    if a.write:
        p = ROOT / "docs/EXPERIMENT_CHECKLIST.md"
        s = p.read_text()
        i, j = s.index(START), s.index(END)
        s = (s[:i] + START + "\n\n*Re-derived from disk by `scripts/paper/coverage_matrix.py`; "
             "do not hand-edit — regenerate.*\n\n" + table + "\n\n" + s[j:])
        p.write_text(s)
        print(f"\nrewrote the table in {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
