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
  * **Out-of-domain and HELD OUT** — MBPP+ pass@1. HumanEval is one of the three
    sources of our own training corpus, so the HumanEval+ reading is contaminated
    for the arms-vs-base contrast (74 of 164 problems are in the train split).
    MBPP is not in the corpus at all, 0 of 399. See `mbpp_plus` for the evidence.

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
from dataclasses import asdict
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
    from evalplus.evaluate import get_groundtruth, get_human_eval_plus_hash
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

    # Expected outputs are NOT a field of the problem dict — they are computed by running
    # the canonical solutions, which is what get_groundtruth does (~17 s, cached by hash).
    # Indexing problems[tid]["expected_output"] raised KeyError for EVERY task; the bare
    # `except: continue` below swallowed all 164 of them and reported pass@1 = 0.0. A base
    # Qwen2.5-Coder-1.5B scores ~0.6 here, so the gate was returning a plausible-looking
    # constant that would have shown "no forgetting" for every arm while measuring nothing.
    expected = get_groundtruth(problems, get_human_eval_plus_hash(), [])

    # PER-TASK verdicts are retained, not just the totals. Every arm is scored on the SAME
    # 164 tasks, so the comparison between two arms is PAIRED and the right test is McNemar
    # on the discordant tasks. Aggregate counts cannot support that: unpaired Wilson
    # intervals at n=164 are ~+-7.5 pp wide and overlap for arms that differ by 14 tasks,
    # so discarding the per-task vector threw away most of the design's power. Measured on
    # the 2026-08-17 dose cells: `mix10` - `mix50` is 14 of 164 tasks, which unpaired reads
    # as "not significant" and paired almost certainly does not.
    #
    # This is a dict rather than two lists so that a later re-scoring cannot silently
    # misalign the arms by task order.
    per_task: dict[str, dict[str, bool]] = {}
    n_base = n_plus = n_err = 0
    for sol in solutions:
        tid = sol["task_id"]
        try:
            res = check_correctness(
                dataset="humaneval", completion_id=0, problem=problems[tid],
                solution=sol["solution"], expected_output=expected[tid],
                base_only=False, fast_check=True, gt_time_limit_factor=4.0,
            )
            ok_base = res["base"][0] == "pass"
            ok_plus = res["plus"][0] == "pass"
            per_task[tid] = {"base": ok_base, "plus": ok_plus}
            n_base += int(ok_base)
            n_plus += int(ok_plus)
        except Exception as exc:  # noqa: BLE001 — counted, never silently absorbed
            n_err += 1
            # Record the failure rather than omitting the task: a missing key must be
            # distinguishable from a failed task when two arms are paired up later.
            per_task[tid] = {"base": None, "plus": None, "error": type(exc).__name__}
            if n_err <= 3:
                print(f"[forgetting] scorer error on {tid}: {type(exc).__name__}: {exc}", flush=True)

    n = len(solutions)
    # A gate that cannot score is not a model result. Fail loudly rather than emit 0.0.
    if n and n_err > n * 0.1:
        raise RuntimeError(
            f"HumanEval+ scorer failed on {n_err}/{n} tasks — this is a harness fault, not "
            f"a model score. Refusing to report pass@1 computed from the remainder.")

    return {
        "model": model_id, "adapter": str(adapter) if adapter else None,
        "n_tasks": n,
        "n_scorer_errors": n_err,
        "pass@1_base": round(n_base / n, 4) if n else None,
        "pass@1_plus": round(n_plus / n, 4) if n else None,
        # See the comment above the scoring loop: this is what makes arm-vs-arm comparison
        # a paired test. Cells written before 2026-08-17 lack it and can only be compared
        # on point estimates.
        "per_task": per_task,
    }


