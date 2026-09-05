"""Child process for the Python batch executor. NOT imported by anything.

Protocol: reads one JSON job from stdin, writes one JSON line per case to stdout.
Job:    {"code": str, "entry_point": str, "cases": [{"args_repr": "(1, 2)"}, ...],
         "trace": {"max_events": int, "max_repr": int} | absent}
Result: {"i": int, "status": "ok"|"raised"|"unserializable"|"error",
         "output": str|null, "exc_type": str|null, "elapsed_ms": float,
         "trace": [str, ...] | absent}

Trace mode (W6 lever 3, 2026-09-04) records an execution trace of the program under
test for the trace-SFT arm: one entry per `line` event in a frame whose code lives in
the program (`<program>` filename), listing ONLY the locals whose value changed since
the previous event in that frame. Values are canonicalised with exec/canon where
possible so the trace speaks the same literal dialect as the answer. After
`max_events` entries a single "..." is appended and tracing is switched off, so a long
loop costs one line, not a runaway completion. `sys.settrace` is process-global and
slows the program ~3-10x; the parent's CPU limit still applies.

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


class _Tracer:
    """sys.settrace hook. Kept minimal: this runs inside the rlimited child."""

    def __init__(self, canon_fn, max_events: int, max_repr: int) -> None:
        self.canon = canon_fn
        self.max_events = max_events
        self.max_repr = max_repr
        self.events: list[str] = []
        self.truncated = False
        # frame id -> last seen {name: rendered value}; keyed by id(frame) so recursion
        # (several live frames of the same function) does not cross-diff.
        self._seen: dict[int, dict[str, str]] = {}

    import types as _types

    _SKIP_TYPES = (_types.FunctionType, _types.BuiltinFunctionType, _types.MethodType,
                   _types.ModuleType, type)

    def _render(self, v):
        """Canonical literal where possible; otherwise `<TypeName>` and never a repr —
        a repr of an iterator or a match object carries a memory address, which is
        noise the model cannot predict and would be trained to hallucinate. Returns
        None for values that should not appear at all (functions, classes, modules:
        a binding like `parse=<function>` is a def statement, not data)."""
        if isinstance(v, self._SKIP_TYPES) or (callable(v) and not isinstance(v, (str, bytes, int, float))):
            return None
        try:
            s = self.canon(v)
        except Exception:  # noqa: BLE001 — sets, tuples of objects, custom classes ...
            if isinstance(v, (set, frozenset, tuple)):
                try:
                    s = repr(v)
                except Exception:  # noqa: BLE001
                    s = f"<{type(v).__name__}>"
            else:
                s = f"<{type(v).__name__}>"
        if len(s) > self.max_repr:
            s = s[: self.max_repr - 1] + "\u2026"
        return s

    def __call__(self, frame, event, arg):
        if frame.f_code.co_filename != "<program>":
            return None  # library frames: do not descend
        if event == "call":
            self._seen[id(frame)] = {}
            return self  # trace this frame's lines
        if event == "return":
            self._seen.pop(id(frame), None)
            return None
        if event != "line" or self.truncated:
            return self
        prev = self._seen.setdefault(id(frame), {})
        cur: dict[str, str] = {}
        changed: list[str] = []
        for k, v in frame.f_locals.items():
            if k.startswith(("__", ".")):  # dunder scaffolding, comprehension internals
                continue
            r = self._render(v)
            if r is None:
                continue
            cur[k] = r
            if prev.get(k) != r:
                changed.append(f"{k}={r}")
        self._seen[id(frame)] = cur
        # The line event fires BEFORE the line runs, so the bindings reported here are the
        # effect of the PREVIOUS statement in this frame; the line number is the statement
        # about to run. `L<n>` alone (no changes) is a statement that bound nothing visible
        # (a condition test, a loop header re-entry) and is kept: it is the control flow.
        # Consecutive bare lines are MERGED onto one trace line ("L8 L11 L14"): on S1's
        # dispatch loop three tests fire per state, and each merged run costs one line of
        # the budget instead of three. The budget counts emitted lines, i.e. tokens.
        tag = f"L{frame.f_lineno}"
        if changed:
            self.events.append(tag + " " + " ".join(changed))
        elif self.events and "=" not in self.events[-1]:
            self.events[-1] += " " + tag
        else:
            self.events.append(tag)
        if len(self.events) >= self.max_events:
            self.events.append("...")
            self.truncated = True
            sys.settrace(None)
            return None
        return self


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

    # The program under test shares this process's stdout, and model-generated programs
    # print. Its output would interleave with the JSON-lines protocol — and a bare
    # `print(42)` even parses as valid JSON, which crashed the parent with
    # `'int' object has no attribute 'get'` after 21 000 generations. So the protocol
    # keeps a PRIVATE dup of the real stdout and fd 1 is pointed at devnull before any
    # program code runs. fd-level, not sys.stdout-level, so C extensions cannot escape it.
    out = os.fdopen(os.dup(1), "w")
    _devnull_fd = os.open(os.devnull, os.O_WRONLY)
    os.dup2(_devnull_fd, 1)
    sys.stdout = os.fdopen(os.dup(1), "w")
    glb: dict = {"__name__": "__obtune_program__", "__builtins__": _builtins()}
    try:
        exec(compile(job["code"], "<program>", "exec"), glb)
        fn = glb[job["entry_point"]]
    except BaseException as e:  # noqa: BLE001 — compile/definition failure is a result, not a crash
        for i in range(len(job["cases"])):
            out.write(json.dumps({"i": i, "status": "error", "output": None,
                                  "exc_type": type(e).__name__, "elapsed_ms": 0.0}) + "\n")
        out.flush()
        return 0

    tcfg = job.get("trace")
    for i, case in enumerate(job["cases"]):
        t0 = time.perf_counter()
        tracer = None
        try:
            args = _parse_args(case["args_repr"])
            if tcfg:
                tracer = _Tracer(canon, int(tcfg.get("max_events", 40)), int(tcfg.get("max_repr", 48)))
                sys.settrace(tracer)
            try:
                value = fn(*args)
            finally:
                if tcfg:
                    sys.settrace(None)
            rec = {"i": i, "status": "ok", "output": canon(value), "exc_type": None}
            if tracer is not None:
                rec["trace"] = tracer.events
        except Unserializable as e:
            rec = {"i": i, "status": "unserializable", "output": None, "exc_type": str(e)[:120]}
        except BaseException as e:  # noqa: BLE001 — the program's own exception is data
            # Only the exception TYPE is recorded: renaming legitimately changes
            # messages and tracebacks, so comparing them would fail every variant.
            rec = {"i": i, "status": "raised", "output": None, "exc_type": type(e).__name__}
        rec["elapsed_ms"] = (time.perf_counter() - t0) * 1000.0
        out.write(json.dumps(rec) + "\n")
    out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
