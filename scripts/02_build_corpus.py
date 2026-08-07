#!/usr/bin/env python
"""Build the training corpus: sources -> filters -> input cases -> dedup -> splits.

Pipeline (each stage's attrition is counted and reported, because a corpus that
silently loses 90% of its programs at one stage is a different corpus than the one
the design doc describes):

  1. load raw programs from the configured sources
  2. L0-normalize (comments/docstrings stripped, 4-space indent) and count LOC
  3. static filters — determinism hazards (random/time/os/IO), LOC and size bounds
  4. input cases — harvest seed args, fuzz to n_cases + gate inputs, require
     non-triviality and byte-identical output across repeats with varied hash seeds
  5. dedup vs the TEST set (AST-hash + MinHash) and vs itself, plus the explicit
     upstream-id exclusion lists in configs/sources.yaml
  6. split by program_id (never by row) and write data/train/base/<lang>.jsonl

    python scripts/02_build_corpus.py --language python --limit 4000
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import load_config  # noqa: E402
from obtune.corpus import dedup as dedup_mod  # noqa: E402
from obtune.corpus import filters, inputs, normalize  # noqa: E402
from obtune.manifest import h1_marker_patterns  # noqa: E402
from obtune.paths import MANIFESTS_ROOT, SPLITS_ROOT, TRAIN_ROOT, iter_jsonl, write_jsonl  # noqa: E402
from obtune.schema import BaseProgram, InputCase  # noqa: E402

SOURCE_LOADERS = {
    "apps": ("obtune.corpus.sources.apps", "load"),
    "cruxeval": ("obtune.corpus.sources.cruxeval", "load"),
    "humaneval": ("obtune.corpus.sources.humaneval", "load"),
    "mbpp": ("obtune.corpus.sources.mbpp", "load"),
    "cruxeval_x": ("obtune.corpus.sources.cruxeval_x", "load"),
    "multipl_e": ("obtune.corpus.sources.multipl_e", "load"),
    "csn": ("obtune.corpus.sources.csn", "load"),
}


def _load_source(name: str, language: str, limit: int | None, module: str | None = None):
    """Resolve a source loader.

    `module` comes from the `loader:` key in configs/sources.yaml and is
    authoritative. Guessing from the source name is not safe: `cruxeval_x_js`
    prefix-matched to the *Python* `cruxeval` loader, which silently fed 799 Python
    programs into the JavaScript corpus where they all died in normalization.
    """
    import importlib

    if module:
        mod_name, attr = module, "load"
    else:
        mod_name, attr = SOURCE_LOADERS[name]
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr)
    kwargs = {}
    if "language" in fn.__code__.co_varnames[: fn.__code__.co_argcount]:
        kwargs["language"] = language
    return list(fn(limit=limit, **kwargs))


def _screen_one(r: dict, seeds: list[str], language: str, case_args: dict):
    """Worker body for stage 4. Returns (program|None, reasons)."""
    try:
        bundle = inputs.build_cases(
            r["program_id"], language, r["code"], r["entry_point"], seeds, **case_args
        )
    except Exception as exc:  # noqa: BLE001 — a bad source program is data, not a crash
        return None, [type(exc).__name__]
    if not getattr(bundle, "ok", False):
        return None, list(getattr(bundle, "reasons", None) or ["unspecified"])
    return {**r, "cases": bundle.cases, "gate_inputs": bundle.gate_inputs}, []


def _test_programs(language: str) -> list[dict]:
    """The L0 test parents, for contamination checking."""
    out: list[dict] = []
    base = ROOT / "data" / "eval" / "testset" / "base"
    for f in sorted(base.glob("*.jsonl")):
        for row in iter_jsonl(f):
            if row.get("language") == language:
                out.append(row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--language", default="python", choices=["python", "javascript"])
    ap.add_argument("--tiers", nargs="*", default=["tier1"],
                    help="which source tiers from configs/sources.yaml (tier1 needs no downloads)")
    ap.add_argument("--limit", type=int, default=None, help="cap raw programs per source")
    ap.add_argument("--target", type=int, default=None, help="stop once this many programs survive")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lang = args.language
    data_cfg = load_config("data.yaml")
    src_cfg = load_config("sources.yaml")
    seed = int(data_cfg.get("seed", 17))
    f_cfg = data_cfg["filters"]
    c_cfg = data_cfg["cases"]

    stage = Counter()
    reasons: Counter = Counter()
    t0 = time.perf_counter()

    # -- 1. load ---------------------------------------------------------- #
    raw: list[dict] = []
    for tier in args.tiers:
        for spec in (src_cfg.get(lang) or {}).get(tier, []) or []:
            module = spec.get("loader")
            loader = spec["name"] if spec["name"] in SOURCE_LOADERS else None
            if not module and not loader:
                print(f"  skip {spec['name']}: no loader registered and no `loader:` key")
                continue
            try:
                got = _load_source(loader or spec["name"], lang, args.limit, module=module)
            except Exception as exc:  # noqa: BLE001
                # One unavailable source must not kill the build: sources are tiered
                # precisely so a corpus can be assembled from whatever is present.
                # The skip is printed and recorded, never silent.
                first = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
                print(f"  skip {spec['name']}: {type(exc).__name__}: {first}")
                reasons[f"source_unavailable:{spec['name']}"] += 1
                continue
            print(f"  loaded {len(got):>6} from {spec['name']}")
            raw.extend(got)
    stage["raw"] = len(raw)
    if not raw:
        print("no source programs loaded — nothing to build")
        return 1

    # -- 2. normalize ----------------------------------------------------- #
    normalized: list[dict] = []
    for r in raw:
        try:
            n = normalize.normalize(r["code"], lang)
        except Exception as exc:  # noqa: BLE001 — a source program that will not parse is data, not a crash
            reasons[f"normalize:{type(exc).__name__}"] += 1
            continue
        code = n.code if hasattr(n, "code") else n
        if not code.strip():
            reasons["normalize:empty"] += 1
            continue
        normalized.append({**r, "code": code, "loc": len(code.splitlines())})
    stage["normalized"] = len(normalized)

    # -- 3. static filters ------------------------------------------------ #
    # A program whose ORIGINAL source already contains an H1 marker (an APPS entry
    # named `base64_to_base10`, say) has to be rejected here, at admission, not
    # later at the variant gate. Rejecting at the gate produces a program that
    # contributes to some conditions but not others — the identifier conditions
    # rename the offending symbol away and pass, while L0/S1/S2 keep it and fail —
    # which silently makes the condition arms cover different program sets. It also
    # leaves data/train/base/ permanently failing scripts/check_manifest.py.
    h1_patterns = h1_marker_patterns()

    kept: list[dict] = []
    for r in normalized:
        hits = [p.pattern for p in h1_patterns if p.search(r["code"])]
        if hits:
            reasons[f"filter:h1_marker:{hits[0]}"] += 1
            continue
        v = filters.check_program(
            r["code"], lang, loc=r.get("loc"),
            loc_min=int(f_cfg["loc_min"]), loc_max=int(f_cfg["loc_max"]),
            max_chars=int(f_cfg["max_chars"]), entry_point=r.get("entry_point"),
        )
        if getattr(v, "ok", False):
            kept.append(r)
        else:
            for why in (getattr(v, "reasons", None) or ["unspecified"]):
                reasons[f"filter:{why}"] += 1
    stage["static_filtered"] = len(kept)
    print(f"  static filters: {len(kept)}/{len(normalized)} survive")

    # -- 4. input cases (the expensive stage: it executes every program) --- #
    # Each program costs ~2s here (fuzzing + 3 determinism repeats x ~25 executions),
    # so a 4k-program corpus is ~2.2 CPU-hours serially. The work is embarrassingly
    # parallel across programs and the executor already sandboxes each run, so it is
    # farmed out; ordering is restored afterwards to keep the corpus reproducible.
    case_args = dict(
        n_cases=int(c_cfg["n_train_cases"]), n_gate_inputs=int(c_cfg["n_gate_inputs"]),
        seed=seed, min_distinct_outputs=int(f_cfg["min_distinct_outputs"]),
        max_output_chars=int(f_cfg["max_output_chars"]),
        determinism_repeats=int(f_cfg["determinism_repeats"]),
    )
    candidates = []
    for r in kept:
        seeds = inputs.harvest_seeds(r.get("seed_cases") or [], lang)
        if not seeds:
            reasons["cases:no_seed_args"] += 1
            continue
        candidates.append((r, seeds))
    if args.target:
        # Overshoot the target so the post-screening yield still reaches it, but do
        # not screen the whole corpus when a small run was requested.
        candidates = candidates[: max(args.target * 6, args.target + 200)]

    programs: list[dict] = []
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(_screen_one, r, seeds, lang, case_args): r["program_id"]
            for r, seeds in candidates
        }
        for fut in as_completed(futures):
            done += 1
            rec, why = fut.result()
            if rec is None:
                for w in why:
                    reasons[f"cases:{w}"] += 1
            else:
                programs.append(rec)
            if done % 250 == 0:
                print(f"    ... {done}/{len(candidates)} screened, {len(programs)} usable "
                      f"({time.perf_counter() - t0:.0f}s)", flush=True)
    # Deterministic order regardless of completion order.
    programs.sort(key=lambda p: p["program_id"])
    if args.target:
        programs = programs[: args.target]
    stage["with_cases"] = len(programs)
    print(f"  input cases: {len(programs)} programs usable")

    # -- 5. dedup vs test set and vs self --------------------------------- #
    exclude = set()
    ex_cfg = src_cfg.get("exclude_ids") or {}
    for v in (ex_cfg.get("dataset_a") or {}).values():
        exclude.update(v or [])
    test_progs = _test_programs(lang)
    res = dedup_mod.dedup(programs, test_progs, exclude_ids=exclude,
                          threshold=float(data_cfg["dedup"]["jaccard_threshold"]))
    unique = res.kept if hasattr(res, "kept") else res
    stage["deduped"] = len(unique)
    dropped = len(programs) - len(unique)
    print(f"  dedup: {len(unique)} unique ({dropped} dropped vs test set / self / exclusion lists)")

    # -- 6. split by program_id and write --------------------------------- #
    # THREE-way split. `test` programs are never trained on AND never used for
    # checkpoint selection, so they are a clean evaluation set — unlike `val`, which
    # model selection touches and which would therefore bias the diagonal of a
    # transfer matrix (the cell where each adapter is evaluated on its own condition).
    rng = random.Random(int(data_cfg["splits"]["seed"]))
    ids = sorted({p["program_id"] for p in unique})
    rng.shuffle(ids)
    n = len(ids)
    n_val = int(n * float(data_cfg["splits"]["val_fraction"])) if n else 0
    n_test = int(n * float(data_cfg["splits"].get("test_fraction", 0.0))) if n else 0
    if n:  # never let rounding empty a split that was asked for
        n_val = max(1, n_val) if data_cfg["splits"]["val_fraction"] > 0 else 0
        n_test = max(1, n_test) if data_cfg["splits"].get("test_fraction", 0) > 0 else 0
    val_ids = set(ids[:n_val])
    test_ids = set(ids[n_val : n_val + n_test])
    assignment = {
        pid: ("val" if pid in val_ids else "test" if pid in test_ids else "train")
        for pid in ids
    }

    rows = []
    for p in unique:
        # inputs.build_cases returns GeneratedCase dataclasses whose fields match
        # schema.InputCase exactly; dicts pass through for callers that pre-converted.
        cases = [c if isinstance(c, dict) else dataclasses.asdict(c) for c in p["cases"]]
        gates = [c if isinstance(c, dict) else dataclasses.asdict(c) for c in p["gate_inputs"]]
        rows.append(BaseProgram(
            program_id=p["program_id"], language=lang, source=p.get("source", "unknown"),
            provenance=p.get("provenance", "curated"), code=p["code"],
            entry_point=p["entry_point"],
            cases=[InputCase(**c) for c in cases],
            gate_inputs=[InputCase(**c) for c in gates],
            loc=int(p.get("loc", 0)), meta=p.get("meta", {}),
        ).model_dump())

    out = Path(args.out) if args.out else (TRAIN_ROOT / "base" / f"{lang}.jsonl")
    write_jsonl(out, rows)
    SPLITS_ROOT.mkdir(parents=True, exist_ok=True)
    (SPLITS_ROOT / f"{lang}.json").write_text(json.dumps(
        {"seed": int(data_cfg["splits"]["seed"]), "by": "program_id",
         "n_train": sum(1 for v in assignment.values() if v == "train"),
         "n_val": sum(1 for v in assignment.values() if v == "val"),
         "n_test": sum(1 for v in assignment.values() if v == "test"),
         "assignment": assignment}, indent=1))

    report = {
        "language": lang, "tiers": args.tiers, "seed": seed,
        "stages": dict(stage),
        "attrition_reasons": dict(reasons.most_common(30)),
        "dedup": getattr(res, "report", lambda: {})() if callable(getattr(res, "report", None)) else {},
        "n_val": sum(1 for v in assignment.values() if v == "val"),
        "elapsed_s": round(time.perf_counter() - t0, 1),
        "out": str(out),
    }
    MANIFESTS_ROOT.mkdir(parents=True, exist_ok=True)
    (MANIFESTS_ROOT / f"corpus_{lang}.json").write_text(json.dumps(report, indent=1))

    print(f"\n  wrote {len(rows)} programs -> {out}")
    print("  stages: " + " -> ".join(f"{k}={v}" for k, v in stage.items()))
    print(f"  top attrition: {dict(reasons.most_common(6))}")
    print(f"  elapsed {report['elapsed_s']}s")
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
