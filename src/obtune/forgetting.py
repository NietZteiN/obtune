"""Catastrophic-forgetting checks: did tuning cost general code ability?

Two complementary readings, because they can disagree and the disagreement is the
interesting case:

  * **In-domain** — accuracy on L0 (clean code) pre/post. Already a column of the
    transfer matrix; surfaced here so a single command answers "what did this
    adapter break?". An adapter that gains on obfuscated code while losing on
    clean code has learned a surface heuristic, not comprehension.
  * **Out-of-domain** — HumanEval+ pass@1 pre/post. Output prediction is a narrow
    task; an adapter that overfits to emitting bare literals may lose the ability
    to write code at all, which the L0 column cannot see because it is the same
    task in the same format.

The generation half runs on vLLM with the same engine settings as the accuracy
grid; scoring uses evalplus's own checker, so the numbers are comparable to
published pass@1 rather than to a grader of our own.

    python -m obtune.forgetting --adapter runs/adapters/.../best --gpu 3
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from obtune.config import PROJECT_ROOT, load_config

RESULTS = PROJECT_ROOT / "results" / "forgetting"


def _extract_code(text: str, prompt: str) -> str:
    """Recover a function body from a chat completion.

    Instruct models wrap answers in fences and often restate the signature; both
    forms have to become plain source or every sample scores as a syntax error and
    the check reports catastrophic forgetting that did not happen.
    """
    fence = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    body = fence.group(1) if fence else text
    if "def " in body:
        return body
    # No signature in the completion: it continued the prompt's signature.
    return prompt + body


def humaneval_plus(
    model_id: str,
    adapter: Optional[Path],
    gpu: Optional[int],
    limit: Optional[int],
    max_tokens: int,
    engine_cfg: dict[str, Any],
) -> dict[str, Any]:
    if gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)  # before torch/vllm import

    from evalplus.data import get_human_eval_plus
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    problems = get_human_eval_plus()
    task_ids = sorted(problems)[: limit or None]

    llm = LLM(
        model=model_id, dtype=engine_cfg.get("dtype", "bfloat16"),
        enable_lora=adapter is not None,
        max_lora_rank=int(engine_cfg.get("max_lora_rank", 64)),
        gpu_memory_utilization=float(engine_cfg.get("gpu_memory_utilization", 0.85)),
        max_model_len=int(engine_cfg.get("max_model_len", 4096)),
        seed=int(engine_cfg.get("seed", 17)), enforce_eager=True, disable_log_stats=True,
    )
    tok = llm.get_tokenizer()

    prompts = []
    for tid in task_ids:
        prompt = problems[tid]["prompt"]
        msgs = [
            {"role": "system", "content": "You are an expert Python programmer."},
            {"role": "user", "content":
                "Complete this function. Reply with the complete function in a single "
                f"```python code block.\n\n```python\n{prompt}```"},
        ]
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))

    sp = SamplingParams(temperature=0.0, max_tokens=max_tokens)
    kw = {}
    if adapter is not None:
        kw["lora_request"] = LoRARequest("forgetting", 1, str(adapter))
    outs = llm.generate(prompts, sp, **kw)

    solutions = [
        {"task_id": tid, "solution": _extract_code(o.outputs[0].text, problems[tid]["prompt"])}
        for tid, o in zip(task_ids, outs)
    ]

    from evalplus.evaluate import check_correctness

    n_base = n_plus = 0
    for sol in solutions:
        try:
            res = check_correctness(
                dataset="humaneval", completion_id=0, problem=problems[sol["task_id"]],
                solution=sol["solution"], expected_output=problems[sol["task_id"]]["expected_output"],
                base_only=False, fast_check=True, gt_time_limit_factor=4.0,
            )
            n_base += int(res["base"][0] == "pass")
            n_plus += int(res["plus"][0] == "pass")
        except Exception:  # noqa: BLE001 — a harness error on one task is not a model failure
            continue

    n = len(solutions)
    return {
        "model": model_id, "adapter": str(adapter) if adapter else None,
        "n_tasks": n,
        "pass@1_base": round(n_base / n, 4) if n else None,
        "pass@1_plus": round(n_plus / n, 4) if n else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b", help="key in configs/models.yaml")
    ap.add_argument("--adapter", default=None, help="adapter dir; omit for the base model")
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    mcfg = load_config("models.yaml")["models"][args.model]
    ecfg = (load_config("eval/_base_eval.yaml").get("engine") or {})
    adapter = Path(args.adapter).resolve() if args.adapter else None

    rep = humaneval_plus(mcfg["hf_id"], adapter, args.gpu, args.limit, args.max_tokens, ecfg)
    rep["model_key"] = args.model
    tag = args.tag or (adapter.parent.name if adapter else "base")

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / f"humanevalplus_{args.model}_{tag}.json"
    out.write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
