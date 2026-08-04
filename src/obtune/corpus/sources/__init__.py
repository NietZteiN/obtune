"""Corpus source loaders — one module per upstream dataset, one shape for all of them.

Every loader exposes::

    load(limit: int | None = None) -> Iterator[dict]

yielding raw (pre-normalization, pre-filter) records::

    {"program_id": str,      # globally unique, prefixed with the source name
     "language":   "python" | "javascript",
     "source":     str,      # matches configs/sources.yaml `name`
     "code":       str,      # raw upstream text
     "entry_point": str,
     "seed_cases": list}     # args_repr strings or positional-value lists

The registry in configs/sources.yaml points at these modules by dotted path. A loader
whose dataset is not present locally raises `DatasetNotCached` with the exact command
to fetch it — never a silent empty iterator, which would look like "the source yielded
nothing useful" in the build log and quietly shrink the corpus.

Working today (Tier 1, zero download): apps, cruxeval, humaneval (Python + the local
JS corpus), csn. Tier 2/3 loaders (mbpp, cruxeval_x, multipl_e) are written to the same
shape and raise DatasetNotCached until their datasets are fetched.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any, Iterator

HF_HOME = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
HF_HUB = HF_HOME / "hub"

SOURCE_MODULES = {
    "apps": "obtune.corpus.sources.apps",
    "cruxeval": "obtune.corpus.sources.cruxeval",
    "humaneval": "obtune.corpus.sources.humaneval",
    "humaneval_x_js": "obtune.corpus.sources.humaneval",
    "mbpp": "obtune.corpus.sources.mbpp",
    "mbppplus": "obtune.corpus.sources.mbpp",
    "cruxeval_x_js": "obtune.corpus.sources.cruxeval_x",
    "multipl_e_mbpp_js": "obtune.corpus.sources.multipl_e",
    "csn": "obtune.corpus.sources.csn",
}


class DatasetNotCached(RuntimeError):
    """The upstream dataset is not in the local HF cache. Message carries the fix."""


def hub_snapshot(repo_id: str) -> Path:
    """Resolve `org/name` to its cached snapshot directory under HF_HOME/hub."""
    slug = "datasets--" + repo_id.replace("/", "--")
    root = HF_HUB / slug / "snapshots"
    if not root.is_dir():
        raise DatasetNotCached(
            f"{repo_id} is not in the local HF cache ({HF_HUB}).\n"
            f"  Fetch with: HF_HOME={HF_HOME} python -c "
            f"\"from huggingface_hub import snapshot_download; "
            f"snapshot_download('{repo_id}', repo_type='dataset')\""
        )
    snaps = sorted(p for p in root.iterdir() if p.is_dir())
    if not snaps:
        raise DatasetNotCached(f"{repo_id}: snapshots directory {root} is empty")
    return snaps[-1]


def find_cached(repo_id: str, *patterns: str) -> Path:
    """First file under the cached snapshot of `repo_id` matching any glob pattern."""
    snap = hub_snapshot(repo_id)
    for pat in patterns:
        hits = sorted(snap.rglob(pat))
        if hits:
            return hits[0]
    raise DatasetNotCached(
        f"{repo_id} is cached at {snap} but none of {patterns} is present. "
        "Re-download the dataset with allow_patterns covering those files."
    )


def parse_assert_cases(test_src: str, entry_point: str, alias: str = "candidate") -> list[str]:
    """Extract `args_repr` strings from an evaluation harness's assert statements.

    Handles the HumanEval/MBPP shapes: `assert candidate(a, b) == expected`,
    `assert f(x) == y`, and `assert abs(candidate(x) - y) < 1e-6`. Only the *arguments*
    are taken — the expected value is deliberately ignored, because the upstream
    expectation is written in the upstream language's repr and this project derives
    every gold answer by re-executing under exec/canon.
    """
    out: list[str] = []
    try:
        tree = ast.parse(test_src)
    except (SyntaxError, ValueError):
        return out
    wanted = {alias, entry_point}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
        if name not in wanted or node.keywords:
            continue
        try:
            values = [ast.literal_eval(a) for a in node.args]
        except (ValueError, SyntaxError, TypeError):
            continue
        out.append("(" + ", ".join(repr(v) for v in values) + ("," if values else "") + ")")
    seen: set[str] = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def take(it: Iterator[dict[str, Any]], limit: int | None) -> Iterator[dict[str, Any]]:
    for i, row in enumerate(it):
        if limit is not None and i >= limit:
            return
        yield row


__all__ = [
    "DatasetNotCached", "SOURCE_MODULES", "HF_HOME", "HF_HUB",
    "hub_snapshot", "find_cached", "parse_assert_cases", "take",
]
