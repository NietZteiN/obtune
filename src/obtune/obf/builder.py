"""Corpus builder: (program × condition) -> gated Variant rows, rejects, coverage.

For every pair it runs up to `max_attempts` attempts with seed `seed + i*seed_stride`
(a prime stride, ported from ../allocation_replication, so attempt seeds never collide
across nearby base seeds), gates each attempt, and keeps the first that passes.

Three outcomes, and keeping them apart is the point (CLAUDE.md §4 "coverage honesty"):

  ok                     the variant passed the gate
  technique_unavailable  the transform *declined* — S1 bailing on a `try`, a program
                         with nothing to rename. Expected coverage loss, not a defect.
  failed                 the transform produced output that the gate rejected, or it
                         raised. This is the number that must stay near zero.

Transform modules are imported lazily and per condition, so a JavaScript module that
does not exist yet degrades that one cell to `technique_unavailable` instead of taking
the whole build down. L0 needs no module: the base program *is* L0, so the builder
emits it directly and lets the gate confirm the identity.

Outputs
  data/rejects/<lang>/<cond>.jsonl     every rejected attempt with its verdict
  data/manifests/coverage_matrix.json  per-language status matrix + common subset
"""
from __future__ import annotations

import importlib
import json
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from obtune.config import GLOBAL_SEED, conditions as load_conditions
from obtune.obf.base import Bail, TransformResult, make_ctx
from obtune.obf.validate import Verdict, gate
from obtune.paths import MANIFESTS_ROOT, REJECTS_ROOT, write_jsonl
from obtune.schema import BaseProgram, Variant

#: condition -> (module, attribute) per language. Resolved lazily; a missing module is
#: reported as technique_unavailable rather than raising.
TRANSFORM_REGISTRY: dict[str, dict[str, tuple[str, str]]] = {
    "python": {
        "L1b": ("obtune.obf.py.adversarial", "transform"),
        "L1r": ("obtune.obf.py.rename", "transform_hex"),
        "L2": ("obtune.obf.py.rename", "transform_seq"),
        "S1": ("obtune.obf.py.flatten", "transform"),
        "S2": ("obtune.obf.py.deadcode", "transform"),
    },
    # The JS transforms are implemented in Babel (obf/js/transforms.mjs) and reached
    # through a Node subprocess; obf/js/adapters.py presents them as fn(ctx) callables.
    "javascript": {
        "L1b": ("obtune.obf.js.adapters", "transform_adversarial"),
        "L1r": ("obtune.obf.js.adapters", "transform_hex"),
        "L2": ("obtune.obf.js.adapters", "transform_seq"),
        "S1": ("obtune.obf.js.adapters", "transform_flatten"),
        "S2": ("obtune.obf.js.adapters", "transform_deadcode"),
    },
}

STATUS_OK = "ok"
STATUS_UNAVAILABLE = "technique_unavailable"
STATUS_FAILED = "failed"


@dataclass
class BuildReport:
    language: str
    seed: int
    conditions: list[str]
    variants: list[Variant] = field(default_factory=list)
    rejects: list[dict[str, Any]] = field(default_factory=list)
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)
    manifest: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {
            c: {STATUS_OK: 0, STATUS_UNAVAILABLE: 0, STATUS_FAILED: 0} for c in self.conditions
        }
        for key, rec in self.entries.items():
            cond = key.rsplit("::", 1)[1]
            bucket = out.setdefault(cond, {STATUS_OK: 0, STATUS_UNAVAILABLE: 0, STATUS_FAILED: 0})
            bucket[rec["status"]] = bucket.get(rec["status"], 0) + 1
        return out

    def common_subset(self) -> list[str]:
        """program_ids for which EVERY requested condition succeeded.

        Headline transfer numbers are computed on this subset so that cells are not
        confounded by S1/S2 declining on different programs.
        """
        per_program: dict[str, set[str]] = {}
        for key, rec in self.entries.items():
            pid, cond = key.rsplit("::", 1)
            if rec["status"] == STATUS_OK:
                per_program.setdefault(pid, set()).add(cond)
        want = set(self.conditions)
        return sorted(pid for pid, got in per_program.items() if want <= got)


def load_transform(language: str, condition: str):
    """Resolve a (language, condition) transform callable, or None if unavailable."""
    spec = TRANSFORM_REGISTRY.get(language, {}).get(condition)
    if spec is None:
        return None
    module_name, attr = spec
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    fn = getattr(module, attr, None)
    return fn if callable(fn) else None


