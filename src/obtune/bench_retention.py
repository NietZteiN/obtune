"""Panel-wide general-coding-benchmark retention: what did tuning cost?

CLAUDE.md §4.7 asks for a forgetting check per adapter. `forgetting.py` answers it one
adapter at a time, building a vLLM engine per invocation. For a 8-model x 6-arm x
2-benchmark panel that is 96 engine starts, so this module inverts the loop: **one engine
per (model, benchmark), every arm served through it as a LoRARequest**.

Three things this module does that `forgetting.py` does not, all of them forced by what
the existing results could not answer:

  * **A 0.0 is diagnosable.** `results/forgetting/humanevalplus_codellama-7b_{tuned_L0,
    mono_all}.json` both read pass@1 = 0.0000 against a base of 0.439, and neither file
    records a format-failure rate or a single generation, so nothing in them distinguishes
    "the adapter cannot write code" from "the adapter answers output-prediction style and
    never emits `def`". Every arm here carries `format_fail_rate`, `entry_point_mismatch`
    and a saved sample of raw completions.
  * **Arms are paired by construction.** One engine, one prompt list, identical sampling;
    the only thing that varies across arms is the LoRARequest. Per-task verdicts are kept
    so arm-vs-arm is McNemar on the discordant tasks, not two unpaired Wilson intervals.
  * **The adapter-applied check (CLAUDE.md §4.2) is enforced, not assumed.** An arm whose
    completions are byte-identical to base's over the whole benchmark did not load, and
    that is reported as a fault rather than as a score of "no forgetting".

`forgetting.py`'s two scoring functions are deliberately left alone: they produced the
published Table 5 numbers and this module is not worth putting those at risk. What is
shared is `_extract_code`, for exactly the reason its own docstring gives.

    python -m obtune.bench_retention --model codellama-7b --benchmark mbpp
"""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from obtune.config import PROJECT_ROOT, load_config
from obtune.forgetting import _extract_code  # v1, kept for the strict column

RESULTS = PROJECT_ROOT / "results" / "retention"

#: The arms the paper's tables report -- Base, Clean, Breadth, KL, Router, Merge -- plus
#: the second merge operator. Two of them do not go through a vLLM LoRARequest and are
#: handled by their own engines, below:
#:
#:   `mole_router`  a learned mixture over EIGHT experts, not a single adapter. Served by
#:                  `mole.eval_mole.HFEngine`, which exposes the same five-member surface
#:                  as `eval_vllm.Engine`. It must be the ONLY arm in its job: the mixture
#:                  holds the base weights plus eight adapters resident, and building it
#:                  beside a vLLM engine in one process fights for the same GPU memory.
#:   `icl_k4`       the UNTUNED weights with four in-context demonstrations of the
#:                  obfuscated output-prediction task. No adapter; the arm is the prompt.
ARMS: list[tuple[str, Optional[str]]] = [
    ("base", None),
    ("tuned_L0", "runs/adapters/{model}/{language}/L0_r32_s17"),
    ("mono_all", "runs/adapters/{model}/{language}/L0-L1b-L1r-L2-S1-S2_r32_s17"),
    ("cons_lam3",
     "runs/adapters_objectives/{model}/{language}/"
     "L0-L1b-L1r-L2-S1-S2_r32_cons_parent_lam3_s17"),
    ("merge_ties", "runs/adapters/{model}/{language}/merge_ties_r32_s17"),
    ("merge_dare_ties", "runs/adapters/{model}/{language}/merge_dare_ties_r32_s17"),
]

#: Arms that are not a LoRA on the base model, and how each is built.
ROUTER_ARM = "mole_router"
ICL_ARM = "icl_k4"
#: The eight experts the router mixes, and the conditions ICL draws demonstrations from.
#: H1 appears in NEITHER: `pick_demos` refuses it outright, because a demo is prompt
#: conditioning and CLAUDE.md §3.2 rule 2 forbids that for the held-out family.
EXPERTS = ["L0", "L1b", "L1r", "L2", "S1", "S2", "S3", "S4"]
ICL_SOURCE = ["L1b", "L1r", "L2", "S1", "S2"]
ICL_K = 4


