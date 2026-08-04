"""xhwl/cruxeval-x, JavaScript split. Tier 2 — a JS analogue of the CruxEval programs.

Same shape as sources/cruxeval.py, but the arguments are JavaScript source text and are
passed through verbatim rather than round-tripped through Python literals.

Not cached on this host today; `load` raises DatasetNotCached with the fetch command.
Contamination note: Dataset B of the test set includes `cruxeval-x-javascript` rows,
so `configs/sources.yaml exclude_ids.dataset_b_sources` lists this source and
corpus/dedup.py checks every candidate against the test-set L0 programs regardless.
"""
from __future__ import annotations

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


def _iter() -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    path = dataset_path()
    for row in pq.read_table(path).to_pylist():
        code = row.get("code") or row.get("solution") or ""
        given = (row.get("input") or "").strip()
        if not code or not given:
            continue
        rid = row.get("id") or row.get("task_id") or row.get("idx")
        yield {
            "program_id": f"cruxevalx_js_{rid}",
            "language": "javascript",
            "source": SOURCE,
            "code": code,
            "entry_point": row.get("entry_point") or "f",
            "seed_cases": [f"({given.rstrip(',')},)"],
            "meta": {"upstream_id": f"cruxeval-x-javascript/{rid}"},
        }
