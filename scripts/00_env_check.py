#!/usr/bin/env python
"""Preflight: is this host actually able to run obtune?

Checks every external dependency the pipeline assumes, and prints a table. Exits
nonzero if anything REQUIRED is missing, so it can gate a pipeline run. Optional
items (idle GPUs, R packages) are reported but do not fail the check — the data
layer runs fine on CPU and the stats layer is a separate phase.

    python scripts/00_env_check.py
"""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from obtune.config import PROJECT_ROOT, load_config  # noqa: E402

REQUIRED_PY = ["torch", "transformers", "peft", "trl", "vllm", "datasets", "pydantic",
               "yaml", "pandas", "pyarrow", "numpy", "scipy",
               "tree_sitter", "tree_sitter_python", "tree_sitter_javascript"]
REQUIRED_NODE_PKGS = ["@babel/core", "@babel/parser", "@babel/traverse",
                      "@babel/generator", "@babel/types", "javascript-obfuscator"]
R_PACKAGES = ["lme4", "glmmTMB", "emmeans", "broom.mixed", "DHARMa", "arrow", "binom"]

results: list[tuple[str, str, str, bool]] = []  # (category, name, detail, required_ok)


def check(category: str, name: str, ok: bool, detail: str, required: bool = True) -> None:
    results.append((category, name, detail, ok or not required))
    mark = "ok  " if ok else ("FAIL" if required else "warn")
    print(f"  [{mark}] {name:<28} {detail}")


def main() -> int:
    print(f"obtune preflight — {PROJECT_ROOT}")

    print("\npython packages")
    for mod in REQUIRED_PY:
        try:
            m = importlib.import_module(mod)
            check("py", mod, True, getattr(m, "__version__", "installed"))
        except ImportError as e:
            check("py", mod, False, f"missing ({e.__class__.__name__})")

    print("\nnode workspace")
    node = shutil.which("node")
    check("node", "node", bool(node), node or "not on PATH")
    if node:
        v = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
        check("node", "node version", True, v)
    nm = PROJECT_ROOT / "js" / "node_modules"
    for pkg in REQUIRED_NODE_PKGS:
        p = nm / pkg / "package.json"
        ver = json.loads(p.read_text()).get("version", "?") if p.exists() else "missing"
        check("node", pkg, p.exists(), ver)

    print("\nmodels (HF cache)")
    models = load_config("models.yaml")["models"]
    try:
        from huggingface_hub import snapshot_download

        for key, spec in models.items():
            try:
                path = snapshot_download(spec["hf_id"], local_files_only=True)
                check("model", key, True, path)
            except Exception:
                check("model", key, False, f"{spec['hf_id']} not cached — run `hf download {spec['hf_id']}`")
    except ImportError:
        check("model", "huggingface_hub", False, "missing")

    print("\ndata inputs")
    data_cfg = load_config("data.yaml")["test_set"]
    for key in ("dataset_a", "dataset_b", "spans_a", "spans_b"):
        p = Path(data_cfg[key])
        check("data", key, p.exists(), str(p) if p.exists() else f"MISSING {p}")
    for link in ("stimuli/dataset_a.jsonl", "human/paper2_graded.csv", "human/paper3_graded.csv"):
        p = PROJECT_ROOT / "data" / link
        check("data", link, p.exists(), "resolves" if p.exists() else "broken symlink")

    print("\ngpus (optional — the data layer is CPU-only)")
    try:
        from obtune import gpu

        stats = gpu.query()
        if not stats:
            check("gpu", "nvidia-smi", False, "unavailable", required=False)
        for s in stats:
            idle = s.is_idle(2000, 5)
            check("gpu", f"gpu{s.index}", idle,
                  f"{s.mem_used_mb} MB used, {s.util_pct}% util — {'IDLE' if idle else 'BUSY'}",
                  required=False)
    except Exception as e:  # noqa: BLE001
        check("gpu", "query", False, str(e), required=False)

    print("\nR stats env (optional — separate phase)")
    rscript = load_config("compute.yaml")["paths"]["rscript"]
    if Path(rscript).exists():
        check("R", "Rscript", True, rscript, required=False)
        expr = ";".join(f'cat("{p}:", requireNamespace("{p}", quietly=TRUE), "\\n")' for p in R_PACKAGES)
        out = subprocess.run([rscript, "-e", expr], capture_output=True, text=True)
        for line in out.stdout.strip().splitlines():
            pkg, _, val = line.partition(":")
            check("R", pkg.strip(), val.strip() == "TRUE", val.strip(), required=False)
    else:
        check("R", "Rscript", False, f"not found at {rscript}", required=False)

    failed = [f"{c}/{n}" for c, n, _, ok in results if not ok]
    print()
    if failed:
        print(f"PREFLIGHT FAILED — {len(failed)} required item(s): {', '.join(failed)}")
        return 1
    print(f"PREFLIGHT OK — {len(results)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
