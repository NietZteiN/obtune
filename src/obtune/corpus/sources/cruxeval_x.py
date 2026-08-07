"""xhwl/cruxeval-x, JavaScript split. Tier 2 — a JS analogue of the CruxEval programs.

Same shape as sources/cruxeval.py, but the arguments are JavaScript source text and are
passed through verbatim rather than round-tripped through Python literals.

Not cached on this host today; `load` raises DatasetNotCached with the fetch command.
Contamination note: Dataset B of the test set includes `cruxeval-x-javascript` rows,
so `configs/sources.yaml exclude_ids.dataset_b_sources` lists this source and
corpus/dedup.py checks every candidate against the test-set L0 programs regardless.
"""
from __future__ import annotations

import re
from typing import Any, Iterator

from obtune.corpus.sources import DatasetNotCached, find_cached, take

REPO_ID = "xhwl/cruxeval-x"
DATA_FILE = "JavaScript-*.parquet"
SOURCE = "cruxeval_x_js"


def dataset_path():
    try:
        return find_cached(REPO_ID, DATA_FILE, "*JavaScript*.parquet", "*JavaScript*.jsonl")
    except DatasetNotCached as e:
        raise DatasetNotCached(
            f"{e}\n"
            "  Fetch just the JS split with:\n"
            "  python -c \"from huggingface_hub import snapshot_download; "
            f"snapshot_download('{REPO_ID}', repo_type='dataset', "
            "allow_patterns=['data/JavaScript-*'])\""
        ) from e


def load(limit: int | None = None) -> Iterator[dict[str, Any]]:
    return take(_iter(), limit)


#: The published parquet has columns (id, code, input_reasoning, output_reasoning) and
#: NO plain `input` column — the call argument is embedded in the assertion inside
#: `output_reasoning` as `candidate(<args>)`. (`input_reasoning` holds the mirror-image
#: task and masks the argument as `????`, so it is the wrong field to read.)
_CANDIDATE_CALL = re.compile(r"candidate\((.*?)\)\s*,\s*\?{3,}", re.DOTALL)
_CANDIDATE_ANY = re.compile(r"candidate\((.*?)\)\s*[,)]", re.DOTALL)


#: The `code` field ships the program AND its test harness concatenated:
#:     function f(...) {...}
#:     const assert = require('node:assert');
#:     function test() { ... } test();
#: The harness must go — `require(` is a banned non-deterministic construct (so the
#: static filter rejected all 729 rows), and leaving an assertion carrying the gold
#: answer in the prompt would hand the model the answer it is being asked to predict.
_HARNESS_RE = re.compile(r"\n\s*(?:const|let|var)\s+assert\s*=\s*require\s*\(", re.MULTILINE)


def _strip_harness(code: str) -> str:
    m = _HARNESS_RE.search(code)
    return (code[: m.start()] if m else code).rstrip() + "\n"


def _extract_args(row: dict[str, Any]) -> str:
    """The literal argument text of the `candidate(...)` call, or ''."""
    for field in ("output_reasoning", "input_reasoning"):
        text = row.get(field) or ""
        for pat in (_CANDIDATE_CALL, _CANDIDATE_ANY):
            m = pat.search(text)
            if m:
                args = m.group(1).strip()
                if args and "?" not in args:
                    return args
    return ""


def _iter() -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    path = dataset_path()
    for row in pq.read_table(path).to_pylist():
        code = _strip_harness(row.get("code") or row.get("solution") or "")
        given = (row.get("input") or "").strip() or _extract_args(row)
        if not code or not given:
            continue
        # `or`-chaining loses id 0, which is a real row: every program then shares the
        # id "None" and dedup collapses the whole corpus to one program.
        rid = next((row[k] for k in ("id", "task_id", "idx") if row.get(k) is not None), None)
        yield {
            "program_id": f"cruxevalx_js_{rid}",
            "language": "javascript",
            "source": SOURCE,
            "code": code,
            "entry_point": row.get("entry_point") or "f",
            "seed_cases": [f"({given.rstrip(',')},)"],
            "meta": {"upstream_id": f"cruxeval-x-javascript/{rid}"},
        }
