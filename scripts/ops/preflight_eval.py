"""Pre-flight an eval config: does every adapter it names exist, with weights, BEFORE a GPU is spent?

Four evals failed this week minutes into an allocation with FileNotFoundError on an adapter path:
mono_all_s42 (never checkpoint-selected), inverse_trained (selected under the wrong root),
cons_lam3_s42 (never trained for Llama), and merge_*_s42 (written to the sweep path instead of the
adapter path). Every one was knowable from the config and the filesystem, and every one cost a queue
wait, an allocation, model loading, and then silently stopped a dependency chain. This is the check
that should have run first.

    python scripts/ops/preflight_eval.py eval/seed42_llama31-8b.yaml --model llama31-8b
    python scripts/ops/preflight_eval.py --all-seed42            # every seed42_*/invtrained_* config

Exit 0 only if every named adapter resolves to a directory holding adapter_model.safetensors.
Nothing here touches the GPU or the results tree; it reads configs and stats files.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from obtune.config import load_config, PROJECT_ROOT

def check(cfg_rel: str, model: str | None) -> list[str]:
    cfg = load_config(cfg_rel)
    model = model or cfg.get("model")
    lang = cfg.get("language", "python")
    if not model:
        return [f"{cfg_rel}: no model in config and none given"]
    bad = []
    for s in cfg.get("systems", []):
        a = s.get("adapter")
        if not a:
            continue
        p = PROJECT_ROOT / a.format(model=model, language=lang)
        if not (p / "adapter_model.safetensors").exists():
            what = "directory missing" if not p.exists() else ("has checkpoints but no best/ -- run ckpt-select"
                    if any(p.parent.glob("checkpoint-*")) and p.name == "best" else "no adapter_model.safetensors")
            bad.append(f"  {s['name']:22s} {what}\n      {p}")
    return bad

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?")
    ap.add_argument("--model")
    ap.add_argument("--all-seed42", action="store_true")
    a = ap.parse_args()
    targets = []
    if a.all_seed42:
        for p in sorted((PROJECT_ROOT / "configs/eval").glob("*.yaml")):
            if p.name.startswith(("seed42_", "invtrained_")):
                targets.append((f"eval/{p.name}", None))
    elif a.config:
        targets.append((a.config, a.model))
    else:
        ap.error("give a config or --all-seed42")
    rc = 0
    for cfg, m in targets:
        bad = check(cfg, m)
        print(f"{'FAIL' if bad else 'ok  '} {cfg}")
        for b in bad: print(b)
        rc |= bool(bad)
    return rc

if __name__ == "__main__":
    sys.exit(main())
