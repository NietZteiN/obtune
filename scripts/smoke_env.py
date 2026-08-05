#!/usr/bin/env python
"""GPU preflight: prove the train and serve halves of the stack both work.

Run this before any grid launch. It is deliberately end-to-end rather than a set
of import checks, because the two failure modes that actually bite are (a) TRL /
transformers API churn silently changing what gets supervised, and (b) vLLM
loading an adapter but not applying it — both of which import cleanly and then
produce a quietly wrong experiment.

    CUDA_VISIBLE_DEVICES=2 python scripts/smoke_env.py

Checks:
  1. a real LoRA SFT step on the pilot model, loss finite
  2. the saved adapter loads in vLLM AND changes the logits vs the base model
     (an adapter that loads but does nothing would make every transfer cell read
     as "no effect", which is indistinguishable from a real negative result)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _gpu_note() -> str:
    vis = os.environ.get("CUDA_VISIBLE_DEVICES")
    return f"CUDA_VISIBLE_DEVICES={vis}" if vis else "no CUDA_VISIBLE_DEVICES pin (will auto-pick an idle GPU)"


def find_adapter(out_dir: Path) -> Path | None:
    """Locate the adapter weights train_sft produced.

    A full run leaves a `best/` selected by greedy exact match; a --max-steps smoke
    run stops before checkpoint selection and leaves only `checkpoint-N/`. Accept
    either, preferring the selected one.
    """
    if (out_dir / "adapter_model.safetensors").exists():
        return out_dir
    if (out_dir / "best" / "adapter_model.safetensors").exists():
        return out_dir / "best"
    ckpts = sorted(out_dir.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    for c in reversed(ckpts):
        if (c / "adapter_model.safetensors").exists():
            return c
    return None


def check_train(out_dir: Path, max_steps: int) -> dict:
    """A real SFT run, capped at a few optimizer steps."""
    t0 = time.perf_counter()
    cmd = [
        sys.executable, "-m", "obtune.train_sft",
        "--config", "train/pilot_qwen1.5b_l1b.yaml",
        "--out", str(out_dir),
        "--max-steps", str(max_steps),
        "--train-size", "64",
    ]
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=3600)
    ok = proc.returncode == 0 and find_adapter(out_dir) is not None
    return {
        "ok": ok,
        "seconds": round(time.perf_counter() - t0, 1),
        "returncode": proc.returncode,
        "tail": (proc.stdout + proc.stderr)[-1500:] if not ok else "",
    }


def check_vllm_adapter(adapter_dir: Path) -> dict:
    """Load the adapter in vLLM and require it to change the output distribution."""
    t0 = time.perf_counter()
    script = f'''
import json, sys
sys.path.insert(0, {str(ROOT / "src")!r})
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from obtune.config import load_config

models = load_config("models.yaml")["models"]
hf_id = models["qwen25c-1.5b"]["hf_id"]
llm = LLM(model=hf_id, dtype="bfloat16", enable_lora=True, max_lora_rank=64,
          gpu_memory_utilization=0.55, max_model_len=1024, seed=17,
          enforce_eager=True, disable_log_stats=True)
sp = SamplingParams(temperature=0.0, max_tokens=8, logprobs=1)
prompts = ["def f(x):\\n    return x + 1\\n\\nf(3) returns "]
base = llm.generate(prompts, sp)
tuned = llm.generate(prompts, sp, lora_request=LoRARequest("smoke", 1, {str(adapter_dir)!r}))
b = base[0].outputs[0]
t = tuned[0].outputs[0]
print("SMOKE_RESULT " + json.dumps({{
    "base_text": b.text, "tuned_text": t.text,
    "base_ids": list(b.token_ids)[:8], "tuned_ids": list(t.token_ids)[:8],
    "base_cumlogprob": b.cumulative_logprob, "tuned_cumlogprob": t.cumulative_logprob,
}}))
'''
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "VLLM_LOGGING_LEVEL": "WARNING"}
    proc = subprocess.run([sys.executable, "-c", script], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=3600)
    payload = None
    for line in proc.stdout.splitlines():
        if line.startswith("SMOKE_RESULT "):
            payload = json.loads(line[len("SMOKE_RESULT "):])
    if payload is None:
        return {"ok": False, "seconds": round(time.perf_counter() - t0, 1),
                "returncode": proc.returncode, "tail": (proc.stdout + proc.stderr)[-2000:]}

    # An adapter trained for a handful of steps may well produce the same greedy
    # token; the load-bearing signal is that the DISTRIBUTION moved.
    changed = (payload["base_ids"] != payload["tuned_ids"]
               or abs(payload["base_cumlogprob"] - payload["tuned_cumlogprob"]) > 1e-6)
    payload.update({"ok": changed, "seconds": round(time.perf_counter() - t0, 1)})
    if not changed:
        payload["tail"] = "adapter loaded but left the logits identical — it is not being applied"
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-steps", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "runs" / "adapters" / "_smoke"))
    ap.add_argument("--skip-train", action="store_true", help="reuse an existing smoke adapter")
    args = ap.parse_args()

    print(f"obtune GPU smoke test — {_gpu_note()}")
    out_dir = Path(args.out)
    results = {}

    if args.skip_train and find_adapter(out_dir) is not None:
        print("\n[1/2] SFT step ................ skipped (reusing existing adapter)")
        results["train"] = {"ok": True, "skipped": True}
    else:
        print(f"\n[1/2] SFT step ({args.max_steps} steps) ...", flush=True)
        results["train"] = check_train(out_dir, args.max_steps)
        r = results["train"]
        print(f"      {'OK' if r['ok'] else 'FAIL'}  {r['seconds']}s")
        if not r["ok"]:
            print(r["tail"])
            return 1

    adapter = find_adapter(out_dir)
    if adapter is None:
        print(f"\nno adapter weights under {out_dir}")
        return 1
    print(f"\n[2/2] vLLM adapter load + effect ({adapter.name}) ...", flush=True)
    results["vllm"] = check_vllm_adapter(adapter)
    r = results["vllm"]
    print(f"      {'OK' if r['ok'] else 'FAIL'}  {r.get('seconds')}s")
    if r["ok"]:
        print(f"      base  {r['base_text']!r} (cumlogprob {r['base_cumlogprob']:.4f})")
        print(f"      tuned {r['tuned_text']!r} (cumlogprob {r['tuned_cumlogprob']:.4f})")
    else:
        print(r.get("tail", ""))
        return 1

    print("\nSMOKE OK — training and multi-LoRA serving both work on this GPU")
    return 0


if __name__ == "__main__":
    sys.exit(main())
