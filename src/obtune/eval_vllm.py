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
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from obtune import data, prompts, scoring
from obtune.config import GLOBAL_SEED, PROJECT_ROOT, RESULTS_DIR, load_config
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
    oracle_route: bool = False
    route_map: Optional[str] = None  # item_id -> adapter path (JSON), for arch="router"

    @classmethod
    def from_config(cls, d: Mapping[str, Any]) -> "SystemSpec":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})

    @property
    def is_routed(self) -> bool:
        return self.route_map is not None


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


def resolve_path(p: str | os.PathLike) -> Path:
    q = Path(p)
    return q if q.is_absolute() else PROJECT_ROOT / q


# --------------------------------------------------------------------------- #
# Prompt + row construction (pure — no engine needed, so it is unit-testable)
# --------------------------------------------------------------------------- #

def render_prompts(items: Sequence[EvalItem], system: SystemSpec, tokenizer: Any) -> list[str]:
    return [
        prompts.render_chat(
            prompts.build_prompt(
                code=it.code,
                entry_point=it.entry_point,
                args_repr=it.args_repr,
                language=it.language,
                condition=it.condition,
                oracle=system.prompt_oracle,
                one_shot=system.one_shot,
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
    for it, out, ntok in zip(items, outputs, n_tokens):
        g = scoring.grade(out, it.output_repr, it.language, float_tol)
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
        outs = self.llm.generate(
            list(texts), params, lora_request=(reqs[0] if uniform else reqs), use_tqdm=True
        )
        return (
            [o.outputs[0].text for o in outs],
            [len(o.outputs[0].token_ids) for o in outs],
        )


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

        df = pd.read_parquet(cell / "trials.parquet")
        return CellResult(cell, len(df), float(df["correct"].mean()),
                          float(df.get("format_fail", 0).mean()) if "format_fail" in df else 0.0,
                          skipped=True)

    items = list(items)[: limit or None]
    texts = render_prompts(items, system, engine.tokenizer)

    if system.is_routed:
        route = _load_route_map(system.route_map)
        missing = [it.item_id for it in items if it.item_id not in route]
        if missing:
            raise KeyError(f"route map is missing {len(missing)} item(s), e.g. {missing[:3]}")
        adapters = [route[it.item_id] for it in items]
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


def run_grid(args: argparse.Namespace) -> dict[str, Any]:
    from obtune.train_sft import resolve_model_cfg

    cfg = load_config(args.config)
    phase = cfg.get("phase", "main")
    languages = cfg.get("languages") or [cfg["language"]]
    models = cfg.get("models") or [cfg["model"]]
    eval_conditions = list(cfg["eval_conditions"])
    systems = [SystemSpec.from_config(s) for s in cfg["systems"]]
    if args.systems:
        keep = set(args.systems.split(","))
        systems = [s for s in systems if s.name in keep]
    if args.eval_conditions:
        eval_conditions = [c for c in eval_conditions if c in set(args.eval_conditions.split(","))]
    if args.route_map:
        for s in systems:
            if s.arch == "router":
                s.route_map = args.route_map

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
                )
                data.validate_eval_items(items)
                for system in systems:
                    cell = cell_dir(out_root, phase, model_key, language, system.name, cond)
                    meta_base = {
                        "run_id": f"{phase}__{model_key}__{language}__{system.name}__{cond}",
                        "run_ts": run_ts,
                        "seed": int((cfg.get("engine") or {}).get("seed", GLOBAL_SEED)),
                        "phase": phase,
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
                    res = run_cell(
                        engine, items, system, cell, cfg, meta_base,
                        resume=resume, limit=args.limit,
                    )
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
    mcfg = resolve_model_cfg(cfg)
    tcfg = _effective_train_knobs(cfg, mcfg)
    root = resolve_path(args.adapter_root) if args.adapter_root else adapter_dir(cfg)
    cks = list_checkpoints(root)
    if not cks:
        raise SystemExit(f"no checkpoints under {root}")

    # The held-in val slice: SAME conditions the adapter was trained on, split=='val'.
    # H1 must never influence checkpoint selection (CLAUDE.md §3.2 rule 2), and neither
    # may the test set — this is the only model-selection signal in the project.
    val_rows = data.load_pairs(cfg["train_conditions"], cfg["language"], splits=["val"])
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


if __name__ == "__main__":
    sys.exit(main())
