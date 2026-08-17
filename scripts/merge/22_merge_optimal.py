#!/usr/bin/env python
"""Choose each expert's checkpoint to maximise MERGED accuracy (Part V, Stage 2).

    python scripts/merge/22_merge_optimal.py --plan          # emit the search plan, no GPU
    python scripts/merge/22_merge_optimal.py --round 1 --enqueue
    python scripts/merge/22_merge_optimal.py --collect       # read results, pick the winner

THE OBJECTIVE THIS CHANGES
--------------------------
`eval_vllm.run_ckpt_select` picks `best` by held-in validation accuracy — each expert's
INDIVIDUAL optimum. Horoi, Wolf, Belilovsky & Dziugaite (arXiv:2506.14126v2) identify exactly
that objective as harmful to merging, and recommend *task-dependent aggressive early stopping*
instead. Every merge in this project is built from `best`, so the recommendation has never been
tested here.

This searches the other objective directly: hold seven experts fixed, sweep the eighth over its
epochs, keep whichever epoch maximises the MERGED accuracy, repeat. Greedy and order-dependent,
which is stated rather than hidden — the plan records the sweep order and a second pass over
the same order is what tests whether it converged.

WHY IT WAITS FOR THE 8-EXPERT BANK
----------------------------------
Sign conflict is a pairwise statistic: 3 experts give 3 pairs, 8 give 28. A merge-optimal
search over the current 3-expert overtrain bank would produce a number nobody should trust,
which is why the pipeline puts `t2_overtrain` ahead of this stage.

COST is eval-bound, not merge-bound: a merge is ~0.4 min, an eval cell 3-6 min. One round over
E experts x K epochs is E*K evaluations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import CONFIG_DIR, RUNS_DIR, load_config  # noqa: E402
from obtune.merge_adapters import MERGE_ROOT, MergeSpec, merge_adapters  # noqa: E402

STATE = RUNS_DIR / "merges" / "merge_optimal" / "state.json"


def epoch_checkpoints(adapter: Path) -> list[str]:
    steps = sorted(int(p.name.split("-")[1]) for p in adapter.glob("checkpoint-*"))
    return [f"checkpoint-{s}" for s in steps]


def _bank(root: Path, model: str, lang: str, conds: list[str], rank: int, seed: int):
    out = {}
    for c in conds:
        d = root / model / lang / f"{c}_r{rank}_s{seed}"
        cks = epoch_checkpoints(d)
        if cks:
            out[c] = (d, cks)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="runs/adapters_overtrain")
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--conditions", nargs="*",
                    default=["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"])
    ap.add_argument("--combination-type", default="dare_ties",
                    help="dare_ties is the strongest merge measured here; ties collapses to "
                         "0.19x the exact mixture and dare_linear is a 7.175x scale artifact")
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--plan", action="store_true", help="print the search plan and exit")
    ap.add_argument("--enqueue", action="store_true")
    ap.add_argument("--collect", action="store_true", help="score the finished round")
    args = ap.parse_args()

    root = ROOT / args.root
    bank = _bank(root, args.model, args.language, args.conditions, args.rank, args.seed)
    if len(bank) < 2:
        raise SystemExit(
            f"merge-optimal selection needs >=2 experts with checkpoints under {root}; "
            f"found {sorted(bank)}. Run the overtraining probe first.")

    # Incumbent: the LAST epoch of each expert, i.e. the accuracy-optimal end point. The search
    # only means something as a departure from a stated starting point.
    state_path = STATE
    if state_path.exists():
        state = json.loads(state_path.read_text())
    else:
        state = {"incumbent": {c: len(cks) for c, (_, cks) in sorted(bank.items())},
                 "order": sorted(bank), "history": []}

    incumbent = state["incumbent"]
    order = [c for c in state["order"] if c in bank]

    print(f"[merge-opt] {len(bank)} experts, combination={args.combination_type}")
    print(f"[merge-opt] incumbent epochs: {incumbent}")
    print(f"[merge-opt] sweep order (greedy, order-dependent): {order}")

    sweep_target = order[(args.round - 1) % len(order)]
    cks = bank[sweep_target][1]
    print(f"[merge-opt] round {args.round}: sweeping {sweep_target} over {len(cks)} epochs")

    candidates = []
    for e in range(1, len(cks) + 1):
        pick = dict(incumbent)
        pick[sweep_target] = e
        # The name MUST encode every expert's epoch, not just the swept one. Without the
        # digest, `mo_r1_L1b_e3` means "L1b at 3, everyone else at the incumbent" — and the
        # incumbent MOVES as the search runs. A pipeline restart mid-loop re-runs round 1
        # against an advanced incumbent, producing the same name for a different merge;
        # `merge_adapters` then skips the existing adapter_model.safetensors and `run_cell`
        # resume skips the existing trials.parquet, so the search silently scores the wrong
        # merge. Verified 2026-08-11: {'L1b':3,'S1':9,'S2':9} and {'L1b':3,'S1':3,'S2':1}
        # both produced `mo_r1_L1b_e3`.
        digest = hashlib.sha256(
            json.dumps(pick, sort_keys=True).encode()).hexdigest()[:8]
        name = f"mo_r{args.round}_{sweep_target}_e{e}_{digest}"
        candidates.append({"name": name, "epochs": pick, "target": sweep_target, "epoch": e,
                           "out": str(MERGE_ROOT / "merge_optimal" / args.model / args.language / name)})
    for c in candidates:
        print(f"    {c['name']:<28} {c['epochs']}")
    if args.plan:
        print("[merge-opt] --plan: nothing written")
        return 0

    if args.collect:
        return _collect(args, state, state_path, candidates)

    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)[args.model]["hf_id"]
    built = []
    for c in candidates:
        out = Path(c["out"])
        if not (out / "adapter_model.safetensors").exists():
            paths = {cond: str(bank[cond][0] / bank[cond][1][ep - 1])
                     for cond, ep in c["epochs"].items() if cond in bank}
            merge_adapters(MergeSpec(base_model_id=hf_id, adapter_paths=paths,
                                     combination_type=args.combination_type, weights=None,
                                     adapter_name=c["name"], seed=args.seed), out)
            print(f"[merge-opt] merged {c['name']}")
        built.append(c)

    cfg_path = CONFIG_DIR / "eval" / f"merge_optimal_r{args.round}_{args.model}_{args.language}.yaml"
    body = [
        "# Generated by scripts/merge/22_merge_optimal.py — do not hand-edit.",
        "#",
        "# One greedy round of MERGE-OPTIMAL checkpoint selection: seven experts held at their",
        "# incumbent epoch, the eighth swept. The winner becomes the next round's incumbent.",
        "# This is the objective Horoi et al. recommend (task-dependent early stopping), as",
        "# opposed to `best`, which maximises each expert's INDIVIDUAL accuracy.",
        "_extends: _base_eval.yaml", "",
        "phase: main",
        f"run_tag: merge_optimal_r{args.round}",
        f"model: {args.model}",
        f"language: {args.language}",
        "", "systems:",
        "  - {name: base, arch: none}",
    ]
    for c in built:
        rel = str(Path(c["out"]).relative_to(ROOT))
        body.append(f"  - {{name: {c['name']}, arch: merge_{args.combination_type}, "
                    f"adapter: {rel}, train_cond: mix}}")
    body += ["", f"eval_conditions: [{', '.join(args.conditions)}]", ""]
    cfg_path.write_text("\n".join(body))
    print(f"[merge-opt] wrote {cfg_path.relative_to(ROOT)} ({len(built)} candidates)")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2))

    if args.enqueue:
        q = RUNS_DIR / "manifest" / "queued"
        q.mkdir(parents=True, exist_ok=True)
        jid = f"evalmergeopt_r{args.round}__{args.model}_{args.language}"
        (q / f"055_{jid}.json").write_text(json.dumps({
            "job_id": jid, "kind": "eval-cell",
            "argv": ["-m", "obtune.eval_vllm", "--config", f"eval/{cfg_path.name}",
                     "--model", args.model, "--language", args.language],
            "raw": False, "est_gpu_h": 0.6, "priority": 55,
            "meta": {"experiment": "rq2/merge-optimal", "round": args.round,
                     "sweeping": sweep_target},
        }, indent=2))
        print(f"[merge-opt] queued {jid}")
    return 0


def _collect(args, state, state_path, candidates) -> int:
    """Read the round's cells and promote the winning epoch into the incumbent."""
    import pandas as pd

    scores: dict[str, float] = {}
    for c in candidates:
        cells = list((ROOT / "results" / "cells").rglob(f"{c['name']}__*/trials.parquet"))
        if not cells:
            continue
        df = pd.concat([pd.read_parquet(p, columns=["correct"]) for p in cells])
        scores[c["name"]] = float(df["correct"].mean())
    if not scores:
        print("[merge-opt] no cells found for this round — has the eval run?")
        return 1
    print(f"  {'candidate':<28}{'merged acc':>12}")
    for n, v in sorted(scores.items(), key=lambda kv: -kv[1]):
        print(f"  {n:<28}{v:>12.4f}")
    winner = max(scores, key=scores.get)
    # Read the target and epoch off the CANDIDATE, never by parsing the name. The old
    # `name.split("_", 2)[2].rsplit("_e", 1)[0]` was a second place where the identifier had
    # to carry meaning, and it would have silently mis-attributed the winner the moment the
    # name format changed — which it just did.
    won = next(c for c in candidates if c["name"] == winner)
    target, ep = won["target"], won["epoch"]
    prev = state["incumbent"].get(target)
    state["incumbent"][target] = ep
    state["history"].append({"round": args.round, "swept": target, "was": prev,
                             "now": ep, "scores": scores})
    state_path.write_text(json.dumps(state, indent=2))
    print(f"\n[merge-opt] {target}: epoch {prev} -> {ep} (merged acc {scores[winner]:.4f})")
    if prev == ep:
        print("[merge-opt] incumbent unchanged — this expert has converged for this order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
