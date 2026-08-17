#!/usr/bin/env python
"""Build the L0-merge control: N random-seed clean-code adapters, merged.

    python scripts/merge/23_l0_control.py --plan     # what it would merge, no work
    python scripts/merge/23_l0_control.py            # build ties + dare_ties

THE CONTROL NOBODY HAS RUN
--------------------------
`merge_dare_ties` reaches .348 on H1. `tuned_L0` — one adapter, trained on clean code, no
obfuscation exposure at all — also reaches .348, on byte-identical items. Nothing currently
in the project distinguishes:

  1. merging six obfuscation specialists recovers clean-code-level competence, from experts
     that individually do much worse on H1; or
  2. merging any N adapters regresses toward the clean-code model, and the specialists'
     obfuscation-specific learning contributed nothing at all.

Reading 2 is the null hypothesis for the entire RQ2 merge result and it has never been
tested. Merging three adapters that are ALL `L0`-trained isolates it: whatever a merge does
to N adapters, this arm does it to N adapters with no obfuscation knowledge between them.

  - If the L0-merge lands near .348, reading 2 holds. The merge headline becomes "merging
    regresses toward the control", merge tuning is not worth GPU time, and §5 must be
    rewritten.
  - If it lands clearly below, the specialists ARE contributing and merge improvement is a
    real target.

That is why this gates the merge-improvement work rather than following it.

WHY THREE
---------
Two adapters make TIES sign-election degenerate — every disagreement is a tie with no
majority. Three is the smallest bank where the election does something. It is NOT matched
to the six-expert real merges, and that is a stated limitation of the 3-seed version rather
than something the numbers hide: expert count is a live confound between this control and
`merge_dare_ties`, and the honest comparison is against a 3-expert specialist merge if one
is ever built.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import RUNS_DIR, load_config  # noqa: E402
from obtune.merge_adapters import MERGE_ROOT, MergeSpec, merge_adapters  # noqa: E402
from obtune.provenance import RunManifest  # noqa: E402

SEEDS = [17, 42, 101]
MODEL, LANG, RANK = "qwen25c-1.5b", "python", 32
# Same two the real RQ2 comparison reports. `dare_linear` is excluded: it is the arm that
# collapsed to a magnitude artifact (§5.2) and its repaired form `dl_rescaled` is a
# separate question from this control.
COMBINATIONS = ["ties", "dare_ties"]


def adapter_paths() -> dict[str, str]:
    """`L0__s<seed>` keys: PEFT adapter names AND the quarantine guard's input, which
    `merge_adapters.base_condition` reduces back to `L0` before validating."""
    out: dict[str, str] = {}
    for s in SEEDS:
        p = RUNS_DIR / "adapters" / MODEL / LANG / f"L0_r{RANK}_s{s}" / "best"
        out[f"L0__s{s}"] = str(p)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print what would be merged and exit")
    ap.add_argument("--dtype", default="float32")
    args = ap.parse_args(argv)

    paths = adapter_paths()
    missing = {k: p for k, p in paths.items() if not Path(p).exists()}
    if args.plan or missing:
        for k, p in paths.items():
            print(f"  {k:12s} {'OK  ' if Path(p).exists() else 'MISS'} {p}")
    if missing:
        # A merge over 2 of 3 adapters would silently produce a DIFFERENT experiment
        # (and a degenerate sign election) while reporting success.
        print(f"\nrefusing to merge: {len(missing)} adapter(s) absent — "
              f"train them first ({', '.join(missing)})", file=sys.stderr)
        return 1
    if args.plan:
        print(f"\nwould build {len(COMBINATIONS)} merges: {', '.join(COMBINATIONS)}")
        return 0

    cfg = load_config("merge/l0_control.yaml")
    base_id = load_config("models.yaml")["models"][MODEL]["hf_id"]
    for comb in COMBINATIONS:
        spec = MergeSpec(
            base_model_id=base_id, adapter_paths=paths, combination_type=comb,
            density=float(cfg["density"]), weights=cfg.get("weights"),
            seed=int(cfg.get("seed", 17)),
        )
        out_dir = MERGE_ROOT / f"{MODEL}_{LANG}_l0control_{comb}" / "d0p5"
        mani = RunManifest(
            experiment="l0_merge_control", run_id=f"l0control_{comb}",
            seed=spec.seed, config_path=str(cfg["_config_path"]),
            config_resolved={**cfg, "combination_type": comb, "adapter_paths": paths,
                             "seeds_merged": SEEDS},
            model_hf_id=base_id,
        ).hash_scripts(["src/obtune/merge_adapters.py", "scripts/merge/23_l0_control.py"]).capture_git()
        p = merge_adapters(spec, out_dir, dtype=args.dtype)
        mani.extra["merges"] = [{"density": spec.density, "path": str(p),
                                 "combination_type": comb}]
        mani.finalize().write(out_dir)
        print(f"  {comb:10s} -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