def resolve_adapter(rel: str, model: str, language: str) -> Path:
    """Locate the servable adapter directory for an arm.

    Trained adapters are checkpoint trees whose servable weights sit in `best/`; merges
    are written flat, the directory *is* the adapter. Guessing wrong yields vLLM's
    "adapter_model.safetensors not found", which the 2026-09-11 entry records as having
    been silent once already, so this resolves explicitly and raises with the path it
    tried.
    """
    root = PROJECT_ROOT / rel.format(model=model, language=language)
    for cand in (root, root / "best"):
        if (cand / "adapter_config.json").exists() and (
            (cand / "adapter_model.safetensors").exists()
            or (cand / "adapter_model.bin").exists()
        ):
            return cand
    raise FileNotFoundError(
        f"no servable adapter at {root} or {root}/best "
        f"(looked for adapter_config.json + adapter_model.safetensors)")


#: Lines that delimit a code block rather than belong to it. Markdown fences are the
#: common case; CodeLlama-Instruct emits `[PYTHON] ... [/PYTHON]` instead, which is not a
#: fence at all and which no regex written for Markdown will find. Both appear in this
#: panel, on the untuned model as well as the adapters.
_MARKER = re.compile(r"""\s*(?:```|~~~|\[/?(?:PYTHON|CODE)\]|</?code>)\s*$""", re.IGNORECASE)
_BLOCKS = [
    re.compile(r"```[ \t]*(?:python|py)?[ \t]*\r?\n(.*?)(?:```|\Z)", re.DOTALL),
    re.compile(r"\[PYTHON\][ \t]*\r?\n?(.*?)(?:\[/PYTHON\]|\Z)", re.DOTALL | re.IGNORECASE),
    re.compile(r"<code>(.*?)(?:</code>|\Z)", re.DOTALL | re.IGNORECASE),
]


def _candidates(raw: str, prompt: str):
    """Every reasonable reading of a completion, cheapest and most literal first.

    Each is tried in order and the first that COMPILES wins; if none does, the strict v1
    reading is kept and the task scores as the failure it is. Compilation is the arbiter
    rather than a regex, so this cannot quietly turn a broken reply into a passing one.
    """
    import textwrap

    yield _extract_code(raw, prompt)

    for rx in _BLOCKS:
        m = rx.search(raw)
        if m:
            body = m.group(1)
            yield body
            yield textwrap.dedent(body)
            if prompt:
                # HumanEval: the block may hold only the body, which must stay indented
                # under the prompt's signature -- so the UNDEDENTED form is offered too.
                yield prompt + body
                yield prompt + textwrap.dedent(body)

    # No usable block: drop every delimiter line, then dedent.
    stripped = "\n".join(l for l in raw.splitlines() if not _MARKER.match(l))
    yield stripped
    yield textwrap.dedent(stripped)

    # Re-anchor on the first def, delimiters already removed. Prose at column zero ahead of
    # an indented def defeats dedent's common-prefix rule on its own.
    lines = stripped.splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"\s*def\s+\w+\s*\(", ln):
            yield textwrap.dedent("\n".join(lines[i:]))
            break

    # HumanEval only: the completion continued the prompt's signature instead of restating
    # it. Indentation is load-bearing here, so the undedented form comes first.
    if prompt:
        yield prompt + stripped
        yield prompt + textwrap.dedent(stripped)


