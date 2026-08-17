#!/usr/bin/env python
"""Merge quality as a function of how long the experts were trained (Part V, Stage 1).

    python scripts/merge/21_epoch_sweep.py --dry-run     # inspect, touch nothing
    python scripts/merge/21_epoch_sweep.py               # merge + write the eval config
    python scripts/merge/21_epoch_sweep.py --enqueue     # ... and queue the eval jobs

Horoi, Wolf, Belilovsky & Dziugaite (arXiv:2506.14126v2) argue that training experts to their
own individual optimum degrades merging. `20_geometry_report.py` measures the proposed
mechanism (sign conflict); this measures the OUTCOME, which is what actually matters and can
move even when the geometry does not.

TWO THINGS THIS FIXES, BOTH REAL
--------------------------------
1. **The heterogeneity confound.** Every existing merge is built from `best`, and `ckpt_select`
   chose a DIFFERENT epoch per condition — L1r and S3 at epoch 1, L0/L1b at epoch 2, and
   L2/S2/S1/S4 at epoch 3. So the merges already combine task vectors of unequal training, and
   no existing number separates "merging is lossy" from "we merged mismatched vectors". Holding
   the epoch UNIFORM across experts is the control that has never been run.
2. **The selection objective.** `best` maximises each expert's INDIVIDUAL accuracy, which is
   exactly the objective the paper identifies as harmful to merging. The sweep lets the two be
   compared directly.

The prediction is a DISSOCIATION, so both halves are reported: individual accuracy should rise
with epochs while merged accuracy falls. A merged number alone cannot show that.

`merge_dare_linear` is excluded: measured 2026-08-10 its effective ||dW|| is 5.58x a single
expert's (ties 0.19x, dare_ties 0.62x), i.e. a mis-scaled merge rather than a method result.
Including it would put a broken arm in a comparison about training length.

Costs ~20-30 s per merge (dominated by the base-model load) and 3-6 min per eval cell.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.config import CONFIG_DIR, RUNS_DIR, load_config  # noqa: E402
from obtune.merge_adapters import MERGE_ROOT, MergeSpec, merge_adapters  # noqa: E402

#: dare_linear deliberately absent — see the module docstring.
COMBINATIONS = ("ties", "dare_ties")


def epoch_checkpoint(adapter: Path, epoch: int) -> str | None:
    """Checkpoint directory for the n-th epoch of this expert.

    Identified by RANK of step number, not absolute step: conditions bail on different numbers
    of programs (S1 has 54 steps/epoch where L0 has 74), so absolute steps are not comparable
    across conditions and only the ordinal is meaningful.
    """
    steps = sorted(int(p.name.split("-")[1]) for p in adapter.glob("checkpoint-*"))
    return f"checkpoint-{steps[epoch - 1]}" if 0 < epoch <= len(steps) else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--languages", nargs="*", default=["python", "javascript"])
    ap.add_argument("--conditions", nargs="*",
                    default=["L0", "L1b", "L1r", "L2", "S1", "S2"])
    ap.add_argument("--epochs", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--root", default="runs/adapters",
                    help="expert bank (runs/adapters_overtrain for the 9-epoch probe)")
    ap.add_argument("--tag", default="epoch_sweep", help="output subdirectory under runs/merges")
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--dry-run", action="store_true", help="report the plan, write nothing")
    ap.add_argument("--enqueue", action="store_true", help="also write eval job files")
    args = ap.parse_args()

    models = load_config("models.yaml")
    hf_id = (models.get("models") or models)[args.model]["hf_id"]

    plan: list[dict] = []
    for lang in args.languages:
        base = ROOT / args.root / args.model / lang
        for epoch in args.epochs:
            paths: dict[str, str] = {}
            for c in args.conditions:
                adir = base / f"{c}_r{args.rank}_s{args.seed}"
                ck = epoch_checkpoint(adir, epoch)
                if ck is None:
                    break
                paths[c] = str(adir / ck)
            if len(paths) != len(args.conditions):
                print(f"[sweep] {lang} epoch {epoch}: incomplete "
                      f"({len(paths)}/{len(args.conditions)} experts) — skipped")
                continue
            for combo in COMBINATIONS:
                plan.append({
                    "language": lang, "epoch": epoch, "combination_type": combo,
                    "adapter_paths": paths,
                    "out": str(MERGE_ROOT / args.tag / args.model / lang
                              / f"{combo}_e{epoch}_r{args.rank}_s{args.seed}"),
                })

    print(f"[sweep] {len(plan)} merge(s) planned "
          f"({len(args.languages)} lang x {len(args.epochs)} epoch x {len(COMBINATIONS)} combo)")
    for p in plan:
        print(f"    {p['language']:<11} epoch {p['epoch']}  {p['combination_type']:<10} -> "
              f"{Path(p['out']).name}")
    if args.dry_run:
        print("[sweep] --dry-run: nothing written")
        return 0

    built: list[dict] = []
    for p in plan:
        out = Path(p["out"])
        if (out / "adapter_model.safetensors").exists():
            print(f"[sweep] exists, skipping: {out.name}")
            built.append(p)
            continue
        spec = MergeSpec(
            base_model_id=hf_id,
            adapter_paths=p["adapter_paths"],
            combination_type=p["combination_type"],
            # weights=None => uniform 1/n. Uniform is the point: any per-expert weighting would
            # confound "trained longer" with "weighted differently".
            weights=None,
            adapter_name=f"{p['combination_type']}_e{p['epoch']}",
            seed=args.seed,
        )
        merge_adapters(spec, out)
        print(f"[sweep] merged {out.name}")
        built.append(p)

    # One dict-style eval config per language: `systems` maps a name to an adapter path, which
    # is the shape preflight's check_eval_config validates and eval_vllm consumes directly.
    for lang in args.languages:
        rows = [p for p in built if p["language"] == lang]
        if not rows:
            continue
        # LIST-style systems, not dict-style. `eval_vllm.expand_systems` iterates rows and
        # calls dict(row), so a {name: path} mapping raises "dictionary update sequence
        # element #0 has length 1". Dict-style belongs to the cft/srh harness
        # (`obtune.cft.evaluate`); configs under configs/eval/ are consumed by eval_vllm and
        # must be lists. Conflating the two cost two failed jobs.
        #
        # `arch` is the real merge arch so the rows land under the right label in
        # stats/R and the transfer filters — and supplying `adapter` explicitly suppresses
        # expand_systems' path derivation (`arch.startswith("merge") and not spec.adapter`),
        # which would otherwise point at runs/adapters/ instead of the sweep's own root.
        systems = [{"name": "base", "arch": "none"}]
        for p in rows:
            systems.append({
                # Namespaced by --tag. Cell paths are
                # results/cells/<phase>/<model>/<lang>/<SYSTEM_NAME>__<cond>, keyed on the
                # system NAME alone — so two sweeps using `ties_e1` write to one directory.
                # With resume:true the second is silently SKIPPED (observed: the 9-epoch
                # sweep's e1/e3 never ran and the table quietly showed only e6/e9); with
                # resume off it would overwrite the first. Neither errors.
                "name": f"{args.tag}_{p['combination_type']}_e{p['epoch']}",
                "arch": f"merge_{p['combination_type']}",
                "adapter": str(Path(p["out"]).relative_to(ROOT)),
                "train_cond": "mix",
            })
        cfg_path = CONFIG_DIR / "eval" / f"merge_{args.tag}_{args.model}_{lang}.yaml"
        body = [
            "# Generated by scripts/merge/21_epoch_sweep.py — do not hand-edit.",
            "#",
            "# Merge quality vs expert training length (Part V, Stage 1). Every system here is",
            "# a UNIFORM-epoch merge, which is the control the existing merges lack: they are",
            "# built from `best`, and ckpt_select picked a different epoch per condition.",
            "#",
            "# H1 is deliberately absent from eval_conditions: this is a merging question,",
            "# entirely within trainable conditions, and CLAUDE.md 3.2 grants H1 only two",
            "# evaluation passes, both already spent.",
            "_extends: _base_eval.yaml",
            "",
            "phase: main",
            f"run_tag: merge_{args.tag}_{lang}",
            f"model: {args.model}",
            f"language: {lang}",
            "",
            "systems:",
        ]
        for row in systems:
            inner = ", ".join(f"{k}: {v}" for k, v in row.items())
            body.append(f"  - {{{inner}}}")
        body += ["", f"eval_conditions: [{', '.join(args.conditions)}]", ""]
        cfg_path.write_text("\n".join(body))
        print(f"[sweep] wrote {cfg_path.relative_to(ROOT)} ({len(systems)} systems)")

        if args.enqueue:
            qdir = RUNS_DIR / "manifest" / "queued"
            qdir.mkdir(parents=True, exist_ok=True)
            jid = f"evalmerge_{args.tag}__{args.model}_{lang}"
            (qdir / f"053_{jid}.json").write_text(json.dumps({
                "job_id": jid, "kind": "eval-cell",
                "argv": ["-m", "obtune.eval_vllm", "--config",
                         f"eval/{cfg_path.name}", "--model", args.model,
                         "--language", lang],
                "raw": False, "est_gpu_h": 1.0, "priority": 53,
                "meta": {"experiment": "rq2/merge-epoch-sweep", "language": lang,
                         "note": "uniform-epoch merges; tests Horoi et al. arXiv:2506.14126v2"},
            }, indent=2))
            print(f"[sweep] queued {jid}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
