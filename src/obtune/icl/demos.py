"""In-context demonstrations for the ICL baseline — quarantine-safe by construction.

THE RULE THIS MODULE EXISTS TO ENFORCE
--------------------------------------
CLAUDE.md §3.2 rule 2 forbids using `H1` for "training, hyperparameter or **prompt selection**".
An in-context demonstration IS prompt conditioning, so an `H1` demo would breach the quarantine
and make every `H1` number in the project contestable — including the merge result, which is the
project's strongest positive.

It is also not the real scenario. A genuinely new obfuscator means you have NO examples of it, so
"matched-condition ICL on a held-out transform" is impossible for a practitioner too.

So demos are drawn only from TRAINABLE conditions, via `data.load_pairs` (the single training-read
entry point, which raises `QuarantineViolation` on H1). `pick_demos` refuses an H1 source outright
rather than relying on that downstream check, because defence in depth is the §3.2 design.

WHAT THE ARMS MEAN
------------------
* `cross`  — demos from trainable conditions, query on `H1`. The real OOD test: do examples of
  transforms the model HAS seen help on one it has not? Directly comparable to the adapter arms,
  which get the same information as weights rather than as context.
* `matched` — demos from the query's own condition. In-distribution reference only.
* `clean`  — demos from `L0`. Isolates "examples of the task" from "examples of the transform".
"""
from __future__ import annotations

import random
from typing import Optional, Sequence

from obtune.prompts import Demo

HELD_OUT = "H1"

# Demo pool, grouped by program and cached per (language, source conditions).
#
# WHY THIS CACHE IS NOT A MICRO-OPTIMISATION
# ------------------------------------------
# `pick_demos` is called once PER EVALUATION ITEM (`eval_vllm._icl_demos` inside
# `render_prompts`). Before this, every one of those calls re-ran
# `data.load_pairs(...)` — which opens one JSONL per source condition and constructs a
# pydantic `TrainPair` for every row in it. With 5 source conditions (~31k train rows) and
# a Grid A cell of 1,658 items that is ~51 MILLION model constructions to choose 1,658
# demos, single-threaded, before a single token is generated.
#
# It went unnoticed because `cell_meta.elapsed_s` times GENERATION only — prompt rendering
# happens before the timer starts, so the Grid B ICL cells reported ~1 s while spending
# minutes here. On Grid A (10x the items) it turned a ~15-minute job into hours and stalled
# the pipeline at 0 % GPU utilisation with the process pinned at 98 % CPU.
#
# DETERMINISM IS PRESERVED EXACTLY, which is the only thing that matters for a cache in
# this position. The previous code filtered the rows, grouped the survivors by program, and
# sampled from `sorted(by_prog)`. Excluding a program removes it wholesale, so
# `sorted(all_pids) - excl` is element-for-element identical to the old `sorted(by_prog)`,
# and `by_prog[pid]` is untouched for every pid that survives. Same seed, same candidate
# sequence, same draw — verified against the pre-cache implementation, not assumed.
_POOL_CACHE: dict[tuple[str, tuple[str, ...]], tuple[dict[str, list], list[str]]] = {}


def _demo_pool(language: str, source_conditions: tuple[str, ...]):
    """`(by_program, sorted_program_ids)` for a demo source, loaded at most once."""
    key = (language, source_conditions)
    hit = _POOL_CACHE.get(key)
    if hit is not None:
        return hit
    from obtune import data

    rows = data.load_pairs(list(source_conditions), language, splits=("train",))
    by_prog: dict[str, list] = {}
    for r in rows:
        by_prog.setdefault(r.program_id, []).append(r)
    val = (by_prog, sorted(by_prog))
    _POOL_CACHE[key] = val
    return val


def clear_demo_pool_cache() -> None:
    """Drop the cached pools. For tests that rewrite the training pairs on disk."""
    _POOL_CACHE.clear()


def pick_demos(
    language: str,
    k: int,
    source_conditions: Sequence[str],
    *,
    exclude_program_ids: Optional[set[str]] = None,
    seed: int = 17,
) -> list[Demo]:
    """`k` demonstrations from `source_conditions`, deterministic under `seed`.

    `exclude_program_ids` must carry the evaluation program so a demo can never be the item
    being scored — the in-context analogue of split leakage (CLAUDE.md §4 silent-failure #1),
    and it would inflate exactly the cells the baseline exists to measure.
    """
    if HELD_OUT in source_conditions:
        raise ValueError(
            f"{HELD_OUT} may not be used as an in-context demo: a demo is prompt "
            f"conditioning, which CLAUDE.md §3.2 rule 2 forbids for the held-out family. "
            f"For the OOD arm use trainable conditions as the source and H1 only as the QUERY."
        )
    if k <= 0:
        return []

    by_prog, all_pids = _demo_pool(language, tuple(source_conditions))
    excl = exclude_program_ids or set()
    pids = [p for p in all_pids if p not in excl] if excl else all_pids
    if not pids:
        raise ValueError(f"no demo candidates for {source_conditions}/{language}")

    rng = random.Random(seed)
    # Sample distinct PROGRAMS, not rows: several rows share a program, and repeating one
    # program k times is a weaker prompt than k different programs.
    chosen = rng.sample(pids, min(k, len(pids)))
    out: list[Demo] = []
    for pid in chosen:
        r = rng.choice(by_prog[pid])
        out.append(Demo(program_id=r.program_id, language=r.language, condition=r.condition,
                        code=r.code, entry_point=r.entry_point, args_repr=r.args_repr,
                        output_repr=r.output_repr, provenance="icl/demos.pick_demos"))
    return out


__all__ = ["pick_demos", "HELD_OUT"]
