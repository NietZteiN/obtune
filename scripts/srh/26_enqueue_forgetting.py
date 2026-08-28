#!/usr/bin/env python
"""Enqueue catastrophic-forgetting cells (HumanEval+ / L0) into the file-queue scheduler.

    python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps
    python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps --write
    python scripts/srh/26_enqueue_forgetting.py --cell qwen25c-1.5b:mix5:runs/.../final

Dry run by default; `--write` is the only thing that puts work in front of a GPU.

WHY THIS EXISTS
---------------
The forgetting cells run so far were enqueued from hand-written manifests
(`runs/manifest/done/05*_forget__*.json`). That worked, but hand-written manifests skip
every precondition the queue itself cannot express, and this thread has already been bitten
by two of them: a `systems:` deep-merge that pointed a 7B eval at a 1.5B adapter
(`scripts/preflight.py` exists because of it), and duplicate job ids writing the same
results directory from two workers. `22_enqueue_evals.py` closed that gap for evaluations;
this closes it for forgetting.

Four preconditions are asserted here, and a job that fails any of them is not enqueued:

  1. **The adapter exists now.** The queue has no dependency edges, so a job naming an
     adapter that is still training would be claimed and would score a missing path.
  2. **The adapter belongs to the model.** The path must contain the model key. This is
     the preflight defect: a 1.5B adapter under a 7B model loads without error and
     produces garbage under a real arm's label.
  3. **No duplicate job id** across queued / running / done.
  4. **The result file does not already exist.** `obtune.forgetting` overwrites without
     asking. Several of those numbers are published in `paper_bidirectional/main.tex`
     Table 5, so a re-run under an existing tag would silently replace a number the paper
     quotes with one produced by a different pass. Pass `--allow-overwrite` to mean it.
     The filename is SUITE-DERIVED (`result_path`); it used to be hardcoded to the
     HumanEval+ stem, which made every MBPP+ cell look already-run.

Preconditions 1 and 2 are skipped for an EMPTY adapter, which means the untouched base
model. Without that exemption the base cell cannot be enqueued at all, and the base cell is
the reference point every forgetting delta is measured against.

PRIORITY IS A SCHEDULING DECISION, NOT A TECHNICAL ONE
------------------------------------------------------
The ladder in use on this host (see `22_enqueue_evals.py`):

    10-50   obtune's own RQ1 / modularity grid
    58-60   forgetting cells for the CFT/SRH thread
    61-63+  Experiment 1 stages

The default here is **59**, which deliberately does *not* jump the queue. As of 2026-08-17
the queue holds five modularity jobs at priority 10-20 (two trainings and three
checkpoint-selections) belonging to the FSE paper, so these cells will be claimed only
after those drain -- possibly hours. That is the correct default: the RQ1/modularity grid
is not this thread's to delay.

If the ATTRIB deadline warrants going first, that is a deliberate act with a cost to the
other paper, so it must be typed explicitly:

    python scripts/srh/26_enqueue_forgetting.py --preset attrib-gaps --priority 5 --write

WHAT THE `attrib-gaps` PRESET ANSWERS
-------------------------------------
Five cells, ~105 s each at 1.5B (measured from the completed cells), longer at 7B.

  * `mix5` / `mix10` / `mix25` at 1.5B -- the dose ladder's general-capability cost.
    Figure 1 shows the reverse-capability BENEFIT saturates by a 5 % reverse share
    (`mix5` 26.1 % vs `mix50` 30.5 %). Section 8 reports that bidirectional data COSTS
    6-7 points of HumanEval+ at 7B. Nobody has measured whether that cost is dose-
    dependent. If it falls with the reverse share while the benefit does not, `mix5`
    dominates `mix50` and section 8 becomes a prescription rather than a caveat; if it is
    flat, that is one honest sentence. Either outcome is publishable, which is what makes
    this the highest-value cell left.
  * `rev` / `fwd2x` at 7B -- the two blank rows in Table 5's 7B column. `rev` is the
    pure-reverse extreme of the cost story; `fwd2x` is the compute control.

(Both of the above completed 2026-08-17 and are folded into the paper.)

WHAT THE `mbpp-7b` PRESET ANSWERS
---------------------------------
    python scripts/srh/26_enqueue_forgetting.py --preset mbpp-7b --suite mbpp

Seven cells, the whole 7B arm set, on a probe that is genuinely held out. The paper's
selectivity claim -- forward-only tuning destroys the reverse direction while general
coding ability is untouched -- currently rests on HumanEval+, and HumanEval is one of the
three sources of our own training corpus. 74 of its 164 problems are in the train split, so
for the arms-vs-base contrast that number is contaminated, which the body admits and the
abstract does not. MBPP is not in the corpus at all: `data/manifests/corpus_python.json`
records `tiers: ['tier1']` and MBPP sits only under `tier2`, never built. 0 of 399.

Either outcome is publishable. If the grouping reproduces, the cost claim and the
selectivity claim both harden on clean data. If it does not, the paper says so before a
reviewer finds it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.sched.worker import DONE, QUEUED, RUNNING  # noqa: E402

DEFAULT_PRIORITY = 59
RESULTS_FORGETTING = ROOT / "results" / "forgetting"

#: (model, tag, adapter) triples. The `7b_` tag prefix is not decoration: the existing 7B
#: cells in results/forgetting/ carry it, and the Table 5 build reads those filenames.
PRESETS: dict[str, list[tuple[str, str, str]]] = {
    "attrib-gaps": [
        ("qwen25c-1.5b", "mix5",
         "runs/adapters_srh/qwen25c-1.5b/python/all5_mix5_r32_s17/final"),
        ("qwen25c-1.5b", "mix10",
         "runs/adapters_srh/qwen25c-1.5b/python/all5_mix10_r32_s17/final"),
        ("qwen25c-1.5b", "mix25",
         "runs/adapters_srh/qwen25c-1.5b/python/all5_mix25_r32_s17/final"),
        ("qwen25c-7b", "7b_rev",
         "runs/adapters_srh/qwen25c-7b/python/all5_rev_r32_s17/final"),
        ("qwen25c-7b", "7b_fwd2x",
         "runs/adapters_srh/qwen25c-7b/python/all5_fwd2x_r32_s17/final"),
    ],
    #: The seven 7B arms of Table 5, on the HELD-OUT probe. Run with `--suite mbpp`.
    #: Every adapter path here is byte-identical to the one the corresponding published
    #: HumanEval+ cell used (checked against the `adapter` field of each
    #: `results/forgetting/humanevalplus_qwen25c-7b_*.json`), so the two probes are
    #: measured on the same weights and the columns are comparable.
    #: `7b_base` carries an EMPTY adapter -- the untouched model. See `problems_for`.
    "mbpp-7b": [
        ("qwen25c-7b", "7b_base", ""),
        ("qwen25c-7b", "7b_sft",
         "runs/adapters_cft/qwen25c-7b/python/sft_r32_s17/final"),
        ("qwen25c-7b", "7b_cft",
         "runs/adapters_cft/qwen25c-7b/python/cft_r32_s17/final"),
        ("qwen25c-7b", "7b_fwd2x",
         "runs/adapters_srh/qwen25c-7b/python/all5_fwd2x_r32_s17/final"),
        ("qwen25c-7b", "7b_rev",
         "runs/adapters_srh/qwen25c-7b/python/all5_rev_r32_s17/final"),
        ("qwen25c-7b", "7b_flip",
         "runs/adapters_srh/qwen25c-7b/python/all5_flip_r32_s17/final"),
        ("qwen25c-7b", "7b_mix50",
         "runs/adapters_srh/qwen25c-7b/python/all5_mix50_r32_s17/final"),
    ],
}

#: MEASURED, not guessed -- means over the 13 healthy cells already in
#: `runs/manifest/done/*forget*.json` (the `u15_*`/`u7b_*` unlearning cells are excluded:
#: they run 150-183 s because over-negated adapters emit long degenerate output, which is a
#: property of those arms and not of the suite). 1.5B mean 97 s over 8 cells, 7B mean 124 s
#: over 5.
#:
#: Note how little the model size matters: 7B is only ~1.3x 1.5B, because the suite is
#: dominated by fixed cost -- engine startup, model load, and 164 HumanEval+ tasks plus the
#: L0 pass -- rather than by forward speed. An earlier version of this table guessed 0.1/0.4,
#: which overstated 7B by 10x and would have made the scheduler reserve far more budget than
#: these cells consume.
EST_GPU_H = {"qwen25c-1.5b": 0.027, "qwen25c-7b": 0.034}

#: MBPP+ needs its own budget: 399 tasks against HumanEval+'s 164, and its scoring is the
#: heavier half (many more `plus_input` cases per task, executed under multiprocessing).
#: The card is held during that CPU-bound phase, so wall-clock overstates real GPU need.
#: Measured `--suite both` 7B cells run 104-158 s; budget ~5-6 min for an MBPP+ cell.
EST_GPU_H_MBPP = {"qwen25c-1.5b": 0.07, "qwen25c-7b": 0.10}


def result_path(model: str, tag: str, suite: str, language: str) -> Path:
    """The file `obtune.forgetting` will write for this cell.

    Suite-derived, because a guard that checks the wrong filename is worse than no guard.
    With the stem hardcoded to `humanevalplus_` -- as it was until 2026-08-17 -- every
    MBPP+ cell reported RESULT EXISTS, because all seven of those HumanEval+ files are on
    disk, and was silently dropped. The tempting workaround (`--allow-overwrite`) would
    have disarmed the guard that protects the Table 5 numbers, which is exactly backwards.

    `both` writes two files; it guards the HumanEval+ one, since that is the number the
    paper quotes.
    """
    stem = {
        "mbpp": f"mbppplus_{model}_{tag}",
        "l0": f"l0_{model}_{language}_{tag}",
    }.get(suite, f"humanevalplus_{model}_{tag}")
    return RESULTS_FORGETTING / f"{stem}.json"


def problems_for(model: str, tag: str, adapter: str, seen: set[str], job_id: str,
                 allow_overwrite: bool, suite: str, language: str) -> list[str]:
    out: list[str] = []

    # An EMPTY adapter is the untouched base model, deliberately -- not a missing path.
    # Both adapter preconditions have to be skipped for it, or the base cell is
    # unenqueueable and there is no reference point to measure a forgetting delta against.
    # That is why `7b_base` was originally run from a hand-written manifest
    # (`runs/manifest/done/060_forget7b__base.json`) instead of through this script.
    if adapter:
        if not (ROOT / adapter).exists():
            out.append(f"MISSING ADAPTER {adapter}")
        # Precondition 2 -- see the module docstring. `in` rather than a parse because
        # adapter layouts differ between runs/adapters_cft and runs/adapters_srh.
        if model not in adapter:
            out.append(f"MODEL MISMATCH {adapter} does not carry model key {model}")
    if job_id in seen:
        out.append("job id already queued/running/done — remove it first to re-run")

    existing = result_path(model, tag, suite, language)
    if existing.exists() and not allow_overwrite:
        out.append(
            f"RESULT EXISTS {existing.relative_to(ROOT)} — running would overwrite it. "
            "Table 5 quotes these; pass --allow-overwrite if that is intended."
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--preset", choices=sorted(PRESETS),
                    help="a named set of cells; see PRESETS")
    ap.add_argument("--cell", action="append", default=[],
                    metavar="MODEL:TAG:ADAPTER",
                    help="an ad-hoc cell; repeatable")
    # These tokens are passed STRAIGHT THROUGH to `obtune.forgetting --suite`, so they must
    # be exactly its choices. Until 2026-08-17 this offered `humanevalplus`, which
    # `forgetting.py` does not accept -- any job enqueued that way died on argparse after
    # being claimed. Fixed by matching the sets; `humanevalplus` is dropped because it never
    # worked, so nothing on disk depends on it.
    ap.add_argument("--suite", default="both",
                    choices=["both", "humaneval", "l0", "mbpp"],
                    help="`mbpp` is the held-out probe (399 tasks) and runs standalone")
    ap.add_argument("--language", default="python")
    ap.add_argument("--priority", type=int, default=DEFAULT_PRIORITY,
                    help=f"lower runs first; default {DEFAULT_PRIORITY} does NOT jump "
                         "the RQ1/modularity grid at 10-20")
    ap.add_argument("--allow-overwrite", action="store_true",
                    help="permit a cell whose result file already exists")
    ap.add_argument("--write", action="store_true",
                    help="actually enqueue; without it this is a dry run")
    args = ap.parse_args()

    cells = list(PRESETS.get(args.preset, [])) if args.preset else []
    for spec in args.cell:
        parts = spec.split(":", 2)
        if len(parts) != 3:
            print(f"bad --cell {spec!r}; want MODEL:TAG:ADAPTER", file=sys.stderr)
            return 2
        cells.append((parts[0], parts[1], parts[2]))
    if not cells:
        print("nothing to do — pass --preset or --cell", file=sys.stderr)
        return 2

    seen = {p.stem for d in (QUEUED, DONE) if d.exists() for p in d.glob("*.json")}
    if RUNNING.exists():
        seen |= {p.stem for p in RUNNING.glob("*/*.json")}

    jobs, blocked = [], []
    for model, tag, adapter in cells:
        # The job id carries the suite, or a second probe over the same arm collides with
        # the first. `forget__qwen25c-7b__7b_rev` and `__7b_fwd2x` already exist in
        # runs/manifest/done/ from the HumanEval+ pass, so without this those two cells are
        # rejected as duplicates while the other five slip through -- a half-run sweep,
        # which is worse than a cleanly blocked one. The suffix is empty for `both` so every
        # id already on disk keeps its current meaning.
        suffix = "" if args.suite == "both" else f"__{args.suite}"
        job_id = f"forget__{model}__{tag}{suffix}"
        probs = problems_for(model, tag, adapter, seen, job_id, args.allow_overwrite,
                             args.suite, args.language)
        if probs:
            blocked.append((job_id, probs))
            continue
        # `--adapter` is omitted entirely for the base model. Passing an empty string would
        # make `Path("").resolve()` the CWD, and forgetting.py would try to load the project
        # root as a LoRA.
        argv = ["-m", "obtune.forgetting", "--model", model,
                "--suite", args.suite, "--language", args.language, "--tag", tag]
        if adapter:
            argv += ["--adapter", adapter]
        est = (EST_GPU_H_MBPP if args.suite == "mbpp" else EST_GPU_H).get(model, 0.4)
        jobs.append({
            "job_id": job_id,
            "kind": "forgetting",
            # The worker prepends sys.executable, runs from PROJECT_ROOT, and pins
            # CUDA_VISIBLE_DEVICES at spawn — so no --gpu here. Passing one would index
            # into the worker's already-masked device list.
            "argv": argv,
            "raw": False,
            "est_gpu_h": est,
            "priority": args.priority,
            "meta": {
                "experiment": "srh/exp1",
                "check": "CLAUDE.md 4.7 catastrophic forgetting",
                "model": model,
                "tag": tag,
                "adapter": adapter or None,
                "suite": args.suite,
                "paper": "paper_bidirectional §8 / Table 5",
                "question": (
                    "is the general-capability cost real on a HELD-OUT probe? HumanEval is "
                    "one of the corpus's three sources, so 74/164 HumanEval+ problems are "
                    "in the train split; MBPP is 0/399. (log/cft-replication/2026-08-17)"
                    if args.suite == "mbpp" else
                    "does the general-capability COST scale with reverse share, given "
                    "that the reverse-capability BENEFIT saturates by 5 %? "
                    "(log/cft-replication/2026-08-17, H-C1)"
                ),
            },
        })

    for job_id, probs in blocked:
        print(f"  [BLOCKED] {job_id}")
        for p in probs:
            print(f"            {p}")
    for j in jobs:
        print(f"  [ok] p{j['priority']:>3} {j['job_id']:<40} "
              f"est {j['est_gpu_h']}h  -> {j['meta']['adapter'] or '(base model, no adapter)'}")

    if blocked:
        print(f"\n{len(blocked)} cell(s) blocked — nothing enqueued for them.")
    if not args.write:
        print(f"\ndry run — {len(jobs)} cell(s) would be enqueued at priority "
              f"{args.priority}. Pass --write to enqueue.")
        if jobs and args.priority >= 50:
            print("NOTE: at this priority these sit behind the RQ1/modularity grid "
                  "(priority 10-20) and will not start until it drains.")
        return 1 if blocked else 0

    QUEUED.mkdir(parents=True, exist_ok=True)
    for j in jobs:
        dest = QUEUED / f"{j['job_id']}.json"
        dest.write_text(json.dumps(j, indent=2))
        print(f"enqueued {dest}")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
