"""Bidirectional evaluation: forward obfuscation and reverse deobfuscation.

    python -m obtune.cft.evaluate --config cft/eval/bidir_v1.yaml

This is the paper's Experiment 1 (§4.1, forward) and Experiment 3 (§4.3, reverse) run
over the same systems, which is what makes the headline comparison possible: a model
that is good forward and useless in reverse exhibits **cognitive specialization**
(§2.2 Definition 2), and CFT's claim is that it recovers the reverse direction without
ever being trained on it.

Systems evaluated (config `systems`):
  `base` — the untuned model. Required: it is the reference for the paper's S2/S3
           comparisons (eq. 2, 3) and the only way to tell "fine-tuning degraded the
           reverse direction" from "the model never had it".
  `sft`  — the gen-only arm (the paper's Standard Fine-Tuning).
  `cft`  — the three-task contrastive arm.

Everything is evaluated on **test-split programs only**, disjoint from the CFT pools by
`program_id`; `assert_eval_disjoint_from_training` enforces it rather than trusting it.
H1 does not appear: it is quarantined (CLAUDE.md §3.2) and the paper's string-encryption
arm is therefore out of scope for this replication, as recorded in `cft/__init__.py`.

Metric provenance is deliberately layered — see `metrics.py`. The paper's criteria are
reported as `reverse_success_paper` / CodeBLEU; obtune's executable criteria are reported
alongside as `reverse_success_exec` / `exec_status`, and where the two disagree the
report says so instead of picking one.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from obtune import paths
from obtune.cft import dataset as cft_data
from obtune.cft import metrics
from obtune.cft import prompts as cft_prompts
from obtune.config import GLOBAL_SEED, RESULTS_DIR, load_config

SCRIPTS_FOR_PROVENANCE = [
    "src/obtune/cft/evaluate.py",
    "src/obtune/cft/metrics.py",
    "src/obtune/cft/prompts.py",
]

DIRECTIONS = ("forward", "reverse")


# --------------------------------------------------------------------------- #
# Eval set

@dataclass
class EvalProgram:
    program_id: str
    language: str
    original_code: str
    entry_point: str
    cases: list[dict[str, str]] = field(default_factory=list)
    #: condition -> {"code", "entry_point"}
    variants: dict[str, dict[str, str]] = field(default_factory=dict)


def load_eval_programs(
    language: str,
    conditions: Sequence[str],
    source: str = "heldout",
    limit: Optional[int] = None,
    seed: int = GLOBAL_SEED,
) -> list[EvalProgram]:
    """Assemble program-level eval rows from the per-case eval item files.

    The eval tree stores one row per (program, condition, input case); the bidirectional
    tasks are per *program*, so rows are folded back up by `program_id`, with the case
    list retained because `metrics.exec_equivalence` needs gold outputs to check
    generated code against.

    `conditions` must exclude H1 — `paths.TRAINABLE_CONDITIONS` is the allowed set, and
    L0 is required because it carries the original source every metric compares to.
    """
    bad = [c for c in conditions if c not in paths.TRAINABLE_CONDITIONS]
    if bad:
        raise paths.QuarantineViolation(
            f"conditions {bad} may not be evaluated here; the held-out obfuscator is read "
            "only through data.load_h1_items under a sanctioned purpose (CLAUDE.md §3.2)"
        )
    want = ["L0"] + [c for c in conditions if c != "L0"]

    by_program: dict[str, EvalProgram] = {}
    for cond in want:
        p = paths.EVAL_ROOT / source / "items" / cond / f"{language}.jsonl"
        if not p.exists():
            raise FileNotFoundError(f"missing eval items for {cond}/{language}: {p}")
        for row in paths.iter_jsonl(p):
            pid = row["program_id"]
            if cond == "L0":
                prog = by_program.setdefault(
                    pid,
                    EvalProgram(
                        program_id=pid,
                        language=language,
                        original_code=row["code"],
                        entry_point=row["entry_point"],
                    ),
                )
                # One row per input case; `output_repr` is canon output (data.py's
                # round-trip check guarantees it), so it is the gold for execution.
                prog.cases.append(
                    {"args_repr": row["args_repr"], "output_canon": row["output_repr"]}
                )
            else:
                prog = by_program.get(pid)
                if prog is None:
                    continue  # no L0 parent loaded => nothing to compare against
                prog.variants.setdefault(
                    cond, {"code": row["code"], "entry_point": row["entry_point"]}
                )

    progs = [p for p in by_program.values() if p.cases]
    progs.sort(key=lambda p: p.program_id)
    cft_prompts.assert_demo_disjoint([p.program_id for p in progs])
    if limit:
        import random

        rng = random.Random(seed)
        rng.shuffle(progs)
        progs = sorted(progs[:limit], key=lambda p: p.program_id)
    return progs


def assert_eval_disjoint_from_training(
    programs: Sequence[EvalProgram], language: str, tasks: Sequence[str] = cft_prompts.TASKS
) -> None:
    """No evaluated program may appear in any CFT training pool (contamination check).

    Cheap relative to a GPU eval, and the failure it catches — an obfuscated variant of
    a training program scored as held-out — would inflate every forward number and would
    be invisible downstream.
    """
    eval_ids = {p.program_id for p in programs}
    train_ids: set[str] = set()
    for task in tasks:
        try:
            train_ids |= {r.program_id for r in cft_data.load_pool(language, task)}
        except FileNotFoundError:
            continue
    overlap = sorted(eval_ids & train_ids)
    if overlap:
        raise cft_data.CFTDataError(
            f"{len(overlap)} program_id(s) in BOTH the CFT training pools and the "
            f"bidirectional eval set (e.g. {overlap[:5]})"
        )


# --------------------------------------------------------------------------- #
# Request construction

@dataclass
class Request:
    trial_id: str
    system: str
    direction: str
    strategy: str
    program_id: str
    condition: str
    language: str
    messages: list[dict[str, str]]
    adapter: Optional[str]


def build_requests(
    programs: Sequence[EvalProgram],
    systems: Mapping[str, Optional[str]],
    conditions: Sequence[str],
    directions: Sequence[str],
    strategies: Sequence[str],
) -> list[Request]:
    reqs: list[Request] = []
    for sys_name, adapter in systems.items():
        for prog in programs:
            for cond in conditions:
                if cond == "L0" or cond not in prog.variants:
                    continue
                if "forward" in directions:
                    reqs.append(
                        Request(
                            trial_id=f"{sys_name}::forward::simple::{prog.program_id}::{cond}",
                            system=sys_name,
                            direction="forward",
                            strategy="simple",
                            program_id=prog.program_id,
                            condition=cond,
                            language=prog.language,
                            messages=cft_prompts.build_gen_messages(
                                prog.original_code, prog.language, cond
                            ),
                            adapter=adapter,
                        )
                    )
                if "reverse" in directions:
                    for strat in strategies:
                        reqs.append(
                            Request(
                                trial_id=f"{sys_name}::reverse::{strat}::{prog.program_id}::{cond}",
                                system=sys_name,
                                direction="reverse",
                                strategy=strat,
                                program_id=prog.program_id,
                                condition=cond,
                                language=prog.language,
                                messages=cft_prompts.build_deobf_messages(
                                    prog.variants[cond]["code"], prog.language, strat
                                ),
                                adapter=adapter,
                            )
                        )
    return reqs


# --------------------------------------------------------------------------- #
# Scoring

def score_trials(
    reqs: Sequence[Request],
    raw_outputs: Sequence[str],
    n_tokens: Sequence[int],
    programs: Mapping[str, EvalProgram],
    criteria: Mapping[str, Any],
    exec_timeout_s: float = 2.0,
    exec_workers: int = 32,
) -> list[dict[str, Any]]:
    """Turn raw generations into scored trial rows.

    Execution runs as ONE batch over every trial, because the executor's cost is
    dominated by interpreter startup and per-trial batching would multiply it by the
    number of trials.
    """
    rows: list[dict[str, Any]] = []
    exec_candidates: list[dict[str, Any]] = []

    for req, raw, ntok in zip(reqs, raw_outputs, n_tokens):
        prog = programs[req.program_id]
        pred, was_fenced = cft_prompts.extract_code(raw)
        obf_code = prog.variants[req.condition]["code"]
        # Reference for the syntactic score depends on direction: forward is judged
        # against the tool's obfuscation (paper eq. 4, S4), reverse against the original.
        if req.direction == "forward":
            target, other = obf_code, prog.original_code
        else:
            target, other = prog.original_code, obf_code

        cb_target = metrics.codebleu_score(pred, target, req.language)
        cb_other = metrics.codebleu_score(pred, other, req.language)
        read_pred = metrics.readability_proxy(pred, req.language)

        # The input the model was shown; `identity` = it echoed its input back, the
        # failure mode the paper reports for StarCoder (§4.1.3) and for every SFT model
        # in reverse (§4.3.3: "outputs nearly identical to the obfuscated input").
        shown = prog.original_code if req.direction == "forward" else obf_code
        rows.append(
            {
                "trial_id": req.trial_id,
                "system": req.system,
                "direction": req.direction,
                "strategy": req.strategy,
                "program_id": req.program_id,
                "condition": req.condition,
                "language": req.language,
                "adapter": req.adapter,
                "output_raw": raw,
                "output_code": pred,
                "n_gen_tokens": int(ntok),
                "was_fenced": int(was_fenced),
                "empty_output": int(not pred.strip()),
                "identity_output": int(pred.strip() == shown.strip()),
                "parse_ok": int(bool(pred.strip()) and metrics.tree_ok(req.language, pred)),
                "codebleu_target": cb_target["codebleu"],
                "codebleu_other": cb_other["codebleu"],
                **{f"cb_target_{k}": v for k, v in cb_target.items() if k != "codebleu"},
                "readability_pred": read_pred.score,
                "readability_original": metrics.readability_proxy(
                    prog.original_code, req.language
                ).score,
                "readability_obfuscated": metrics.readability_proxy(obf_code, req.language).score,
                "identifier_recall_original": metrics.identifier_recall(
                    pred, prog.original_code, req.language
                ),
            }
        )
        exec_candidates.append(
            {
                "code": pred,
                "language": req.language,
                "entry_point": prog.entry_point
                if req.direction == "reverse"
                else prog.variants[req.condition]["entry_point"],
                "cases": prog.cases,
            }
        )

    verdicts = metrics.exec_equivalence(
        exec_candidates, timeout_s=exec_timeout_s, workers=exec_workers
    )

    sim_threshold = float(criteria.get("reverse_sim_threshold", 0.4))
    read_tol = float(criteria.get("reverse_readability_tolerance", 0.1))
    for row, verdict in zip(rows, verdicts):
        row.update(verdict.as_dict())
        if row["direction"] == "reverse":
            # `codebleu_target` is similarity to the ORIGINAL in reverse, and the
            # paper's criterion is about similarity to the OBFUSCATED input, which is
            # `codebleu_other` here.
            row["reverse_success_paper"] = int(
                metrics.reverse_success_paper(
                    sim_to_obfuscated=row["codebleu_other"],
                    readability_deobf=row["readability_pred"],
                    readability_original=row["readability_original"],
                    parses=bool(row["parse_ok"]),
                    sim_threshold=sim_threshold,
                    readability_tolerance=read_tol,
                )
            )
            row["reverse_success_exec"] = int(verdict.all_match)
            # Both criteria at once: semantics preserved AND the obfuscation actually
            # undone. This is the number we would defend.
            row["reverse_success_strict"] = int(
                verdict.all_match and row["reverse_success_paper"] == 1
            )
        else:
            row["forward_success_exec"] = int(metrics.forward_success_exec(verdict))
    return rows


# --------------------------------------------------------------------------- #
# Aggregation

def _mean(values: Iterable[float]) -> float:
    vals = [v for v in values if v == v]  # drop NaN (identifier_recall on nameless refs)
    return sum(vals) / len(vals) if vals else float("nan")


AGG_FIELDS = (
    "codebleu_target",
    "codebleu_other",
    "readability_pred",
    "readability_original",
    "readability_obfuscated",
    "identifier_recall_original",
    "exec_pass_rate",
    "parse_ok",
    "identity_output",
    "empty_output",
    "was_fenced",
    "n_gen_tokens",
    "reverse_success_paper",
    "reverse_success_exec",
    "reverse_success_strict",
    "forward_success_exec",
)


def summarize(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Cell means keyed by (system, direction, strategy, condition), plus margins."""
    cells: dict[tuple, list[Mapping[str, Any]]] = defaultdict(list)
    for r in rows:
        cells[(r["system"], r["direction"], r["strategy"], r["condition"])].append(r)
        cells[(r["system"], r["direction"], r["strategy"], "ALL")].append(r)

    out: list[dict[str, Any]] = []
    for (system, direction, strategy, condition), group in sorted(
        cells.items(), key=lambda kv: tuple(map(str, kv[0]))
    ):
        cell = {
            "system": system,
            "direction": direction,
            "strategy": strategy,
            "condition": condition,
            "n": len(group),
            "n_programs": len({r["program_id"] for r in group}),
            "exec_status": dict(sorted(Counter(r["exec_status"] for r in group).items())),
        }
        for f in AGG_FIELDS:
            present = [r[f] for r in group if f in r]
            if present:
                cell[f] = _mean(present)
        out.append(cell)
    return {"cells": out}


