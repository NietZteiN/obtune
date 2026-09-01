"""Offline vLLM evaluation — one parquet per (system, eval_condition) cell.

    python -m obtune.eval_vllm --config configs/eval/pilot_w1.yaml --mode grid
    python -m obtune.eval_vllm --config configs/train/pilot_qwen1.5b_l1b.yaml --mode ckpt-select

Structure
---------
The unit of work is a **cell** = (system, eval_condition). One engine is built per
model and reused across every cell, because engine startup dominates a 1.5k-item cell.
Adapters ride on `LoRARequest`s attached per request, so a single engine serves the
base system, several per-condition adapters and a routed system in the same process.

Idempotent resume (the pattern from model_understanding/src/batch_runner.py, moved from
per-item files to per-cell parquets): a cell whose `trials.parquet` already exists is
skipped. That makes the grid restartable after an OOM or a preempted tmux session
without re-spending GPU time, and it makes `--mode grid` safe to re-run as new adapters
finish training.

Two correctness checks live here rather than in analysis, because after the engine is
torn down the evidence is gone:
  * `assert_adapter_effective` — a tuned cell whose outputs are byte-identical to the
    base cell means the LoRA silently failed to load (CLAUDE.md §4.2). vLLM will happily
    ignore an adapter whose target modules do not match.
  * H1 reads go through `data.load_h1_items`, which requires an access purpose and
    appends to the quarantine access log (CLAUDE.md §3.2 rule 3).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from obtune import data, prompts, scoring
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RESULTS_DIR, RUNS_DIR, load_config
from obtune.provenance import sha256_dir, sha256_file, sha256_text
from obtune.schema import EvalItem, TrialRow

STUB_MARKER = "STUB_DO_NOT_USE"
SCRIPTS_FOR_PROVENANCE = [
    "src/obtune/eval_vllm.py",
    "src/obtune/prompts.py",
    "src/obtune/scoring.py",
    "src/obtune/data.py",
]


@dataclass
class SystemSpec:
    """One row of `systems:` in a configs/eval/*.yaml."""

    name: str
    arch: str = "none"
    adapter: Optional[str] = None
    train_cond: Optional[str] = None
    prompt_oracle: bool = False
    one_shot: bool = False
    #: ICL baseline: draw `icl_k` in-context demos from these conditions. H1 is refused by
    #: `icl.demos.pick_demos` — a demo is prompt conditioning, which CLAUDE.md §3.2 rule 2
    #: forbids for the held-out family. For the OOD arm, H1 is the QUERY, never the source.
    icl_source: Optional[list] = None
    icl_k: int = 0
    #: Oracle routing: the item's TRUE condition selects its adapter, upper-bounding the
    #: learned router. Declared in configs since the design doc was written but never read
    #: by any code path until now — an `arch="per_type"` row with no adapter, which
    #: `expand_systems` rejected outright.
    oracle_route: bool = False
    #: condition -> adapter path, populated by `expand_systems` for oracle-routed systems.
    adapter_map: Optional[dict[str, str]] = None
    route_map: Optional[str] = None  # item_id -> adapter path (JSON), for arch="router"
    #: External baseline (e.g. "semcoder"). Such a model is run in ITS OWN prompt and
    #: answer format, not obtune's — measuring a published model through a foreign
    #: template would understate it and make the comparison meaningless.
    baseline: Optional[str] = None
    prompt_style: Optional[str] = None  # baseline-specific, e.g. monologue | cot
    #: Symbolic-normalization baseline: rewrite the obfuscated program with the static
    #: passes in `normalize.PROFILES[normalize]` BEFORE prompting. Zero training, zero
    #: extra GPU — the "what does a compiler-style normalizer already recover?" arm.
    #: Soundness is gated offline by scripts/analysis/21_validate_normalized.py.
    normalize: Optional[str] = None

    @classmethod
    def from_config(cls, d: Mapping[str, Any]) -> "SystemSpec":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})

    @property
    def is_routed(self) -> bool:
        return self.route_map is not None

    @property
    def is_oracle_routed(self) -> bool:
        return bool(self.oracle_route)


@dataclass
class CellResult:
    cell_dir: Path
    n_items: int
    accuracy: float
    format_fail_rate: float
    skipped: bool = False
    elapsed_s: float = 0.0
    tokens_per_sec: float = 0.0


def cell_dir(
    out_root: Path, phase: str, model: str, language: str, system: str, eval_cond: str
) -> Path:
    return Path(out_root) / phase / model / language / f"{system}__{eval_cond}"


class GridCollisionError(RuntimeError):
    """A resume target was evaluated on a different grid than the one now requested."""


def _assert_resume_same_grid(cell: Path, meta_base: Mapping[str, Any]) -> None:
    """Refuse to resume a cell that belongs to the other evaluation grid.

    `cell_dir` keys on `phase` but NOT on `eval_source`, so a `heldout` (Grid A) run and a
    `testset` (Grid B) run that share a phase and a system name resolve to the SAME path.
    Under `resume: true` the second run then finds the first's parquet and skips it — the
    job reports success while writing nothing, and the resulting table mixes n=1670 and
    n=176 cells in one row. That happened on 2026-08-13/14 and cost 33 cells; the phase-level
    fix of 2026-08-13 only moved the collision down one level. See MASTER_REPORT §12.1.

    Fail loudly instead. A grid mismatch is never something the operator meant, and the
    remedy is a one-line config change (give the run its own `phase`), so an error here is
    strictly better than a silent skip. Cells written before this field existed carry no
    `eval_source`; those fall back to comparing item counts, which is the same discriminator
    used to reconstruct the damage after the fact.
    """
    want = meta_base.get("eval_source")
    meta_p = cell / "cell_meta.json"
    if want is None or not meta_p.exists():
        return
    try:
        have_meta = json.loads(meta_p.read_text())
    except (OSError, ValueError):
        return  # unreadable meta is not evidence of a mismatch; leave resume alone
    have = have_meta.get("eval_source")
    if have is None or have == want:
        return
    raise GridCollisionError(
        f"refusing to resume {cell}: it was evaluated on eval_source={have!r} "
        f"(n_items={have_meta.get('n_items')}) but this run requests eval_source={want!r}. "
        f"Two grids are aliasing at one cell path because `cell_dir` keys on `phase` only. "
        f"Give this run its own `phase:` in its config (and add it to TrialRow.phase), or "
        f"pass --no-resume with a distinct --out-root."
    )


def resolve_path(p: str | os.PathLike) -> Path:
    q = Path(p)
    return q if q.is_absolute() else PROJECT_ROOT / q


# --------------------------------------------------------------------------- #
# Prompt + row construction (pure — no engine needed, so it is unit-testable)
# --------------------------------------------------------------------------- #

def drop_overlong(
    items: Sequence[EvalItem], texts: Sequence[str], tokenizer: Any,
    max_model_len: int, max_new_tokens: int,
) -> tuple[list[EvalItem], list[str], list[dict[str, Any]]]:
    """Remove prompts that cannot fit the context window.

    vLLM raises on an over-long prompt, which kills the ENTIRE cell — a single
    pathological item (one APPS program shipped a 19,950-character argument literal)
    took out all 1,671 items with it. Dropping and recording is the right trade: the
    item is unanswerable either way, and the other 1,670 are not.

    Truncating instead would be worse than dropping. A truncated program is a
    different program, so the model would be graded against the output of code it
    never saw.
    """
    budget = max_model_len - max_new_tokens
    keep_i: list[EvalItem] = []
    keep_t: list[str] = []
    dropped: list[dict[str, Any]] = []
    for it, tx in zip(items, texts):
        n = len(tokenizer(tx).input_ids)
        if n > budget:
            dropped.append({"item_id": it.item_id, "program_id": it.program_id,
                            "n_tokens": n, "budget": budget})
        else:
            keep_i.append(it)
            keep_t.append(tx)
    return keep_i, keep_t, dropped


def _icl_demo(system: "SystemSpec", item) -> Optional[object]:
    """One in-context demo for `item`, or None when the system is not an ICL arm.

    The evaluated program is excluded so it can never be its own demo — in-context split
    leakage, which would inflate exactly the cells the baseline exists to measure.
    Deterministic per item so a cell is reproducible.
    """
    if not system.icl_k or not system.icl_source:
        return None
    from obtune.icl.demos import pick_demos

    demos = _icl_demos(system, item)
    return demos[0] if demos else None


def _icl_demos(system: "SystemSpec", item) -> list:
    """All `icl_k` demos for `item`, in prompt order (empty when not an ICL arm)."""
    if not system.icl_k or not system.icl_source:
        return []
    from obtune.icl.demos import pick_demos

    pid = getattr(item, "program_id", None) or getattr(item, "snippet_id", None)
    return pick_demos(item.language, system.icl_k, list(system.icl_source),
                      exclude_program_ids={pid} if pid else None,
                      seed=_stable_seed(pid, system.name))


def _stable_seed(*parts: Any) -> int:
    """A per-item seed that is identical across processes.

    NOT `hash()`: Python randomizes string hashing per interpreter, and `seedutil` setting
    PYTHONHASHSEED in-process is too late to change it. Using `hash()` here would have made
    every ICL cell pick different demos on re-run — silently unreproducible, which
    CLAUDE.md's seed rule exists to prevent.
    """
    digest = hashlib.sha256("\x00".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(digest[:4], "big")


def _normalized_code(system: "SystemSpec", item) -> str:
    """`item.code` after the static normalization passes, or unchanged when not that arm."""
    if not system.normalize:
        return item.code
    from obtune.normalize import normalize

    return normalize(item.code, item.language, entry_point=item.entry_point,
                     profile=system.normalize).code


def render_prompts(items: Sequence[EvalItem], system: SystemSpec, tokenizer: Any) -> list[str]:
    if system.baseline == "semcoder":
        from obtune.baselines.semcoder import SemCoderSpec

        spec = SemCoderSpec(style=system.prompt_style or "monologue")
        # Raw completion prompts, not the chat template: this is the form SemCoder was
        # trained and evaluated in upstream.
        return [spec.build(it.code, it.entry_point, it.args_repr) for it in items]
    if system.icl_k:
        # k demos need the composing builder. At k=1 it is byte-identical to the frozen
        # one-shot path (asserted in tests/test_icl_prompts.py), so the k-sweep does not
        # confound "more demonstrations" with "a different prompt format".
        from obtune.icl.prompts import build_icl_prompt

        return [
            prompts.render_chat(
                build_icl_prompt(
                    code=_normalized_code(system, it),
                    entry_point=it.entry_point,
                    args_repr=it.args_repr,
                    language=it.language,
                    condition=it.condition,
                    oracle=system.prompt_oracle,
                    demos=_icl_demos(system, it),
                ),
                tokenizer,
            )
            for it in items
        ]
    return [
        prompts.render_chat(
            prompts.build_prompt(
                code=_normalized_code(system, it),
                entry_point=it.entry_point,
                args_repr=it.args_repr,
                language=it.language,
                condition=it.condition,
                oracle=system.prompt_oracle,
                one_shot=system.one_shot,
                demo=None,
            ),
            tokenizer,
        )
        for it in items
    ]


def build_trial_rows(
    items: Sequence[EvalItem],
    outputs: Sequence[str],
    n_tokens: Sequence[int],
    system: SystemSpec,
    meta: Mapping[str, Any],
    float_tol: float = scoring.DEFAULT_FLOAT_TOL,
) -> list[dict[str, Any]]:
    """Grade + shape into schema.TrialRow dicts. Validated row by row, on purpose:
    a malformed trial must fail here, not in the R stats layer three days later."""
    rows: list[dict[str, Any]] = []
    extract = None
    if system.baseline == "semcoder":
        from obtune.baselines.semcoder import extract_answer as extract

    for it, out, ntok in zip(items, outputs, n_tokens):
        # A baseline answers in its own format; recover the literal before grading, or
        # every row scores zero against a correct answer wrapped in [ANSWER] tags.
        graded_text = extract(out) if extract else out
        g = scoring.grade(graded_text, it.output_repr, it.language, float_tol)
        row = TrialRow(
            run_id=meta["run_id"],
            run_ts=meta["run_ts"],
            seed=int(meta["seed"]),
            phase=meta["phase"],
            experiment_id=meta["experiment_id"],
            base_model=meta["base_model"],
            model_family=meta["model_family"],
            adapter_id=meta.get("adapter_id"),
            adapter_arch=system.arch,
            train_cond=system.train_cond,
            eval_cond=it.condition,
            language=it.language,
            dataset=it.dataset,
            snippet_id=it.program_id,
            item_id=it.item_id,
            is_core=1,
            h1_access_purpose=meta.get("h1_access_purpose") if it.condition == "H1" else None,
            prompt_id=meta["prompt_id"],
            output_raw=out,
            output_parsed=g.pred_norm,
            correct=int(g.correct),
            parse_ok=int(g.parse_ok),
            grade_method=g.grade_method,
            error_category=scoring.error_category(g, it.language),
            n_gen_tokens=int(ntok),
            gpu_id=meta.get("gpu_id"),
            config_sha=meta.get("config_sha"),
            script_sha=meta.get("script_sha"),
        )
        d = row.model_dump()
        d["raw_exact"] = int(g.raw_exact)  # grading-sensitivity appendix column
        d["format_fail"] = int(g.format_fail)
        rows.append(d)
    return rows


def write_cell(cell: Path, rows: list[dict[str, Any]], meta: Mapping[str, Any]) -> Path:
    import pandas as pd

    cell.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    out = cell / "trials.parquet"
    df.to_parquet(out, index=False)
    (cell / "cell_meta.json").write_text(json.dumps(dict(meta), indent=2, default=str))
    return out


def assert_adapter_effective(tuned_cell: Path, base_cell: Path) -> None:
    """A tuned cell identical to base means the adapter never loaded (CLAUDE.md §4.2)."""
    import pandas as pd

    if not (tuned_cell / "trials.parquet").exists() or not (base_cell / "trials.parquet").exists():
        return
    a = pd.read_parquet(tuned_cell / "trials.parquet").set_index("item_id")["output_raw"]
    b = pd.read_parquet(base_cell / "trials.parquet").set_index("item_id")["output_raw"]
    common = a.index.intersection(b.index)
    if len(common) == 0:
        return
    if (a.loc[common] == b.loc[common]).all():
        raise RuntimeError(
            f"{tuned_cell.name}: every generation is byte-identical to {base_cell.name}. "
            "The LoRA adapter is not being applied — check target_modules and max_lora_rank."
        )


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #

def _gpu_mem_util(ecfg: dict) -> float:
    """vLLM's share of the GPU, with a shared-box escape hatch.

    The configured 0.90 assumes an idle GPU, which is the normal case for a grid
    run. On this host other people's jobs come and go, and vLLM refuses to start
    (rather than shrinking) when the requested fraction exceeds what is free —
    so OBTUNE_GPU_MEM_UTIL lets a run fit into the headroom beside a neighbour
    instead of either failing or crowding them out. Grid runs leave it unset.
    """
    env = os.environ.get("OBTUNE_GPU_MEM_UTIL")
    if env:
        return float(env)
    return float(ecfg.get("gpu_memory_utilization", 0.90))


class _UnroutedCell(RuntimeError):
    """A routed cell whose condition has no route-map entries at all (i.e. H1)."""


class Engine:
    """Thin wrapper over `vllm.LLM` with a per-adapter LoRARequest registry.

    `--stub` swaps generation for a deterministic no-model echo so the plumbing
    (prompt rendering, grading, parquet, resume) can be exercised on a box with no free
    GPU. Stub cells are stamped with a marker file and are refused by trial_table.py.
    """

    def __init__(self, model_id: str, ecfg: Mapping[str, Any], stub: bool = False):
        self.model_id = model_id
        self.ecfg = dict(ecfg)
        self.stub = stub
        self._llm = None
        self._tokenizer = None
        self._lora_ids: dict[str, int] = {}

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        return self._tokenizer

    @property
    def llm(self):
        if self._llm is None:
            from vllm import LLM

            self._llm = LLM(
                model=self.model_id,
                dtype=self.ecfg.get("dtype", "bfloat16"),
                gpu_memory_utilization=_gpu_mem_util(self.ecfg),
                enable_lora=True,
                max_lora_rank=int(self.ecfg.get("max_lora_rank", 64)),
                max_loras=int(self.ecfg.get("max_loras", 4)),
                max_cpu_loras=int(self.ecfg.get("max_cpu_loras", 32)),
                max_model_len=int(self.ecfg.get("max_model_len", 2048)),
                seed=int(self.ecfg.get("seed", GLOBAL_SEED)),
                enforce_eager=bool(self.ecfg.get("enforce_eager", False)),
            )
        return self._llm

    def lora_request(self, adapter_path: Optional[str]):
        if adapter_path is None:
            return None
        from vllm.lora.request import LoRARequest

        p = str(resolve_path(adapter_path))
        if p not in self._lora_ids:
            self._lora_ids[p] = len(self._lora_ids) + 1  # vLLM requires lora_int_id >= 1
        return LoRARequest(lora_name=Path(p).parent.name + "/" + Path(p).name,
                           lora_int_id=self._lora_ids[p], lora_path=p)

    def version(self) -> str:
        if self.stub:
            return "stub-no-model"
        import vllm

        return f"vllm-{vllm.__version__}"

    def generate(
        self, texts: Sequence[str], sampling: Mapping[str, Any], adapters: Sequence[Optional[str]]
    ) -> tuple[list[str], list[int]]:
        if self.stub:
            # Deterministic, obviously-not-a-model output. Never mistaken for a result.
            return [f"<stub:{sha256_text(t)[:8]}>" for t in texts], [4] * len(texts)
        from vllm import SamplingParams

        params = SamplingParams(
            temperature=float(sampling.get("temperature", 0.0)),
            top_p=float(sampling.get("top_p", 1.0)),
            max_tokens=int(sampling.get("max_tokens", 64)),
            stop=list(sampling.get("stop", []) or []),
            seed=int(sampling.get("seed", GLOBAL_SEED)),
        )
        # One LoRARequest per prompt: this is what makes a routed cell (a different
        # adapter per item) a single batched call instead of one call per adapter.
        reqs = [self.lora_request(a) for a in adapters]
        uniform = all(r is None for r in reqs) or (
            len({(r.lora_int_id if r else None) for r in reqs}) == 1
        )
        # TELEMETRY, not debug cruft. On 2026-08-12 every system in six eval runs produced
        # output byte-identical to base, and nothing in the logs said how many adapters the
        # call had actually been given — the failure was only visible after the fact, from
        # an assertion at the very end of a one-hour run. One line here answers "was a LoRA
        # applied, and to how many prompts" while the run is still going.
        n_lora = sum(1 for r in reqs if r is not None)
        print(f"[engine] {len(texts)} prompt(s), {n_lora} with a LoRA, "
              f"{len({r.lora_int_id for r in reqs if r})} distinct adapter(s), "
              f"uniform={uniform}", flush=True)
        outs = self.llm.generate(
            list(texts), params, lora_request=(reqs[0] if uniform else reqs), use_tqdm=True
        )
        gen = [o.outputs[0].text for o in outs]
        # If N distinct prompts come back as 1 distinct completion, the batch collapsed and
        # every downstream number is meaningless. Cheap to check, and it is exactly the
        # symptom that went unnoticed for six runs.
        print(f"[engine] returned {len(gen)} completion(s): "
              f"{len(set(texts))} distinct prompt(s) -> {len(set(gen))} distinct output(s)",
              flush=True)
        return (gen, [len(o.outputs[0].token_ids) for o in outs])


# --------------------------------------------------------------------------- #
# Grid mode
# --------------------------------------------------------------------------- #

def _load_route_map(path: str) -> dict[str, str]:
    with open(resolve_path(path)) as f:
        m = json.load(f)
    if not isinstance(m, dict):
        raise ValueError(f"route map {path} must be a JSON object item_id -> adapter path")
    return {str(k): str(v) for k, v in m.items()}


def run_cell(
    engine: Engine,
    items: Sequence[EvalItem],
    system: SystemSpec,
    cell: Path,
    cfg: Mapping[str, Any],
    meta_base: Mapping[str, Any],
    resume: bool = True,
    limit: Optional[int] = None,
) -> CellResult:
    import time

    if resume and (cell / "trials.parquet").exists():
        import pandas as pd

        _assert_resume_same_grid(cell, meta_base)
        df = pd.read_parquet(cell / "trials.parquet")
        return CellResult(cell, len(df), float(df["correct"].mean()),
                          float(df.get("format_fail", 0).mean()) if "format_fail" in df else 0.0,
                          skipped=True)

    items = list(items)[: limit or None]
    texts = render_prompts(items, system, engine.tokenizer)
    items, texts, overlong = drop_overlong(
        items, texts, engine.tokenizer,
        max_model_len=int(engine.ecfg.get("max_model_len", 4096)),
        max_new_tokens=int((engine.ecfg.get("max_tokens") or 64)),
    )
    if overlong:
        print(f"[eval_vllm] dropped {len(overlong)} over-long prompt(s): "
              f"{[d['item_id'] for d in overlong][:3]}")
    if not items:
        raise RuntimeError("every prompt in this cell exceeded the context window")

    n_skipped_h1 = 0
    if system.is_routed:
        route = _load_route_map(system.route_map)
        missing = [it.item_id for it in items if it.item_id not in route]
        if missing and len(missing) == len(items):
            # The WHOLE cell is unrouted. Expected for H1: it is the held-out family, has
            # no adapter, and CLAUDE.md §3.2 forbids it from router training, so it can
            # never appear in a route map. Its routing behaviour is reported from
            # routing.parquet (the entropy analysis), which needs no generation pass.
            # Skipped loudly rather than crashed — and never silently, because a whole
            # missing cell for a TRAINABLE condition would be a real defect.
            raise _UnroutedCell(
                f"no route-map entry for any item in this cell (condition="
                f"{items[0].condition!r}); expected for H1, a defect for anything else"
            )
        if missing:
            # A PARTIAL miss is always a bug: the route map and the eval set disagree
            # about which items exist, usually because they were built from different
            # eval sources (heldout ids look like `x::L0::0`, testset ids like `A:Py/1::L0::0`).
            raise KeyError(
                f"route map is missing {len(missing)} of {len(items)} item(s), e.g. "
                f"{missing[:3]} — route map and eval set were built from different sources?"
            )
        adapters = [route[it.item_id] for it in items]
    elif system.is_oracle_routed:
        amap = system.adapter_map or {}
        # H1 has no adapter by construction — it is the held-out family. Rather than
        # route it to base and label the row "oracle_route" (which would report the base
        # model as an oracle-routed result), those items are excluded here and the
        # routing upper bound for H1 is computed in analysis as the per-item best-of-6
        # over the already-run per-condition cells, at zero extra GPU cost (design doc §4.3).
        keep = [i for i, it in enumerate(items) if it.condition in amap]
        n_skipped_h1 = len(items) - len(keep)
        if n_skipped_h1:
            print(f"[eval_vllm] oracle_route: skipping {n_skipped_h1} item(s) whose condition "
                  f"has no adapter (expected for H1); the H1 bound is an analysis-side "
                  f"best-of-N over the per-condition cells")
        items = [items[i] for i in keep]
        texts = [texts[i] for i in keep]
        if not items:
            raise RuntimeError(
                "oracle_route cell has no items with an adapter — every condition in this "
                "cell is held out, so there is nothing to route"
            )
        adapters = [amap[it.condition] for it in items]
    else:
        adapters = [system.adapter] * len(items)

    t0 = time.time()
    outs, ntoks = engine.generate(texts, cfg.get("sampling", {}), adapters)
    elapsed = time.time() - t0

    adapter_ids = sorted({a for a in adapters if a})
    meta = {
        **meta_base,
        "system": system.name,
        "adapter_arch": system.arch,
        "n_skipped_no_adapter": n_skipped_h1,
        "adapter_id": system.adapter or (system.name if adapter_ids else None),
        "adapter_paths": adapter_ids,
        "adapter_sha256": {
            a: (sha256_dir(resolve_path(a)) if resolve_path(a).exists() else "missing")
            for a in adapter_ids
        },
        "engine": engine.version(),
        "sampling": dict(cfg.get("sampling", {})),
        "n_items": len(items),
        "eval_cond": items[0].condition if items else None,
        "elapsed_s": round(elapsed, 2),
        "gen_tokens": int(sum(ntoks)),
        "tokens_per_sec": round(sum(ntoks) / elapsed, 2) if elapsed > 0 else 0.0,
        **prompts.provenance_block(oracle=system.prompt_oracle, one_shot=system.one_shot),
    }
    rows = build_trial_rows(
        items, outs, ntoks, system, {**meta, **prompts.provenance_block(
            oracle=system.prompt_oracle, one_shot=system.one_shot)},
        float_tol=float((cfg.get("scoring") or {}).get("float_tol", scoring.DEFAULT_FLOAT_TOL)),
    )
    acc = sum(r["correct"] for r in rows) / len(rows) if rows else 0.0
    ff = sum(r["format_fail"] for r in rows) / len(rows) if rows else 0.0
    meta["accuracy"] = round(acc, 6)
    meta["format_fail_rate"] = round(ff, 6)
    write_cell(cell, rows, meta)
    if engine.stub:
        (cell / STUB_MARKER).write_text(
            "This cell was produced by --stub (no model was loaded). Not a result.\n"
        )
    return CellResult(cell, len(rows), acc, ff, elapsed_s=elapsed,
                      tokens_per_sec=meta["tokens_per_sec"])


def expand_systems(
    raw_systems: Sequence[Mapping[str, Any]],
    model_key: str,
    language: str,
    train_conditions: Sequence[str],
    seeds: Sequence[int],
    rank: int = 32,
    route_map: Optional[str] = None,
) -> list[SystemSpec]:
    """Turn `systems:` config rows into concrete SystemSpecs.

    A row carrying `expand_over: train_conditions` becomes one system per
    (train condition x seed), with its adapter path derived the same way
    train_sft.adapter_dir() builds it. Without this the row collapses to a single
    system with `adapter: None`, which evaluates the BASE weights while labelling
    the cell `per_type` — a silent, invisible corruption of the whole matrix.
    """
    from obtune.train_sft import cond_tag

    out: list[SystemSpec] = []
    for row in raw_systems:
        row = dict(row)
        if row.pop("expand_over", None) != "train_conditions":
            out.append(SystemSpec.from_config(row))
            continue
        for cond in train_conditions:
            for seed in seeds:
                tag = cond_tag([cond])
                adapter = (RUNS_DIR / "adapters" / model_key / language
                           / f"{tag}_r{rank}_s{seed}" / "best")
                spec = dict(row)
                spec["name"] = f"tuned_{cond}_s{seed}" if len(seeds) > 1 else f"tuned_{cond}"
                spec["train_cond"] = cond
                spec["adapter"] = str(adapter)
                out.append(SystemSpec.from_config(spec))

    # `{model}` / `{language}` in an explicit `adapter:` path. A model-neutral eval config
    # cannot hard-code `runs/adapters_formatonly/qwen25c-7b/python/...` and still serve the
    # panel, and deriving the path is not an option for banks that live OUTSIDE
    # runs/adapters/ (the format floor has its own adapter_root precisely so it cannot
    # overwrite the real L0 bank). Substitution keeps one config per experiment instead of
    # one per (experiment x model).
    for spec in out:
        if spec.adapter and ("{model}" in spec.adapter or "{language}" in spec.adapter):
            spec.adapter = spec.adapter.format(model=model_key, language=language)
        if spec.adapter_map:
            spec.adapter_map = {
                k: v.format(model=model_key, language=language)
                if ("{model}" in v or "{language}" in v) else v
                for k, v in spec.adapter_map.items()
            }

    # A merge system's adapter sits at a conventional path written by merge_adapters
    # (`runs/adapters/<model>/<lang>/<name>_r<rank>_s<seed>`), exactly as a per-condition
    # adapter does — so derive it rather than making every eval config repeat six paths
    # that must then be kept in sync with the merge jobs.
    for spec in out:
        if spec.arch.startswith("merge") and not spec.adapter:
            spec.adapter = str(RUNS_DIR / "adapters" / model_key / language
                               / f"{spec.name}_r{rank}_s{seeds[0]}")

    # Oracle routing needs the same condition -> adapter layout the per-condition
    # expansion uses, but as a MAP rather than one adapter per system: the dispatch is
    # per item, on the item's true condition.
    for spec in out:
        if spec.arch == "oracle_route":
            spec.oracle_route = True
    for spec in out:
        if spec.oracle_route and not spec.adapter_map:
            spec.adapter_map = {
                cond: str(RUNS_DIR / "adapters" / model_key / language
                          / f"{cond_tag([cond])}_r{rank}_s{seeds[0]}" / "best")
                for cond in train_conditions
            }

    if route_map:
        for spec in out:
            if spec.arch == "router" and not spec.route_map:
                spec.route_map = route_map

    return out


def validate_systems(out: Sequence[SystemSpec]) -> list[SystemSpec]:
    """Refuse systems that would silently evaluate base weights under a tuned label.

    Called AFTER the `--systems` filter, not inside `expand_systems`. Validating every
    row in the config meant a job asking only for `base` still died on the config's
    `router` row — 28 eval-cell and 8 eval-rq2 jobs failed that way without ever loading
    a model. The guards themselves are load-bearing and unchanged; only *when* they run
    has moved, so a system that is actually about to run is still refused.
    """
    for spec in out:
        if spec.arch in ("per_type", "mono") or spec.arch.startswith("merge"):
            # An oracle-routed system legitimately carries no single adapter — it carries
            # a map and picks per item. Without this exemption the config row declared in
            # grid_v1.yaml was rejected outright, which is why the feature was dead.
            if not spec.adapter and not spec.oracle_route:
                raise ValueError(
                    f"system {spec.name!r} has arch={spec.arch!r} but no adapter path — "
                    "it would evaluate base weights labelled as a tuned system"
                )
        if spec.oracle_route and not spec.adapter_map:
            raise ValueError(
                f"system {spec.name!r} sets oracle_route but has no adapter_map — it "
                "would evaluate base weights labelled as oracle-routed"
            )
        if spec.arch == "router" and not spec.route_map:
            raise ValueError(
                f"system {spec.name!r} has arch='router' but no route map — it would "
                "evaluate base weights labelled as routed. Pass --route-map."
            )
    return out


def run_grid(args: argparse.Namespace) -> dict[str, Any]:
    from obtune.train_sft import resolve_model_cfg

    cfg = load_config(args.config)
    phase = cfg.get("phase", "main")
    languages = cfg.get("languages") or [cfg["language"]]
    # A model-neutral eval config pins no model at all, so `--model` SUPPLIES it rather than
    # restricting an existing list. When the config does pin models the old semantics hold:
    # asking for one it does not declare is still an error, which is what stops a job
    # evaluating a model the config was never written for.
    declared = cfg.get("models") or ([cfg["model"]] if "model" in cfg else None)
    if getattr(args, "model", None):
        if declared is not None and args.model not in declared:
            raise ValueError(f"--model {args.model!r} is not in {args.config} ({declared})")
        models = [args.model]
    elif declared is None:
        raise ValueError(
            f"{args.config} declares no `model:` and no --model was given. A model-neutral "
            "config REQUIRES --model; guessing one would evaluate the wrong base."
        )
    else:
        models = declared
    if getattr(args, "language", None):
        if args.language not in languages:
            raise ValueError(f"--language {args.language!r} is not in {args.config} ({languages})")
        languages = [args.language]
    eval_conditions = list(cfg["eval_conditions"])
    raw_systems = list(cfg["systems"])
    eval_source = args.source or cfg.get("eval_source", data.DEFAULT_EVAL_SOURCE)
    grid_train_conditions = list(cfg.get("train_conditions") or [])
    grid_seeds = [int(x) for x in (cfg.get("seeds") or [cfg.get("seed", GLOBAL_SEED)])]
    if args.eval_conditions:
        eval_conditions = [c for c in eval_conditions if c in set(args.eval_conditions.split(","))]

    out_root = resolve_path(args.out_root) if args.out_root else RESULTS_DIR / "cells"
    if args.stub and out_root.is_relative_to(RESULTS_DIR / "cells") and not args.allow_stub_in_results:
        raise SystemExit(
            "--stub writes fake generations; point --out-root somewhere outside "
            "results/cells/ (or pass --allow-stub-in-results if you really mean it)."
        )

    resume = bool((cfg.get("output") or {}).get("resume", True)) and not args.no_resume
    run_ts = datetime.now(timezone.utc).isoformat()
    config_sha = sha256_file(cfg["_config_path"])
    script_sha = sha256_file(PROJECT_ROOT / "src" / "obtune" / "eval_vllm.py")
    summary: dict[str, Any] = {"cells": [], "config": args.config, "run_ts": run_ts}

    for model_key in models:
        mcfg = resolve_model_cfg({"model": model_key})
        for language in languages:
            # Adapter paths depend on model AND language, so systems are expanded
            # here rather than once at config-load time.
            systems = expand_systems(
                raw_systems, model_key, language, grid_train_conditions, grid_seeds,
                rank=int((cfg.get("peft") or {}).get("r", 32)),
                route_map=args.route_map,
            )
            if args.systems:
                keep = set(args.systems.split(","))
                systems = [sy for sy in systems if sy.name in keep]
                if not systems:
                    raise ValueError(
                        f"--systems {args.systems!r} selected nothing from "
                        f"{args.config}; check the names in its `systems:` block"
                    )
            if args.route_map:
                for sy in systems:
                    if sy.arch == "router":
                        sy.route_map = args.route_map
            # Validate only what will actually run (see validate_systems).
            validate_systems(systems)

            engine = Engine(
                mcfg["hf_id"],
                # An explicit engine.max_model_len in the eval config wins: eval
                # prompts are longer than training sequences (a one-shot oracle demo
                # prepended to flattened S1/S2 code overruns the train-time bound),
                # and silently truncating them would corrupt exactly the structural
                # conditions the transfer matrix is about.
                {"max_model_len": mcfg.get("max_seq_len", 1536) + 128,
                 **(cfg.get("engine") or {})},
                stub=args.stub,
            )
            for cond in eval_conditions:
                items = data.load_eval_items(
                    [cond],
                    language,
                    h1_access_purpose=cfg.get("h1_access_purpose"),
                    script="eval_vllm.py",
                    source=eval_source,
                )
                data.validate_eval_items(items)
                for system in systems:
                    cell = cell_dir(out_root, phase, model_key, language, system.name, cond)
                    meta_base = {
                        "run_id": f"{phase}__{model_key}__{language}__{system.name}__{cond}",
                        "run_ts": run_ts,
                        "seed": int((cfg.get("engine") or {}).get("seed", GLOBAL_SEED)),
                        "phase": phase,
                        # The grid this cell was evaluated on. Absent before 2026-08-14, which
                        # is how two grids came to alias at one path: `cell_dir` keys on
                        # `phase` but not on `eval_source`, so a `heldout` run resumed
                        # `testset` cells and skipped them. Recorded here so `_resume_ok`
                        # can compare, and so the grid of any cell is readable without
                        # counting rows. See `docs/MASTER_REPORT_2026-08-12.md` §12.1.
                        "eval_source": eval_source,
                        "experiment_id": cfg.get("experiment_id", Path(args.config).stem),
                        "base_model": mcfg["hf_id"],
                        "model_family": mcfg["family"],
                        "adapter_id": system.adapter,
                        "h1_access_purpose": cfg.get("h1_access_purpose"),
                        "gpu_id": os.environ.get("CUDA_VISIBLE_DEVICES"),
                        "config_sha": config_sha,
                        "script_sha": script_sha,
                        "git_commit": _git_commit(),
                        **prompts.provenance_block(
                            oracle=system.prompt_oracle, one_shot=system.one_shot
                        ),
                    }
                    try:
                        res = run_cell(
                            engine, items, system, cell, cfg, meta_base,
                            resume=resume, limit=args.limit,
                        )
                    except _UnroutedCell as exc:
                        # Recorded as a skipped cell, not a failure: the routed system
                        # genuinely has nothing to say about a held-out condition.
                        print(f"[eval_vllm] {model_key}/{language} {system.name}__{cond}: "
                              f"SKIPPED — {exc}", flush=True)
                        summary["cells"].append({
                            "model": model_key, "language": language,
                            "system": system.name, "eval_cond": cond,
                            "n": 0, "skipped": True, "skip_reason": "unrouted_condition",
                        })
                        continue
                    print(
                        f"[eval_vllm] {model_key}/{language} {system.name}__{cond}: "
                        f"n={res.n_items} acc={res.accuracy:.3f} "
                        f"format_fail={res.format_fail_rate:.3f}"
                        f"{' (resumed)' if res.skipped else ''}",
                        flush=True,
                    )
                    summary["cells"].append(
                        {
                            "model": model_key, "language": language, "system": system.name,
                            "eval_cond": cond, "n": res.n_items, "accuracy": res.accuracy,
                            "format_fail_rate": res.format_fail_rate, "skipped": res.skipped,
                            "tokens_per_sec": res.tokens_per_sec, "path": str(res.cell_dir),
                        }
                    )
                # Adapter-applied check, per condition, against this grid's base cell.
                base_sys = next((s for s in systems if s.arch == "none" and not s.prompt_oracle), None)
                if base_sys is not None and not args.stub:
                    base_cell = cell_dir(out_root, phase, model_key, language, base_sys.name, cond)
                    for system in systems:
                        if system.adapter or system.is_routed:
                            assert_adapter_effective(
                                cell_dir(out_root, phase, model_key, language, system.name, cond),
                                base_cell,
                            )
    return summary


def _git_commit() -> Optional[str]:
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Checkpoint selection
# --------------------------------------------------------------------------- #

def list_checkpoints(adapter_root: Path) -> list[tuple[str, Path]]:
    """Epoch checkpoints in training order, plus `final` if present."""
    cks = sorted(
        (p for p in adapter_root.glob("checkpoint-*") if p.is_dir()),
        key=lambda p: int(p.name.split("-")[-1]),
    )
    out = [(p.name, p) for p in cks]
    fin = adapter_root / "final"
    if fin.is_dir():
        out.append(("final", fin))
    return out


def select_checkpoint(
    accs: Sequence[tuple[str, float]], tolerance_pts: float
) -> tuple[str, float]:
    """Earliest checkpoint wins ties. A later epoch must beat the incumbent by MORE
    than `tolerance_pts` (configs/train/_base_lora.yaml ckpt_select.tolerance_pts) to
    take over — noise on a ~1k val slice is worth ~1 pt, so without a tolerance this
    would just pick the noisiest epoch, and later epochs are the more over-fit ones."""
    if not accs:
        raise ValueError("no checkpoints to select from")
    best_name, best_acc = accs[0]
    tol = tolerance_pts / 100.0
    for name, acc in accs[1:]:
        if acc > best_acc + tol:
            best_name, best_acc = name, acc
    return best_name, best_acc


def run_ckpt_select(args: argparse.Namespace) -> dict[str, Any]:
    from obtune.train_sft import _effective_train_knobs, adapter_dir, resolve_model_cfg

    cfg = load_config(args.config)
    # `--model` is an OVERRIDE here, exactly as in train_sft. Without this, a model-neutral
    # train config silently inherits `model: qwen25c-1.5b` from _base_lora.yaml and this
    # path builds the WRONG base model, then fails deep inside vLLM with a tensor-shape
    # mismatch (1536 vs 4096 -- Qwen-1.5B's hidden size against CodeLlama-7b's) that names
    # neither model. Training was unaffected only because train_sft applies the override.
    if getattr(args, "model", None):
        cfg["model"] = args.model
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    root = resolve_path(args.adapter_root) if args.adapter_root else adapter_dir(cfg)
    cks = list_checkpoints(root)
    if not cks:
        raise SystemExit(f"no checkpoints under {root}")

    # The held-in val slice: SAME conditions the adapter was trained on, split=='val'.
    # H1 must never influence checkpoint selection (CLAUDE.md §3.2 rule 2), and neither
    # may the test set — this is the only model-selection signal in the project.
    #
    # `allow_composites` is forwarded from the SAME config the adapter was trained with,
    # exactly as `data.build_sft_splits` does it. Without this an adapter trained on the
    # `C_` ladder trains for hours and then dies here on QuarantineViolation, because the
    # composite codes are deliberately outside `paths.TRAINABLE_CONDITIONS` — a failure
    # that costs a full training run and lands only at checkpoint selection. Reading it
    # from the config rather than defaulting it True keeps the guard doing its job for
    # every other arm: a config that did not opt in still cannot load composites here.
    val_rows = data.load_pairs(cfg["train_conditions"], cfg["language"], splits=["val"],
                               allow_composites=bool(cfg.get("allow_composites", False)))
    if args.limit:
        val_rows = val_rows[: args.limit]
    items = [
        EvalItem(
            item_id=r.item_id, program_id=r.program_id, dataset="A", condition=r.condition,
            language=r.language, code=r.code, entry_point=r.entry_point,
            args_repr=r.args_repr, output_repr=r.output_repr,
        )
        for r in val_rows
    ]
    ecfg = load_config("eval/_base_eval.yaml")
    engine = Engine(
        mcfg["hf_id"],
        {**ecfg["engine"], "max_model_len": int(tcfg["max_seq_len"]) + 128},
        stub=args.stub,
    )
    texts = render_prompts(items, SystemSpec(name="ckpt"), engine.tokenizer)

    accs: list[tuple[str, float]] = []
    for name, path in cks:
        outs, _ = engine.generate(texts, ecfg["sampling"], [str(path)] * len(texts))
        gs = [scoring.grade(o, it.output_repr, it.language) for o, it in zip(outs, items)]
        acc = sum(g.correct for g in gs) / len(gs)
        accs.append((name, acc))
        print(f"[ckpt-select] {name}: exact_match={acc:.4f} (n={len(gs)})", flush=True)

    tol = float((cfg.get("ckpt_select") or {}).get("tolerance_pts", 0.2))
    best_name, best_acc = select_checkpoint(accs, tol)
    best_link = root / "best"
    if best_link.is_symlink() or best_link.exists():
        best_link.unlink()
    best_link.symlink_to(dict(cks)[best_name].resolve(), target_is_directory=True)

    out = {
        "adapter_root": str(root),
        "metric": (cfg.get("ckpt_select") or {}).get("metric", "exact_match"),
        "tolerance_pts": tol,
        "n_val_items": len(items),
        "val_conditions": list(cfg["train_conditions"]),
        "accuracies": dict(accs),
        "best": best_name,
        "best_accuracy": best_acc,
        "best_symlink": str(best_link),
        "engine": engine.version(),
        "selected_utc": datetime.now(timezone.utc).isoformat(),
    }
    (root / "ckpt_select.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out


# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="vLLM offline evaluation")
    ap.add_argument("--config", required=True)
    ap.add_argument("--mode", choices=["grid", "ckpt-select"], default="grid")
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--out-root", default=None, help="default results/cells")
    ap.add_argument("--adapter-root", default=None, help="ckpt-select: override the adapter dir")
    ap.add_argument("--route-map", default=None, help="JSON item_id -> adapter path (routed cells)")
    ap.add_argument("--systems", default=None, help="comma-separated subset of system names")
    # Without these, a job runs the config's FULL model x language cross-product. The RQ2
    # jobs are emitted one per (model, language) but carried no filter, so each redundantly
    # re-ran all six combinations — and died on the models that have no adapters
    # (a 1.5B/javascript job failed loading a 7B/python merge).
    ap.add_argument("--model", default=None, help="restrict to one model key from the config")
    ap.add_argument("--language", default=None, help="restrict to one language from the config")
    ap.add_argument("--source", default=None, choices=["testset", "heldout"],
                    help="evaluation set: testset = the human-labelled ICSE programs, "
                         "heldout = corpus programs in the `test` split (higher n)")
    ap.add_argument("--eval-conditions", default=None, help="comma-separated subset")
    ap.add_argument("--limit", type=int, default=None, help="cap items per cell (smoke runs)")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--stub", action="store_true", help="no model; deterministic fake generations")
    ap.add_argument("--allow-stub-in-results", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="render prompts, write nothing")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.gpu is not None:
        from obtune import gpu

        gpu.pin([args.gpu])
    elif not args.stub and not args.dry_run and not os.environ.get("CUDA_VISIBLE_DEVICES"):
        from obtune import gpu

        gpu.pin(gpu.pick_free_gpus(1))

    if args.dry_run:
        cfg = load_config(args.config)
        systems = [SystemSpec.from_config(s) for s in cfg.get("systems", [{"name": "base"}])]
        lang = (cfg.get("languages") or [cfg.get("language", "python")])[0]
        cond = cfg["eval_conditions"][0]
        items = data.load_eval_items([cond], lang, h1_access_purpose=cfg.get("h1_access_purpose"),
                                     script="eval_vllm.py --dry-run")
        from transformers import AutoTokenizer
        from obtune.train_sft import resolve_model_cfg

        mcfg = resolve_model_cfg({"model": (cfg.get("models") or [cfg["model"]])[0]})
        tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
        texts = render_prompts(items[:1], systems[0], tok)
        print(json.dumps({
            "systems": [s.name for s in systems],
            "eval_conditions": cfg["eval_conditions"],
            "n_items_first_cell": len(items),
            "prompt_id": prompts.prompt_id(systems[0].prompt_oracle, systems[0].one_shot),
            "prompt_template_sha256": prompts.template_sha256(),
        }, indent=2))
        print("--- rendered prompt (first item) ---")
        print(texts[0])
        return 0

    if args.mode == "ckpt-select":
        run_ckpt_select(args)
        return 0
    summary = run_grid(args)
    print(json.dumps({"n_cells": len(summary["cells"])}, indent=2))
    return 0


def _main_fastfail() -> int:
    """`main()`, but a GridCollisionError exits IMMEDIATELY instead of unwinding.

    THE THIRD WEDGE. `_assert_resume_same_grid` correctly refuses to resume a cell from the
    other grid — but raising inside a process that has already built a vLLM engine means
    Python runs `multiprocessing.util._exit_function`, which joins an `EngineCore` child
    that never terminates. The traceback reaches the job log and the process then sleeps
    FOREVER holding ~45 GB, with its claim stuck in `running/`. That is the 2026-08-11
    failure mode, and on 2026-08-15 three fill jobs reproduced it in a row.

    `kill_stalled` does eventually reap this (CPU time is the discriminator and a wedged
    process accrues none), but only after 30 minutes idle plus grace — during which a GPU is
    held and the pipeline's drain cannot advance.

    A grid collision is a CONFIG error: nothing has been written, there is no state to flush,
    and no cleanup is owed. `os._exit` skips the atexit handlers that hang, so the worker
    sees a fast non-zero exit, records the failure, and frees the card in seconds. Every
    other exception keeps the normal path, because those may legitimately need cleanup.
    """
    try:
        return main()
    except GridCollisionError as exc:
        print(f"[eval_vllm] GRID COLLISION — exiting immediately without vLLM teardown:\n{exc}",
              file=sys.stderr, flush=True)
        sys.stderr.flush()
        os._exit(3)


if __name__ == "__main__":
    sys.exit(_main_fastfail())
