#!/usr/bin/env python
"""B7: what each arm actually costs to deploy.

    python scripts/analysis/80_deployment_cost.py <model>

The paper's defence against the router is that the merge is cheaper to deploy. That claim
currently carries no number. This measures three, per arm, on one GPU:

  stored parameters   trainable parameters shipped alongside the base model
  peak memory         torch.cuda.max_memory_allocated across a fixed decode workload
  throughput          generated tokens per second on that same workload

Arms: untuned, a single LoRA, the six-way merge, and the router. The router's cost is the
point of the table -- it must hold every expert resident and run a gate per token, where the
merge ships ONE adapter the same size as a single LoRA. Measured, not asserted.

Identical prompts, identical decode settings, identical token budget for every arm, so the
only difference is the arm. Greedy, as every eval here is.
"""
from __future__ import annotations
import sys, json, time, gc
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"src"))

N_PROMPTS, MAX_NEW = 32, 64
N_WARM, N_TIMED = 3, 3
EXPERTS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"]
SHORT = {"codellama-7b": "codellama7b", "codellama-13b": "codellama13b",
         "codellama-34b": "codellama34b", "llama31-8b": "llama318b",
         "granite31-8b": "granite318b", "codegemma-7b": "codegemma7b",
         "gemma3-12b": "gemma312b", "starcoder2-15b": "starcoder215b"}

def _params(d: Path) -> int:
    from safetensors.torch import load_file
    f = d/"adapter_model.safetensors"
    if not f.exists(): return 0
    return sum(t.numel() for t in load_file(str(f)).values())

def main() -> int:
    import torch, yaml
    from transformers import AutoModelForCausalLM, AutoTokenizer
    m = sys.argv[1] if len(sys.argv) > 1 else "codellama-7b"
    reg = yaml.safe_load((ROOT/"configs/models.yaml").read_text()); reg = reg.get("models", reg)
    base_id = reg[m]["hf_id"]
    root = ROOT/f"runs/adapters/{m}/python"

    arms = [("untuned", None),
            ("single LoRA", root/"L0_r32_s17"/"best"),
            ("merge", root/"merge_dare_ties_r32_s17")]
    tok = AutoTokenizer.from_pretrained(base_id)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    prompts = ["def f(x):\n    return x * 2\n\n# f(21) returns"] * N_PROMPTS
    enc = tok(prompts, return_tensors="pt", padding=True).to("cuda")

    def timed(model):
        """Median of N_TIMED runs after N_WARM warm-ups.

        A single warm-up is not enough: the FIRST arm measured pays one-off CUDA context and
        autotuning costs, which made the untuned model read 489 tok/s against 1045 for both
        adapter arms -- i.e. adding an adapter appeared to double throughput. Warming properly
        and taking a median removes it.
        """
        import statistics
        with torch.no_grad():
            for _ in range(N_WARM):
                model.generate(**enc, max_new_tokens=8, do_sample=False)
        rates = []
        for _ in range(N_TIMED):
            torch.cuda.synchronize(); t0 = time.perf_counter()
            with torch.no_grad():
                g = model.generate(**enc, max_new_tokens=MAX_NEW, do_sample=False)
            torch.cuda.synchronize(); dt = time.perf_counter() - t0
            rates.append(int((g.shape[1] - enc["input_ids"].shape[1]) * g.shape[0]) / dt)
        return statistics.median(rates)

    out = {}
    for name, adapter in arms:
        gc.collect(); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        model = AutoModelForCausalLM.from_pretrained(base_id, dtype=torch.bfloat16, device_map="cuda")
        if adapter is not None:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, str(adapter))
        model.eval()
        out[name] = dict(stored_params=_params(adapter) if adapter else 0,
                         peak_mem_gb=round(torch.cuda.max_memory_allocated()/2**30, 2),
                         tokens_per_s=round(timed(model), 1), n_prompts=N_PROMPTS, max_new=MAX_NEW)
        print(f"  {name:14s} params {out[name]['stored_params']:>12,}  "
              f"peak {out[name]['peak_mem_gb']:>6.2f} GB  {out[name]['tokens_per_s']:>8.1f} tok/s")
        del model; gc.collect(); torch.cuda.empty_cache()

    # The router is the comparison the paper's cost defence rests on, so it cannot be omitted:
    # it holds EVERY expert resident and runs a gate per token, where the merge ships one
    # adapter the size of a single LoRA.
    gate_p = ROOT/f"runs/mole/{m}/python/routerlora_{SHORT[m]}_s17/gate.pt"
    if gate_p.exists():
        try:
            from obtune.mole.model import build_mole_model
            paths = {c: str(root/f"{c}_r32_s17"/"best") for c in EXPERTS
                     if (root/f"{c}_r32_s17"/"best").exists()}
            gc.collect(); torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
            gate_sd = torch.load(gate_p, map_location="cpu")
            holder = build_mole_model(m, paths, d_router=64, shared_query=False, device_map="cuda")
            if hasattr(holder.gate, "load_state_dict"):
                holder.gate.load_state_dict(gate_sd if not isinstance(gate_sd, dict)
                                            or "state_dict" not in gate_sd else gate_sd["state_dict"])
            holder.model.eval()
            stored = sum(_params(root/f"{c}_r32_s17"/"best") for c in paths)
            stored += sum(t.numel() for t in (gate_sd.values() if isinstance(gate_sd, dict) else [])
                          if hasattr(t, "numel"))
            out["router"] = dict(stored_params=stored, n_experts=len(paths),
                                 peak_mem_gb=round(torch.cuda.max_memory_allocated()/2**30, 2),
                                 tokens_per_s=round(timed(holder.model), 1),
                                 n_prompts=N_PROMPTS, max_new=MAX_NEW)
            print(f"  {'router':14s} params {stored:>12,}  "
                  f"peak {out['router']['peak_mem_gb']:>6.2f} GB  "
                  f"{out['router']['tokens_per_s']:>8.1f} tok/s  ({len(paths)} experts)")
            del holder; gc.collect(); torch.cuda.empty_cache()
        except Exception as e:
            out["router"] = {"error": f"{type(e).__name__}: {e}"}
            print(f"  router FAILED: {type(e).__name__}: {e}")
    else:
        print(f"  router: no gate at {gate_p}")

    f = ROOT/f"results/analysis/pipeline/deployment_cost_{m}.json"
    f.write_text(json.dumps(out, indent=2)); print(f"wrote {f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