def assert_adapters_effective(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """CLAUDE.md §4.2 — prove a tuned system's outputs differ from the base's.

    An adapter that silently failed to load produces a full result table that is a
    perfect copy of the base row-for-row, and nothing downstream would notice.
    """
    by_key: dict[tuple, dict[str, str]] = defaultdict(dict)
    for r in rows:
        key = (r["direction"], r["strategy"], r["program_id"], r["condition"])
        by_key[key][r["system"]] = r["output_raw"]
    report: dict[str, Any] = {}
    systems = sorted({r["system"] for r in rows} - {"base"})
    for sysname in systems:
        pairs = [(v["base"], v[sysname]) for v in by_key.values() if "base" in v and sysname in v]
        if not pairs:
            continue
        identical = sum(1 for a, b in pairs if a == b)
        report[sysname] = {"n_compared": len(pairs), "identical_to_base": identical,
                           "identical_rate": identical / len(pairs)}
        if identical == len(pairs):
            raise RuntimeError(
                f"system {sysname!r} produced output identical to the base model on all "
                f"{len(pairs)} trials — the adapter did not take effect (CLAUDE.md §4.2)"
            )
    return report


# --------------------------------------------------------------------------- #
# Entry point

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Bidirectional CFT evaluation")
    ap.add_argument("--config", required=True)
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--out", default=None, help="override the results directory")
    ap.add_argument("--limit", type=int, default=None, help="cap the number of eval programs")
    ap.add_argument("--systems", default=None, help="comma-separated subset of the configured systems")
    ap.add_argument("--stub", action="store_true",
                    help="no model: deterministic placeholder generations, for plumbing tests")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config)

    language = cfg["language"]
    conditions = list(cfg["conditions"])
    directions = list(cfg.get("directions", DIRECTIONS))
    strategies = list(cfg.get("reverse_strategies", ["simple"]))
    criteria = dict(cfg.get("criteria", {}) or {})
    seed = int(cfg.get("seed", GLOBAL_SEED))

    systems: dict[str, Optional[str]] = {}
    for name, spec in (cfg.get("systems") or {}).items():
        systems[name] = None if spec in (None, "none", "base") else str(spec)
    if args.systems:
        want = set(args.systems.split(","))
        systems = {k: v for k, v in systems.items() if k in want}
    if not systems:
        raise SystemExit("no systems selected")

    if args.gpu is not None and not args.stub:
        from obtune import gpu

        gpu.pin([args.gpu])
    gpu_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")

    programs = load_eval_programs(
        language, conditions, source=cfg.get("eval_source", "heldout"),
        limit=args.limit or cfg.get("limit"), seed=seed,
    )
    assert_eval_disjoint_from_training(programs, language)
    prog_index = {p.program_id: p for p in programs}

    reqs = build_requests(programs, systems, conditions, directions, strategies)
    print(
        f"[cft.eval] {len(programs)} programs x {len(systems)} systems "
        f"-> {len(reqs)} generations",
        flush=True,
    )

    from obtune.eval_vllm import Engine

    mcfg = load_config("models.yaml")["models"][cfg["model"]]
    engine = Engine(mcfg["hf_id"], cfg.get("engine", {}), stub=args.stub)
    texts = [
        engine.tokenizer.apply_chat_template(r.messages, tokenize=False, add_generation_prompt=True)
        if not args.stub
        else json.dumps(r.messages)
        for r in reqs
    ]
    raw, ntok = engine.generate(texts, cfg.get("sampling", {}), [r.adapter for r in reqs])

    rows = score_trials(
        reqs, raw, ntok, prog_index, criteria,
        exec_timeout_s=float(cfg.get("exec", {}).get("timeout_s", 2.0)),
        exec_workers=int(cfg.get("exec", {}).get("workers", 32)),
    )
    effective = assert_adapters_effective(rows) if not args.stub else {}
    summary = summarize(rows)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = Path(args.out) if args.out else RESULTS_DIR / f"{stamp}_cft-bidirectional" / language
    out_dir.mkdir(parents=True, exist_ok=True)
    paths.write_jsonl(out_dir / "trials.jsonl", rows)

    from obtune.provenance import RunManifest

    meta = {
        "language": language,
        "conditions": conditions,
        "directions": directions,
        "reverse_strategies": strategies,
        "systems": systems,
        "criteria": criteria,
        "n_programs": len(programs),
        "n_trials": len(rows),
        "adapter_effectiveness": effective,
        "codebleu_impl": metrics.CODEBLEU_VERSION,
        "readability_note": (
            "readability_* is metrics.readability_proxy, NOT Scalabrino et al.'s model "
            "used by the paper; only within-run contrasts are interpretable"
        ),
        "readability_weights": metrics.READABILITY_WEIGHTS,
        **cft_prompts.provenance_block(),
    }
    (out_dir / "summary.json").write_text(
        json.dumps({"meta": meta, **summary}, indent=2, sort_keys=True) + "\n"
    )
    manifest = (
        RunManifest(
            experiment="cft/bidirectional_eval",
            run_id=f"cft_bidir__{cfg['model']}__{language}",
            seed=seed,
            config_path=str(cfg.get("_config_path", args.config)),
            config_resolved=cfg,
            model_hf_id=mcfg["hf_id"],
            gpu_visible=gpu_visible,
            extra=meta,
        )
        .capture_git()
        .hash_scripts(SCRIPTS_FOR_PROVENANCE)
        .finalize()
    )
    manifest.write(out_dir)
    print(f"[cft.eval] wrote {out_dir}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
