"""Regression: distinct adapter paths must yield distinct vLLM `lora_name`s.

vLLM's prefix cache hashes KV blocks on `lora_name` (not `lora_int_id`). On 2026-09-03 the
name was `<parent>/<leaf>`, so every `<tag>/best` under runs/adapters, runs/adapters_formatonly
and runs/adapters_overtrain collided, and the second adapter evaluated in an engine decoded on
top of the first one's cached prefill. 28 cells were affected, including the CodeLlama H1
pilot's tuned_L0 row. This test pins the fix without needing vllm installed.
"""
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _fake_vllm():
    """A minimal stand-in so Engine.lora_request can run without vllm/GPU."""
    pkg = types.ModuleType("vllm")
    lora = types.ModuleType("vllm.lora")
    req = types.ModuleType("vllm.lora.request")

    class LoRARequest:
        def __init__(self, lora_name, lora_int_id, lora_path):
            self.lora_name, self.lora_int_id, self.lora_path = lora_name, lora_int_id, lora_path

    req.LoRARequest = LoRARequest
    lora.request = req
    pkg.lora = lora
    return {"vllm": pkg, "vllm.lora": lora, "vllm.lora.request": req}


def test_same_leaf_different_root_get_distinct_names(monkeypatch):
    for k, v in _fake_vllm().items():
        monkeypatch.setitem(sys.modules, k, v)
    from obtune.eval_vllm import Engine

    eng = Engine("dummy", {}, stub=True)
    a = eng.lora_request("runs/adapters/codellama-7b/python/L0_r32_s17/best")
    b = eng.lora_request("runs/adapters_formatonly/codellama-7b/python/L0_r32_s17/best")
    c = eng.lora_request("runs/adapters_overtrain/codellama-7b/python/L0_r32_s17/best")
    names = {a.lora_name, b.lora_name, c.lora_name}
    assert len(names) == 3, f"lora_name collision: {names}"
    assert len({a.lora_int_id, b.lora_int_id, c.lora_int_id}) == 3
    # the same path asked twice is the same adapter: same id, same name
    a2 = eng.lora_request("runs/adapters/codellama-7b/python/L0_r32_s17/best")
    assert (a2.lora_name, a2.lora_int_id) == (a.lora_name, a.lora_int_id)
