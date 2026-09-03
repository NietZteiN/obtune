"""Model-agnosticism lint — the invariant that survives a base-model swap.

WHY THIS EXISTS. The Qwen panel became unusable on this cluster overnight, and rebuilding
the corpus on CodeLlama cost far less than it might have: `prompts.py` already went through
`apply_chat_template`, and `configs/models.yaml` already carried n_layers / hidden_size /
max_seq_len / batch shape. What DID bite was the quiet coupling -- five modules defaulting
`--model` to `qwen25c-1.5b`, and an absolute layer set `[4, 9, 14, 19, 23, 27]` that means
different relative depths on a 32- or 40-layer model.

This lint keeps the codebase swappable after nobody is looking for it any more. It is
modelled on tests/test_quarantine_lint.py: grep for the failure, not for good intentions.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "obtune"
# scripts/ is scanned too: the knockout and steering entry points defaulted --model to
# qwen25c-1.5b and --layers to Qwen's 28-layer indices, and the first version of this
# lint looked only at src/ -- so the pins that survived longest were the ones outside it.
SCRIPTS = ROOT / "scripts"
MODELS_YAML = ROOT / "configs" / "models.yaml"

# Files allowed to name a concrete model: the registry itself, and migration/verification
# scripts that pin historical runs by construction.
# baselines/semcoder.py is a legitimate exception: SemCoder is `role: baseline_only`, never
# fine-tuned here, and is run in ITS OWN published prompt/answer format rather than obtune's
# template. Naming it there is the point of the module, not stray coupling.
ALLOWED = {"config.py", "semcoder.py"}


def _model_keys_and_ids() -> tuple[set[str], set[str]]:
    m = yaml.safe_load(MODELS_YAML.read_text())["models"]
    return set(m), {v["hf_id"] for v in m.values()}


def test_no_hardcoded_hf_ids_in_src() -> None:
    """An HF id outside models.yaml means one code path can't follow a model swap."""
    _, hf_ids = _model_keys_and_ids()
    offenders = []
    for py in list(SRC.rglob("*.py")) + list(SCRIPTS.rglob("*.py")):
        if py.name in ALLOWED:
            continue
        text = py.read_text()
        for line_no, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("*"):
                continue  # prose and docstring bullets may cite a model
            for hf in hf_ids:
                if hf in line:
                    offenders.append(f"{py.relative_to(ROOT)}:{line_no}: {hf}")
    assert not offenders, "hardcoded HF ids outside models.yaml:\n  " + "\n  ".join(offenders)


def test_model_flags_have_no_default() -> None:
    """`--model` must never default: a forgotten flag has to fail, not run the wrong base.

    This is the exact shape that let five modules quietly stay pinned to qwen25c-1.5b.
    """
    keys, _ = _model_keys_and_ids()
    pattern = re.compile(r'add_argument\(\s*"--model".*?\)', re.S)
    offenders = []
    for py in list(SRC.rglob("*.py")) + list(SCRIPTS.rglob("*.py")):
        for m in pattern.finditer(py.read_text()):
            frag = m.group(0)
            if "required=True" in frag:
                continue
            if re.search(r'default\s*=\s*"([^"]+)"', frag):
                got = re.search(r'default\s*=\s*"([^"]+)"', frag).group(1)
                if got in keys:
                    offenders.append(f"{py.relative_to(ROOT)}: --model defaults to {got!r}")
    assert not offenders, "\n  ".join(["--model must be required, not defaulted:"] + offenders)


def test_align_layers_are_fractional() -> None:
    """The alignment arm must express depth as fractions, not absolute layer indices."""
    acfg = yaml.safe_load((ROOT / "configs/train/_base_align.yaml").read_text())["align"]
    assert "layer_fracs" in acfg, "_base_align.yaml must carry layer_fracs (model-agnostic depth)"
    assert not acfg.get("layers"), (
        "_base_align.yaml pins absolute `layers`; those indices mean different relative "
        "depths on models of different size. Use layer_fracs."
    )


def test_every_declared_model_is_complete() -> None:
    """A half-declared model fails deep inside training, not at config load."""
    m = yaml.safe_load(MODELS_YAML.read_text())["models"]
    required = {"hf_id", "n_layers", "router_layer", "hidden_size", "max_seq_len",
                "per_device_batch", "grad_accum", "role"}
    for key, cfg in m.items():
        missing = required - set(cfg)
        assert not missing, f"models.yaml::{key} is missing {sorted(missing)}"
        assert 0 <= cfg["router_layer"] < cfg["n_layers"], f"{key}: router_layer out of range"


def test_no_absolute_layer_sets() -> None:
    """No literal Qwen layer set outside the fraction resolver.

    `[4, 9, 14, 19, 23, 27]` is 28-layer Qwen. On CodeLlama-7b (32) or -13b (40) the same
    integers probe different RELATIVE depths, so an arm keeps running and quietly stops
    measuring what it measured before. `obtune.config.layer_indices_for` is the one place
    that turns depth fractions into indices.
    """
    needle = "4, 9, 14, 19, 23, 27"
    # config.py DEFINES the resolver and cites the old literal to explain why it exists.
    exempt = {"config.py"}
    offenders = []
    for py in list(SRC.rglob("*.py")) + list(SCRIPTS.rglob("*.py")):
        if py.name in exempt:
            continue
        for i, line in enumerate(py.read_text().splitlines(), 1):
            st = line.strip()
            if needle in line and not st.startswith("#"):
                offenders.append(f"{py.relative_to(ROOT)}:{i}")
    assert not offenders, (
        "absolute Qwen layer indices outside the resolver:\n  " + "\n  ".join(offenders))


def test_no_model_key_constants() -> None:
    """No module-level constant holding a configs/models.yaml key.

    This is the most dangerous form of the pin and the last one found: two merge scripts
    carried `MODEL, LANG, RANK = "qwen25c-1.5b", "python", 32` at module level. Because the
    old panel's adapters still exist on disk, such a script does not fail -- it silently
    merges the WRONG model's adapters and writes the result under the current panel's name.
    Neither the HF-id check nor the argparse-default check can see it.
    """
    keys, _ = _model_keys_and_ids()
    assign = re.compile(r'^\s*[A-Z_][A-Z0-9_]*(?:\s*,\s*[A-Z_][A-Z0-9_]*)*\s*=.*?"([^"]+)"')
    offenders = []
    for py in list(SRC.rglob("*.py")) + list(SCRIPTS.rglob("*.py")):
        if py.name in ALLOWED:
            continue
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            # A dict literal keyed by model (e.g. EST_GPU_H = {"a": 1, "b": 2}) is a
            # per-model lookup TABLE, which is the correct way to hold per-model values --
            # the opposite of a pin. Only scalar/tuple assignments are flagged.
            if "= {" in line.replace(" ", "= {").replace("={", "= {"):
                continue
            m = assign.match(line)
            if m and m.group(1) in keys:
                offenders.append(f"{py.relative_to(ROOT)}:{i}: {m.group(1)}")
    assert not offenders, (
        "module-level constants pinning a model key:\n  " + "\n  ".join(offenders))
