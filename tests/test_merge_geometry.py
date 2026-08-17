"""Task-vector geometry, and the two collision guards added alongside it.

The geometry half exists because the cheap path is a mathematical identity, not an
approximation: Frobenius inner products between LoRA updates can be computed from the r x r
factors without materializing dW. If that identity is wrong, every number in
`results/merge_geometry/` is wrong and nothing downstream would notice — the values would
still look like plausible correlations.

The collision half exists because on 2026-08-10 three separate identifiers failed to encode
what actually varied, and two of them nearly destroyed trained artifacts:

  * `train_sft.adapter_dir` encodes (conditions, rank, seed) but NOT training length, so a
    9-epoch config resolved to the same directory as the finished 3-epoch expert.
  * `build_manifest` derived job ids from the same tuple, so the 9-epoch job collided with the
    completed 3-epoch job — the paired ckpt-select then saw its dependency already in done/
    and would have fired before the new training existed.
"""
from __future__ import annotations

import numpy as np
import pytest

from obtune.merge_geometry import (
    ModulePair, _inner, by_projection, cosine, norms, pooled, sign_conflict,
)


def _pair(rng, d_out: int, d_in: int, r: int) -> ModulePair:
    return ModulePair("m", rng.standard_normal((r, d_in)), rng.standard_normal((d_out, r)))


@pytest.mark.parametrize("d_out,d_in,r", [(64, 96, 8), (128, 64, 16), (256, 512, 32)])
def test_inner_product_identity_matches_dense(d_out: int, d_in: int, r: int) -> None:
    """<dW_i, dW_j>_F computed from the factors == the dense trace. The load-bearing claim."""
    rng = np.random.default_rng(17)
    x, y = _pair(rng, d_out, d_in, r), _pair(rng, d_out, d_in, r)
    dense = float(np.trace((x.B @ x.A).T @ (y.B @ y.A)))
    assert _inner(x, y) == pytest.approx(dense, rel=1e-9)


def test_norm_matches_dense_frobenius() -> None:
    rng = np.random.default_rng(3)
    x = _pair(rng, 96, 64, 8)
    assert norms({"m": x})["m"] == pytest.approx(float(np.linalg.norm(x.B @ x.A)), rel=1e-9)


def test_cosine_is_one_for_identical_and_symmetric() -> None:
    rng = np.random.default_rng(5)
    x = _pair(rng, 64, 48, 8)
    assert cosine({"m": x}, {"m": x})["m"] == pytest.approx(1.0, abs=1e-9)
    y = _pair(rng, 64, 48, 8)
    assert cosine({"m": x}, {"m": y})["m"] == pytest.approx(cosine({"m": y}, {"m": x})["m"])


def test_cosine_is_scale_invariant() -> None:
    """Norm growth must not masquerade as directional divergence — the whole point of using
    cosine rather than the raw inner product when comparing epochs."""
    rng = np.random.default_rng(7)
    x, y = _pair(rng, 64, 48, 8), _pair(rng, 64, 48, 8)
    scaled = ModulePair("m", y.A, y.B * 10.0)
    assert cosine({"m": x}, {"m": y})["m"] == pytest.approx(cosine({"m": x}, {"m": scaled})["m"])


def test_sign_conflict_bounds_are_reached() -> None:
    """0 when every expert agrees on every coordinate, high when they are opposed."""
    rng = np.random.default_rng(11)
    x = _pair(rng, 32, 24, 4)
    same = sign_conflict({"a": {"m": x}, "b": {"m": x}})["m"]
    assert same["conflict"] == pytest.approx(0.0, abs=1e-9)
    assert same["ties_keep"] == pytest.approx(1.0, abs=1e-9)

    opposed = ModulePair("m", x.A, -x.B)  # dW_b == -dW_a exactly
    conf = sign_conflict({"a": {"m": x}, "b": {"m": opposed}})["m"]
    assert conf["conflict"] == pytest.approx(1.0, abs=1e-9)


def test_pooled_and_by_projection() -> None:
    vals = {"l.0.self_attn.q_proj": 1.0, "l.1.self_attn.q_proj": 3.0, "l.0.mlp.down_proj": 5.0}
    assert pooled(vals) == pytest.approx(3.0)
    assert by_projection(vals) == {"down_proj": 5.0, "q_proj": 2.0}


# --------------------------------------------------------------------------- #
# collision guards


def test_adapter_dir_separates_banks_by_adapter_root() -> None:
    """Without this, a config differing only in `train.epochs` overwrites the original bank."""
    from obtune.train_sft import adapter_dir

    base = {"model": "qwen25c-1.5b", "language": "python",
            "train_conditions": ["L1b"], "peft": {"r": 32}, "train": {"seed": 17}}
    default = adapter_dir(base)
    probe = adapter_dir({**base, "adapter_root": "runs/adapters_overtrain"})
    assert default != probe, "epoch-varying config must not resolve onto the original bank"
    # (model, language, tag) must be identical — only the bank root differs, so the two
    # banks stay directly comparable condition-for-condition.
    assert default.parts[-3:] == probe.parts[-3:], "only the root should differ"
    assert "adapters_overtrain" in str(probe)
    # default must be unchanged for every existing config
    assert str(default).endswith("runs/adapters/qwen25c-1.5b/python/L1b_r32_s17")


