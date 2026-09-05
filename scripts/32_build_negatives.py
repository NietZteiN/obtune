#!/usr/bin/env python
"""Build the verified-negatives corpus for the `negatives` objective (obtune.objectives).

    python scripts/32_build_negatives.py --conditions L0 L1b L1r L2 S1 S2 --workers 32

For every (program, condition) TRAIN group in data/train/pairs/<cond>/python.jsonl:
  1. propose up to --n-mutants single-operator mutants (cft/mutate.py: AOR/ROR/LCR/ICR);
  2. execute the PARENT and each mutant on every case of the group (exec/pool.run_batch);
  3. keep the first mutant whose parent reproduces the gold on all cases, which runs ok on
     >= --min-ok-frac of the cases, and which DIFFERS from the gold on at least one case;
  4. emit ONE NegativePair for that mutant's first differing case:
        code            = mutant code
        output_repr     = the mutant's TRUE output          (positive twin)
        orig_output_repr= the parent's gold on that case    (what unlikelihood pushes down)

The mutation is applied to the CONDITION's surface (the obfuscated code), not to the L0
parent, so the negative and its positive twin share the surface the model is trained on.
Output goes under data/train/negatives/<cond>/python.jsonl -- inside TRAIN_ROOT, so
`paths.load_training_jsonl` and the manifest/H1-marker scan cover it like any other
training file. Rebuild the manifest afterwards (scripts/build_manifest.py).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune import data  # noqa: E402
from obtune.cft import mutate  # noqa: E402
from obtune.exec.pool import BatchItem, run_batch  # noqa: E402
from obtune.objectives import NegativePair, negatives_path  # noqa: E402
from obtune.paths import write_jsonl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conditions", nargs="+", default=["L0", "L1b", "L1r", "L2", "S1", "S2"])
    ap.add_argument("--language", default="python")
    ap.add_argument("--n-mutants", type=int, default=8)
    ap.add_argument("--min-ok-frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=32)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--limit", type=int, default=None, help="groups per condition (smoke)")
    args = ap.parse_args()

    for cond in args.conditions:
        t0 = time.time()
        rows = data.load_pairs([cond], args.language, splits=["train"])
        groups: dict[str, list] = defaultdict(list)
        for r in rows:
            groups[r.program_id].append(r)
        keys = sorted(groups)[: args.limit] if args.limit else sorted(groups)
        stats = {"groups": len(keys), "no_candidates": 0, "parent_mismatch": 0,
                 "no_verified": 0, "kept": 0, "families": defaultdict(int)}

        # One batch: parent + all mutants for every group, executed on the group's cases.
        items, index = [], []  # index[i] = (program_id, mutant_or_None)
        muts: dict[str, list[mutate.Mutant]] = {}
        for pid in keys:
            g = groups[pid]
            ms = mutate.propose(pid, args.language, g[0].code, g[0].entry_point, args.n_mutants, args.seed)
            if not ms:
                stats["no_candidates"] += 1
                continue
            muts[pid] = ms
            argv = [r.args_repr for r in g]
            items.append(BatchItem(f"{pid}::parent", args.language, g[0].code, g[0].entry_point, argv))
            index.append((pid, None))
            for k, m in enumerate(ms):
                items.append(BatchItem(f"{pid}::mut{k}", args.language, m.code, m.entry_point, argv))
                index.append((pid, k))
        print(f"[{cond}] executing {len(items)} programs over {len(muts)} groups ...", flush=True)
        results = run_batch(items, timeout_s=2.0, mem_mb=512, workers=args.workers)
        by_key = {(pid, k): res for (pid, k), res in zip(index, results)}

        out: list[dict] = []
        for pid, ms in muts.items():
            g = groups[pid]
            par = by_key[(pid, None)]
            if not (par.child_status == "ok" and len(par.cases) == len(g)
                    and all(c.ok and c.output == r.output_repr for c, r in zip(par.cases, g))):
                stats["parent_mismatch"] += 1
                continue
            chosen = None
            for k, m in enumerate(ms):
                res = by_key[(pid, k)]
                if res.child_status != "ok" or len(res.cases) != len(g):
                    continue
                n_ok = sum(c.ok for c in res.cases)
                if n_ok < args.min_ok_frac * len(g):
                    continue
                diff = [i for i, (c, r) in enumerate(zip(res.cases, g)) if c.ok and c.output != r.output_repr]
                if not diff:
                    continue
                m.n_cases_checked, m.n_cases_ok, m.n_cases_differing, m.verified = len(g), n_ok, len(diff), True
                chosen = (m, diff[0], res.cases[diff[0]].output)
                break
            if chosen is None:
                stats["no_verified"] += 1
                continue
            m, i, mut_out = chosen
            r = g[i]
            rec = NegativePair(
                item_id=f"{r.item_id}::mut", program_id=r.program_id, program_group_id=r.program_group_id,
                condition=r.condition, language=r.language, code=m.code, entry_point=r.entry_point,
                args_repr=r.args_repr, output_repr=mut_out, split=r.split, provenance="synthetic",
                parent_item_id=r.item_id, orig_output_repr=r.output_repr, mutation=m.as_meta(),
            )
            out.append(rec.model_dump())
            stats["kept"] += 1
            stats["families"][m.candidate.family] += 1
        p = write_jsonl(negatives_path(cond, args.language), out)
        stats["families"] = dict(stats["families"])
        stats["elapsed_s"] = round(time.time() - t0, 1)
        print(f"[{cond}] wrote {len(out)} -> {p}\n  {json.dumps(stats)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