def mbpp_plus(
    model_id: str,
    adapter: Optional[Path],
    gpu: Optional[int],
    limit: Optional[int],
    max_tokens: int,
    engine_cfg: dict[str, Any],
) -> dict[str, Any]:
    """Out-of-domain forgetting on a probe that is genuinely HELD OUT.

    Why this exists alongside `humaneval_plus`, which measures the same construct:
    HumanEval is one of the three sources of our own training corpus, so 74 of the 164
    HumanEval+ problems have their reference solutions in the train split (counted from
    `data/train/base/python.jsonl` against `data/splits/python.json`). Every trained arm
    saw those; the untouched base model did not. That makes "tuning cost no general
    ability" a claim resting on a contaminated comparison for the arms-vs-base contrast,
    which is exactly the comparison the paper's selectivity claim needs.

    MBPP is NOT in the corpus. `data/manifests/corpus_python.json` records `tiers:
    ['tier1']`, and MBPP/MBPPPlus are declared only under `tier2` in
    `configs/sources.yaml`, which was never built -- the provenance histogram over
    `data/train/base/python.jsonl` is apps 1584 / cruxeval 543 / humaneval 104 / mbpp 0.
    So MBPP+ is 0/399 contaminated and settles what HumanEval+ cannot.

    Deliberately a parallel function rather than a `dataset=` parameter on
    `humaneval_plus`: that function produced the seven published Table 5 numbers, and
    refactoring it under a deadline to add a second probe would put those at risk for no
    gain. The two share `_extract_code` and nothing else.
    """
    if gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)  # before torch/vllm import

    from evalplus.data import get_mbpp_plus, get_mbpp_plus_hash
    from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
    from evalplus.evaluate import get_groundtruth
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    problems = get_mbpp_plus()
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
        # THE NAME INSTRUCTION IS LOAD-BEARING. Unlike HumanEval, an MBPP+ `prompt` is a
        # bare docstring -- a natural-language task plus one example assert -- and carries
        # no function signature. The required name exists ONLY inside that assert
        # (`entry_point` is not shown to the model). A model that invents its own name
        # produces a correct program that scores zero, uniformly across arms, which would
        # read as catastrophic forgetting in every cell rather than as a prompt defect.
        # `entry_point_mismatch` below is the counter that distinguishes the two, and the
        # smoke test gates on it.
        msgs = [
            {"role": "system", "content": "You are an expert Python programmer."},
            {"role": "user", "content":
                "Write a Python function that satisfies the following specification. The "
                "assert statement shows the exact function name and signature you must "
                "use. Reply with the complete function in a single ```python code "
                f"block.\n\n```python\n{prompt}```"},
        ]
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True))

    sp = SamplingParams(temperature=0.0, max_tokens=max_tokens)
    kw = {}
    if adapter is not None:
        kw["lora_request"] = LoRARequest("forgetting_mbpp", 1, str(adapter))
    outs = llm.generate(prompts, sp, **kw)

    # `_extract_code(text, "")` -- NOT `(text, problems[tid]["prompt"])` as the HumanEval
    # path does. That fallback fires precisely when the completion contains no `def`, and
    # for MBPP the "prompt" is a docstring, so prepending it yields a module that defines
    # nothing and scores zero. An empty prefix keeps the failure legible as a format
    # failure instead of disguising it as a wrong answer.
    solutions = [
        {"task_id": tid, "solution": _extract_code(o.outputs[0].text, "")}
        for tid, o in zip(task_ids, outs)
    ]

    from evalplus.evaluate import check_correctness

    # Third argument is the special-oracle list, not a formality: three MBPP tasks have
    # unserializable outputs and are checked only for not-None. evalplus's own CLI does
    # exactly this swap (evalplus/evaluate.py:152-160). It matches on `entry_point`
    # (function names), not task ids, so it is passed through verbatim.
    expected = get_groundtruth(problems, get_mbpp_plus_hash(), MBPP_OUTPUT_NOT_NONE_TASKS)

    # Per-task verdicts retained for the same reason as the HumanEval path: every arm is
    # scored on the same 399 tasks, so arm-vs-arm is PAIRED (McNemar on the discordant
    # tasks). It also gives the CLAUDE.md §4.2 adapter-applied check for free -- zero
    # discordant tasks against `7b_base` over 399 means the LoRA never loaded.
    per_task: dict[str, dict[str, bool]] = {}
    n_base = n_plus = n_err = 0
    for sol in solutions:
        tid = sol["task_id"]
        try:
            res = check_correctness(
                dataset="mbpp", completion_id=0, problem=problems[tid],
                solution=sol["solution"], expected_output=expected[tid],
                base_only=False, fast_check=True, gt_time_limit_factor=4.0,
            )
            ok_base = res["base"][0] == "pass"
            ok_plus = res["plus"][0] == "pass"
            per_task[tid] = {"base": ok_base, "plus": ok_plus}
            n_base += int(ok_base)
            n_plus += int(ok_plus)
        except Exception as exc:  # noqa: BLE001 — counted, never silently absorbed
            n_err += 1
            per_task[tid] = {"base": None, "plus": None, "error": type(exc).__name__}
            if n_err <= 3:
                print(f"[forgetting] scorer error on {tid}: {type(exc).__name__}: {exc}", flush=True)

    n = len(solutions)
    if n and n_err > n * 0.1:
        raise RuntimeError(
            f"MBPP+ scorer failed on {n_err}/{n} tasks — this is a harness fault, not "
            f"a model score. Refusing to report pass@1 computed from the remainder.")

    # Two diagnostics the HumanEval path lacks. `format_fail_rate` is required by
    # CLAUDE.md §4.6; `entry_point_mismatch` is specific to MBPP's nameless prompt and is
    # the ONLY signal that separates "the model cannot code" from "the instruction failed".
    # Both are reported rather than asserted, because a tuned arm legitimately having a
    # higher format-failure rate IS the forgetting this module measures.
    n_format_fail = sum(1 for s in solutions if "def " not in s["solution"])
    n_ep_mismatch = sum(
        1 for s in solutions
        if not re.search(rf"def\s+{re.escape(problems[s['task_id']]['entry_point'])}\s*\(",
                         s["solution"])
    )

    return {
        "model": model_id, "adapter": str(adapter) if adapter else None,
        "benchmark": "mbppplus",
        "n_tasks": n,
        "n_scorer_errors": n_err,
        "pass@1_base": round(n_base / n, 4) if n else None,
        "pass@1_plus": round(n_plus / n, 4) if n else None,
        "format_fail_rate": round(n_format_fail / n, 4) if n else None,
        "entry_point_mismatch": n_ep_mismatch,
        "per_task": per_task,
    }


