"""google-research-datasets/mbpp (+ evalplus/mbppplus extra inputs). Tier 2.

Shape is identical to HumanEval's Python path: one small function, seed inputs parsed
out of `assert` statements. MBPPPlus is *not* a source of new programs — it is a source
of additional test inputs for MBPP's programs, so `load` merges its `assertion`/`test`
fields into the seed list of the matching `task_id` when it is cached.

Not cached on this host today; `load` raises DatasetNotCached with the fetch command.
"""
from __future__ import annotations

import ast
from typing import Any, Iterator

from obtune.corpus.sources import DatasetNotCached, find_cached, parse_assert_cases, take

REPO_ID = "google-research-datasets/mbpp"
PLUS_REPO_ID = "evalplus/mbppplus"
SOURCE = "mbpp"


def dataset_paths() -> list:
    snap_files = []
    for pat in ("*train*.parquet", "*test*.parquet", "*validation*.parquet", "*.jsonl"):
        try:
            snap_files.append(find_cached(REPO_ID, pat))
        except DatasetNotCached:
            continue
    if not snap_files:
        raise DatasetNotCached(
            f"{REPO_ID} is not cached. Fetch with:\n"
            "  python -c \"from huggingface_hub import snapshot_download; "
            f"snapshot_download('{REPO_ID}', repo_type='dataset')\""
        )
    return sorted(set(snap_files))


def load(limit: int | None = None, with_plus: bool = True) -> Iterator[dict[str, Any]]:
    return take(_iter(with_plus), limit)


def _iter(with_plus: bool) -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    extra = _plus_cases() if with_plus else {}
    for path in dataset_paths():
        rows = pq.read_table(path).to_pylist() if path.suffix == ".parquet" else _read_jsonl(path)
        for row in rows:
            code = row.get("code") or ""
            entry = _entry_point(code, row.get("test_list") or [])
            if not entry:
                continue
            tests = "\n".join(row.get("test_list") or []) + "\n" + "\n".join(row.get("challenge_test_list") or [])
            seeds = parse_assert_cases(tests, entry)
            seeds += extra.get(str(row.get("task_id")), [])
            if not seeds:
                continue
            yield {
                "program_id": f"mbpp_{row['task_id']}",
                "language": "python",
                "source": SOURCE,
                "code": code,
                "entry_point": entry,
                "seed_cases": seeds,
                "meta": {"upstream_id": f"mbpp/{row['task_id']}"},
            }


def _plus_cases() -> dict[str, list[str]]:
    """Extra inputs from MBPPPlus, keyed by MBPP task_id. Absent cache is not an error —
    the base programs are still usable, just with fewer seeds."""
    try:
        path = find_cached(PLUS_REPO_ID, "*.parquet", "*.jsonl")
    except DatasetNotCached:
        return {}
    import pyarrow.parquet as pq

    rows = pq.read_table(path).to_pylist() if path.suffix == ".parquet" else _read_jsonl(path)
    out: dict[str, list[str]] = {}
    for row in rows:
        tid = str(row.get("task_id") or row.get("mbpp_task_id") or "")
        code = row.get("code") or ""
        entry = _entry_point(code, row.get("test_list") or [])
        if not tid or not entry:
            continue
        out.setdefault(tid, []).extend(parse_assert_cases(row.get("test") or "", entry))
    return out


def _read_jsonl(path) -> list[dict[str, Any]]:
    import json

    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _entry_point(code: str, test_list: list[str]) -> str | None:
    """MBPP names no entry point; it is the function the asserts call."""
    try:
        defined = {n.name for n in ast.walk(ast.parse(code))
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    except (SyntaxError, ValueError):
        return None
    for test in test_list:
        try:
            tree = ast.parse(test)
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in defined:
                return node.func.id
    return None
