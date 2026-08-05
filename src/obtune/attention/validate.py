"""Gate for the RQ3 attention layer: class coverage + span->token resolution.

WHY a hard gate: every RQ3 number is a *share of attention on a token class*. If 10% of
the code's characters fall outside the classification, or 10% of classified spans never
reach a token under the real subword tokenizer, the shares are quietly measuring
something else and no downstream statistic can detect it. transcoders/convert_stimuli.py
learned this the expensive way and validated at 1.0; the same check runs here, on the
same tokenizer the pilot uses, and FAILS the run below the threshold rather than
printing a warning nobody reads.

Two numbers are reported per (language, condition):
  * class_coverage       — fraction of non-whitespace characters given a real lexical
                           class (not `other`/unlexed).
  * span_resolution_rate — fraction of classified spans that map to >=1 model token AND
                           whose text appears in the decode of those tokens (the decode
                           check catches BOS shifts and off-by-one offsets).

Run (tokenizer only, no GPU):
    PYTHONPATH=src python -m obtune.attention.validate
    PYTHONPATH=src python -m obtune.attention.validate --model Qwen/Qwen2.5-Coder-7B-Instruct
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from obtune.attention.fixtures import FIXTURES, FixtureProgram
from obtune.attention.metrics import ATTN_DIR, resolve_spans_to_tokens, token_class_assignment
from obtune.attention.token_classes import CLASSES, classify_code
from obtune.config import load_config
from obtune.paths import EVAL_ROOT, iter_jsonl

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
MIN_RATE = 0.98


def _ensure_hf_home() -> None:
    """Point HF at the shared cache before transformers is imported (CLAUDE.md: keep
    weights off $HOME's small NFS mount)."""
    if os.environ.get("HF_HOME"):
        return
    try:
        hf = load_config("compute.yaml").get("paths", {}).get("hf_home")
    except Exception:
        hf = None
    if hf:
        os.environ["HF_HOME"] = str(hf)


def _testset_rows() -> list[FixtureProgram]:
    """Real test-set rows when they exist; embedded ICSE fixtures otherwise."""
    root = EVAL_ROOT / "testset" / "variants"
    rows: list[FixtureProgram] = []
    if root.exists():
        for p in sorted(root.rglob("*.jsonl")):
            for r in iter_jsonl(p):
                rows.append(FixtureProgram(
                    program_id=r.get("program_id", r.get("item_id", "?")),
                    condition=r.get("condition", "?"),
                    tier_icse=r.get("tier_icse") or "",
                    language=r["language"],
                    entry_point=r.get("entry_point", ""),
                    code=r["code"],
                ))
    return rows


def _eval_max_model_len(default: int = 4096) -> int:
    """Match the evaluation context window.

    Truncating here at a different length than eval does makes span resolution
    look broken when it is not: a 168-line S1 variant runs to ~2.5k tokens, so a
    2048 cap silently dropped the tail of the largest flattened program and read
    as a 0.978 resolution failure. Attention metrics must be computed over the
    same token window the accuracy numbers came from.
    """
    try:
        from obtune.config import load_config

        return int((load_config("eval/_base_eval.yaml").get("engine") or {})
                   .get("max_model_len", default))
    except Exception:  # noqa: BLE001 — config problems must not break validation
        return default


EVAL_MAX_MODEL_LEN = _eval_max_model_len()


def validate(
    programs: Sequence[FixtureProgram],
    model_id: str = DEFAULT_MODEL,
    *,
    min_rate: float = MIN_RATE,
    max_length: int = EVAL_MAX_MODEL_LEN,
) -> dict[str, Any]:
    _ensure_hf_home()
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_id)

    per_group: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"n_prog": 0, "spans": 0, "resolved": 0, "cov_num": 0.0, "cov_den": 0.0,
                 "code_tokens": 0, "tokens": 0}
    )
    per_program: list[dict[str, Any]] = []
    class_token_counts: dict[str, int] = {c: 0 for c in CLASSES}

    for prog in programs:
        cls = classify_code(prog.code, prog.language, prog.entry_point or None)
        enc = tok(prog.code, return_offsets_mapping=True, truncation=True,
                  max_length=max_length, add_special_tokens=False)
        offsets = [tuple(map(int, o)) for o in enc["offset_mapping"]]
        spans = [(s.start, s.end) for s in cls.spans if s.base_cls != "other"]
        _, n_res, n_tot = resolve_spans_to_tokens(
            spans, offsets, char_base=0, tokenizer=tok,
            input_ids=enc["input_ids"], code=prog.code,
        )
        tok_cls, code_mask = token_class_assignment(cls, offsets, 0)
        for i, c in enumerate(tok_cls):
            if code_mask[i]:
                class_token_counts[CLASSES[int(c)]] += 1

        nonws = sum(1 for ch in prog.code if not ch.isspace())
        cov = cls.coverage()
        g = per_group[(prog.language, prog.condition)]
        g["n_prog"] += 1
        g["spans"] += n_tot
        g["resolved"] += n_res
        g["cov_num"] += cov * nonws
        g["cov_den"] += nonws
        g["code_tokens"] += int(code_mask.sum())
        g["tokens"] += len(offsets)

        per_program.append({
            "program_id": prog.program_id, "condition": prog.condition,
            "language": prog.language, "entry_point": prog.entry_point,
            "class_coverage": round(cov, 6),
            "span_resolution_rate": round(n_res / n_tot, 6) if n_tot else None,
            "n_spans": n_tot, "n_tokens": len(offsets),
            "n_code_tokens": int(code_mask.sum()),
            "partition_ok": cls.partition_ok(), "parse_ok": cls.parse_ok,
            "n_slice_names": len(cls.slice_result.critical_names) if cls.slice_result else 0,
            "notes": cls.notes,
        })

    groups = {
        f"{lang}/{cond}": {
            "n_programs": int(v["n_prog"]),
            "class_coverage": round(v["cov_num"] / v["cov_den"], 6) if v["cov_den"] else None,
            "span_resolution_rate": round(v["resolved"] / v["spans"], 6) if v["spans"] else None,
            "n_spans": int(v["spans"]),
            "n_code_tokens": int(v["code_tokens"]),
        }
        for (lang, cond), v in sorted(per_group.items())
    }
    tot_spans = sum(v["spans"] for v in per_group.values())
    tot_res = sum(v["resolved"] for v in per_group.values())
    tot_cov_n = sum(v["cov_num"] for v in per_group.values())
    tot_cov_d = sum(v["cov_den"] for v in per_group.values())
    overall_rate = tot_res / tot_spans if tot_spans else 0.0
    overall_cov = tot_cov_n / tot_cov_d if tot_cov_d else 0.0

    failures: list[str] = []
    if overall_rate < min_rate:
        failures.append(f"overall span_resolution_rate {overall_rate:.4f} < {min_rate}")
    if overall_cov < min_rate:
        failures.append(f"overall class_coverage {overall_cov:.4f} < {min_rate}")
    for k, g in groups.items():
        if g["span_resolution_rate"] is not None and g["span_resolution_rate"] < min_rate:
            failures.append(f"{k}: span_resolution_rate {g['span_resolution_rate']:.4f} < {min_rate}")
        if g["class_coverage"] is not None and g["class_coverage"] < min_rate:
            failures.append(f"{k}: class_coverage {g['class_coverage']:.4f} < {min_rate}")
    bad_part = [p["program_id"] + "/" + p["condition"] for p in per_program if not p["partition_ok"]]
    if bad_part:
        failures.append(f"{len(bad_part)} programs whose class spans do not tile the source: {bad_part[:5]}")

    return {
        "model_id": model_id,
        "min_rate": min_rate,
        "n_programs": len(programs),
        "overall": {
            "class_coverage": round(overall_cov, 6),
            "span_resolution_rate": round(overall_rate, 6),
            "n_spans": tot_spans,
        },
        "by_language_condition": groups,
        "code_token_class_counts": class_token_counts,
        "per_program": per_program,
        "failures": failures,
        "passed": not failures,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate token classification + span resolution")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--min-rate", type=float, default=MIN_RATE)
    ap.add_argument("--out", default=str(ATTN_DIR / "span_validation.json"))
    ap.add_argument("--fixtures-only", action="store_true",
                    help="ignore data/eval/testset even if it exists")
    args = ap.parse_args(argv)

    rows = [] if args.fixtures_only else _testset_rows()
    source = "data/eval/testset/variants"
    if not rows:
        rows = list(FIXTURES)
        source = "obtune.attention.fixtures (embedded ICSE stimuli)"
    print(f"validating {len(rows)} programs from {source} with tokenizer {args.model}")

    rep = validate(rows, args.model, min_rate=args.min_rate)
    rep["source"] = source
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2))

    for k, g in rep["by_language_condition"].items():
        print(f"  {k:<26} n={g['n_programs']:<3} coverage={g['class_coverage']:.4f} "
              f"span_resolution={g['span_resolution_rate']:.4f} ({g['n_spans']} spans)")
    o = rep["overall"]
    print(f"  {'OVERALL':<26} coverage={o['class_coverage']:.4f} "
          f"span_resolution={o['span_resolution_rate']:.4f} ({o['n_spans']} spans)")
    print(f"  code-token class counts: {rep['code_token_class_counts']}")
    print(f"report -> {out}")

    if rep["failures"]:
        for f in rep["failures"]:
            print(f"  [FAIL] {f}")
        raise SystemExit(f"attention span validation FAILED ({len(rep['failures'])} check(s))")
    print("SPAN VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