def l0_output_prediction(
    model_id: str,
    adapter: Optional[Path],
    gpu: Optional[int],
    limit: Optional[int],
    engine_cfg: dict[str, Any],
    language: str = "python",
    source: str = "heldout",
    seed: int = 17,
) -> dict[str, Any]:
    """In-domain forgetting: obtune's OWN task (output prediction) on clean L0 code.

    The half this module's docstring promised and never implemented. It matters most for
    adapters that were trained to *emit code* — the CFT replication's arms and the SRH
    follow-up's `rev`/`flip` arms all do, and they are far likelier than an
    output-prediction adapter to destroy the ability to answer with a bare literal.
    HumanEval+ cannot see that: it rewards writing code, which is exactly what these
    adapters were trained to do.

    Deliberately routed through the same `prompts.build_prompt` and `scoring.grade` the
    accuracy grid uses, so the number is directly comparable to a transfer-matrix cell
    rather than to a grader of our own (CLAUDE.md §4.3, §4.5).
    """
    if gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)  # before torch/vllm import

    from obtune import data, prompts, scoring

    items = data.load_eval_items(["L0"], language, script="forgetting.py", source=source)
    if limit:
        items = sorted(items, key=lambda i: i.item_id)[:limit]
    if not items:
        raise RuntimeError(f"no L0 eval items for {language}/{source}")

    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    llm = LLM(
        model=model_id, dtype=engine_cfg.get("dtype", "bfloat16"),
        enable_lora=adapter is not None,
        max_lora_rank=int(engine_cfg.get("max_lora_rank", 64)),
        gpu_memory_utilization=float(engine_cfg.get("gpu_memory_utilization", 0.85)),
        max_model_len=int(engine_cfg.get("max_model_len", 4096)),
        seed=seed, enforce_eager=True, disable_log_stats=True,
    )
    tok = llm.get_tokenizer()
    texts = [
        prompts.render_chat(
            prompts.build_prompt(
                code=i.code, entry_point=i.entry_point, args_repr=i.args_repr,
                language=i.language, condition=i.condition,
            ),
            tok,
        )
        for i in items
    ]
    # vLLM RAISES on an over-long prompt and kills the whole run — the accuracy grid
    # learned this the hard way (eval_vllm.drop_overlong, whose docstring names the same
    # 1,671-item L0 set and the single APPS program with a 19,950-character literal that
    # took it out). This module rebuilt the generation path without that guard, so the
    # forgetting gate failed on its first ever invocation for exactly that reason.
    # Reuse the grid's function rather than reimplementing the budget arithmetic.
    from obtune.eval_vllm import drop_overlong

    max_new = 64
    items, texts, dropped = drop_overlong(
        items, texts, tok,
        max_model_len=int(engine_cfg.get("max_model_len", 4096)),
        max_new_tokens=max_new,
    )
    if dropped:
        print(f"[forgetting] dropped {len(dropped)} over-long L0 prompt(s); "
              f"they are unanswerable in this context window either way", flush=True)
    if not items:
        raise RuntimeError("every L0 prompt exceeded the context window")

    sp = SamplingParams(temperature=0.0, max_tokens=max_new, seed=seed)
    kw = {}
    if adapter is not None:
        kw["lora_request"] = LoRARequest("forgetting_l0", 1, str(adapter))
    outs = llm.generate(texts, sp, **kw)

    grades = [
        scoring.grade(o.outputs[0].text, it.output_repr, it.language)
        for it, o in zip(items, outs)
    ]
    n = len(grades)
    return {
        "model": model_id, "adapter": str(adapter) if adapter else None,
        "language": language, "source": source, "condition": "L0",
        "n_items": n,
        "n_dropped_overlong": len(dropped),
        "n_programs": len({i.program_id for i in items}),
        "accuracy": round(sum(g.correct for g in grades) / n, 4),
        "format_fail_rate": round(sum(g.format_fail for g in grades) / n, 4),
        "parse_ok_rate": round(sum(g.parse_ok for g in grades) / n, 4),
        **prompts.provenance_block(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="qwen25c-1.5b", help="key in configs/models.yaml")
    ap.add_argument("--adapter", default=None, help="adapter dir; omit for the base model")
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--tag", default=None)
    ap.add_argument(
        "--suite", default="humaneval",
        # `mbpp` is deliberately NOT part of `both`. `both` means L0 + HumanEval+, the
        # enqueue path defaults to it, and widening it would re-run and overwrite the seven
        # `humanevalplus_qwen25c-7b_*.json` files that paper_bidirectional Table 5 quotes.
        choices=["humaneval", "l0", "both", "mbpp"],
        help="which forgetting check(s) to run; CLAUDE.md §4.7 wants both per adapter. "
             "`mbpp` is the held-out probe and runs standalone, never as part of `both`",
    )
    ap.add_argument("--language", default="python")
    args = ap.parse_args()

    mcfg = load_config("models.yaml")["models"][args.model]
    ecfg = (load_config("eval/_base_eval.yaml").get("engine") or {})
    adapter = Path(args.adapter).resolve() if args.adapter else None
    tag = args.tag or (adapter.parent.name if adapter else "base")
    RESULTS.mkdir(parents=True, exist_ok=True)

    # `--suite both` builds two vLLM engines in one process, which fight over the same
    # GPU memory fraction. Fine interactively at a low `gpu_memory_utilization`; the
    # enqueue path emits two separate jobs instead. L0 runs first so the cheaper, more
    # informative check lands even if the second engine cannot allocate.
    written: list[Path] = []
    if args.suite in ("l0", "both"):
        rep = l0_output_prediction(
            mcfg["hf_id"], adapter, args.gpu, args.limit, ecfg, language=args.language
        )
        rep["model_key"] = args.model
        out = RESULTS / f"l0_{args.model}_{args.language}_{tag}.json"
        out.write_text(json.dumps(rep, indent=2))
        written.append(out)
        print(json.dumps(rep, indent=2))

    if args.suite in ("humaneval", "both"):
        rep = humaneval_plus(mcfg["hf_id"], adapter, args.gpu, args.limit, args.max_tokens, ecfg)
        rep["model_key"] = args.model
        out = RESULTS / f"humanevalplus_{args.model}_{tag}.json"
        out.write_text(json.dumps(rep, indent=2))
        written.append(out)
        print(json.dumps(rep, indent=2))

    if args.suite == "mbpp":
        rep = mbpp_plus(mcfg["hf_id"], adapter, args.gpu, args.limit, args.max_tokens, ecfg)
        rep["model_key"] = args.model
        # Provenance is embedded IN the result rather than written as a sibling
        # `run_manifest.json`, because `RunManifest.write` hardcodes that filename and
        # `results/forgetting/` is flat and shared by every cell -- each cell would clobber
        # the last. The HumanEval+ path records no provenance at all, which is a known gap
        # (see log/cft-replication/); this is the pattern to follow when it is closed.
        from obtune.provenance import RunManifest, sha256_dir

        rm = RunManifest(
            experiment="srh/mbpp-plus",
            run_id=f"mbppplus_{args.model}_{tag}",
            seed=int(ecfg.get("seed", 17)),
            config_path="configs/eval/_base_eval.yaml",
            config_resolved=ecfg,
            model_hf_id=mcfg["hf_id"],
            adapter=(
                {"path": str(adapter), "sha256": sha256_dir(adapter)} if adapter else None
            ),
        )
        rep["provenance"] = asdict(
            rm.hash_scripts(["src/obtune/forgetting.py"]).capture_git().finalize()
        )
        out = RESULTS / f"mbppplus_{args.model}_{tag}.json"
        out.write_text(json.dumps(rep, indent=2, default=str))
        written.append(out)
        # per_task is 399 entries; printing the whole report buries the numbers that matter.
        print(json.dumps({k: v for k, v in rep.items()
                          if k not in ("per_task", "provenance")}, indent=2))

    for p in written:
        print(f"\nwrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
