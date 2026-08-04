"""nuprl/MultiPL-E, `mbpp-js` config. Tier 2 — MBPP problems translated to JavaScript.

MultiPL-E rows carry a `prompt` (signature + doc comment) and `tests` (a generated
`candidate(...)` harness). The program is `prompt + <a reference solution>`; MultiPL-E
itself ships no reference solution, so this loader is only usable together with a
solutions file (the MultiPL-E "solutions" artifacts, or this project's own
corpus/transpile.py output). `load` therefore takes an optional `solutions` mapping and
refuses to invent bodies.

Not cached on this host today; `load` raises DatasetNotCached with the fetch command.
"""
from __future__ import annotations

import re
from typing import Any, Iterator

from obtune.corpus.sources import DatasetNotCached, find_cached, take

REPO_ID = "nuprl/MultiPL-E"
CONFIG = "mbpp-js"
SOURCE = "multipl_e_mbpp_js"

_ARGS_RX = re.compile(r"candidate\s*\((.*?)\)\s*(?:,|\)|===|==|\.)", re.S)


def dataset_path():
    try:
        return find_cached(REPO_ID, f"*{CONFIG}*.parquet", f"*{CONFIG}*.jsonl")
    except DatasetNotCached as e:
        raise DatasetNotCached(
            f"{e}\n"
            "  Fetch just the mbpp-js config with:\n"
            "  python -c \"from huggingface_hub import snapshot_download; "
            f"snapshot_download('{REPO_ID}', repo_type='dataset', "
            f"allow_patterns=['*{CONFIG}*'])\""
        ) from e


def load(limit: int | None = None, solutions: dict[str, str] | None = None) -> Iterator[dict[str, Any]]:
    return take(_iter(solutions or {}), limit)


def _iter(solutions: dict[str, str]) -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    for row in pq.read_table(dataset_path()).to_pylist():
        name = row.get("name") or row.get("task_id")
        body = solutions.get(str(name))
        if not body:
            # No reference body: skipping is the honest option. Emitting a
            # signature-only program would produce a stimulus whose "output" is
            # undefined for every input and pollute the determinism statistics.
            continue
        seeds = _seed_cases(row.get("tests") or "")
        if not seeds:
            continue
        yield {
            "program_id": f"multiple_js_{name}",
            "language": "javascript",
            "source": SOURCE,
            "code": (row.get("prompt") or "") + body,
            "entry_point": _entry_point(row.get("prompt") or ""),
            "seed_cases": seeds,
            "meta": {"upstream_id": f"{CONFIG}/{name}"},
        }


def _entry_point(prompt: str) -> str:
    m = re.search(r"(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", prompt)
    return m.group(1) if m else "candidate"


def _seed_cases(tests: str) -> list[str]:
    """Pull `candidate(<args>)` argument text straight out of the generated harness.

    Regex rather than Babel here because MultiPL-E harnesses are machine-generated from
    one template; if that template ever changes, an empty seed list is the correct and
    visible failure, not a silently mis-parsed one.
    """
    out, seen = [], set()
    for m in _ARGS_RX.finditer(tests):
        args = m.group(1).strip()
        rendered = f"({args.rstrip(',')},)" if args else "()"
        if rendered not in seen:
            seen.add(rendered)
            out.append(rendered)
    return out[:8]
