"""Regression tests for the five RQ2 defects that made the whole chain fail silently.

Every one of these was a *silent* failure: the merges completed with returncode 0 and
produced byte-identical adapters; the route map was written in a format the evaluator
could not read; oracle routing was configured and never ran. None of them raised, so none
of them would have been noticed in the results — only in their absence.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from obtune.config import PROJECT_ROOT

ROOT = Path(__file__).resolve().parents[1]


def _build_manifest():
    spec = importlib.util.spec_from_file_location("bm", ROOT / "scripts" / "build_manifest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rq2():
    return _build_manifest().rq2_jobs(Path("configs/eval/grid_v1.yaml"))


# --------------------------------------------------------------------------- #
# 1. The three merges must actually be three different merges

def test_merge_jobs_pass_distinct_combination_types(rq2):
    """All three merges on disk were byte-identical TIES: `merge_adapters.main` had no
    `--combination-type` flag and read `ties` from the config, while the combo survived
    only in `job["meta"]`, which nothing consumed."""
    merges = [j for j in rq2 if j["kind"] == "merge" and "qwen25c-1.5b_python" in j["job_id"]]
    assert len(merges) == 3
    passed = []
    for j in merges:
        argv = j["argv"]
        assert "--combination-type" in argv, f"{j['job_id']} would silently re-run TIES"
        passed.append(argv[argv.index("--combination-type") + 1])
    assert sorted(passed) == ["dare_linear", "dare_ties", "ties"]
    # ...and each still declares the same thing in its meta, so the two cannot drift.
    assert sorted(j["meta"]["combination_type"] for j in merges) == sorted(passed)


def test_merge_cli_override_beats_the_config():
    from obtune import merge_adapters

    src = (ROOT / "src" / "obtune" / "merge_adapters.py").read_text()
    assert "--combination-type" in src
    assert 'args.combination_type or cfg["combination_type"]' in src
    assert hasattr(merge_adapters, "MergeSpec")


# --------------------------------------------------------------------------- #
# 2. Two feature sets: the router trains on train pairs, routes eval items

def test_router_features_jobs_have_inputs(rq2):
    """The emitted job used to carry no `--train-jsonl` at all, so it exited
    `no rows` — the actual first failure in the chain."""
    feats = [j for j in rq2 if j["job_id"].startswith("router_features")
             and "qwen25c-1.5b_python" in j["job_id"]]
    assert len(feats) == 2, "expected a train feature job and an eval feature job"
    by_stage = {j["meta"]["stage"]: j for j in feats}
    assert set(by_stage) == {"features_train", "features_eval"}

    train_argv = by_stage["features_train"]["argv"]
    assert "--train-jsonl" in train_argv
    assert any("data/train/pairs/" in a for a in train_argv)

    eval_argv = by_stage["features_eval"]["argv"]
    assert "--eval-jsonl" in eval_argv
    assert any("data/eval/" in a for a in eval_argv)
    assert "--train-jsonl" not in eval_argv, "eval features must not be read as training data"


def test_router_trains_on_train_features_and_routes_eval_features(rq2):
    """Routing decisions are made on EVAL items. A single features.npz for both meant the
    router routed the very rows it was fitted on."""
    jobs = {j["job_id"]: j for j in rq2}
    tr = jobs["router_train__qwen25c-1.5b_python"]["argv"]
    ro = jobs["router_route__qwen25c-1.5b_python"]["argv"]
    assert tr[tr.index("--features") + 1].endswith("features_train.npz")
    assert ro[ro.index("--features") + 1].endswith("features_eval.npz")


# --------------------------------------------------------------------------- #
# 3. The route map must be the JSON the evaluator reads

def test_route_job_writes_parquet_and_json_separately(rq2):
    """`route.py` wrote a parquet to the `.json` path the evaluator then `json.load`ed."""
    argv = {j["job_id"]: j["argv"] for j in rq2}["router_route__qwen25c-1.5b_python"]
    assert argv[argv.index("--out") + 1].endswith(".parquet")
    assert argv[argv.index("--route-map") + 1].endswith("route_map.json")


def test_eval_route_map_path_matches_what_route_writes(rq2):
    jobs = {j["job_id"]: j for j in rq2}
    written = jobs["router_route__qwen25c-1.5b_python"]["argv"]
    consumed = jobs["evalrq2__qwen25c-1.5b_python_router"]["argv"]
    assert (written[written.index("--route-map") + 1]
            == consumed[consumed.index("--route-map") + 1])


def test_route_map_is_item_id_to_adapter():
    """The exact shape `eval_vllm._load_route_map` requires."""
    src = (ROOT / "src" / "obtune" / "router" / "route.py").read_text()
    assert 'r["item_id"]: r["adapter"]' in src


# --------------------------------------------------------------------------- #
# 4. adapter_map.json is materialized — but never during a dry run

def test_adapter_map_is_written_from_job_meta(tmp_path, monkeypatch, rq2):
    bm = _build_manifest()
    monkeypatch.setattr(bm, "PROJECT_ROOT", tmp_path)
    written = bm.write_adapter_maps(rq2)
    assert written, "no adapter map was materialized"
    for p in written:
        amap = json.loads(p.read_text())
        assert amap and all(isinstance(v, str) for v in amap.values())
        assert "H1" not in amap, "H1 has no adapter and must never appear in a route target"


def test_rq2_jobs_is_side_effect_free(rq2):
    """`--dry-run` must write nothing. Materialization belongs in main(), not in the
    job-listing function."""
    src = (ROOT / "scripts" / "build_manifest.py").read_text()
    body = src.split("def rq2_jobs")[1].split("\ndef ")[0]
    assert "write_text" not in body
    assert "mkdir" not in body


# --------------------------------------------------------------------------- #
# 5. Oracle routing exists, and cannot contaminate RQ1

def test_oracle_routing_builds_an_adapter_map():
    from obtune.eval_vllm import expand_systems

    (spec,) = expand_systems(
        [{"name": "oracle_routing", "arch": "oracle_route", "oracle_route": True}],
        "qwen25c-1.5b", "python", ["L0", "L1b", "L1r", "L2", "S1", "S2"], [17],
    )
    assert spec.is_oracle_routed
    assert set(spec.adapter_map) == {"L0", "L1b", "L1r", "L2", "S1", "S2"}
    assert "H1" not in spec.adapter_map


def test_oracle_routing_is_not_labelled_per_type():
    """`stats/R/03_rq1_transfer.R` selects the RQ1 transfer matrix with
    `adapter_arch == "per_type"`. Labelling this RQ2 upper-bound system `per_type` would
    fold it into the RQ1 headline."""
    import yaml

    cfg = yaml.safe_load((ROOT / "configs" / "eval" / "grid_v1.yaml").read_text())
    row = next(r for r in cfg["systems"] if r["name"] == "oracle_routing")
    assert row["arch"] == "oracle_route"

    from obtune.schema import TrialRow

    assert "oracle_route" in TrialRow.model_fields["adapter_arch"].annotation.__args__
    assert 'ARCHS <- c(' in (ROOT / "stats" / "R" / "config.R").read_text()
    assert '"oracle_route"' in (ROOT / "stats" / "R" / "config.R").read_text()


def test_a_tuned_system_with_no_adapter_is_still_refused():
    """The exemption for oracle routing must not weaken the guard that catches a
    per-type system silently evaluating base weights.

    The guard now lives in `validate_systems` (run after the --systems filter) rather
    than inside `expand_systems`; it must still refuse.
    """
    from obtune.eval_vllm import expand_systems, validate_systems

    out = expand_systems([{"name": "bad", "arch": "per_type"}],
                         "qwen25c-1.5b", "python", ["L0"], [17])
    with pytest.raises(ValueError, match="no adapter path"):
        validate_systems(out)


def test_oracle_route_without_a_map_is_refused():
    from obtune.eval_vllm import SystemSpec, expand_systems

    out = expand_systems([{"name": "o", "arch": "oracle_route", "oracle_route": True}],
                         "qwen25c-1.5b", "python", ["L0"], [17])
    out[0].adapter_map = None
    with pytest.raises(ValueError, match="no adapter_map"):
        for spec in out:
            if spec.oracle_route and not spec.adapter_map:
                raise ValueError("system 'o' sets oracle_route but has no adapter_map")
    assert SystemSpec(name="x").adapter_map is None


# --------------------------------------------------------------------------- #
# Task vectors

def test_task_vector_scaling_is_exact_on_lora_b_only():
    import torch

    from obtune import taskvec

    tv = taskvec.TaskVector(
        name="t", path=Path("/tmp"), config={"r": 32, "lora_alpha": 64},
        tensors={"m.lora_A.weight": torch.ones(2, 2), "m.lora_B.weight": torch.ones(2, 2)},
    )
    neg = taskvec.negate(tv)
    assert torch.allclose(neg.tensors["m.lora_A.weight"], torch.ones(2, 2))
    assert torch.allclose(neg.tensors["m.lora_B.weight"], -torch.ones(2, 2))
    assert tv.scaling == 2.0


def test_task_vector_refuses_dora_and_rslora():
    from obtune import taskvec

    for flag in ("use_dora", "use_rslora"):
        with pytest.raises(ValueError, match=flag):
            taskvec._assert_plain_lora({flag: True}, "test")
    taskvec._assert_plain_lora({"use_dora": False, "use_rslora": False}, "test")  # no raise


def test_task_vector_path_guard_rejects_h1_and_quarantine():
    from obtune import taskvec

    for bad in ("runs/adapters/m/python/H1_r32_s17/best", "data/quarantine/h1/x"):
        with pytest.raises(ValueError, match="held-out H1|quarantine"):
            taskvec._assert_no_h1_path(PROJECT_ROOT / bad)
    # an arm name that merge_adapters._assert_no_h1 would wrongly reject must pass here
    taskvec._assert_no_h1_path(PROJECT_ROOT / "runs/adapters_srh/m/python/all5_flip_r32_s17")


def test_task_vector_rank_guard():
    from obtune import taskvec

    taskvec.assert_servable_rank(64, 64)
    with pytest.raises(ValueError, match="max_lora_rank"):
        taskvec.assert_servable_rank(192, 64)


def test_task_vector_uses_cat_not_linear():
    """PEFT's `linear` puts sqrt(|w*s|) on A and B separately, so the reconstruction picks
    up cross terms B_i A_j and is not task arithmetic for more than one adapter.

    Asserted on the actual call node, not on the file text — the module docstring names
    `linear` precisely to explain why it is wrong, so a substring check would either fail
    on the explanation or pass on a stale one.
    """
    import ast

    tree = ast.parse((ROOT / "src" / "obtune" / "taskvec.py").read_text())
    combos = [
        kw.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "attr", "") == "add_weighted_adapter"
        for kw in node.keywords
        if kw.arg == "combination_type" and isinstance(kw.value, ast.Constant)
    ]
    assert combos == ["cat"], f"expected the merge call to use 'cat', got {combos}"


# --------------------------------------------------------------------------- #
# Failures found by actually running the queue

def test_systems_are_validated_after_filtering_not_before():
    """28 eval-cell and 8 eval-rq2 jobs failed without ever loading a model because
    `expand_systems` validated EVERY row in the config — so a job asking only for `base`
    died on the config's `router` row, which it was never going to run."""
    from obtune.config import load_config
    from obtune.eval_vllm import expand_systems, validate_systems

    cfg = load_config("eval/grid_rq1.yaml")
    out = expand_systems(cfg["systems"], "qwen25c-1.5b", "javascript",
                         cfg["train_conditions"], cfg.get("seeds", [17]))
    # expansion itself must not raise, even though `router` has no route map
    assert any(s.arch == "router" for s in out)

    base_only = [s for s in out if s.name == "base"]
    validate_systems(base_only)  # the actual job — must pass

    # ...but the guard must still fire when that system IS selected
    with pytest.raises(ValueError, match="no route map"):
        validate_systems([s for s in out if s.arch == "router"])


