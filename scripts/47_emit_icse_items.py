#!/usr/bin/env python
"""E10 — materialize the legacy Papers-1/3 tier rows as EvalItems, so the human baselines
can be compared against the models on the SAME items. NEVER trainable.

WHY THIS EXISTS. `docs/TIER_MAPPING.md` and CLAUDE.md §3.1: 350 byte-identical rows (70 programs
× 5 legacy tiers, 200 Python / 150 JavaScript) are the only rows comparable to the Paper-2 human
study. They live in a SEPARATE namespace because tier semantics differ per language, and this
script keeps them there — the emitted label is `T_<tier>` (schema.TierCondition), which is not a
ladder code and cannot be passed to anything on the training path.

The rows already carry gold I/O (`input`, `expected_output`) from the human study, so nothing is
re-executed: the gold here is the *same string the human participants were graded against*, which
is the whole point. `input` is a JSON argument array and becomes the `args_repr` tuple the prompt
builder expects.

Writes data/eval/testset/items/T_<tier>/<language>.jsonl. Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune.schema import EvalItem  # noqa: E402
from obtune.testset import ingest  # noqa: E402

SRC = ROOT / "data" / "eval" / "testset" / "legacy_icse"
DST = ROOT / "data" / "eval" / "testset" / "items"
TIERS = ["L0", "L1", "L1b", "L2", "L3"]


def args_repr_from(inp: str, code: str, language: str) -> tuple[str | None, str | None]:
    """The study stored the input in THREE formats and all three appear in these 350 rows:
    a JSON argument array (`[14]`), a Python-literal array (`['world']`), and a call expression
    (`myFunct([1, 3, 5, 0])`, including keyword form in the LeetCode rows). Rather than reinvent
    the parsing, reuse `testset.ingest`, which already solved exactly this for the same corpus —
    `_call_parts` resolves keywords against the callee's real signature, `_args_from_array_literal`
    handles the array forms. Returns (args_repr, callee_or_None).

    prompts.format_call wants a Python tuple literal; a 1-tuple needs its trailing comma."""
    text = inp.strip()
    callee, args = ingest._call_parts(text, code, language)
    if args is not None:
        return args, callee
    arr = ingest._args_from_array_literal(text)
    if arr is not None:
        return arr, None
    try:                                     # last resort: a bare JSON array
        vals = json.loads(text)
        vals = vals if isinstance(vals, list) else [vals]
        inner = ", ".join(repr(v) for v in vals)
        return (f"({inner},)" if len(vals) == 1 else f"({inner})"), None
    except Exception:
        return None, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    rows = [json.loads(l) for f in ("dataset_a", "dataset_b")
            for l in (SRC / f"{f}.jsonl").open()]
    print(f"read {len(rows)} legacy rows from {SRC}")

    out: dict[tuple[str, str], list[dict]] = {}
    bad = 0
    for r in rows:
        tier, lang = r["tier_icse"], r["language"]
        args, callee = args_repr_from(r["input"], r["code"], lang)
        if args is None:
            print(f"  SKIP {r['task_id']} {tier}: cannot parse input {r['input']!r}", file=sys.stderr)
            bad += 1
            continue
        # The stored callee is a placeholder in Dataset B ("myFunct"); the code's own definition
        # wins, exactly as in ingest, or the prompt would name a function that does not exist.
        entry = ingest._entry_from_code(r["code"], lang) or callee or r["fn_name"]
        try:
            item = EvalItem(
                item_id=f"{r['task_id']}::T_{tier}::0",
                program_id=r["task_id"],
                dataset=r["dataset"],
                condition=f"T_{tier}",
                language=lang,
                code=r["code"],
                entry_point=entry,
                args_repr=args,
                output_repr=str(r["expected_output"]),
                case_role="human",
                tier_icse=tier,
                meta={"source": "legacy_icse", "dataset_source": r.get("dataset_source"),
                      "question_number": r.get("question_number"),
                      "source_sha256": r.get("source_sha256"), "fn_name_stored": r.get("fn_name"),
                      "input_raw": r["input"],
                      # the human study's own tag, so the E10 join needs no re-derivation
                      "human_question_tag": f"{r['task_id']}_{tier}"},
            )
        except Exception as e:
            print(f"  SKIP {r['task_id']} {tier}: {type(e).__name__}: {e}", file=sys.stderr)
            bad += 1
            continue
        out.setdefault((f"T_{tier}", lang), []).append(item.model_dump())

    print(f"{'would write' if a.dry_run else 'writing'} {len(out)} files, {sum(map(len, out.values()))} items"
          f"{f' ({bad} skipped)' if bad else ''}")
    for (cond, lang), items in sorted(out.items()):
        p = DST / cond / f"{lang}.jsonl"
        langs = Counter(i["language"] for i in items)
        print(f"  {p.relative_to(ROOT)}  {len(items):>4} items  {dict(langs)}")
        if not a.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w") as fh:
                for i in items:
                    fh.write(json.dumps(i) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
