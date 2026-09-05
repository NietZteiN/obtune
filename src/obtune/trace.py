"""Execution-trace SFT (W6 lever 3, 2026-09-04).

The direct-answer format asks the model to emit the return value with no intermediate
computation. That is the right format for MEASURING invariance (CLAUDE.md §4.6: a
format failure must not be repaired by the grader), but it caps what a 7B model can
compute in one forward pass — and H1's mechanisms (string encoding, MBA arithmetic)
are exactly the ones that need intermediate steps. Self-consistency showed the
ceiling is not the model's knowledge: `tuned_L0` gets the right answer in 8 draws
0.53-0.59 of the time against 0.43 greedy (`selfcons_generic`).

This arm changes the TARGET, not the loss: the completion becomes an execution trace
of the program as written — the obfuscated program, line numbers and identifiers and
all — followed by the answer. Traces come from the interpreter (`exec/runner_py.py`,
trace mode), so they are correct by construction and free. The model is taught to
*execute*, which is invariant to every meaning-preserving transform by definition;
whether a LoRA on a 7B model can learn to do it is the experiment.

Completion format (one line per event, no blank lines, so the "\\n\\n" stop is safe):

    L8 x=4
    L2 n=4
    L3 s=0
    L4 i=0
    L5
    ...
    => 4

`L<n>` is the line ABOUT TO RUN; the bindings after it are what the previous statement
in that frame changed. A bare `L<n>` is a statement that bound nothing visible (a test,
a loop header) and is kept because it IS the control flow — on S1 (flattened) code the
dispatch loop is the whole story. After `max_events` entries the trace is cut with a
single `...` and the answer follows; the model then learns "trace this far, then
answer", which for long executions degrades gracefully to the direct-answer regime.

The answer is the last line starting with `=> `. A completion without one is a format
failure, exactly as an unparsable literal is in the direct arm — no rescue from the
trace body, or the grader would be doing the model's job.

Rejected: (a) "final values of all variables" instead of a per-line trace — cheaper,
but it drops the control flow, which is the part obfuscation attacks. (b) Dropping rows
whose trace overflows — biases training to short executions; the `...` cut keeps every
row and marks the budget explicitly. (c) Tracing the CLEAN parent and showing it beside
the obfuscated code — that is deobfuscation supervision, which the project's positioning
forbids (CLAUDE.md §3).
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from obtune.config import RUNS_DIR
from obtune.exec.pool import BatchItem, run_batch

TRACE_VERSION = "v1"
DEFAULT_TRACE_CFG: dict[str, int] = {"max_events": 48, "max_repr": 48}
ANSWER_MARK = "=> "


def format_completion(trace: Sequence[str], output_repr: str) -> str:
    body = "\n".join(t for t in trace if t.strip())
    return (body + "\n" if body else "") + ANSWER_MARK + output_repr


def extract_answer(text: str) -> str:
    """Last `=> ` line, or "" (graded as a format failure). Strict on purpose."""
    ans = ""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(ANSWER_MARK.strip()):
            ans = s[len(ANSWER_MARK.strip()):].strip()
    return ans


def _key(code: str, entry_point: str, args_repr: str, cfg: Mapping[str, int]) -> str:
    blob = json.dumps([TRACE_VERSION, code, entry_point, args_repr, dict(cfg)], sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def cache_dir(language: str) -> Path:
    d = RUNS_DIR / "trace_cache" / language
    d.mkdir(parents=True, exist_ok=True)
    return d


def attach_traces(
    rows: Sequence[Any],
    language: str,
    cfg: Optional[Mapping[str, int]] = None,
    workers: int = 8,
    timeout_s: float = 4.0,
) -> tuple[list[tuple[Any, str]], dict[str, Any]]:
    """Return [(row, completion_text)] for every row whose trace could be produced AND
    whose traced return value equals the row's gold, plus a report of what was dropped.

    Rows are TrainPair-like (code, entry_point, args_repr, output_repr). Traces are
    cached under runs/trace_cache/<language>/ keyed by (code, entry, args, cfg), so the
    six-condition arm and the L0-only arm share work and a re-run costs nothing.
    """
    cfg = dict(cfg or DEFAULT_TRACE_CFG)
    cdir = cache_dir(language)
    cache: dict[str, dict[str, Any]] = {}
    cpath = cdir / f"{TRACE_VERSION}_{cfg['max_events']}_{cfg['max_repr']}.jsonl"
    if cpath.exists():
        for line in cpath.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r["status"] == "ok" and r.get("trace") is None:
                    # Written by a runner that predates trace mode (the 2026-09-04
                    # calibration slices): a hit here would silently drop the row as
                    # `trace_ok`. Treat it as a miss; the retrace appends a full record
                    # and, last line winning, shadows this one.
                    continue
                cache[r["k"]] = r

    keys = [_key(r.code, r.entry_point, r.args_repr, cfg) for r in rows]
    todo = [(r, k) for r, k in zip(rows, keys) if k not in cache]
    # One child process per distinct program text: the runner traces every case of a
    # program in one interpreter, so group by (code, entry_point).
    groups: dict[tuple[str, str], list[tuple[Any, str]]] = defaultdict(list)
    for r, k in todo:
        groups[(r.code, r.entry_point)].append((r, k))
    items = [
        BatchItem(program_id=f"{rk[0][0].program_id}", language=language, code=code,
                  entry_point=ep, args_reprs=[r.args_repr for r, _ in rk], trace=cfg)
        for (code, ep), rk in groups.items()
    ]
    n_new = 0
    if items:
        results = run_batch(items, timeout_s=timeout_s, workers=workers)
        with cpath.open("a") as fh:
            for (code, ep), res in zip(groups.keys(), results):
                for (r, k), c in zip(groups[(code, ep)], res.cases):
                    rec = {"k": k, "status": c.status, "output": c.output, "trace": c.trace}
                    cache[k] = rec
                    fh.write(json.dumps(rec) + "\n")
                    n_new += 1

    out: list[tuple[Any, str]] = []
    drops: dict[str, int] = defaultdict(int)
    n_cut = 0
    for r, k in zip(rows, keys):
        rec = cache[k]
        if rec["status"] != "ok" or rec.get("trace") is None:
            drops[f"trace_{rec['status']}"] += 1
            continue
        if rec["output"] != r.output_repr:
            # The traced run disagrees with the gold label. The gold came from the same
            # runner without tracing, so this is a hash-seed / nondeterminism artefact; a
            # trace whose own answer is not the label would teach the wrong thing.
            drops["gold_mismatch"] += 1
            continue
        tr = list(rec["trace"])
        n_cut += int(bool(tr) and tr[-1] == "...")
        out.append((r, format_completion(tr, r.output_repr)))
    report = {
        "trace_version": TRACE_VERSION, "cfg": cfg, "cache": str(cpath),
        "n_rows": len(rows), "n_traced": n_new, "n_kept": len(out),
        "n_cut_at_budget": n_cut, "cut_fraction": (n_cut / len(out)) if out else None,
        "drops": dict(drops),
    }
    return out, report
