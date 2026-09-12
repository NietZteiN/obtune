# Does vLLM start on the h100 MIG node (g-06-01) now that VLLM_WORKER_MULTIPROC_METHOD=spawn is
# set in scripts/env.sh? That node was excluded from every obtune job on 2026-09-10 after two
# checkpoint-select jobs died 28 min in with "Cannot re-initialize CUDA in forked subprocess".
# The exclusion costs 4 idle 47 GB slices on a partition that is otherwise 100% allocated, so
# the fix is worth retesting rather than carrying the exclusion forward indefinitely.
import os
print("multiproc:", os.environ.get("VLLM_WORKER_MULTIPROC_METHOD"), flush=True)
import torch
print("cuda:", torch.cuda.is_available(), torch.cuda.get_device_name(0),
      f"{torch.cuda.get_device_properties(0).total_memory/2**30:.1f} GiB", flush=True)
from vllm import LLM, SamplingParams
llm = LLM(model="codellama/CodeLlama-7b-Instruct-hf", dtype="bfloat16",
          gpu_memory_utilization=0.85, max_model_len=2048, enforce_eager=True)
out = llm.generate(["def add(a, b):\n    return"], SamplingParams(temperature=0, max_tokens=8))
print("GENERATED:", repr(out[0].outputs[0].text), flush=True)
print("MIG_PROBE_PASS", flush=True)
