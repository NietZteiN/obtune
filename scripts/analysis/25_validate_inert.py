#!/usr/bin/env python
"""SOUNDNESS GATE for the `inert` normalize profile: normalizing must not change behaviour.

`normalize(profile="inert")` claims that everything it deletes is code that cannot affect the
result. That claim is a static analysis, and a static analysis that is subtly wrong would not
announce itself — it would quietly hand the model a program with a piece of the computation
removed, and the accuracy drop would be read as "normalization does not help" rather than
"normalization broke the program". So the claim is checked the only way that settles it: delete
the code, RUN both versions on the program's own real cases, and require the outputs to match
under the project's own execution gate (`exec.pool`, same runner, timeout and canonicalizer used
to build the corpus in the first place).

This is one-sided by design. A pass here means the profile did not change behaviour on these
programs; it is not a proof of soundness in general. A single failure, though, is decisive, and
that asymmetry is what makes the gate worth running before the profile is used for anything.

Usage:
    python scripts/analysis/25_validate_inert.py [--conditions S2 S3 S4 L0] [--per-cond 120]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from obtune.exec.pool import BatchItem, run_batch          # noqa: E402
from obtune.normalize import normalize                      # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", nargs="*", default=["S2", "S3", "S4", "L0", "S1", "L1r"])
    ap.add_argument("--per-cond", type=int, default=120)
    ap.add_argument("--profile", default="inert")
    ap.add_argument("--language", default="python")
    args = ap.parse_args()

    failures = 0
    for cond in args.conditions:
        path = Path("data/train/pairs") / cond / f"{args.language}.jsonl"
        if not path.exists():
            print(f"{cond:5s} SKIP (no corpus at {path})")
            continue

        cases: dict[str, list[str]] = defaultdict(list)
        order: list[dict] = []
        with path.open() as fh:
            for line in fh:
                r = json.loads(line)
                if r["program_id"] not in cases and len(order) < args.per_cond:
                    order.append(r)
                cases[r["program_id"]].append(r["args_repr"])

        before, after = [], []
        for r in order:
            out = normalize(r["code"], args.language,
                            entry_point=r["entry_point"], profile=args.profile)
            if out.code == r["code"]:
                continue                      # profile was a no-op here; nothing to check
            a = cases[r["program_id"]]
            before.append(BatchItem(r["program_id"], args.language, r["code"], r["entry_point"], a))
            after.append(BatchItem(r["program_id"], args.language, out.code, r["entry_point"], a))

        if not before:
            print(f"{cond:5s} profile never fired on {len(order)} programs — nothing to verify")
            continue

        pa = {p.program_id: p for p in run_batch(before, workers=32)}
        pb = {p.program_id: p for p in run_batch(after, workers=32)}
        agree = mismatch = unusable = 0
        bad: list[tuple[str, str]] = []
        for pid, a in pa.items():
            b = pb.get(pid)
            if b is None or not a.all_ok:
                unusable += 1                 # original does not run cleanly: nothing to compare
                continue
            if not b.all_ok:
                mismatch += 1
                bad.append((pid, f"normalized program failed to run ({b.child_status})"))
            elif all(x.matches(y) for x, y in zip(a.cases, b.cases)):
                agree += 1
            else:
                mismatch += 1
                bad.append((pid, "different output"))
        failures += mismatch
        verdict = "OK " if mismatch == 0 else "FAIL"
        print(f"{cond:5s} {verdict} fired on {len(before):3d}/{len(order)} programs   "
              f"exec-parity {agree}/{agree + mismatch}   (skipped {unusable} whose original "
              f"does not run)")
        for pid, why in bad[:5]:
            print(f"          !! {pid}: {why}")

    print("\nSOUNDNESS GATE:", "PASS" if failures == 0 else f"FAIL ({failures} mismatches)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
