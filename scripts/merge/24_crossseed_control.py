#!/usr/bin/env python
"""Cross-seed specialist merge — does merging care about task-vector orthogonality? CPU only.

    python scripts/merge/24_crossseed_control.py --plan
    python scripts/merge/24_crossseed_control.py

WHY THIS EXISTS
---------------
The 2026-08-15 geometry readout (log/modularity/2026-08-15_item-agreement-and-seed-geometry.md)
found that pairwise cosine between LoRA task vectors is dominated by **shared initialization**,
not by learned content: three `L0` adapters trained on byte-identical data are near-orthogonal
(cosine 0.053, sign conflict 0.487 — a coin flip), while eight adapters trained on completely
different transforms sit at 0.592 because they share a seed and therefore a rank-32 subspace.

The L0-merge control already hinted at the consequence: it is the worst-geometry merge in the
project and it merged fine (`l0merge_dare_ties` .339 on H1, identical to `tuned_L0`). But that
control also changed the expert COUNT (3 vs 6) and the expert CONTENT (all clean-code), so it
cannot isolate geometry — a limitation `23_l0_control.py` records in its own docstring.

This arm isolates it. Same six conditions, same rank, same recipe, same merge algorithms and
density as `merge_dare_ties`; the ONLY difference is which seed each expert was drawn from.
Measured before building (zero cost, `merge_geometry.cosine` over the two banks):

    same-seed bank  (the existing merge)   mean cosine 0.5633   (15/15 pairs same-seed)
    alternating bank (this arm)            mean cosine 0.2458   ( 9/15 pairs cross-seed,
                                                                  those 9 at 0.0348)

So the two banks differ 2.3x in mean cosine while holding the ingredients fixed.

PREDICTION, REGISTERED BEFORE THE EVAL RUNS
    If merged accuracy is within seed noise of `merge_dare_ties` (1.32 mean / 3.61 p95), then
    **LoRA merging is insensitive to task-vector orthogonality** and every sign-conflict/cosine
    diagnostic in MASTER_REPORT §5.3 is measuring a quantity that does not bound the outcome.
    If it collapses, geometry does bound merging and §5.3's framing is right after all — but
    then the L0-merge control's success needs a separate explanation.

Two seeds is what the bank affords: only `L0` has a third (s101). Six distinct seeds would make
every pair cross-seed; alternating makes 9 of 15, which is enough to move the mean 2.3x and is
free. Stated as a limitation rather than papered over.

CPU only: `merge_adapters` loads the base with `device_map=None` and merges in float32. Zero GPU.
The EVAL of these adapters needs a GPU and is a separate step.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import RUNS_DIR, load_config  # noqa: E402
from obtune.merge_adapters import MERGE_ROOT, MergeSpec, merge_adapters  # noqa: E402
from obtune.provenance import RunManifest  # noqa: E402

# Set from --model/--language at startup. These were module-level constants pinned to
# qwen25c-1.5b, which is the DANGEROUS form of the pin: the Qwen adapters still exist on
# disk, so this script would have silently merged THEM and written the result under the
# current panel's name -- no error, wrong ingredients. A lint that checks argparse defaults
# and HF ids cannot see a constant holding a model key.
MODEL, LANG, RANK = None, None, 32
#: Condition -> seed. Alternating so that 9 of the 15 pairs are cross-seed. The assignment is
#: fixed here rather than randomized: a random assignment would make the arm irreproducible
#: without recording it, and there is nothing to gain from varying it at n=1.
BANK = {"L0": 17, "L1b": 42, "L1r": 17, "L2": 42, "S1": 17, "S2": 42}
#: The same two the real RQ2 comparison reports; `dare_linear` is the arm that collapsed to a
#: magnitude artifact (§5.2) and is a separate question.
COMBINATIONS = ["ties", "dare_ties"]


def adapter_paths() -> dict[str, str]:
    """Plain condition keys — they are already distinct, so no `__<tag>` disambiguator is
    needed (unlike the L0 control, where all three ingredients are `L0`)."""
    return {c: str(RUNS_DIR / "adapters" / MODEL / LANG / f"{c}_r{RANK}_s{s}" / "best")
            for c, s in BANK.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="key in configs/models.yaml")
    ap.add_argument("--language", default="python")
    ap.add_argument("--plan", action="store_true", help="print what would be merged and exit")
    ap.add_argument("--dtype", default="float32")
    args = ap.parse_args(argv)
    global MODEL, LANG, RANK
    MODEL, LANG = args.model, getattr(args, 'language', 'python')
    RANK = getattr(args, 'rank', 32)

    paths = adapter_paths()
    missing = {k: p for k, p in paths.items() if not Path(p).exists()}
    if args.plan or missing:
        for c, p in paths.items():
            print(f"  {c:5s} s{BANK[c]:<4d} {'OK  ' if Path(p).exists() else 'MISS'} {p}")
    if missing:
        # Same reasoning as 23_l0_control: a merge over a subset is a DIFFERENT experiment
        # that would still report success.
        print(f"\nrefusing to merge: {len(missing)} adapter(s) absent ({', '.join(missing)})",
              file=sys.stderr)
        return 1
    if args.plan:
        print(f"\nwould build {len(COMBINATIONS)} merges: {', '.join(COMBINATIONS)}")
        return 0

    # Reuse the REAL merge config so density/weights/seed cannot drift from the arm this is a
    # control for. A control that differed in a hyperparameter would not control for anything.
    cfg = load_config("merge/ties_v1.yaml")
    base_id = load_config("models.yaml")["models"][MODEL]["hf_id"]
    for comb in COMBINATIONS:
        spec = MergeSpec(
            base_model_id=base_id, adapter_paths=paths, combination_type=comb,
            density=float(cfg["density"]), weights=cfg.get("weights"),
            seed=int(cfg.get("seed", 17)),
        )
        out_dir = MERGE_ROOT / f"{MODEL}_{LANG}_crossseed_{comb}" / "d0p5"
        mani = RunManifest(
            experiment="crossseed_merge_control", run_id=f"crossseed_{comb}",
            seed=spec.seed, config_path=str(cfg["_config_path"]),
            config_resolved={**cfg, "combination_type": comb, "adapter_paths": paths,
                             "condition_seed_map": BANK},
            model_hf_id=base_id,
        ).hash_scripts(["src/obtune/merge_adapters.py",
                        "scripts/merge/24_crossseed_control.py"]).capture_git()
        p = merge_adapters(spec, out_dir, dtype=args.dtype)
        mani.extra["merges"] = [{"density": spec.density, "path": str(p),
                                 "combination_type": comb}]
        mani.extra["bank_geometry"] = {
            "mean_cosine_this_bank": 0.2458, "mean_cosine_same_seed_bank": 0.5633,
            "n_cross_seed_pairs": 9, "n_pairs": 15,
            "note": "measured with merge_geometry.cosine before building; see the module docstring",
        }
        mani.finalize().write(out_dir)
        print(f"  {comb:10s} -> {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