def extract_code(raw: str, prompt: str) -> tuple[str, bool]:
    """Recover a runnable function, and say whether a repair was needed.

    THIS EXISTS BECAUSE EXTRACTION FAILURE IS INDISTINGUISHABLE FROM FORGETTING.
    `forgetting._extract_code` returns the completion verbatim when it contains a `def` and
    its fence regex does not match. Two ways that happens, both found on 2026-09-22 and both
    reading as a total collapse in general coding ability:

      * **No fence at all.** The chat template's first generated token is a space, so the
        solution begins `" def f(...)"` and raises `IndentationError` on line 1. Observed on
        CodeLlama-34B `tuned_L0`, which scored 0.0000 while emitting the same correct
        function the untuned model got credit for. Corrected: 0.5414, against base 0.5338.
      * **A fence the regex misses.** `"``` \n"` -- backticks, space, newline -- is not
        ```(python)?\n, so the backticks end up inside the "solution". Observed on the same
        model's TIES merge: 74 % uncompilable, pass@1 0.1754.

    Both are selected for by the thing being measured: training on output prediction changes
    how a model frames an answer, so the arms that are supposed to show forgetting are
    exactly the arms that trip the extractor, and the untuned control never does.

    The repair is applied ARM-BLIND, to the untuned model and every adapter identically --
    the discipline `inverse.extract_call` follows for the backward task -- and every
    candidate must COMPILE to be accepted, so it cannot manufacture a pass. The repair rate
    and the residual uncompilable rate are both reported beside pass@1.
    """
    v1 = _extract_code(raw, prompt)
    for i, cand in enumerate(_candidates(raw, prompt)):
        if _compiles(cand):
            return cand, i > 0
    return v1, False  # genuinely unrunnable; score it as the failure it is


def _compiles(src: str) -> bool:
    try:
        compile(src, "<solution>", "exec")
        return True
    except (SyntaxError, ValueError):
        return False


def pick_icl_demos(language: str = "python", k: int = ICL_K, seed: int = 17):
    """A FIXED demonstration prefix, identical for every benchmark task.

    `eval_vllm` draws per-item demos and excludes the item's own program, which is the
    in-context analogue of split leakage. There is no such per-item exclusion available
    here: an MBPP+/HumanEval+ task carries no `program_id` in our corpus's namespace, so
    nothing can be matched against. A fixed prefix is the honest substitute -- it is the
    same four programs for all 399 (or 164) tasks, so it cannot be tuned per item, and the
    four `program_id`s are written into the result for audit.

    **The residual risk is HumanEval+ only, and it is why MBPP+ is the primary probe
    here.** HumanEval is one of the three sources of our own corpus, so a demo program
    could in principle be a benchmark problem; MBPP is 0/399 in the corpus and cannot
    collide. The demo program ids are recorded so the HumanEval+ reading can be checked
    rather than trusted.
    """
    from obtune.icl.demos import pick_demos

    return pick_demos(language, k, list(ICL_SOURCE), seed=seed)


def build_prompts(benchmark: str, tok, limit: Optional[int], demos=()):
    """Render the benchmark's prompts once, for every arm to share.

    Identical text for every arm is what makes the comparison paired; rendering per arm
    would let a tokenizer or template difference leak in as a "forgetting" effect.
    """
    if benchmark == "humaneval":
        from evalplus.data import get_human_eval_plus

        problems = get_human_eval_plus()
        task_ids = sorted(problems)[: limit or None]
        instruction = (
            "Complete this function. Reply with the complete function in a single "
            "```python code block.\n\n```python\n{p}```")
    elif benchmark == "mbpp":
        from evalplus.data import get_mbpp_plus

        problems = get_mbpp_plus()
        task_ids = sorted(problems)[: limit or None]
        # The name instruction is load-bearing -- see forgetting.mbpp_plus. An MBPP+
        # prompt is a bare docstring with no signature; the required name exists only
        # inside its assert, and a model that invents one scores zero uniformly across
        # arms, which reads as forgetting in every cell rather than as a prompt defect.
        instruction = (
            "Write a Python function that satisfies the following specification. The "
            "assert statement shows the exact function name and signature you must use. "
            "Reply with the complete function in a single ```python code block."
            "\n\n```python\n{p}```")
    else:
        raise ValueError(f"unknown benchmark {benchmark!r}")

    # NOT every panel model accepts a system role. StarCoder2-15B's template raises
    # `TemplateError: System messages are not allowed in this template`, and the Gemma
    # lineage is the same. Detected once, on the first item, and the system text is then
    # folded into the user turn for every item -- so the instruction still reaches the
    # model and the prompt stays identical across arms, which is what keeps the
    # comparison paired. Failing here instead would drop those models from the panel.
    SYSTEM = "You are an expert Python programmer."
    def render(body: str) -> str:
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": body}]
        try:
            return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except Exception:
            return tok.apply_chat_template(
                [{"role": "user", "content": f"{SYSTEM}\n\n{body}"}],
                tokenize=False, add_generation_prompt=True)

    def render_icl(body: str) -> str:
        """Demo turns first, then the benchmark question, under the BENCHMARK's own system
        prompt. Keeping that system turn is deliberate: swapping in the obfuscation task's
        system prompt would change two things at once, and the arm exists to isolate one --
        what four obfuscated output-prediction exchanges in context do to code generation.
        """
        from obtune import prompts as P

        msgs = [{"role": "system", "content": SYSTEM}]
        for d in demos:
            msgs.append({"role": "user", "content": P.build_user_content(
                d.code, d.entry_point, d.args_repr, d.language, condition=d.condition)})
            msgs.append({"role": "assistant", "content": d.output_repr})
        msgs.append({"role": "user", "content": body})
        try:
            return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except Exception:
            msgs[1]["content"] = f"{SYSTEM}\n\n{msgs[1]['content']}"
            return tok.apply_chat_template(msgs[1:], tokenize=False, add_generation_prompt=True)

    r = render_icl if demos else render
    texts = [r(instruction.format(p=problems[tid]["prompt"])) for tid in task_ids]
    if texts:
        print(f"[retention] system role accepted: "
              f"{'system' in texts[0].lower() or SYSTEM in texts[0]}", flush=True)
    return problems, task_ids, texts


