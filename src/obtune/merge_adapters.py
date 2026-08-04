"""LoRA-space merging of the per-condition adapters (RQ2 "merge" arm).

The RQ2 question is whether six per-condition adapters can be collapsed into ONE set of
weights that keeps most of the per-type benefit — i.e. whether the conditions occupy
compatible subspaces or fight each other. TIES and DARE are the two standard answers
(sign-consensus pruning and stochastic drop-and-rescale); both are implemented inside
PEFT's `LoraModel.add_weighted_adapter`, so this module is a driver, not a re-derivation.

Why not mergekit (recorded because it was tried and rejected): its LoRA path merges each
adapter into the base weights and re-extracts a LoRA by SVD, which changes the rank and
introduces reconstruction error before the merge algorithm even runs; it also pins
`accelerate~=1.6`, which conflicts with this environment (see configs/merge/ties_v1.yaml).

VERIFIED API (peft 0.20.0, peft/tuners/lora/model.py:664) — exact call used below:

    peft_model.base_model.add_weighted_adapter(
        adapters=["L0", "L1b", "L1r", "L2", "S1", "S2"],
        weights=[1/6] * 6,
        adapter_name="merged",
        combination_type="ties",          # linear | ties | dare_ties | dare_linear |
                                          # magnitude_prune | *_svd | cat
        density=0.5,                      # required by ties/dare/magnitude_prune
        majority_sign_method="total",     # ties/dare_ties only
    )

Two behaviours of that method that matter and are easy to get wrong:
  * It accounts for each source adapter's own scaling: internally the weight becomes
    `weight * target.scaling[adapter]`, so our r=32/alpha=64 (scaling 2.0) ingredients are
    NOT silently halved. The merged adapter is written with `lora_alpha = r`, i.e. its own
    scaling is 1.0, with the factor already baked into the weights.
  * It returns silently if `adapter_name` already exists. Every density in a sweep
    therefore gets its own adapter name AND its own freshly-loaded model.

Output is a plain adapter directory (`adapter_config.json` + `adapter_model.safetensors`)
that vLLM's multi-LoRA path can serve unchanged.

H1 can never be an ingredient: `_assert_no_h1` rejects it by label and by path.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

from obtune.config import PROJECT_ROOT, RUNS_DIR, load_config
from obtune.paths import TRAINABLE_CONDITIONS
from obtune.provenance import RunManifest, sha256_dir
from obtune.seedutil import set_seed

__all__ = ["MergeSpec", "merge_adapters", "density_sweep", "resolve_adapter_paths",
           "ADAPTER_ROOT", "MERGE_ROOT"]

ADAPTER_ROOT = RUNS_DIR / "adapters"
MERGE_ROOT = RUNS_DIR / "merges"

# combination types that consume `density`; passing it to the others is an error in PEFT
_DENSITY_TYPES = {"ties", "dare_ties", "dare_linear", "magnitude_prune",
                  "ties_svd", "dare_ties_svd", "dare_linear_svd", "magnitude_prune_svd"}
_SIGN_TYPES = {"ties", "dare_ties", "ties_svd", "dare_ties_svd"}


@dataclass
class MergeSpec:
    base_model_id: str
    adapter_paths: dict[str, str]  # condition -> adapter dir
    combination_type: str = "ties"
    density: float = 0.5
    weights: Optional[list[float]] = None  # None => uniform 1/n
    majority_sign_method: str = "total"
    adapter_name: str = "merged"
    seed: int = 17

    def resolved_weights(self) -> list[float]:
        n = len(self.adapter_paths)
        if self.weights is None:
            return [1.0 / n] * n
        if len(self.weights) != n:
            raise ValueError(f"{len(self.weights)} weights for {n} adapters")
        return list(self.weights)


def _assert_no_h1(conditions: Sequence[str], paths: Sequence[str]) -> None:
    """Quarantine layer for the merge stage (CLAUDE.md §3.2 item 2).

    A merge that included an H1-trained adapter would make every downstream H1 number a
    train-on-test result, and nothing in the trial table would show it.
    """
    bad = [c for c in conditions if c not in TRAINABLE_CONDITIONS]
    if bad:
        raise ValueError(f"refusing to merge non-trainable conditions {bad}; "
                         f"allowed: {list(TRAINABLE_CONDITIONS)}")
    for p in paths:
        rp = str(Path(p).resolve())
        if "quarantine" in rp or "/H1" in rp or rp.endswith("H1"):
            raise ValueError(f"refusing to merge adapter from a quarantined path: {rp}")


def resolve_adapter_paths(
    conditions: Sequence[str],
    *,
    model_key: str,
    language: str,
    rank: int = 32,
    seed: int = 17,
    root: Path = ADAPTER_ROOT,
    checkpoint: str = "best",
) -> dict[str, str]:
    """Layout convention from configs/eval/pilot_w1.yaml:
    runs/adapters/<model>/<lang>/<cond>_r<rank>_s<seed>/<checkpoint>"""
    out: dict[str, str] = {}
    for c in conditions:
        p = root / model_key / language / f"{c}_r{rank}_s{seed}" / checkpoint
        out[c] = str(p)
    return out


def merge_adapters(spec: MergeSpec, out_dir: str | Path, *, dtype: str = "float32") -> Path:
    """Merge and write a normal adapter directory. Returns the directory.

    `dtype=float32` on purpose: TIES sign-consensus and DARE rescaling are sums over many
    small deltas, and doing them in bf16 (7-bit mantissa) changes which entries survive
    pruning. The base weights are only a scaffold here — nothing is trained — so the
    memory cost of fp32 is acceptable and the merge becomes deterministic.
    """
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    conds = list(spec.adapter_paths.keys())
    _assert_no_h1(conds, list(spec.adapter_paths.values()))
    missing = [c for c, p in spec.adapter_paths.items() if not Path(p).exists()]
    if missing:
        raise FileNotFoundError(f"adapter dirs missing for {missing}")
    set_seed(spec.seed)  # DARE draws a Bernoulli mask — the seed is load-bearing

    base = AutoModelForCausalLM.from_pretrained(
        spec.base_model_id, dtype=getattr(torch, dtype), device_map=None)
    model = PeftModel.from_pretrained(base, spec.adapter_paths[conds[0]], adapter_name=conds[0])
    for c in conds[1:]:
        model.load_adapter(spec.adapter_paths[c], adapter_name=c)

    kwargs: dict[str, Any] = {
        "adapters": conds,
        "weights": spec.resolved_weights(),
        "adapter_name": spec.adapter_name,
        "combination_type": spec.combination_type,
    }
    if spec.combination_type in _DENSITY_TYPES:
        kwargs["density"] = spec.density
    if spec.combination_type in _SIGN_TYPES:
        kwargs["majority_sign_method"] = spec.majority_sign_method
    model.base_model.add_weighted_adapter(**kwargs)
    if spec.adapter_name not in model.peft_config:
        raise RuntimeError(f"PEFT did not create adapter {spec.adapter_name!r} "
                           "(it returns silently when the name already exists)")
    model.set_adapter(spec.adapter_name)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(out.parent)) as tmp:
        # save_pretrained nests non-"default" adapters under <tmp>/<name>/; vLLM wants a
        # flat directory, so the contents are lifted one level.
        model.save_pretrained(tmp, selected_adapters=[spec.adapter_name])
        src = Path(tmp) / spec.adapter_name
        if not src.exists():
            src = Path(tmp)
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, out / f.name)

    cfg_path = out / "adapter_config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["base_model_name_or_path"] = spec.base_model_id
    cfg_path.write_text(json.dumps(cfg, indent=2))

    (out / "merge_spec.json").write_text(json.dumps({
        "base_model_id": spec.base_model_id,
        "combination_type": spec.combination_type,
        "density": spec.density if spec.combination_type in _DENSITY_TYPES else None,
        "weights": spec.resolved_weights(),
        "majority_sign_method": (spec.majority_sign_method
                                 if spec.combination_type in _SIGN_TYPES else None),
        "adapters": {c: {"path": p, "sha256": sha256_dir(p)}
                     for c, p in spec.adapter_paths.items()},
        "merged_r": cfg.get("r"), "merged_lora_alpha": cfg.get("lora_alpha"),
        "seed": spec.seed, "dtype": dtype,
        "peft_call": "LoraModel.add_weighted_adapter(adapters, weights, adapter_name, "
                     "combination_type, density=, majority_sign_method=)",
    }, indent=2))
    del model, base
    return out


def density_sweep(
    spec: MergeSpec,
    densities: Sequence[float],
    out_root: str | Path,
    *,
    dtype: str = "float32",
) -> list[tuple[float, Path]]:
    """Produce one merged adapter per density.

    The sweep exists because TIES/DARE density is the one merge hyperparameter that
    changes the answer to RQ2: too dense and the conditions overwrite each other, too
    sparse and the merged adapter is a no-op. configs/merge/ties_v1.yaml sweeps it on the
    1.5B model only and applies the winner to 7B/8B — the sweep is selected on the
    held-in val slice, NEVER on H1 (§3.2 item 2).
    """
    out_root = Path(out_root)
    made: list[tuple[float, Path]] = []
    for d in densities:
        tag = f"{spec.combination_type}_d{str(d).replace('.', 'p')}"
        sub = MergeSpec(**{**spec.__dict__, "density": float(d),
                           "adapter_name": f"merged_{tag}"})
        made.append((float(d), merge_adapters(sub, out_root / tag, dtype=dtype)))
    return made


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Merge per-condition LoRA adapters (RQ2)")
    ap.add_argument("--config", default="merge/ties_v1.yaml")
    ap.add_argument("--model", default="qwen25c-1.5b")
    ap.add_argument("--language", default="python")
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--out", default=None, help="output adapter dir (single merge)")
    ap.add_argument("--sweep", action="store_true", help="run the density sweep from the config")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--adapter-dir", default=None,
                    help="JSON {condition: path} overriding the layout convention")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    models = load_config("models.yaml")["models"]
    base_id = models[args.model]["hf_id"]
    conds = list(cfg["adapters"])
    seed = int(cfg.get("seed", 17))

    if args.adapter_dir:
        paths = json.loads(Path(args.adapter_dir).read_text())
    else:
        paths = resolve_adapter_paths(conds, model_key=args.model, language=args.language,
                                      rank=args.rank, seed=seed)

    spec = MergeSpec(
        base_model_id=base_id, adapter_paths=paths,
        combination_type=str(cfg["combination_type"]), density=float(cfg["density"]),
        weights=cfg.get("weights"), seed=seed,
    )
    tag = f"{args.model}_{args.language}_{spec.combination_type}"
    mani = RunManifest(
        experiment="merge_adapters", run_id=tag, seed=seed,
        config_path=str(cfg["_config_path"]), config_resolved=cfg,
        model_hf_id=base_id,
    ).hash_scripts(["src/obtune/merge_adapters.py"]).capture_git()

    if args.sweep:
        root = Path(args.out or (MERGE_ROOT / tag))
        made = density_sweep(spec, cfg["density_sweep"], root, dtype=args.dtype)
        for d, p in made:
            print(f"  density={d}: {p}")
        mani.extra["merges"] = [{"density": d, "path": str(p)} for d, p in made]
        out_dir = root
    else:
        out_dir = Path(args.out or (MERGE_ROOT / tag / f"d{str(spec.density).replace('.', 'p')}"))
        p = merge_adapters(spec, out_dir, dtype=args.dtype)
        print(f"  merged adapter -> {p}")
        mani.extra["merges"] = [{"density": spec.density, "path": str(p)}]

    mani.finalize().write(out_dir)
    print(f"  manifest -> {out_dir / 'run_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
