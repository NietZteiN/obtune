#!/usr/bin/env python
"""Build the plain uniform-average merge -- A5's missing operator control.

    python scripts/merge/26_linear_merge.py <model> [<model> ...]

TIES and DARE-TIES each add two steps to averaging: sparsification (top-density by magnitude,
or random drop with rescaling) and sign election followed by a disjoint merge. The paper
compares them to each other and to nothing else, so it cannot say whether either step buys
anything over simply averaging the six specialists. This builds that baseline.

`linear` takes no density -- PEFT's _DENSITY_TYPES excludes it and passing one raises -- so the
operator is the only difference from merge_dare_ties_r32_s17: same six adapters, same uniform
weights, same rank, same seed.
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))

CONDS = ["L0", "L1b", "L1r", "L2", "S1", "S2"]

def main() -> int:
    from obtune.merge_adapters import MergeSpec, merge_adapters, resolve_adapter_paths
    import yaml
    models = sys.argv[1:] or ["codellama-7b"]
    reg = yaml.safe_load((ROOT/"configs/models.yaml").read_text())
    for m in models:
        entry = reg.get("models", reg).get(m)
        base = entry["hf_id"] if isinstance(entry, dict) else entry
        paths = resolve_adapter_paths(CONDS, model_key=m, language="python")
        missing = [c for c, p in paths.items() if not Path(p).exists()]
        if missing:
            print(f"{m}: missing specialists {missing}; skipped"); continue
        out = ROOT/f"runs/adapters/{m}/python/merge_linear_r32_s17"
        if (out/"adapter_model.safetensors").exists():
            print(f"{m}: already built at {out}"); continue
        spec = MergeSpec(base_model_id=base, adapter_paths=paths,
                         combination_type="linear", weights=None,
                         adapter_name="merge_linear", seed=17)
        merge_adapters(spec, out)
        print(f"{m}: wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