def score(benchmark: str, problems, task_ids, raw: list[str]) -> dict[str, Any]:
    """Extract, execute and score one arm's completions.

    `raw` is the model text BEFORE extraction, and one diagnostic is deliberately computed
    on it rather than on the recovered solution. On HumanEval the prompt carries the
    signature, so `_extract_code` prepends it whenever the completion has no `def` of its
    own -- which means an arm that replies with a bare literal (`"42"`), the exact failure
    mode an output-prediction adapter is expected to have, still yields a solution
    containing `def` and reads as `format_fail_rate = 0.0`. Verified: scoring `"42"`
    against HumanEval+ gives format_fail 0.0, against MBPP+ gives 1.0. `raw_no_def_rate`
    is what separates "wrote a wrong function" from "did not write a function at all" on
    both benchmarks, and it is why MBPP+ is the primary probe here.
    """
    from evalplus.evaluate import check_correctness

    if benchmark == "humaneval":
        from evalplus.evaluate import get_groundtruth, get_human_eval_plus_hash

        # Expected outputs are computed by running the canonical solutions, not read off
        # the problem dict -- indexing problems[tid]["expected_output"] raises KeyError
        # for every task, which an earlier bare `except: continue` turned into a
        # plausible-looking pass@1 of 0.0. See forgetting.humaneval_plus.
        expected = get_groundtruth(problems, get_human_eval_plus_hash(), [])
        dataset = "humaneval"
        # The HumanEval prompt carries the signature, so a completion that continued it
        # is recovered by prepending the prompt.
        pairs = [extract_code(r, problems[t]["prompt"]) for t, r in zip(task_ids, raw)]
        sols = [{"task_id": t, "solution": c} for t, (c, _) in zip(task_ids, pairs)]
    else:
        from evalplus.data import get_mbpp_plus_hash
        from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
        from evalplus.evaluate import get_groundtruth

        expected = get_groundtruth(problems, get_mbpp_plus_hash(), MBPP_OUTPUT_NOT_NONE_TASKS)
        dataset = "mbpp"
        # Empty prefix, NOT the prompt: an MBPP "prompt" is a docstring, so prepending it
        # yields a module that defines nothing and disguises a format failure as a wrong
        # answer.
        pairs = [extract_code(r, "") for r in raw]
        sols = [{"task_id": t, "solution": c} for t, (c, _) in zip(task_ids, pairs)]

    per_task: dict[str, dict[str, Any]] = {}
    n_base = n_plus = n_err = 0
    for s in sols:
        tid = s["task_id"]
        try:
            res = check_correctness(
                dataset=dataset, completion_id=0, problem=problems[tid],
                solution=s["solution"], expected_output=expected[tid],
                base_only=False, fast_check=True, gt_time_limit_factor=4.0,
            )
            ok_b, ok_p = res["base"][0] == "pass", res["plus"][0] == "pass"
            per_task[tid] = {"base": ok_b, "plus": ok_p}
            n_base += int(ok_b)
            n_plus += int(ok_p)
        except Exception as exc:  # noqa: BLE001 — counted, never silently absorbed
            n_err += 1
            per_task[tid] = {"base": None, "plus": None, "error": type(exc).__name__}
            if n_err <= 3:
                print(f"[retention] scorer error on {tid}: {type(exc).__name__}: {exc}",
                      flush=True)

    n = len(sols)
    if n and n_err > n * 0.1:
        raise RuntimeError(
            f"{benchmark} scorer failed on {n_err}/{n} tasks — a harness fault, not a "
            f"model score. Refusing to report pass@1 from the remainder.")

    # THE DIAGNOSTICS THE EXISTING 0.0 READINGS LACK. A tuned arm legitimately having a
    # high format-failure rate IS the forgetting being measured, so these are reported
    # beside pass@1, never used to repair it.
    n_fmt = sum(1 for s in sols if "def " not in s["solution"])
    n_raw_nodef = sum(1 for r in raw if "def " not in r)
    n_repaired = sum(1 for _, rep in pairs if rep)
    n_uncompilable = sum(1 for s in sols if not _compiles(s["solution"]))
    n_ep = sum(1 for s in sols
               if not re.search(rf"def\s+{re.escape(problems[s['task_id']]['entry_point'])}\s*\(",
                                s["solution"]))
    return {
        "n_tasks": n,
        "n_scorer_errors": n_err,
        "pass@1_base": round(n_base / n, 4) if n else None,
        "pass@1_plus": round(n_plus / n, 4) if n else None,
        "format_fail_rate": round(n_fmt / n, 4) if n else None,
        "raw_no_def_rate": round(n_raw_nodef / n, 4) if n else None,
        "entry_point_mismatch": n_ep,
        "entry_point_mismatch_rate": round(n_ep / n, 4) if n else None,
        # Auditability of the arm-blind extraction repair: how many solutions needed it,
        # and how many are still unrunnable after it (those are real failures).
        "extraction_repaired": n_repaired,
        "extraction_repaired_rate": round(n_repaired / n, 4) if n else None,
        "uncompilable_rate": round(n_uncompilable / n, 4) if n else None,
        "per_task": per_task,
        "_pairs": pairs,
    }


