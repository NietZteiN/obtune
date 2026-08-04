"""Deduplication and test-set contamination control.

Two complementary signals, because either alone leaks:

* **ast_hash** — sha256 of the *alpha-canonicalized* program text (the L2 transform:
  every binding renamed to a sequential minimal name, annotations stripped). Two
  programs that differ only in identifier names hash identically. This is the exact
  check, and it is the one that matters most here: a training corpus built from
  HumanEval/APPS/CruxEval contains the same classic routine under a dozen names, and
  the test set is drawn from HumanEval-X, so an identifier-only difference between a
  train row and a test row would be pure leakage.

* **MinHash / LSH** — approximate Jaccard over 5-gram shingles of the canonicalized
  token stream, 128 permutations, banded LSH, threshold from configs/data.yaml (0.8).
  Catches the near-duplicates ast_hash cannot: a reordered loop, an extra guard clause,
  a `while` rewritten as a `for`.

Implemented here rather than with `datasketch`: the algorithm is 40 lines of hashlib +
numpy, and a corpus artifact that must be byte-reproducible across environments should
not depend on a third-party library's internal hash choices.

Application order (corpus/build.py):
  1. drop train programs whose upstream id is in configs/sources.yaml `exclude_ids`
  2. drop train programs matching any test-set L0 program (ast_hash or MinHash)
  3. drop train-vs-train duplicates, keeping the first occurrence in source order
"""
from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np

MINHASH_PERMS = 128
SHINGLE_N = 5
LSH_BANDS = 16  # 16 bands x 8 rows: candidate threshold ~ (1/16)^(1/8) = 0.71,
LSH_ROWS = MINHASH_PERMS // LSH_BANDS  # deliberately below 0.8 so the exact
# signature comparison afterwards, not the banding, decides.

# Largest prime below 2**32. Both the shingle hashes and the permutation coefficients
# live below it, so `a*x + b` stays inside uint64 and the whole signature can be
# computed as one vectorized numpy expression instead of 128 Python loops.
_P = 4294967291

_TOKEN_RX = re.compile(r"[A-Za-z_$][A-Za-z_$0-9]*|\d+\.\d+|\d+|\S")


# ------------------------------------------------------------------ canonicalization


def canonicalize(code: str, language: str) -> tuple[str, str]:
    """Return (canonical_text, method). `method` records which path produced it so the
    dedup report says whether the real L2 transform or the fallback was used."""
    if language == "python":
        fn = _l2_python()
        if fn is not None:
            try:
                return fn(code), "obf.py.rename.L2"
            except Exception:  # noqa: BLE001 — a transform failure must not stop dedup
                pass
        return _alpha_canon_python(code), "fallback:ast_alpha"
    if language == "javascript":
        fn = _l2_javascript()
        if fn is not None:
            try:
                return fn(code), "obf.js.driver.L2"
            except Exception:  # noqa: BLE001
                pass
        return _alpha_canon_javascript(code), "fallback:babel_alpha"
    raise ValueError(f"unknown language: {language}")


