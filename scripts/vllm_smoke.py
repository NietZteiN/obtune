"""Guarded vLLM smoke test.

The 2026-08-28 verdict "NOT fixed for vLLM" came from /work/jvl210002/migration/gputest.py,
which builds LLM(...) at module top level. vLLM spawns its engine core, spawn re-imports the
main module, and the re-run of that line trips _check_not_importing_main -- a harness bug that
is indistinguishable, in the log, from an environment failure. This puts the engine
construction behind the guard so the environment is what actually gets tested.
"""
import os

# flashinfer JIT-compiles its sampling kernel on first use and needs nvcc/CUDA_HOME, which
# juno's compute nodes do not have ("Could not find nvcc and default cuda_home=
# '/usr/local/cuda' doesn't exist", job 359038). The pip env does ship nvidia/cuda_nvcc, but
# that is a CUDA 13 toolkit against a 12.4 driver -- the exact mismatch that broke this env
# once already. vLLM's native sampler needs no compiler, and every eval in this project is
# greedy (temperature=0), so the flashinfer path buys nothing to begin with.
os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")

import torch


def main() -> int:
    print("torch", torch.__version__, "| cuda build", torch.version.cuda, flush=True)
    print("cuda available:", torch.cuda.is_available(), flush=True)
    assert torch.cuda.is_available(), "CUDA STILL UNAVAILABLE"
    print("device:", torch.cuda.get_device_name(0), flush=True)

    from vllm import LLM, SamplingParams
    llm = LLM(model="Qwen/Qwen2.5-Coder-1.5B-Instruct", max_model_len=1024,
              gpu_memory_utilization=0.35, enforce_eager=True)
    out = llm.generate(["def f(x): return x*2\nf(21) = "],
                       SamplingParams(temperature=0, max_tokens=8))
    print("VLLM OK ->", repr(out[0].outputs[0].text), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
