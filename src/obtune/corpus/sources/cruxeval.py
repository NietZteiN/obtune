"""cruxeval-org/cruxeval — 800 short pure functions, one given input each.

CruxEval is the closest upstream analogue of this project's task (it *is* input/output
prediction), so its programs are already the right shape: a single `def f(...)`, no
imports, no I/O, one concrete input per row. The single given input is a seed; the
fuzzer supplies the rest.

The row's `output` field is discarded on purpose. Every gold answer in this project is
re-derived by executing under exec/canon, so that Python and JavaScript stimuli are
graded against the same serialization. Trusting an upstream repr here would silently
reintroduce the Python/JS formatting split the canon contract exists to remove.
"""
from __future__ import annotations

import json
from typing import Any, Iterator

from obtune.corpus.sources import find_cached, take

REPO_ID = "cruxeval-org/cruxeval"
SOURCE = "cruxeval"


def dataset_path():
    return find_cached(REPO_ID, "test.jsonl")


def load(limit: int | None = None) -> Iterator[dict[str, Any]]:
    return take(_iter(), limit)


def _iter() -> Iterator[dict[str, Any]]:
    with open(dataset_path()) as f:
        for line in f:
            row = json.loads(line)
            given = (row.get("input") or "").strip()
            if not given:
                continue
            yield {
                "program_id": f"cruxeval_{row['id']}",
                "language": "python",
                "source": SOURCE,
                "code": row["code"],
                "entry_point": "f",
                # `input` is the comma-separated positional-argument source text, so
                # wrapping it in parentheses is already the args_repr form.
                "seed_cases": [f"({given.rstrip(',')},)"],
                "meta": {"upstream_id": f"cruxeval/{row['id']}"},
            }