def ast_hash(code: str, language: str) -> str:
    text, _ = canonicalize(code, language)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _l2_python():
    """The real L2 transform if a peer has published it; None otherwise.

    Imported by name at call time. corpus/ must import cleanly before src/obtune/obf/
    exists, and the fallback below is alpha-equivalent anyway — L2 is preferred only
    because using the same canonicalizer for dedup and for the L2 condition guarantees
    the two can never disagree about what "the same program" means.
    """
    try:
        import importlib

        mod = importlib.import_module("obtune.obf.py.rename")
    except Exception:  # noqa: BLE001
        return None
    for name in ("canonicalize_l2", "apply_l2", "l2"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None


def _l2_javascript():
    try:
        import importlib

        mod = importlib.import_module("obtune.obf.js.driver")
    except Exception:  # noqa: BLE001
        return None
    for name in ("canonicalize_l2", "apply_l2", "l2"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None


class _AlphaRenamer(ast.NodeTransformer):
    """Rename every binding to a1, a2, ... in first-appearance order and drop
    annotations — a hand-rolled stand-in for L2 that is exact for alpha-equivalence.

    Deliberately scope-blind (one flat name map for the whole module). Two programs
    that differ only by which scope a name lives in are the same program for dedup
    purposes, and a scope-correct implementation belongs in obf/py/rename.py, not here.
    Attribute names (`x.append`) and keyword-argument names are left alone: they are
    part of the API being called, not of the program's own naming.
    """

    def __init__(self) -> None:
        self.names: dict[str, str] = {}

    def _alias(self, name: str) -> str:
        if name not in self.names:
            self.names[name] = f"a{len(self.names)}"
        return self.names[name]

    def visit_Name(self, node: ast.Name) -> ast.AST:
        node.id = self._alias(node.id)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = self._alias(node.arg)
        node.annotation = None
        return node

    def _fn(self, node: Any) -> ast.AST:
        node.name = self._alias(node.name)
        node.returns = None
        self.generic_visit(node)
        return node

    visit_FunctionDef = _fn
    visit_AsyncFunctionDef = _fn

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        node.name = self._alias(node.name)
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST:
        self.generic_visit(node)
        if node.value is None:
            return ast.Pass()
        return ast.Assign(targets=[node.target], value=node.value)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        if node.name:
            node.name = self._alias(node.name)
        self.generic_visit(node)
        return node

    def visit_Global(self, node: ast.Global) -> ast.AST:
        node.names = [self._alias(n) for n in node.names]
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.AST:
        node.names = [self._alias(n) for n in node.names]
        return node


def _alpha_canon_python(code: str) -> str:
    tree = ast.parse(code)
    tree = ast.fix_missing_locations(_AlphaRenamer().visit(tree))
    return ast.unparse(tree)


def _alpha_canon_javascript(code: str) -> str:
    """Alpha-canonicalize JS through the Babel helper; on any failure fall back to the
    raw text so dedup degrades to "exact match only" instead of crashing the build."""
    from obtune.corpus.normalize import NormalizationError, _node_js_helper

    try:
        return _node_js_helper({"op": "alpha", "code": code})["code"]
    except (NormalizationError, OSError):
        return code


# ------------------------------------------------------------------------- MinHash


def shingles(text: str, n: int = SHINGLE_N) -> set[str]:
    toks = _TOKEN_RX.findall(text)
    if len(toks) < n:
        return {"\x1f".join(toks)} if toks else set()
    return {"\x1f".join(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def _perm_params(perms: int, seed: int = 17) -> tuple[np.ndarray, np.ndarray]:
    """(a, b) for the universal family h_i(x) = (a_i*x + b_i) mod _P.

    Fixed seed: the permutation family is part of the artifact's identity, so it must
    be identical in every process and every rerun.
    """
    rng = np.random.default_rng(seed)
    a = rng.integers(1, _P, size=perms, dtype=np.uint64)
    b = rng.integers(0, _P, size=perms, dtype=np.uint64)
    return a, b


_A, _B = _perm_params(MINHASH_PERMS)


def minhash(text: str, perms: int = MINHASH_PERMS, n: int = SHINGLE_N) -> np.ndarray:
    """128-element MinHash signature of the text's 5-gram shingle set."""
    sh = shingles(text, n)
    if not sh:
        return np.full(perms, _P, dtype=np.uint64)
    base = np.array(
        [int.from_bytes(hashlib.sha1(s.encode("utf-8")).digest()[:4], "big") % _P for s in sorted(sh)],
        dtype=np.uint64,
    )
    a = _A[:perms, None]
    b = _B[:perms, None]
    return ((a * base[None, :] + b) % np.uint64(_P)).min(axis=1)


def jaccard(sig_a: np.ndarray, sig_b: np.ndarray) -> float:
    """Estimated Jaccard similarity: the fraction of permutations that agree."""
    return float(np.mean(sig_a == sig_b))


def lsh_keys(sig: np.ndarray, bands: int = LSH_BANDS, rows: int = LSH_ROWS) -> list[str]:
    return [
        f"{bi}:" + hashlib.sha1(sig[bi * rows:(bi + 1) * rows].tobytes()).hexdigest()[:16]
        for bi in range(bands)
    ]


# ---------------------------------------------------------------------- application


@dataclass
class DedupDecision:
    program_id: str
    reason: str          # exclude_id | test_ast_hash | test_minhash | train_ast_hash | train_minhash
    matched: str | None  # the program_id (or upstream id) it collided with
    similarity: float | None = None


@dataclass
class DedupResult:
    kept: list[dict[str, Any]] = field(default_factory=list)
    dropped: list[DedupDecision] = field(default_factory=list)
    canon_methods: dict[str, int] = field(default_factory=dict)

    def report(self) -> dict[str, Any]:
        by_reason: dict[str, int] = {}
        for d in self.dropped:
            by_reason[d.reason] = by_reason.get(d.reason, 0) + 1
        return {
            "n_kept": len(self.kept),
            "n_dropped": len(self.dropped),
            "dropped_by_reason": by_reason,
            "canonicalizer_methods": self.canon_methods,
            "minhash": {"perms": MINHASH_PERMS, "shingle_n": SHINGLE_N,
                        "bands": LSH_BANDS, "rows": LSH_ROWS},
            "dropped": [vars(d) for d in self.dropped],
        }


class _Index:
    """ast_hash exact index + MinHash LSH index over one program population."""

    def __init__(self) -> None:
        self.by_hash: dict[str, str] = {}
        self.buckets: dict[str, list[str]] = {}
        self.sigs: dict[str, np.ndarray] = {}

    def add(self, program_id: str, canon_text: str, h: str) -> None:
        self.by_hash.setdefault(h, program_id)
        sig = minhash(canon_text)
        self.sigs[program_id] = sig
        for k in lsh_keys(sig):
            self.buckets.setdefault(k, []).append(program_id)

    def match(self, canon_text: str, h: str, threshold: float) -> tuple[str, str, float] | None:
        if h in self.by_hash:
            return self.by_hash[h], "ast_hash", 1.0
        sig = minhash(canon_text)
        seen: set[str] = set()
        for k in lsh_keys(sig):
            for pid in self.buckets.get(k, ()):
                if pid in seen:
                    continue
                seen.add(pid)
                j = jaccard(sig, self.sigs[pid])
                if j >= threshold:
                    return pid, "minhash", j
        return None


def dedup(
    train_programs: Sequence[dict[str, Any]],
    test_programs: Sequence[dict[str, Any]] = (),
    exclude_ids: Iterable[str] = (),
    threshold: float = 0.8,
) -> DedupResult:
    """Filter `train_programs` against exclusion ids, the test set, and themselves.

    Programs are dicts with at least program_id/language/code; `meta.upstream_id` is
    consulted for the exclude list so a contaminated upstream problem is dropped even
    when its program_id was assigned by us.
    """
    excl = set(exclude_ids)
    res = DedupResult()

    test_idx = _Index()
    for p in test_programs:
        text, method = canonicalize(p["code"], p["language"])
        res.canon_methods[method] = res.canon_methods.get(method, 0) + 1
        test_idx.add(p["program_id"], text, hashlib.sha256(text.encode()).hexdigest())

    train_idx = _Index()
    for p in train_programs:
        pid = p["program_id"]
        upstream = str(p.get("meta", {}).get("upstream_id", ""))
        if pid in excl or (upstream and upstream in excl):
            res.dropped.append(DedupDecision(pid, "exclude_id", upstream or pid))
            continue

        text, method = canonicalize(p["code"], p["language"])
        res.canon_methods[method] = res.canon_methods.get(method, 0) + 1
        h = hashlib.sha256(text.encode()).hexdigest()

        hit = test_idx.match(text, h, threshold)
        if hit:
            res.dropped.append(DedupDecision(pid, f"test_{hit[1]}", hit[0], hit[2]))
            continue
        hit = train_idx.match(text, h, threshold)
        if hit:
            res.dropped.append(DedupDecision(pid, f"train_{hit[1]}", hit[0], hit[2]))
            continue

        train_idx.add(pid, text, h)
        res.kept.append({**p, "meta": {**p.get("meta", {}), "ast_hash": h}})
    return res
