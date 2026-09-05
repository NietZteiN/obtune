"""Batch program executor — the single entry point for running corpus programs.

One child process per (program, case-list): the ~42 ms Python / ~89 ms Node startup
is amortized over all of a program's cases instead of paid per case. The parent
enforces a wall-clock timeout and kills the child's whole process group, so a
program that spins in C code or forks cannot outlive its slot.

Used by: corpus/inputs.py (determinism + non-triviality filters), obf/validate.py
(the semantic-preservation gate), testset/ingest.py (golden re-execution).
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

_HERE = Path(__file__).resolve().parent
RUNNER_PY = _HERE / "runner_py.py"
RUNNER_JS = _HERE / "runner_js.mjs"

# Resolve node against the *caller's* PATH once, at import: the child runs with a
# minimal PATH (/usr/bin:/bin) that does not include the conda-provided node.
NODE_BIN = os.environ.get("OBTUNE_NODE") or shutil.which("node") or "node"


@dataclass
class CaseResult:
    status: str  # ok | raised | unserializable | error | timeout | crash
    output: str | None = None
    exc_type: str | None = None
    elapsed_ms: float = 0.0
    trace: list[str] | None = None  # only when BatchItem.trace was set (trace-SFT arm)

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    def matches(self, other: "CaseResult") -> bool:
        """Semantic-equivalence comparison used by the gate.

        `raised` compares by exception TYPE only — obfuscation legitimately changes
        messages, line numbers and tracebacks (the lesson encoded in
        allocation_replication's validate.py `_normalize_stderr`).
        """
        if self.status != other.status:
            return False
        if self.status == "ok":
            return self.output == other.output
        if self.status == "raised":
            return self.exc_type == other.exc_type
        return True  # unserializable/error/timeout on both sides: equally unusable


@dataclass
class ProgramResult:
    program_id: str
    cases: list[CaseResult] = field(default_factory=list)
    child_status: str = "ok"  # ok | timeout | crash
    stderr: str = ""

    @property
    def all_ok(self) -> bool:
        return self.child_status == "ok" and all(c.ok for c in self.cases)

    @property
    def total_ms(self) -> float:
        return sum(c.elapsed_ms for c in self.cases)


@dataclass
class BatchItem:
    program_id: str
    language: str
    code: str
    entry_point: str
    args_reprs: Sequence[str]
    #: {"max_events": int, "max_repr": int} to ask the Python runner for an execution
    #: trace per case (see runner_py.py, trace mode). None = plain execution.
    trace: dict | None = None


def _run_one(item: BatchItem, timeout_s: float, mem_mb: int, hash_seed: int) -> ProgramResult:
    n = len(item.args_reprs)
    job = {
        "code": item.code,
        "entry_point": item.entry_point,
        "cases": [{"args_repr": a} for a in item.args_reprs],
        "mem_mb": mem_mb,
        "cpu_s": max(1, int(timeout_s * n) + 1),
        "timeout_ms": int(timeout_s * 1000),
    }
    if item.trace:
        if item.language != "python":
            raise ValueError("trace mode is implemented for python only")
        job["trace"] = dict(item.trace)
    if item.language == "python":
        cmd = [sys.executable, "-I", "-S", str(RUNNER_PY)]
    elif item.language == "javascript":
        cmd = [NODE_BIN, f"--max-old-space-size={mem_mb}", "--no-warnings", str(RUNNER_JS)]
    else:
        raise ValueError(f"unknown language: {item.language}")

    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONHASHSEED": str(hash_seed),
        "PYTHONDONTWRITEBYTECODE": "1",
        "HOME": "/nonexistent",
        "LANG": "C.UTF-8",
        "NODE_OPTIONS": "",
    }
    res = ProgramResult(program_id=item.program_id)
    proc = None
    try:
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, env=env, cwd="/tmp", start_new_session=True,
        )
        out, err = proc.communicate(json.dumps(job), timeout=timeout_s * n + 10)
        res.stderr = err[-2000:] if err else ""
    except subprocess.TimeoutExpired:
        if proc is not None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            proc.wait(timeout=5)
        res.child_status = "timeout"
        res.cases = [CaseResult(status="timeout") for _ in range(n)]
        return res
    except OSError as e:
        res.child_status = "crash"
        res.stderr = str(e)
        res.cases = [CaseResult(status="crash") for _ in range(n)]
        return res

    by_index: dict[int, CaseResult] = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Defence in depth against the program under test writing to the protocol
        # channel. `json.loads("42")` succeeds and returns an int, so a JSONDecodeError
        # guard alone is not enough — a printed number used to reach `r["i"]` and raise
        # AttributeError, killing the whole batch.
        if not isinstance(r, dict) or "i" not in r:
            continue
        by_index[r["i"]] = CaseResult(
            status=r.get("status", "error"), output=r.get("output"),
            exc_type=r.get("exc_type"), elapsed_ms=float(r.get("elapsed_ms", 0.0)),
            trace=r.get("trace"),
        )
    if len(by_index) != n:
        # Child died mid-run. A negative returncode means it was killed by a signal;
        # SIGXCPU/SIGKILL is the RLIMIT_CPU guard firing on a spinning program, which
        # is a timeout rather than a defect in our harness.
        killed_by_signal = proc.returncode is not None and proc.returncode < 0
        res.child_status = "timeout" if killed_by_signal else "crash"
    fill = CaseResult(status=res.child_status if res.child_status != "ok" else "crash")
    res.cases = [by_index.get(i, fill) for i in range(n)]
    return res


def run_batch(
    items: Iterable[BatchItem],
    timeout_s: float = 2.0,
    mem_mb: int = 512,
    workers: int = 32,
    hash_seed: int = 0,
) -> list[ProgramResult]:
    """Execute many programs concurrently. Order of results matches `items`.

    `hash_seed` pins PYTHONHASHSEED. The determinism filter deliberately varies it
    across repeats to expose hash-order-dependent programs; everything else pins 0.
    """
    items = list(items)
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda it: _run_one(it, timeout_s, mem_mb, hash_seed), items))


def run_one(item: BatchItem, **kw: Any) -> ProgramResult:
    return run_batch([item], **kw)[0]
