"""Child process for the Python batch executor. NOT imported by anything.

Protocol: reads one JSON job from stdin, writes one JSON line per case to stdout.
Job:    {"code": str, "entry_point": str, "cases": [{"args_repr": "(1, 2)"}, ...]}
Result: {"i": int, "status": "ok"|"raised"|"unserializable"|"error",
         "output": str|null, "exc_type": str|null, "elapsed_ms": float}

Isolation: rlimits (address space + CPU), own process group, empty CWD, no network
imports preloaded. The parent additionally enforces a wall-clock timeout and kills
the whole process group.
"""
from __future__ import annotations

import ast
import json
import os
import resource
import sys
import time


def _limit(mem_mb: int, cpu_s: int) -> None:
    resource.setrlimit(resource.RLIMIT_AS, (mem_mb << 20, mem_mb << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))


# Removed from the program's builtins. This is hygiene, not a security sandbox:
# corpus/filters.py is what actually keeps I/O-touching programs out of the corpus.
# The point here is that a program which slips past the static filter produces an
# exception rather than a *plausible but unreproducible* gold label — reading a file
# or stdin would make the label depend on the machine, not the program.
_BLOCKED_BUILTINS = ("open", "input", "exec", "eval", "compile", "breakpoint", "help")


def _builtins() -> dict:
    import builtins as _b

    d = {k: getattr(_b, k) for k in dir(_b) if not k.startswith("_")}
    d["__import__"] = _b.__import__  # programs legitimately `import math`, `from collections import ...`
    for name in _BLOCKED_BUILTINS:
        d.pop(name, None)
    return d


def _parse_args(args_repr: str):
    """`args_repr` is the literal argument tuple source, e.g. "(3, [1, 2])"."""
    node = ast.parse(args_repr.strip(), mode="eval")
    value = ast.literal_eval(node)
    return value if isinstance(value, tuple) else (value,)


def main() -> int:
    job = json.loads(sys.stdin.read())
    mem_mb = int(job.get("mem_mb", 512))
    cpu_s = int(job.get("cpu_s", 10))
    try:
        _limit(mem_mb, cpu_s)
    except (ValueError, OSError):
        pass  # rlimits unavailable; parent timeout still applies

    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))
    from canon import Unserializable, canon  # local import so rlimits are already set

    out = sys.stdout
    glb: dict = {"__name__": "__obtune_program__", "__builtins__": _builtins()}
    try:
        exec(compile(job["code"], "<program>", "exec"), glb)
        fn = glb[job["entry_point"]]
    except BaseException as e:  # noqa: BLE001 — compile/definition failure is a result, not a crash
        for i in range(len(job["cases"])):
            out.write(json.dumps({"i": i, "status": "error", "output": None,
                                  "exc_type": type(e).__name__, "elapsed_ms": 0.0}) + "\n")
        return 0

    for i, case in enumerate(job["cases"]):
        t0 = time.perf_counter()
        try:
            args = _parse_args(case["args_repr"])
            value = fn(*args)
            rec = {"i": i, "status": "ok", "output": canon(value), "exc_type": None}
        except Unserializable as e:
            rec = {"i": i, "status": "unserializable", "output": None, "exc_type": str(e)[:120]}
        except BaseException as e:  # noqa: BLE001 — the program's own exception is data
            # Only the exception TYPE is recorded: renaming legitimately changes
            # messages and tracebacks, so comparing them would fail every variant.
            rec = {"i": i, "status": "raised", "output": None, "exc_type": type(e).__name__}
        rec["elapsed_ms"] = (time.perf_counter() - t0) * 1000.0
        out.write(json.dumps(rec) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