def _params_for(spec: dict[str, Any]) -> dict[str, Any]:
    """conditions.yaml `params` plus the condition's `size_cap`.

    S2 (and any future size-inflating transform) has to know the cap it will be judged
    against: a 9-line program blows through S2's 4x cap on three junk blocks alone, and
    generating blind then losing five gated attempts is both slow and dishonest about
    the failure. The cap lives one level above `params` in the frozen config, so it is
    merged in here rather than duplicated there.
    """
    params = dict(spec.get("params") or {})
    params.setdefault("size_cap", spec.get("size_cap"))
    # The floor travels with the cap: a transform that self-budgets from the ratio
    # alone would starve short programs even though the gate would have accepted them.
    params.setdefault("size_cap_floor_chars", spec.get("size_cap_floor_chars", 0))
    return params


def _identity_transform(ctx) -> TransformResult:
    """L0 — the base program *is* the L0 stimulus; the gate confirms the identity."""
    return TransformResult(ctx.src, True, notes=["L0 is the base program verbatim"])


def _variant_from(
    program: BaseProgram, condition: str, result: TransformResult, seed_used: int, attempt: int
) -> Variant:
    entry_new = result.entry_point_out or program.entry_point
    meta = {
        "seed": seed_used,
        "attempt": attempt,
        "notes": list(result.notes),
        "skipped_constructs": list(result.skipped_constructs),
        **{k: v for k, v in result.extra.items() if k != "entry_point_new"},
    }
    return Variant(
        program_id=program.program_id,
        condition=condition,
        language=program.language,
        code=result.src_out,
        entry_point=entry_new,
        entry_point_parent=program.entry_point,
        rename_map=dict(result.rename_map),
        transform_meta=meta,
    )


def _build_one(
    program_dict: dict[str, Any], condition: str, seed: int, cfg: dict[str, Any]
) -> tuple[str, str, dict[str, Any], dict[str, Any] | None, list[dict[str, Any]]]:
    """Worker body. Returns (program_id, condition, record, variant_dict|None, rejects)."""
    program = BaseProgram.model_validate(program_dict)
    language = program.language
    spec = (cfg.get("conditions") or {}).get(condition, {})
    params = _params_for(spec)
    max_attempts = int(cfg.get("max_attempts", 5))
    stride = int(cfg.get("seed_stride", 7919))

    record: dict[str, Any] = {
        "status": STATUS_FAILED,
        "attempts": 0,
        "seed_used": None,
        "notes": [],
        "skipped_constructs": [],
        "gate": None,
    }
    rejects: list[dict[str, Any]] = []

    fn = _identity_transform if condition == "L0" else load_transform(language, condition)
    if fn is None:
        record["status"] = STATUS_UNAVAILABLE
        record["notes"].append(f"no importable transform for {language}/{condition}")
        return program.program_id, condition, record, None, rejects

    declined_only = True
    for attempt in range(max_attempts):
        attempt_seed = seed + attempt * stride
        record["attempts"] = attempt + 1
        record["seed_used"] = attempt_seed
        ctx = make_ctx(
            language, program.program_id, condition, program.code, program.entry_point,
            attempt=attempt, seed=attempt_seed, params=params,
        )
        try:
            result = fn(ctx)
        except Bail as exc:
            record["notes"].append(f"attempt {attempt}: declined: {exc}")
            record["skipped_constructs"].append(str(exc))
            continue
        except Exception:
            declined_only = False
            record["notes"].append(f"attempt {attempt}: raised: {traceback.format_exc(limit=3)}")
            continue

        record["skipped_constructs"] = list(result.skipped_constructs)
        record["notes"].extend(f"attempt {attempt}: {n}" for n in result.notes)
        if not result.applied:
            record["notes"].append(f"attempt {attempt}: transform declined")
            continue

        variant = _variant_from(program, condition, result, attempt_seed, attempt)
        try:
            verdict: Verdict = gate(program, variant, cfg)
        except Exception:
            declined_only = False
            record["notes"].append(f"attempt {attempt}: gate raised: {traceback.format_exc(limit=3)}")
            continue

        record["gate"] = verdict.as_dict()
        if verdict.ok:
            variant.gate = {"checks": verdict.checks, "metrics": verdict.metrics}
            record["status"] = STATUS_OK
            return program.program_id, condition, record, variant.model_dump(), rejects

        declined_only = False
        rejects.append(
            {
                "program_id": program.program_id,
                "condition": condition,
                "language": language,
                "attempt": attempt,
                "seed": attempt_seed,
                "entry_point": variant.entry_point,
                "failed_checks": [k for k, v in verdict.checks.items() if not v],
                "mismatch_details": verdict.mismatch_details,
                "metrics": verdict.metrics,
                "code": variant.code,
            }
        )
        record["notes"].append(
            f"attempt {attempt}: gate rejected "
            f"{[k for k, v in verdict.checks.items() if not v]}"
        )

    record["notes"].append(f"exhausted {max_attempts} attempts")
    # "Never produced a candidate at all" is coverage loss by design; "produced one the
    # gate rejected" is a defect. Only the second may inflate the failure count.
    if declined_only:
        record["status"] = STATUS_UNAVAILABLE
    return program.program_id, condition, record, None, rejects


