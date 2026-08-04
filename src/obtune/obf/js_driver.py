"""Python front-end for the Babel JavaScript transforms.

WHY a subprocess bridge: the trainable JS conditions (L0/L1r/L2/L1b/S1/S2) are
implemented in Babel (obf/js/transforms.mjs) because only Babel gives us the
authoritative binding graph needed for safe renames and flattening. This module
shells out to obf/js/driver.mjs once per BATCH — never once per program — so the
~89 ms Node startup is amortized, matching the batching discipline in exec/pool.py.

`transform_js` returns TransformResult-shaped dicts (the shape obf/builder.py maps
onto schema.Variant): program_id, condition, language, ok, code, entry_point,
entry_point_parent, rename_map, skipped_constructs, seed, error. `entry_point`
is the POST-transform name (L1b/L1r/L2 rename the entry function); `entry_point_parent`
is the L0 name the caller passed in.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

_HERE = Path(__file__).resolve().parent
DRIVER_MJS = _HERE / "js" / "driver.mjs"

# Resolve node against the caller's PATH once (the child env below carries only a
# minimal PATH, exactly as exec/pool.py does — conda's node is not on /usr/bin).
NODE_BIN = os.environ.get("OBTUNE_NODE") or shutil.which("node") or "node"

# JS conditions this driver can produce. H1 is deliberately absent — it is
# generated only by scripts/gen_h1_quarantined.py via obf/h1/js_h1.mjs.
JS_TRAINABLE_CONDITIONS = ("L0", "L1b", "L1r", "L2", "S1", "S2")


@dataclass
class JsTransformJob:
    program_id: str
    condition: str
    code: str
    entry_point: str
    seed: int


def _child_env() -> dict[str, str]:
    # Minimal, deterministic env. Babel is resolved by driver.mjs from the js/
    # workspace via import.meta.url (a filesystem lookup, independent of PATH);
    # OBTUNE_JS_DIR is forwarded only if the caller set an override.
    env = {
        "PATH": "/usr/bin:/bin",
        "NODE_OPTIONS": "",
        "LANG": "C.UTF-8",
        "HOME": "/nonexistent",
    }
    if os.environ.get("OBTUNE_JS_DIR"):
        env["OBTUNE_JS_DIR"] = os.environ["OBTUNE_JS_DIR"]
    return env


def _run_batch_once(jobs: Sequence[JsTransformJob], timeout_s: float) -> list[dict[str, Any]]:
    payload = {
        "jobs": [
            {
                "program_id": j.program_id,
                "condition": j.condition,
                "code": j.code,
                "entry_point": j.entry_point,
                "seed": int(j.seed) & 0xFFFFFFFF,
            }
            for j in jobs
        ]
    }
    proc = subprocess.run(
        [NODE_BIN, "--no-warnings", str(DRIVER_MJS)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=_child_env(),
        timeout=timeout_s,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"driver.mjs exited {proc.returncode}: {proc.stderr[-2000:]}"
        )

    by_id: dict[tuple[str, str], dict[str, Any]] = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        by_id[(rec.get("program_id"), rec.get("condition"))] = rec

    results: list[dict[str, Any]] = []
    for j in jobs:
        rec = by_id.get((j.program_id, j.condition))
        if rec is None:
            # The child dropped a job (e.g. crashed mid-batch). Surface it as a
            # failed row rather than silently shifting the alignment.
            results.append(_result_dict(j, ok=False, code=j.code, entry_point=j.entry_point,
                                        rename_map={}, skipped=[], error="no result emitted by driver.mjs"))
            continue
        results.append(
            _result_dict(
                j,
                ok=bool(rec.get("ok")),
                code=rec.get("code", j.code),
                entry_point=rec.get("entry_point", j.entry_point),
                rename_map=rec.get("rename_map") or {},
                skipped=rec.get("skipped_constructs") or [],
                error=rec.get("error"),
            )
        )
    return results


def _result_dict(job: JsTransformJob, *, ok: bool, code: str, entry_point: str,
                 rename_map: dict[str, str], skipped: list[str], error: str | None) -> dict[str, Any]:
    return {
        "program_id": job.program_id,
        "condition": job.condition,
        "language": "javascript",
        "ok": ok,
        "code": code,
        "entry_point": entry_point,
        "entry_point_parent": job.entry_point,
        "rename_map": rename_map,
        "skipped_constructs": list(skipped),
        "seed": int(job.seed) & 0xFFFFFFFF,
        "error": error,
    }


def transform_js(
    jobs: Iterable[JsTransformJob | dict[str, Any]],
    batch_size: int = 256,
    timeout_s: float = 120.0,
) -> list[dict[str, Any]]:
    """Transform many JS programs, one Node process per `batch_size` chunk.

    Order of results matches the input. Accepts JsTransformJob objects or plain
    dicts with the same fields.
    """
    norm: list[JsTransformJob] = []
    for j in jobs:
        if isinstance(j, JsTransformJob):
            norm.append(j)
        else:
            norm.append(
                JsTransformJob(
                    program_id=j["program_id"],
                    condition=j["condition"],
                    code=j["code"],
                    entry_point=j["entry_point"],
                    seed=int(j.get("seed", 0)),
                )
            )
    out: list[dict[str, Any]] = []
    for i in range(0, len(norm), batch_size):
        out.extend(_run_batch_once(norm[i : i + batch_size], timeout_s))
    return out