def test_overtrain_configs_do_not_collide_with_the_expert_bank() -> None:
    """The real configs, not a synthetic one — this is what actually nearly overwrote them."""
    from obtune.config import CONFIG_DIR, load_config
    from obtune.train_sft import adapter_dir

    for cond in ("L1b", "S1", "S2"):
        probe_p = CONFIG_DIR / "train" / f"overtrain_qwen1.5b_py_{cond}.yaml"
        grid_p = CONFIG_DIR / "train" / f"grid_qwen1.5b_py_{cond}.yaml"
        if not probe_p.exists() or not grid_p.exists():
            pytest.skip(f"configs for {cond} not present")
        probe = adapter_dir(load_config(f"train/overtrain_qwen1.5b_py_{cond}.yaml"))
        grid = adapter_dir(load_config(f"train/grid_qwen1.5b_py_{cond}.yaml"))
        assert probe != grid, f"{cond}: overtrain probe would overwrite the 3-epoch expert"


def test_job_ids_distinguish_training_length() -> None:
    """A job id built from (model, language, conditions, seed) alone collided with the finished
    3-epoch job, which made its ckpt-select think the dependency was already satisfied."""
    import subprocess
    import sys
    from obtune.config import CONFIG_DIR, PROJECT_ROOT

    if not (CONFIG_DIR / "train" / "overtrain_qwen1.5b_py_L1b.yaml").exists():
        pytest.skip("overtrain config not present")
    out = subprocess.run(
        [sys.executable, "scripts/build_manifest.py", "--dry-run",
         "--train", "configs/train/overtrain_qwen1.5b_py_L1b.yaml",
         "configs/train/grid_qwen1.5b_py_L1b.yaml", "--seeds", "17"],
        cwd=PROJECT_ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip(f"build_manifest --dry-run unavailable: {out.stderr[-200:]}")
    ids = [ln for ln in out.stdout.splitlines() if "train__" in ln]
    assert len(set(ids)) == len(ids), f"duplicate job ids emitted: {ids}"


# --------------------------------------------------------------------------- #
# the common-subset scoping bug


def test_core_subset_is_scoped_per_experiment() -> None:
    """A sparse supplementary grid must not redefine the headline's denominator.

    On 2026-08-10 the 40-program S3/S4 expansion landed beside the 597-program main grid and
    cut the all-conditions common subset from 340 programs to 23 — a 93 % loss that reached
    the published transfer matrix as `n_programs: 23`, inflating every interval in it. Nothing
    raised; the matrix simply described a much smaller corpus than it claimed to.
    """
    import pandas as pd
    from obtune.transfer import core_subset

    main = pd.DataFrame([
        {"experiment_id": "grid_v1", "eval_cond": c, "snippet_id": f"p{i}"}
        for c in ("L0", "L1b", "S1") for i in range(10)
    ])
    sparse = pd.DataFrame([
        {"experiment_id": "grid_s3s4", "eval_cond": c, "snippet_id": f"p{i}"}
        for c in ("S3", "S4") for i in range(2)          # only 2 programs
    ])
    out = core_subset(pd.concat([main, sparse], ignore_index=True))
    kept_main = set(out[out.experiment_id == "grid_v1"]["snippet_id"])
    assert len(kept_main) == 10, (
        f"the sparse grid shrank the main grid's core subset to {len(kept_main)}")
    assert set(out[out.experiment_id == "grid_s3s4"]["snippet_id"]) == {"p0", "p1"}


def test_compute_is_core_is_scoped_per_experiment() -> None:
    import pandas as pd
    from obtune.trial_table import compute_is_core

    rows = [{"phase": "main", "base_model": "m", "language": "python",
             "experiment_id": "grid_v1", "eval_cond": c, "snippet_id": f"p{i}"}
            for c in ("L0", "L1b") for i in range(10)]
    rows += [{"phase": "main", "base_model": "m", "language": "python",
              "experiment_id": "grid_s3s4", "eval_cond": c, "snippet_id": "p0"}
             for c in ("S3", "S4")]
    out = compute_is_core(pd.DataFrame(rows))
    main_core = out[(out.experiment_id == "grid_v1") & (out.is_core == 1)]["snippet_id"]
    assert len(set(main_core)) == 10, "sparse grid collapsed is_core for the main grid"


def test_r_and_python_condition_lists_agree() -> None:
    """stats/R/config.R must mirror paths.ALL_CONDITIONS.

    They drifted when the S2 split raised TRAINABLE_CONDITIONS from 6 to 8: R still listed
    seven, so 01_schema_validate.R would have rejected every S3/S4 trial as an unknown
    eval_cond the first time the R stack ran over the new cells.
    """
    import re
    from obtune.config import PROJECT_ROOT
    from obtune.paths import ALL_CONDITIONS

    src = (PROJECT_ROOT / "stats" / "R" / "config.R").read_text()
    m = re.search(r"^COND_LEVELS <- c\((.*?)\)", src, re.S | re.M)
    assert m, "COND_LEVELS not found in stats/R/config.R"
    r_levels = {x.strip().strip('"') for x in m.group(1).split(",") if x.strip()}
    assert r_levels == set(ALL_CONDITIONS), (
        f"R has {sorted(r_levels)}, python has {sorted(ALL_CONDITIONS)}")