def build_router_engine(model_key: str, language: str, mcfg: dict, ecfg: dict):
    """The learned 8-expert mixture, behind the same engine surface as vLLM.

    `mole.eval_mole.HFEngine` already exposes `.tokenizer/.ecfg/.stub/.generate/.version`,
    so the sweep's loop does not change; only what builds the engine does. The gate is the
    arm -- `build_mole_model` attaches the expert bank and the trained `gate.pt` is loaded
    over the freshly-initialised router, exactly as `eval_mole.main` does it.

    ENGINE CAVEAT, stated because it cannot be removed: this is an HF generate path while
    every other arm runs on vLLM. Both are greedy on identical prompts over identical
    tasks, and the project has measured that residual before at ~0.2 points (vLLM batch
    numerics), so the comparison is sound -- but it is not the same decoder, and the
    router's number should not be read to a finer resolution than that.
    """
    import torch
    from transformers import AutoTokenizer

    from obtune.mole.eval_mole import HFEngine
    from obtune.mole.model import build_mole_model

    experts = {}
    for e in EXPERTS:
        d = PROJECT_ROOT / f"runs/adapters/{model_key}/{language}/{e}_r32_s17/best"
        if not (d / "adapter_config.json").exists():
            raise FileNotFoundError(f"router needs expert {e}; {d} is missing")
        experts[e] = str(d)

    short = model_key.replace("-", "").replace(".", "")
    gates = sorted((PROJECT_ROOT / f"runs/mole/{model_key}/{language}").glob(
        "routerlora_*_s17/gate.pt"))
    if not gates:
        raise FileNotFoundError(
            f"router needs a trained gate under runs/mole/{model_key}/{language}")
    gate_p = gates[0]

    holder = build_mole_model(model_key, experts, d_router=64, shared_query=False,
                              dtype=ecfg.get("dtype", "bfloat16"), device_map="auto")
    sd = torch.load(gate_p, map_location="cpu")
    holder.gate.load_state_dict(sd.get("state_dict", sd))
    holder.gate.to(next(holder.model.parameters()).device)
    print(f"[retention] router gate loaded from {gate_p} "
          f"({holder.summary.get('n_experts')} experts)", flush=True)

    tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    return HFEngine(holder, tok, ecfg=ecfg, batch_size=int(ecfg.get("batch_size", 16)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, help="key in configs/models.yaml")
    ap.add_argument("--benchmark", required=True, choices=["humaneval", "mbpp"])
    ap.add_argument("--language", default="python")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--arms", default=None, help="comma-separated subset of ARMS")
    ap.add_argument("--gpu-mem-util", type=float, default=None)
    args = ap.parse_args()

    from obtune.eval_vllm import Engine
    from obtune.provenance import RunManifest, sha256_dir

    mcfg = load_config("models.yaml")["models"][args.model]
    ecfg = dict((load_config("eval/_base_eval.yaml").get("engine") or {}))
    if args.gpu_mem_util is not None:
        ecfg["gpu_memory_utilization"] = args.gpu_mem_util

    want = set(args.arms.split(",")) if args.arms else None

    # The router owns its process. The mixture holds the base weights plus eight adapters
    # resident; building it beside a vLLM engine means two models on one card. Refused
    # here rather than discovered as an OOM forty minutes in.
    router_only = want == {ROUTER_ARM}
    if want and ROUTER_ARM in want and not router_only:
        raise SystemExit(
            f"--arms {ROUTER_ARM} must be run alone: the mixture and a vLLM engine cannot "
            f"share a GPU. Submit it as its own job.")
    icl = bool(want) and ICL_ARM in want

    demos = ()
    if icl:
        demos = pick_icl_demos(args.language)
        print(f"[retention] ICL k={len(demos)} demos from {ICL_SOURCE}: "
              f"{[d.program_id for d in demos]}", flush=True)

    if router_only:
        resolved = [(ROUTER_ARM, None)]
        engine = build_router_engine(args.model, args.language, mcfg, ecfg)
    else:
        arms = [(n, p) for n, p in ARMS if want is None or n in want]
        if icl:
            arms = [(ICL_ARM, None)] + [a for a in arms if a[0] != ICL_ARM]
        # Resolve every adapter BEFORE the engine starts. A missing path found 40 minutes
        # in wastes the whole allocation, and a missing adapter has been silent here before
        # (log/setup/2026-09-11_missing-adapter-was-silent.md).
        resolved = []
        for name, rel in arms:
            resolved.append((name, None if rel is None else
                             resolve_adapter(rel, args.model, args.language)))
            print(f"[retention] arm {name:16s} -> {resolved[-1][1]}", flush=True)
        engine = Engine(mcfg["hf_id"], ecfg)

    problems, task_ids, texts = build_prompts(
        args.benchmark, engine.tokenizer, args.limit, demos=demos)
    print(f"[retention] {args.model} / {args.benchmark}: {len(task_ids)} tasks "
          f"x {len(resolved)} arms", flush=True)

    # NO STOP STRINGS. _base_eval.yaml's `stop: ["\n\n", "```"]` is right for
    # output-prediction, where the answer is one token; here it would cut a generated
    # function at its first blank line and at the closing fence, and every arm would read
    # as catastrophic forgetting.
    sampling = {"temperature": 0.0, "top_p": 1.0, "max_tokens": args.max_tokens,
                "stop": [], "seed": int(ecfg.get("seed", 17))}

    RESULTS.mkdir(parents=True, exist_ok=True)
    base_raw: Optional[list[str]] = None
    summary: dict[str, Any] = {}

    for name, adir in resolved:
        t0 = time.time()
        raw, _ = engine.generate(texts, sampling, [None if adir is None else str(adir)] * len(texts))
        gen_s = round(time.time() - t0, 1)

        if name == "base":
            base_raw = raw
            identical = None
        elif base_raw is None:
            # No base arm in this process (router job, or an --arms subset). The check is
            # skipped rather than faked; `None` means "not tested", not "passed".
            identical = None
        else:
            # CLAUDE.md §4.2: an adapter that changed nothing did not load. Reported as a
            # fault on the run, not folded into the score.
            identical = sum(1 for a, b in zip(raw, base_raw or []) if a == b)
            if base_raw is not None and identical == len(raw):
                print(f"[retention] *** FAULT: arm {name} is byte-identical to base on all "
                      f"{len(raw)} tasks — the LoRA did not load ***", flush=True)

        rep = score(args.benchmark, problems, task_ids, raw)
        pairs = rep.pop("_pairs")  # (solution, was_repaired) per task, for the sidecar
        # Raw text of the completions that yielded no `def`, kept verbatim so a pass@1 of
        # 0.0 can be read by a human without rerunning the model.
        fmt_failures = [
            r for tid, r in zip(task_ids, raw)
            if "def " not in extract_code(
                r, "" if args.benchmark == "mbpp" else problems[tid]["prompt"])[0]
        ]
        rep.update({
            "model_key": args.model, "model": mcfg["hf_id"], "arm": name,
            "benchmark": {"humaneval": "humanevalplus", "mbpp": "mbppplus"}[args.benchmark],
            "adapter": str(adir) if adir else None,
            "icl_demos": ([d.program_id for d in demos] if (icl and name == ICL_ARM) else None),
            "engine": engine.version(),
            "gen_seconds": gen_s,
            "identical_to_base": identical,
            # Saved so a 0.0 is readable by a human without a rerun: the first five
            # completions, plus up to fifteen that produced no `def` at all.
            "sample_generations": raw[:5],
            "sample_format_failures": fmt_failures[:15],
        })
        rm = RunManifest(
            experiment="retention/benchmark-panel",
            run_id=f"{rep['benchmark']}_{args.model}_{name}",
            seed=int(ecfg.get("seed", 17)),
            config_path="configs/eval/_base_eval.yaml",
            config_resolved={"engine": ecfg, "sampling": sampling},
            model_hf_id=mcfg["hf_id"],
            adapter=({"path": str(adir), "sha256": sha256_dir(adir)} if adir else None),
        )
        rep["provenance"] = asdict(
            rm.hash_scripts(["src/obtune/bench_retention.py"]).capture_git().finalize())

        out = RESULTS / f"{rep['benchmark']}_{args.model}_{name}.json"
        out.write_text(json.dumps(rep, indent=2, default=str))

        # EVERY generation, to a sidecar. This is the lesson of the artefact this module
        # was written to catch: `results/forgetting/` kept per-task booleans and nothing
        # else, so a pass@1 of 0.0000 could not be told from a broken extractor without
        # re-running the model. With the raw text on disk, any future change to
        # `extract_code` is a re-scoring job, not a GPU job.
        rawdir = RESULTS / "raw"
        rawdir.mkdir(parents=True, exist_ok=True)
        with (rawdir / f"{rep['benchmark']}_{args.model}_{name}.jsonl").open("w") as fh:
            for tid, r, (sol, repd) in zip(task_ids, raw, pairs):
                fh.write(json.dumps({"task_id": tid, "raw": r, "solution": sol,
                                     "extraction_repaired": repd}) + "\n")
        summary[name] = {k: rep[k] for k in
                         ("pass@1_base", "pass@1_plus", "format_fail_rate",
                          "raw_no_def_rate", "entry_point_mismatch_rate",
                          "extraction_repaired_rate", "uncompilable_rate",
                          "identical_to_base", "gen_seconds")}
        print(f"[retention] {name:16s} pass@1+ {rep['pass@1_plus']}  "
              f"fmt_fail {rep['format_fail_rate']}  raw_no_def "
              f"{rep['raw_no_def_rate']}  repaired "
              f"{rep['extraction_repaired_rate']}  uncompilable "
              f"{rep['uncompilable_rate']}  ({gen_s}s)", flush=True)

    print("\n" + json.dumps({"model": args.model, "benchmark": args.benchmark,
                             "arms": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
