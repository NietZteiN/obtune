"""`_extends` merges settings but must not silently add experimental arms.

Incident of 2026-08-11 (`log/cft-replication/2026-08-11_codebleu-scoring-hang.md`, second
addendum): `systems:` is a dict, `_deep_merge` recurses into dicts, so every
`unlearn/negation_*` config inherited a `cft` arm that appears nowhere in the file. At 7B
the inherited entry pointed at a 1.5B adapter and was reported under a real arm's label;
at 1.5B it tripped the §4.2 adapter guard and killed four evaluations.

Merge remains the DEFAULT — the SRH eval configs declare only their new arms and rely on
inheriting `base`/`sft`/`cft`, and their published tables contain those arms. `_replace`
is the opt-out for a config whose block is exhaustive.
"""
from __future__ import annotations

import textwrap

import pytest
import yaml

from obtune.config import CONFIG_DIR, _deep_merge, load_config


def _write(tmp_path, name: str, body: str):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body))
    return p


def test_dicts_merge_by_default(tmp_path) -> None:
    """Settings blocks must keep inheriting: a child overriding one engine key keeps the rest."""
    _write(tmp_path, "parent.yaml", """
        engine: {dtype: bfloat16, max_model_len: 4096, seed: 17}
        systems: {base: null, sft: a/path}
    """)
    child = _write(tmp_path, "child.yaml", """
        _extends: parent.yaml
        engine: {max_model_len: 8192}
    """)
    cfg = load_config(child)
    assert cfg["engine"] == {"dtype": "bfloat16", "max_model_len": 8192, "seed": 17}
    assert set(cfg["systems"]) == {"base", "sft"}


def test_replace_makes_a_block_exhaustive(tmp_path) -> None:
    """The bug: without _replace the child inherits `sft`, which it never declared."""
    _write(tmp_path, "parent.yaml", """
        engine: {dtype: bfloat16, seed: 17}
        systems: {base: null, sft: a/path, cft: another/path}
    """)
    merged = _write(tmp_path, "merged.yaml", """
        _extends: parent.yaml
        systems: {base: null, u_lam0: tv/path}
    """)
    replaced = _write(tmp_path, "replaced.yaml", """
        _extends: parent.yaml
        _replace: [systems]
        systems: {base: null, u_lam0: tv/path}
    """)
    assert set(load_config(merged)["systems"]) == {"base", "sft", "cft", "u_lam0"}
    assert set(load_config(replaced)["systems"]) == {"base", "u_lam0"}
    # _replace is scoped to the listed key only — everything else still merges.
    assert load_config(replaced)["engine"] == {"dtype": "bfloat16", "seed": 17}


def test_replace_accepts_a_bare_string(tmp_path) -> None:
    _write(tmp_path, "parent.yaml", "systems: {base: null, sft: a/path}\n")
    child = _write(tmp_path, "child.yaml", """
        _extends: parent.yaml
        _replace: systems
        systems: {only: me}
    """)
    assert set(load_config(child)["systems"]) == {"only"}


def test_replace_without_extends_is_an_error(tmp_path) -> None:
    """Silently ignoring it would let a typo'd `_extends` disable the guard invisibly."""
    child = _write(tmp_path, "child.yaml", "_replace: [systems]\nsystems: {a: b}\n")
    with pytest.raises(ValueError, match="_replace"):
        load_config(child)


def test_replace_applies_only_at_the_declared_level() -> None:
    """Listing `systems` must not reach into a nested dict that happens to share the name."""
    base = {"outer": {"systems": {"inherited": 1}}}
    override = {"outer": {"systems": {"mine": 2}}}
    out = _deep_merge(base, override, {"systems"})
    assert out["outer"]["systems"] == {"inherited": 1, "mine": 2}


@pytest.mark.parametrize("rel", sorted(
    str(p.relative_to(CONFIG_DIR)) for p in (CONFIG_DIR / "unlearn").glob("negation_*.yaml")
))
def test_unlearn_configs_declare_exactly_what_they_evaluate(rel: str) -> None:
    """No unlearning run may evaluate an arm that is not written in its own file.

    This is the regression guard on the incident. `cft` in particular must be absent:
    the unlearning sweep is FLIP - lambda*FWD and the contrastive arm plays no part in it.
    """
    declared = set((yaml.safe_load((CONFIG_DIR / rel).read_text()) or {}).get("systems", {}))
    resolved = set(load_config(rel)["systems"])
    assert resolved == declared, f"{rel} evaluates undeclared arm(s): {sorted(resolved - declared)}"
    assert "cft" not in resolved, f"{rel} still carries a cft arm"
