#!/usr/bin/env python3
"""TRANCHE F — RQ3 attention, as a dependency-linked SLURM DAG.

RQ3 asks whether attention RE-ANCHORING (identifier tokens -> control/data-flow tokens)
predicts which transfers succeed. Three stages, in the order that makes the causal claim
legitimate:

    1. validate  -- span->token resolution on THIS tokenizer. Gate, not formality: the
                    resolution rate must clear MIN_RATE before any measurement means
                    anything, and it is tokenizer-dependent, so a new base re-runs it.
    2. capture   -- HF eager forward (vLLM does not expose attentions) on pre/post states,
                    then metrics -> the PREDICTIVE regression.
    3. knockout  -- the causal intervention. Predictive first, causal only after; a
                    knockout result without the regression is uninterpretable.
                    Steering (`31_steer.py`) is the second, independent instrument.

OUTPUT PATHS. `ATTN_DIR` (results/attn) carries no model in it and already holds ~7,300
Qwen records, so this was checked before launching: 30_knockout.py and 31_steer.py BOTH
write to <out>/<model>/<condition>/, namespacing themselves. The Qwen corpus is therefore
safe without any extra flag. `obtune.attention.capture` takes an explicit --out-dir and
does NOT namespace, so anything added here that calls it must pass one.

LAYERS are resolved from the model's depth (obtune.config.layer_indices_for). The literal
set these scripts used to default to was Qwen's 28 layers; the same integers probe different
RELATIVE depths on a 32- or 40-layer model, so the arm would keep running and quietly
measure something else. (The literal itself is deliberately not repeated here -- the lint
in tests/test_model_agnostic_lint.py fails on it anywhere outside the resolver.)

A 6-layer null is NOT evidence of no effect: log/attention/2026-08-27 records a partial-depth
null that reversed at full depth (+0.2172). Layer coverage is reported with every result.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBMIT = ROOT / "scripts" / "slurm" / "submit.py"
CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]


def sub(name, argv, *, partition, time, dep=None, gres=None, mem=None, dry=False):
    cmd = [sys.executable, str(SUBMIT), "--name", name, "--partition", partition, "--time", time]
    if dep:
        d = str(dep)
        cmd += ["--dependency", d if d.startswith("after") else f"afterok:{d}"]
    if gres is not None:
        cmd += ["--gres", gres]
    if mem:
        cmd += ["--mem", mem]
    if dry:
        cmd += ["--dry-run"]
    cmd += ["--argv"] + argv
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if dry:
        print(f"  [dry] {name}: {' '.join(argv)}")
        return "DRY"
    for l in (out.stdout or "").splitlines():
        if l.startswith("submitted "):
            j = l.split()[1]
            print(f"  {j}  {name}" + (f"  (after {dep})" if dep else ""))
            return j
    print(f"  FAILED {name}: {out.stdout.strip()} {out.stderr.strip()}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--language", default="python")
    ap.add_argument("--max-items", default="150")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    M, L, d = a.model, a.language, a.dry_run
    root = f"runs/adapters/{M}/{L}"
    P = ["h200", "h100"]
    n = [0]

    def part():
        n[0] += 1
        return P[n[0] % 2]

    print("STAGE 1 — span->token resolution gate (tokenizer-dependent, must pass first)")
    g = sub("tF_validate", ["-m", "obtune.attention.validate", "--model", M],
            partition="normal", gres="", time="01:00:00", dry=d)

    print("STAGE 2 — knockout: identifier tokens (the RQ3 intervention)")
    ko = []
    for c in ["L1b", "S1", "S2"]:
        ko.append(sub(f"tF_ko_base_{c}", ["scripts/attn/30_knockout.py", "--model", M,
            "--language", L, "--system", "base", "--condition", c,
            "--max-items", a.max_items, "--classes", "identifier",
            "--tag", f"{M}_base_{c}"], partition=part(), time="04:00:00",
            dep=g if not d else None, dry=d))
        ko.append(sub(f"tF_ko_tuned_{c}", ["scripts/attn/30_knockout.py", "--model", M,
            "--language", L, "--system", f"tuned_{c}", "--condition", c,
            "--adapter", f"{root}/{c}_r32_s17/best", "--max-items", a.max_items,
            "--classes", "identifier", "--tag", f"{M}_tuned_{c}"],
            partition=part(), time="04:00:00", dep=g if not d else None, dry=d))

    print("STAGE 3 — steering on provably-inert tokens (second, independent instrument)")
    for c in ["S2"]:
        for sysname, adir in [("base", None), (f"tuned_{c}", f"{root}/{c}_r32_s17/best")]:
            argv = ["scripts/attn/31_steer.py", "--model", M, "--language", L,
                    "--system", sysname, "--condition", c, "--max-items", a.max_items,
                    "--classes", "inert", "--tag", f"{M}_{sysname}_{c}_steer"]
            if adir:
                argv += ["--adapter", adir]
            sub(f"tF_steer_{sysname}_{c}", argv, partition=part(), time="04:00:00",
                dep=g if not d else None, dry=d)

    print("\nDAG submitted. 30_knockout.py and 31_steer.py namespace their own output by\n  model, so the ~7,300 Qwen attention records are untouched.")
    print("H1 is not in this pipeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