def build_variants(
    base_programs: Iterable[BaseProgram],
    conditions: Sequence[str],
    language: str,
    workers: int = 8,
    *,
    seed: int | None = None,
    cfg: dict[str, Any] | None = None,
    write: bool = True,
    rejects_root: Path | None = None,
    manifests_root: Path | None = None,
) -> BuildReport:
    """Build and gate every (program, condition) variant for one language."""
    cfg = cfg or load_conditions()
    seed = int(cfg.get("global_seed", GLOBAL_SEED)) if seed is None else int(seed)
    programs = [p for p in base_programs if p.language == language]
    conditions = list(conditions)

    report = BuildReport(language=language, seed=seed, conditions=conditions)
    tasks = [(p.model_dump(), c) for p in programs for c in conditions]
    if not tasks:
        report.manifest = _write_manifest(report, manifests_root, write)
        return report

    if workers <= 1:
        results = [_build_one(pd, c, seed, cfg) for pd, c in tasks]
    else:
        results = []
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_build_one, pd, c, seed, cfg): (pd["program_id"], c) for pd, c in tasks}
            for fut in as_completed(futures):
                pid, cond = futures[fut]
                try:
                    results.append(fut.result())
                except Exception:
                    # A worker crash costs one cell, never the whole build.
                    results.append(
                        (
                            pid, cond,
                            {
                                "status": STATUS_FAILED, "attempts": 0, "seed_used": None,
                                "notes": [f"worker crashed: {traceback.format_exc(limit=3)}"],
                                "skipped_constructs": [], "gate": None,
                            },
                            None, [],
                        )
                    )

    for pid, cond, record, variant_dict, rejects in results:
        report.entries[f"{pid}::{cond}"] = record
        report.rejects.extend(rejects)
        if variant_dict is not None:
            report.variants.append(Variant.model_validate(variant_dict))

    report.variants.sort(key=lambda v: (v.condition, v.program_id))
    report.entries = dict(sorted(report.entries.items()))

    if write:
        _write_rejects(report, rejects_root)
    report.manifest = _write_manifest(report, manifests_root, write)
    return report


def _write_rejects(report: BuildReport, rejects_root: Path | None) -> None:
    root = Path(rejects_root or REJECTS_ROOT) / report.language
    by_cond: dict[str, list[dict[str, Any]]] = {c: [] for c in report.conditions}
    for row in report.rejects:
        by_cond.setdefault(row["condition"], []).append(row)
    for cond, rows in by_cond.items():
        write_jsonl(root / f"{cond}.jsonl", rows)


def _write_manifest(report: BuildReport, manifests_root: Path | None, write: bool) -> dict[str, Any]:
    """Merge this language's block into data/manifests/coverage_matrix.json."""
    block = {
        "language": report.language,
        "seed": report.seed,
        "conditions": report.conditions,
        "n_programs": len({k.rsplit("::", 1)[0] for k in report.entries}),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "summary": report.summary(),
        "common_subset": report.common_subset(),
        "entries": report.entries,
    }
    if not write:
        return block
    path = Path(manifests_root or MANIFESTS_ROOT) / "coverage_matrix.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    doc: dict[str, Any] = {"languages": {}}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
            if isinstance(existing.get("languages"), dict):
                doc = existing
        except (json.JSONDecodeError, OSError):
            pass  # a corrupt manifest is regenerated, never silently merged into
    doc["languages"][report.language] = block
    doc["updated_at"] = block["generated_at"]
    path.write_text(json.dumps(doc, indent=2, sort_keys=False))
    return block


__all__ = ["BuildReport", "build_variants", "load_transform", "TRANSFORM_REGISTRY"]
