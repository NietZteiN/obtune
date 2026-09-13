"""run_cell refuses a mixture arch on an engine without a mixture path -- and ONLY there.

The first version keyed on the arch alone and refused eval_mole's HFEngine, the one engine that
implements mixtures (job 392173, 2026-09-13). The check is on the engine."""
from types import SimpleNamespace
import pytest
from obtune.eval_vllm import assert_engine_implements, Engine


def _sys(arch): return SimpleNamespace(name="s", arch=arch)


def test_vllm_engine_refuses_mixture():
    class Vllm(Engine):
        def __init__(self): pass
    with pytest.raises(ValueError, match="mixture architecture"):
        assert_engine_implements(Vllm(), _sys("mole_uniform"))


def test_engine_with_mixture_path_is_allowed():
    assert_engine_implements(SimpleNamespace(supports_mixture=True), _sys("mole_router"))


def test_hf_engine_declares_mixture_path():
    from obtune.mole.eval_mole import HFEngine
    assert HFEngine.supports_mixture is True


def test_non_mixture_arch_is_allowed_everywhere():
    assert_engine_implements(SimpleNamespace(), _sys("mono"))
    assert_engine_implements(SimpleNamespace(supports_mixture=False), _sys("merge_ties"))
