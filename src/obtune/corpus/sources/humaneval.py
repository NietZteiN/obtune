"""HumanEval, both languages.

Python: `openai_humaneval` from the HF cache. The program is `prompt +
canonical_solution` (the prompt ends mid-signature, so concatenation is the only
correct join), and the seed inputs come from the `check(candidate)` asserts.

JavaScript: the local HumanEval-X JS corpus at the path in configs/sources.yaml
(164 programs, structured `io_pairs`, all <= 60 LOC). Its `obf_code_L1/L2/L3` and
`code_L1b` fields are the *legacy ICSE* variants and are deliberately ignored — this
project regenerates every condition from the L0 parent so that Python and JavaScript
get identical transform semantics, and the legacy JS variants carry H1-family
string-keyed dispatch (docs/TIER_MAPPING.md).

Contamination note: the test set's Dataset A and the HumanEval-X half of Dataset B are
drawn from these same two corpora. `configs/sources.yaml exclude_ids` lists the
task_ids to drop outright, and corpus/dedup.py independently catches the rest.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator

from obtune.corpus.sources import DatasetNotCached, find_cached, parse_assert_cases, take

REPO_ID = "openai_humaneval"
SOURCE_PY = "humaneval"
SOURCE_JS = "humaneval_x_js"
# Single source of truth is configs/sources.yaml; this constant only exists so the
# loader can be called without threading the config through. OBTUNE_JS_CORPUS wins,
# which is what makes the module portable across clusters (2026-08-28 migration).
JS_CORPUS_PATH = Path(
    os.environ.get(
        "OBTUNE_JS_CORPUS",
        "/work/jvl210002/migration/dataset/humaneval_js/humaneval_x_js_full.json",
    )
)


def load(limit: int | None = None, language: str = "python") -> Iterator[dict[str, Any]]:
    if language == "python":
        return load_python(limit)
    if language == "javascript":
        return load_javascript(limit)
    raise ValueError(f"unknown language: {language}")


# ---------------------------------------------------------------------------- Python


def dataset_path():
    return find_cached(REPO_ID, "*.parquet")


def load_python(limit: int | None = None) -> Iterator[dict[str, Any]]:
    return take(_iter_python(), limit)


def _iter_python() -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    for row in pq.read_table(dataset_path()).to_pylist():
        entry = row["entry_point"]
        seeds = parse_assert_cases(row.get("test") or "", entry)
        if not seeds:
            continue
        task_id = row["task_id"]  # "HumanEval/0"
        yield {
            "program_id": "humaneval_py_" + task_id.split("/")[-1],
            "language": "python",
            "source": SOURCE_PY,
            "code": row["prompt"] + row["canonical_solution"],
            "entry_point": entry,
            "seed_cases": seeds,
            "meta": {"upstream_id": task_id,
                     "upstream_id_alt": "Python/" + task_id.split("/")[-1]},
        }


# ------------------------------------------------------------------------ JavaScript


def js_corpus_path(path: str | Path | None = None) -> Path:
    p = Path(path) if path else JS_CORPUS_PATH
    if not p.exists():
        raise DatasetNotCached(
            f"local HumanEval-X JS corpus not found at {p}. "
            "Set the path in configs/sources.yaml (javascript.tier1.humaneval_x_js.path)."
        )
    return p


def load_javascript(limit: int | None = None, path: str | Path | None = None) -> Iterator[dict[str, Any]]:
    return take(_iter_javascript(path), limit)


def _iter_javascript(path: str | Path | None) -> Iterator[dict[str, Any]]:
    rows = json.loads(js_corpus_path(path).read_text())
    for row in rows:
        code = row.get("code_L0")
        if not code:
            continue
        seeds = []
        for pair in row.get("io_pairs", []):
            # `inputs_raw` is the argument list as JS source text; `inputs` is the same
            # thing already decoded. Prefer the raw text — it preserves literals (regex,
            # -0, 1e21) that a JSON round-trip through Python would flatten.
            raw = pair.get("inputs_raw")
            if raw:
                seeds.append("(" + ", ".join(raw) + ("," if raw else "") + ")")
            elif "inputs" in pair:
                seeds.append("(" + ", ".join(json.dumps(v) for v in pair["inputs"]) + ",)")
        if not seeds:
            continue
        task_id = row["task_id"]  # "JavaScript/0"
        yield {
            "program_id": "humaneval_js_" + task_id.split("/")[-1],
            "language": "javascript",
            "source": SOURCE_JS,
            "code": code,
            "entry_point": row["fn_name"],
            "seed_cases": seeds,
            "meta": {"upstream_id": task_id},
        }
