"""claudios/code_search_net, python config. Tier 3 — real-world code, no I/O given.

CSN is the scale-out source: ~450k Python functions scraped from GitHub. It is Tier 3
precisely because it ships no test inputs, so every case has to be synthesized. This
loader therefore emits `seed_cases` derived from the function's own *signature* —
parameter annotations and literal defaults — and marks the row
`meta.needs_input_synthesis = True`. corpus/inputs.py accepts those as `fallback_types`
and fuzzes from them; programs whose signature carries no usable type information yield
nothing and are dropped by `build_cases` with `no_usable_seed_inputs`.

Expected yield is low (configs/sources.yaml notes ~5-7%): most CSN functions are
methods, take framework objects, or touch the filesystem, and corpus/filters.py rejects
all of those. That is the intended behaviour — a low-yield source is still worth having
when its programs look nothing like a benchmark, which is exactly the distribution
shift the transfer matrix needs.
"""
from __future__ import annotations

import ast
from typing import Any, Iterator

from obtune.corpus.sources import find_cached, take

REPO_ID = "claudios/code_search_net"
SOURCE = "csn"

# Annotation names we can synthesize values for. Anything else means "we do not know
# what this function eats", and guessing would just burn sandbox time.
_ANNOTATION_SAMPLES: dict[str, list[Any]] = {
    "int": [0, 1, 7, -3],
    "float": [0.0, 1.5, -2.25],
    "bool": [True, False],
    "str": ["", "abc", "Hello World"],
    "bytes": [],  # canon rejects bytes outputs; not worth generating inputs for
    "list": [[], [1, 2, 3], ["a", "b"]],
    "List": [[], [1, 2, 3]],
    "dict": [{}, {"a": 1}],
    "Dict": [{}, {"a": 1}],
    "tuple": [(), (1, 2)],
    "Tuple": [(), (1, 2)],
    "set": [],  # set iteration order is not stable across processes
}


def dataset_paths() -> list:
    """All cached python-split parquet shards, train first."""
    snap = find_cached(REPO_ID, "*train*.parquet", "*.parquet").parent
    return sorted(snap.glob("*.parquet"))


def load(limit: int | None = None, max_loc: int = 60) -> Iterator[dict[str, Any]]:
    return take(_iter(max_loc), limit)


def _iter(max_loc: int) -> Iterator[dict[str, Any]]:
    import pyarrow.parquet as pq

    for path in dataset_paths():
        table = pq.read_table(path, columns=_columns(path))
        for row in table.to_pylist():
            code = row.get("func_code_string") or row.get("whole_func_string") or ""
            if not code or code.count("\n") > max_loc * 2:
                continue
            fn = _top_level_function(code)
            if fn is None:
                continue
            seeds = _signature_seeds(fn)
            yield {
                # Path AND function name: a file contributes several functions
                # (aiohttp/cookiejar.py gave `_is_domain_match` and `_is_path_match` the
                # same id in the 2026-09-03 scale build, 16 collisions in 909 programs).
                "program_id": "csn_" + (str(row.get("func_path_in_repository") or "")
                                        .replace("/", "_").replace(".", "_")[:60]
                                        + "_" + fn.name[:40]),
                "language": "python",
                "source": SOURCE,
                "code": code,
                "entry_point": fn.name,
                "seed_cases": seeds,
                "meta": {"upstream_id": str(row.get("func_code_url") or ""),
                         "needs_input_synthesis": True},
            }


def _columns(path) -> list[str]:
    import pyarrow.parquet as pq

    names = set(pq.ParquetFile(path).schema.names)
    wanted = ["func_code_string", "whole_func_string", "func_name",
              "func_path_in_repository", "func_code_url"]
    return [c for c in wanted if c in names]


def _top_level_function(code: str) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return None
    fns = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    if len(fns) != 1:
        return None
    fn = fns[0]
    args = fn.args
    if args.vararg or args.kwarg or args.kwonlyargs or args.posonlyargs:
        return None
    if args.args and args.args[0].arg in ("self", "cls"):
        return None
    return fn


def _signature_seeds(fn: ast.FunctionDef) -> list[str]:
    """One args_repr per annotation/default combination we can actually build.

    Two seeds are produced (a "small" and a "second" draw) so corpus/inputs.py has more
    than one observation per slot and can infer container element types.
    """
    params = fn.args.args
    if not params:
        return []
    defaults = [None] * (len(params) - len(fn.args.defaults)) + list(fn.args.defaults)
    columns: list[list[Any]] = []
    for p, dflt in zip(params, defaults):
        samples = _samples_for(p.annotation, dflt)
        if not samples:
            return []
        columns.append(samples)
    out = []
    for i in range(2):
        values = [col[i % len(col)] for col in columns]
        out.append("(" + ", ".join(repr(v) for v in values) + ",)")
    return list(dict.fromkeys(out))


def _samples_for(annotation: ast.expr | None, default: ast.expr | None) -> list[Any]:
    if annotation is not None:
        name = _annotation_root(annotation)
        if name in _ANNOTATION_SAMPLES:
            return _ANNOTATION_SAMPLES[name]
    if default is not None:
        try:
            value = ast.literal_eval(default)
        except (ValueError, SyntaxError):
            return []
        if value is None:
            return []
        return [value, value]
    return []


def _annotation_root(node: ast.expr) -> str | None:
    while isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.split("[")[0]
    return None