def test_run_grid_refuses_a_systems_filter_that_matches_nothing():
    src = (ROOT / "src" / "obtune" / "eval_vllm.py").read_text()
    assert "selected nothing from" in src, (
        "a --systems typo should fail loudly, not silently evaluate zero cells"
    )


def test_router_features_does_not_build_a_language_model_head():
    """`extract_features` only reads hidden states, but AutoModelForCausalLM also
    computes [batch, seq, vocab] logits — 32 x 1536 x 151936 in bf16 is ~14 GB, which
    OOM'd the feature job on a 48 GB card."""
    import ast

    src = (ROOT / "src" / "obtune" / "router" / "features.py").read_text()
    tree = ast.parse(src)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "transformers"
        for alias in node.names
    }
    assert "AutoModel" in imported
    assert "AutoModelForCausalLM" not in imported


def test_worker_respects_declared_dependencies():
    """`depends_on` was recorded by build_manifest and read by nothing.

    Priorities order the queue but do not sequence it: two jobs at the same priority
    start together on different workers, so `router_train` began before
    `router_features` had written its .npz. Eight jobs failed that way, none of them a
    code fault.
    """
    from obtune.sched.worker import Job, dependencies_met

    dep = Job(job_id="b", kind="train", argv=[], meta={"depends_on": "a"})
    assert not dependencies_met(dep, set())
    assert dependencies_met(dep, {"a"})

    multi = Job(job_id="c", kind="train", argv=[], meta={"depends_on": ["a", "b"]})
    assert not dependencies_met(multi, {"a"})
    assert dependencies_met(multi, {"a", "b"})

    assert dependencies_met(Job(job_id="d", kind="train", argv=[], meta={}), set())


def test_rq2_chain_declares_its_dependencies(rq2):
    """The ordering the worker now enforces has to actually be declared."""
    jobs = {j["job_id"]: j for j in rq2}
    chain = {
        "router_train__qwen25c-1.5b_python": "router_features_train__qwen25c-1.5b_python",
        "router_route__qwen25c-1.5b_python": [
            "router_train__qwen25c-1.5b_python",
            "router_features_eval__qwen25c-1.5b_python",
        ],
        "evalrq2__qwen25c-1.5b_python_router": "router_route__qwen25c-1.5b_python",
        "evalrq2__qwen25c-1.5b_python_merge_ties": "merge__qwen25c-1.5b_python__ties",
    }
    for job_id, expected in chain.items():
        assert jobs[job_id]["meta"]["depends_on"] == expected, job_id


def test_eval_output_path_is_model_qualified():
    """Date + language is not a unique key for a result.

    A 7B run overwrote a completed 1.5B run's 21,000-row trials.jsonl because both wrote
    to `results/<date>_cft-bidirectional/python/`. The model must be in the path.
    """
    src = (ROOT / "src" / "obtune" / "cft" / "evaluate.py").read_text()
    assert 'str(cfg["model"])' in src, "output dir must include the model key"
