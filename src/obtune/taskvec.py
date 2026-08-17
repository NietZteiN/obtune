"""LoRA task-vector arithmetic — scaling, negation, and combination of adapters.

A *task vector* is the weight delta a fine-tune induces, `theta_ft - theta_base`
(Ilharco et al., "Editing Models with Task Arithmetic"). For a LoRA adapter that delta is
available in closed form, which makes the arithmetic exact rather than approximate:

    dW = (alpha / r) * B @ A

`configs/train/_base_lora.yaml` sets `r=32, alpha=64` and leaves `use_dora`/`use_rslora`
unset — verified `false` in the adapters on disk — so the scaling is the plain constant
`alpha/r`, and multiplying `lora_B` by a scalar `lam` multiplies the whole delta by `lam`.
Negation (`lam = -1`) and interpolation are therefore *exact* weight-space operations, not
low-rank approximations of one. If DoRA or rslora is ever enabled this stops being true —
`_assert_plain_lora` refuses rather than silently producing a wrong vector.

Two uses this module exists for:

  * **Negation as an ablation.** Subtracting a condition's task vector from a monolithic
    or merged adapter asks whether that condition's contribution is separable in weight
    space. It is the weight-space counterpart of the activation-space interventions, and
    the cheapest available "unlearning-flavoured" control (no gradients, seconds to run).
  * **Composition.** `combine` builds `sum_i lam_i * dW_i` as a single adapter.

On `combination_type` — the one trap
------------------------------------
PEFT's `add_weighted_adapter(combination_type="linear")` is NOT exact task arithmetic for
more than one adapter. Verified in `peft/tuners/lora/model.py`: the generalized
task-arithmetic path puts `sqrt(|w * scaling|)` on **A and B separately** (with the sign on
A only), so the reconstructed `B_new @ A_new` picks up cross terms `B_i A_j` for `i != j`.
`combination_type="cat"` instead concatenates, putting the full `weight * scaling` on A, and
reconstructs exactly `sum_i w_i s_i B_i A_i`. So `cat` is what this module uses, and the
resulting rank is `sum_i r_i` — with six r=32 ingredients that is 192, above the
`max_lora_rank: 64` in the eval configs, which `assert_servable_rank` checks up front
rather than letting vLLM fail at load time.

Quarantine
----------
`merge_adapters._assert_no_h1` validates ingredient names against `TRAINABLE_CONDITIONS`,
which is wrong here: task vectors are keyed by *arm* (`mono`, `flip`, `sft`), not by
condition, so every legitimate call would be rejected. `_assert_no_h1_path` below is a
path-only guard — it refuses anything under `data/quarantine/` or any `H1` adapter
directory, which is the property that actually matters.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from obtune.config import PROJECT_ROOT, RUNS_DIR, load_config
from obtune.provenance import RunManifest, sha256_dir

__all__ = ["TaskVector", "load_task_vector", "scale", "negate", "combine",
           "assert_servable_rank", "TASKVEC_ROOT"]

TASKVEC_ROOT = RUNS_DIR / "taskvecs"

#: Adapter directories or names that may never be an ingredient.
_H1_PATH_RE = re.compile(r"(^|/)(H1)(_|/|$)|/quarantine/")


def _assert_no_h1_path(path: str | Path, name: str = "") -> Path:
    """Path-only quarantine guard.

    `merge_adapters._assert_no_h1` keys on `TRAINABLE_CONDITIONS`, so it rejects every arm
    name (`mono`, `flip`, `sft`) that this module legitimately operates on. What actually
    needs guarding is the *location*: nothing from the quarantine tree, and no adapter
    trained on H1, may become an ingredient.
    """
    p = Path(path).resolve()
    if _H1_PATH_RE.search(str(p)) or _H1_PATH_RE.search(name):
        raise ValueError(
            f"refusing to use {name or p} as a task-vector ingredient: it names the "
            "held-out H1 family or lives under the quarantine tree (CLAUDE.md §3.2)"
        )
    return p


def _assert_plain_lora(cfg: Mapping[str, Any], where: str) -> None:
    """`dW = (alpha/r) B@A` only holds for vanilla LoRA.

    DoRA decomposes into magnitude and direction, and rslora changes the scaling to
    `alpha/sqrt(r)`; under either, scaling `lora_B` no longer scales the delta linearly and
    every number this module produces would be quietly wrong.
    """
    for flag in ("use_dora", "use_rslora"):
        if cfg.get(flag):
            raise ValueError(
                f"{where}: {flag}=True — the closed-form task vector dW=(alpha/r)·B@A does "
                "not hold, so scaling lora_B would not scale the delta. Refusing."
            )


@dataclass
class TaskVector:
    """One adapter's delta, kept in LoRA factors rather than materialized as dense dW.

    Materializing `B @ A` for every target module would cost gigabytes and lose the
    low-rank structure that makes the result servable as an adapter.
    """

    name: str
    path: Path
    config: dict[str, Any]
    tensors: dict[str, Any] = field(default_factory=dict)

    @property
    def r(self) -> int:
        return int(self.config["r"])

    @property
    def alpha(self) -> int:
        return int(self.config["lora_alpha"])

    @property
    def scaling(self) -> float:
        return self.alpha / self.r


def load_task_vector(path: str | Path, name: str = "") -> TaskVector:
    from safetensors.torch import load_file

    p = _assert_no_h1_path(path, name)
    cfg = json.loads((p / "adapter_config.json").read_text())
    _assert_plain_lora(cfg, str(p))
    tensors = load_file(str(p / "adapter_model.safetensors"))
    return TaskVector(name=name or p.parent.name, path=p, config=cfg, tensors=tensors)


def scale(tv: TaskVector, lam: float) -> TaskVector:
    """Multiply the delta by `lam`, exactly, by scaling the B factors only.

    B carries the scalar and A is untouched: `dW = (alpha/r)(lam·B)A = lam·dW`. Scaling
    both by `sqrt(lam)` would be equivalent for positive `lam` but undefined for the
    negation this module exists to support.
    """
    out = dict(tv.tensors)
    for k, v in tv.tensors.items():
        if ".lora_B." in k:
            out[k] = v * lam
    return TaskVector(name=f"{tv.name}*{lam:g}", path=tv.path, config=dict(tv.config), tensors=out)


def negate(tv: TaskVector) -> TaskVector:
    """`lam = -1`. Subtracting a task vector is the weight-space ablation of that task."""
    return scale(tv, -1.0)


def assert_servable_rank(total_rank: int, max_lora_rank: int = 64) -> None:
    """`cat` sums the ranks; vLLM refuses an adapter above its configured `max_lora_rank`.

    Checked here so the failure names the cause, instead of surfacing hours later as a
    vLLM load error in an eval job.
    """
    if total_rank > max_lora_rank:
        raise ValueError(
            f"combined adapter has rank {total_rank} > max_lora_rank {max_lora_rank}. "
            "Raise `engine.max_lora_rank` in the eval config, or combine fewer adapters "
            "(combination_type='cat' sums the ingredient ranks)."
        )


def combine(
    base_model_id: str,
    ingredients: Mapping[str, float],
    out_dir: str | Path,
    *,
    max_lora_rank: int = 64,
    dtype: str = "float32",
    adapter_name: str = "taskvec",
) -> Path:
    """Build `sum_i lam_i * dW_i` as one servable adapter, via PEFT `cat`.

    `ingredients` maps adapter directory -> coefficient; negative coefficients are the
    point of the module. `cat` rather than `linear` — see the module docstring; `linear`
    introduces cross terms `B_i A_j` and is not task arithmetic for more than one adapter.
    """
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    paths = {p: float(w) for p, w in ingredients.items()}
    if not paths:
        raise ValueError("no ingredients")
    ranks = []
    for p in paths:
        tv = load_task_vector(p)
        _assert_plain_lora(tv.config, str(p))
        ranks.append(tv.r)
    assert_servable_rank(sum(ranks), max_lora_rank)

    torch_dtype = getattr(torch, dtype)
    model = AutoModelForCausalLM.from_pretrained(base_model_id, dtype=torch_dtype)
    names = []
    peft_model = None
    for i, p in enumerate(paths):
        nm = f"ing{i}"
        names.append(nm)
        if peft_model is None:
            peft_model = PeftModel.from_pretrained(model, str(p), adapter_name=nm)
        else:
            peft_model.load_adapter(str(p), adapter_name=nm)

    peft_model.base_model.add_weighted_adapter(
        adapters=names,
        weights=[paths[p] for p in paths],
        adapter_name=adapter_name,
        combination_type="cat",
    )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    peft_model.set_adapter(adapter_name)
    peft_model.save_pretrained(str(out), selected_adapters=[adapter_name])

    # PEFT nests the saved adapter under <out>/<adapter_name>/; flatten it so vLLM's
    # multi-LoRA path can serve the directory unchanged (same fix merge_adapters applies).
    nested = out / adapter_name
    if nested.is_dir():
        for f in nested.iterdir():
            f.rename(out / f.name)
        nested.rmdir()

    cfg_path = out / "adapter_config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["base_model_name_or_path"] = base_model_id
    cfg_path.write_text(json.dumps(cfg, indent=2))

    (out / "taskvec_spec.json").write_text(json.dumps({
        "base_model_id": base_model_id,
        "combination_type": "cat",
        "ingredients": [
            {"path": str(p), "coefficient": w, "sha256": sha256_dir(Path(p))}
            for p, w in paths.items()
        ],
        "total_rank": sum(ranks),
    }, indent=2, sort_keys=True))
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LoRA task-vector arithmetic (RQ2)")
    ap.add_argument("--model", default="qwen25c-1.5b", help="key in configs/models.yaml")
    ap.add_argument("--ingredient", action="append", default=[], metavar="PATH=COEF",
                    help="adapter dir and its coefficient, e.g. runs/.../S1_r32_s17/best=-1.0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-lora-rank", type=int, default=64)
    ap.add_argument("--dtype", default="float32")
    args = ap.parse_args(argv)

    if not args.ingredient:
        raise SystemExit("pass at least one --ingredient PATH=COEF")
    ingredients: dict[str, float] = {}
    for spec in args.ingredient:
        path, _, coef = spec.rpartition("=")
        if not path:
            raise SystemExit(f"malformed --ingredient {spec!r}; expected PATH=COEF")
        p = path if Path(path).is_absolute() else str(PROJECT_ROOT / path)
        ingredients[p] = float(coef)

    base_id = load_config("models.yaml")["models"][args.model]["hf_id"]
    out = combine(base_id, ingredients, args.out,
                  max_lora_rank=args.max_lora_rank, dtype=args.dtype)
    mani = (
        RunManifest(
            experiment="taskvec", run_id=Path(args.out).name, seed=17,
            config_path="(cli)", config_resolved={"ingredients": ingredients},
            model_hf_id=base_id,
        )
        .hash_scripts(["src/obtune/taskvec.py"])
        .capture_git()
        .finalize()
    )
    mani.write(out)
    print(f"  task vector -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
