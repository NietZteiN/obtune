"""Adapters presenting the Babel JS transforms in the shape obf/builder.py expects.

The Python transforms are in-process callables `fn(ctx) -> TransformResult`, and
builder.py's registry resolves every (language, condition) pair that way. The JS
transforms live behind a Node subprocess (obf/js_driver.py), so this module is the
thin bridge: one `SnippetCtx` in, one `TransformResult` out.

Cost note (measured 2026-08-04): a driver invocation costs ~272 ms of fixed Node +
Babel startup and ~2.2 ms marginal per program, so batching is worth ~120x on
throughput. We deliberately do NOT batch here, because builder.py parallelizes with
a ProcessPoolExecutor and retries with per-attempt seeds — a parent-side batch cache
would not reach the workers, and threading a prefetch through the pickled task
payload would mean shipping the whole corpus to every worker. At 32 workers a full
JS corpus build (~12k programs x 5 conditions) costs roughly 8 minutes of startup
overhead, which is not worth that complexity. If JS corpus builds later become a
bottleneck, the fix is a persistent Node worker per process, not a cache here.
"""
from __future__ import annotations

from obtune.obf.base import Bail, TransformResult
from obtune.obf.js_driver import JsTransformJob, transform_js


def _run(ctx, condition: str) -> TransformResult:
    job = JsTransformJob(
        program_id=ctx.program_id,
        condition=condition,
        code=ctx.src,
        entry_point=ctx.entry_point,
        # driver.mjs seeds mulberry32 from a uint32; ctx.seed already varies per
        # attempt (seed + attempt * stride), so retries genuinely resample.
        seed=int(ctx.seed) & 0xFFFFFFFF,
    )
    rec = transform_js([job])[0]

    if not rec.get("ok"):
        error = rec.get("error") or "transform declined"
        skipped = rec.get("skipped_constructs") or []
        # A construct-level decline is a Bail (expected coverage loss, retried with a
        # new seed then recorded as technique_unavailable); anything else is a real
        # failure and must not be silently downgraded to "declined".
        if skipped:
            raise Bail(f"{condition}: {'; '.join(skipped)}")
        raise RuntimeError(f"js {condition} transform failed: {error}")

    extra: dict = {}
    entry_new = rec.get("entry_point")
    if entry_new and entry_new != ctx.entry_point:
        extra["entry_point_new"] = entry_new
    for key in ("misdirection_strength", "n_states", "n_predicate_blocks", "n_dead_helpers"):
        if key in rec:
            extra[key] = rec[key]

    return TransformResult(
        src_out=rec["code"],
        applied=True,
        notes=list(rec.get("notes") or []),
        skipped_constructs=list(rec.get("skipped_constructs") or []),
        rename_map=dict(rec.get("rename_map") or {}),
        extra=extra,
    )


def transform_hex(ctx) -> TransformResult:
    """L1r — random hex renaming of every binding, entry function included."""
    return _run(ctx, "L1r")


def transform_seq(ctx) -> TransformResult:
    """L2 — sequential minification (a, b, c, ...) + annotation stripping."""
    return _run(ctx, "L2")


def transform_adversarial(ctx) -> TransformResult:
    """L1b — adversarial/misleading renaming, strongest misdirection on the entry fn."""
    return _run(ctx, "L1b")


def transform_flatten(ctx) -> TransformResult:
    """S1 — control-flow flattening into a switch dispatch loop."""
    return _run(ctx, "S1")


def transform_deadcode(ctx) -> TransformResult:
    """S2 — opaque predicates + never-called dead helpers."""
    return _run(ctx, "S2")


def transform_deadhelpers(ctx) -> TransformResult:
    """S3 — never-called program-scope helpers only (the S2 half that must be IGNORED)."""
    return _run(ctx, "S3")


def transform_opaque(ctx) -> TransformResult:
    """S4 — opaque predicates only (the S2 half that must be REASONED ABOUT)."""
    return _run(ctx, "S4")
