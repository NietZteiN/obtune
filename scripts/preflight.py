#!/usr/bin/env python
"""Validate everything the pipeline is about to run, before it runs.

    python scripts/preflight.py            # check; exit 1 on any ERROR
    python scripts/preflight.py --queued   # only the jobs currently queued

Written after three defects that a config-level check would have caught, all of which
cost GPU-hours or data:

  * a 7B eval config inherited the 1.5B `sft` adapter through a `systems:` deep-merge,
    so a 1.5B LoRA would have loaded onto a 7B base under a real arm's label;
  * every RQ2 eval job ran the config's full model x language cross-product because no
    `--model`/`--language` filter was passed, and died loading another model's adapter;
  * two evaluations wrote to the same results directory (date + language, no model), and
    the second destroyed the first's 21,000-row trials.jsonl.

The common shape: a path or a scope that is *derived* rather than *asserted*. Everything
below asserts.
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from obtune import paths  # noqa: E402
from obtune.config import CONFIG_DIR, PROJECT_ROOT, RUNS_DIR, load_config  # noqa: E402

ERRORS: list[str] = []
WARNS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNS.append(msg)


#: Model keys as they appear inside adapter paths, so a path can be checked against the
#: config's declared model. `qwen25c-1.5b` must not appear under a `qwen25c-7b` run.
def _model_in_path(path: str) -> str | None:
    m = re.search(r"(qwen25c-1\.5b|qwen25c-7b|llama31-8b)", path)
    return m.group(1) if m else None


def check_eval_config(rel: Path) -> None:
    try:
        cfg = load_config(str(rel))
    except Exception as exc:  # noqa: BLE001
        err(f"{rel}: will not load: {exc}")
        return
    model = cfg.get("model")
    systems = cfg.get("systems")
    # TWO harnesses, TWO incompatible `systems` shapes, and nothing checked which was which:
    #   * configs/eval/*        -> obtune.eval_vllm, which iterates rows and calls dict(row),
    #                              so `systems` must be a LIST of dicts.
    #   * configs/{cft,srh,unlearn}/eval/* -> obtune.cft.evaluate, which wants a MAPPING of
    #                              name -> adapter path.
    # A generated config used the wrong one and two jobs died at expand_systems with
    # "dictionary update sequence element #0 has length 1". The shape is a property of the
    # directory, so it is checkable up front.
    is_vllm_config = str(rel).startswith("eval/")
    if is_vllm_config and isinstance(systems, dict):
        err(f"{rel}: `systems` is a mapping, but configs/eval/ is consumed by eval_vllm, "
            f"which requires a LIST of system rows. Mapping style belongs to the "
            f"cft/srh harness.")
        return
    if not is_vllm_config and isinstance(systems, list):
        err(f"{rel}: `systems` is a list, but this config is consumed by cft.evaluate, "
            f"which requires a mapping of name -> adapter path.")
        return

    if not isinstance(systems, dict):
        _check_grid_eval_config(rel, cfg)
        return  # the rest of this function is for dict-style (named-adapter) configs
    lang = cfg.get("language")

    for name, adapter in systems.items():
        if adapter in (None, "none", "base"):
            continue
        got = _model_in_path(str(adapter))
        if got and model and got != model:
            err(f"{rel}: system {name!r} points at {got} but the config's model is "
                f"{model} — a {got} LoRA loaded onto a {model} base "
                f"(usually a `systems:` deep-merge leaking the parent's paths)")
        if lang and f"/{lang}/" not in str(adapter):
            warn(f"{rel}: system {name!r} path does not contain /{lang}/ — {adapter}")
        p = PROJECT_ROOT / adapter
        if not p.exists():
            warn(f"{rel}: system {name!r} adapter not present yet: {adapter}")

    # duplicate adapters => the same cell evaluated twice under two names
    seen: dict[str, list[str]] = defaultdict(list)
    for name, adapter in systems.items():
        if adapter:
            seen[str(adapter)].append(name)
    for adapter, names in seen.items():
        if len(names) > 1:
            err(f"{rel}: systems {names} share one adapter — duplicate work under two labels")

    if "base" not in systems:
        warn(f"{rel}: no `base` system; assert_adapters_effective cannot run")


def _check_grid_eval_config(rel: Path, cfg: dict) -> None:
    """Grid-style configs (`systems:` as a list) declare condition SETS, not adapter paths.

    Their failure mode is different and was not covered: a `per_type` row expands over
    `train_conditions`, so naming a condition whose adapter does not exist for one of the
    declared models kills the run partway through an otherwise complete matrix — and
    naming H1 anywhere spends one of its two permitted evaluation accesses (CLAUDE.md
    §3.2) as a side effect of an unrelated experiment.
    """
    from obtune.paths import TRAINABLE_CONDITIONS

    train_conds = list(cfg.get("train_conditions") or [])
    eval_conds = list(cfg.get("eval_conditions") or [])

    for c in train_conds:
        if c not in TRAINABLE_CONDITIONS:
            err(f"{rel}: train_condition {c!r} is not trainable "
                f"(allowed: {list(TRAINABLE_CONDITIONS)})")
    if "H1" in train_conds:
        err(f"{rel}: H1 appears in train_conditions — it is never trainable (CLAUDE.md §3.2)")

    # H1 as an eval column is legitimate, but ONLY for a config that declares which of the
    # two permitted accesses it is spending.
    if "H1" in eval_conds and not cfg.get("h1_access_purpose"):
        err(f"{rel}: H1 is in eval_conditions but `h1_access_purpose` is unset. H1 gets "
            f"exactly two evaluation passes (pilot, final); an undeclared read spends one "
            f"silently and invalidates the Invariance Index.")

    # An explicit `adapter:` suppresses expand_systems' per-language derivation, so a path
    # naming one language in a config that declares several silently evaluates the wrong
    # adapter under the right label. grid_rq1.yaml hard-coded the python merge paths while
    # declaring [python, javascript]; only `resume` (grid_v1 got there first) kept it latent.
    langs = [str(x) for x in (cfg.get("languages") or ([cfg["language"]] if cfg.get("language") else []))]
    if len(langs) > 1:
        for sysrow in (cfg.get("systems") or []):
            ad = str((sysrow or {}).get("adapter") or "")
            named = [l for l in ("python", "javascript") if f"/{l}/" in ad]
            if named and set(named) != set(langs):
                err(f"{rel}: system {sysrow.get('name')!r} hard-codes a {named} adapter while "
                    f"the config declares languages {langs}. Drop the explicit `adapter:` and "
                    f"let expand_systems derive it per language.")

    # per_type expands over train_conditions: every (model, language, condition) needs an
    # adapter, or the grid dies mid-run.
    expands = any(isinstance(sysrow, dict) and sysrow.get("expand_over") == "train_conditions"
                  for sysrow in (cfg.get("systems") or []))
    if not expands:
        return
    missing = []
    for model in (cfg.get("models") or []):
        for lang in (cfg.get("languages") or []):
            for c in train_conds:
                d = RUNS_DIR / "adapters" / str(model) / str(lang) / f"{c}_r32_s17" / "final"
                if not d.exists():
                    missing.append(f"{model}/{lang}/{c}")
    if missing:
        warn(f"{rel}: per_type expands over train_conditions but {len(missing)} adapter(s) "
             f"are absent: {missing[:6]}{' …' if len(missing) > 6 else ''}")


def check_pipeline_stage_configs() -> None:
    """Every config the pipeline's LATER stages will enqueue must already exist.

    Preflight otherwise validates only what is queued right now, which is exactly the wrong
    scope for a script whose whole purpose is to run stages that have not started. A
    stage-4 config that does not exist is discoverable today and is a dead pipeline in six
    hours' time.
    """
    pipeline = ROOT / "scripts" / "pipeline.sh"
    if not pipeline.exists():
        return
    text = pipeline.read_text()
    referenced = set(re.findall(r'"--config",\s*"([^"]+)"', text))
    referenced |= set(re.findall(r'--config (\S+\.yaml)', text))
    referenced |= set(re.findall(r'configs/(\S+\.yaml)', text))
    for c in sorted(referenced):
        c = c.removeprefix("configs/")
        # A reference built from a shell variable (`overtrain_..._${c}.yaml`) cannot be
        # resolved statically. Skipping it is right — asserting on the literal string would
        # be a guaranteed false positive — but it does mean loop-built paths are unchecked
        # here, so a stage that loops over configs must verify them itself (t2_overtrain
        # tests `[ -f "$f" ]` before adding each one).
        if "$" in c:
            continue
        if not (CONFIG_DIR / c).exists():
            err(f"pipeline.sh references config {c!r}, which does not exist — the stage "
                f"that enqueues it will fail after everything before it has already run")


def check_output_collisions(eval_cfgs: list[Path]) -> None:
    """Two eval configs must not resolve to the same results directory."""
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out: dict[str, list[str]] = defaultdict(list)
    for rel in eval_cfgs:
        try:
            cfg = load_config(str(rel))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(cfg.get("systems"), dict):
            continue
        tag = cfg.get("run_tag") or Path(str(cfg.get("_config_path", rel))).stem
        key = f"{stamp}_cft-bidirectional/{cfg.get('model')}/{cfg.get('language')}/{tag}"
        out[key].append(str(rel))
    for key, cfgs in out.items():
        if len(cfgs) > 1:
            err(f"output collision: {cfgs} all write to results/{key} — "
                "the last to finish destroys the others")


def check_cell_path_grid_collisions(eval_cfgs: list[Path]) -> None:
    """No two eval configs may write the same cell path on DIFFERENT grids.

    `eval_vllm.cell_dir` is `{phase}/{model}/{language}/{system}__{cond}` — it keys on
    `phase` but not on `eval_source`. Two configs that share all of those while declaring
    different `eval_source` therefore target the same directories, and under the default
    `resume: true` the second silently skips the first's cells: the job reports success,
    writes nothing, and leaves a table mixing Grid A (n~1670) and Grid B (n~176) cells in
    one row. That is exactly what cost 33 cells on 2026-08-13/14 (MASTER_REPORT §12.1),
    and the 2026-08-13 phase rename only moved the collision down one level rather than
    removing it.

    Catching it here makes the whole class a CPU-time config error instead of a GPU-hours
    silent no-op. `eval_vllm._assert_resume_same_grid` is the runtime backstop for cells
    that already exist; this is the static check for configs that have not run yet.
    """
    from obtune.data import DEFAULT_EVAL_SOURCE

    seen: dict[tuple[str, ...], list[tuple[str, str]]] = defaultdict(list)
    for rel in eval_cfgs:
        try:
            cfg = load_config(str(rel))
        except Exception:  # noqa: BLE001
            continue
        systems = cfg.get("systems")
        conds = cfg.get("eval_conditions")
        if not systems or not conds:
            continue
        src = str(cfg.get("eval_source", DEFAULT_EVAL_SOURCE))
        names = [s.get("name") for s in systems if isinstance(s, dict)] \
            if isinstance(systems, list) else list(systems)
        for name in filter(None, names):
            for cond in conds:
                key = (str(cfg.get("phase")), str(cfg.get("model")),
                       str(cfg.get("language")), str(name), str(cond))
                seen[key].append((src, str(rel)))
    # WARN, not ERROR. Several of these are pre-existing and load-bearing: `main` has held
    # both grids since the project began (RQ1 is `heldout`, the merge/mixture arms are
    # `testset`), and erroring would block every pipeline run on debt that predates the
    # check. The authoritative protection is `eval_vllm._assert_resume_same_grid`, which
    # HARD-FAILS at runtime on the one thing that actually corrupts a result — resuming
    # across grids. This static pass exists to keep the debt visible and to catch a NEW
    # collision while it is still a config edit.
    # Aggregated by the SET of configs involved, not per cell. Per-cell warnings produced
    # ~59 near-identical lines, and `gate()` re-runs preflight before every stage, so the
    # pipeline log filled with the same paragraph dozens of times per run. One line per
    # distinct collision group, with a count of the cells it covers.
    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for key, entries in seen.items():
        by_source: dict[str, set[str]] = defaultdict(set)
        for s, c in entries:
            by_source[s].add(c)
        if len(by_source) > 1:
            sig = tuple(sorted(f"{s}={','.join(sorted(cs))}" for s, cs in by_source.items()))
            groups[sig].append("/".join(key))
    for sig, cells in sorted(groups.items()):
        where = "; ".join(f"eval_source={p.split('=', 1)[0]}: {p.split('=', 1)[1]}" for p in sig)
        warn(f"cell-path grid collision ({len(cells)} cells, e.g. {cells[0]}) — {where}. "
             "Same cell path, different eval_source: whichever runs second RESUMES the first "
             "and writes nothing. This is why §8.2's Grid B `base` cells are missing. Fix by "
             "giving one run its own `phase:` (and adding it to schema.TrialRow.phase). "
             "See MASTER_REPORT §12.1.")


def check_train_config(rel: Path) -> None:
    try:
        cfg = load_config(str(rel))
    except Exception as exc:  # noqa: BLE001
        err(f"{rel}: will not load: {exc}")
        return
    lang = cfg.get("language")
    conds = cfg.get("train_conditions") or []
    # Mirror `data.load_pairs`: a config that opts in with `allow_composites: true` may also
    # name `C_` codes. They sit outside TRAINABLE_CONDITIONS on purpose (so they cannot shift
    # the RQ1 grid or the router's class count), but they ARE trainable for a config that
    # asks. Without this, any composite-trained arm makes preflight permanently red — and a
    # gate that is always failing is a gate nobody reads.
    allowed = set(paths.TRAINABLE_CONDITIONS)
    if cfg.get("allow_composites"):
        from obtune.data import _trainable_composites  # local, as the other checks here do
        allowed |= set(_trainable_composites())
    for c in conds:
        if c not in allowed:
            err(f"{rel}: condition {c!r} is not trainable "
                f"(allowed: {sorted(allowed)})")
            continue
        pair = paths.TRAIN_ROOT / "pairs" / c / f"{lang}.jsonl"
        if not pair.exists() or pair.stat().st_size == 0:
            err(f"{rel}: no training pairs for {c}/{lang} — {pair} "
                "(run scripts/06_emit_pairs.py)")


def _queued_config_names() -> set[str]:
    """Config filenames referenced by jobs currently in the queue."""
    out: set[str] = set()
    for p in (RUNS_DIR / "manifest" / "queued").glob("*.json"):
        try:
            argv = [str(a) for a in json.loads(p.read_text()).get("argv", [])]
        except Exception:  # noqa: BLE001
            continue
        if "--config" in argv:
            out.add(Path(argv[argv.index("--config") + 1]).name)
    return out


def check_adapter_dir_collisions(train_cfgs: list[Path]) -> None:
    """Two configs training into one directory.

    Severity depends on whether either is actually QUEUED. A dormant collision (e.g. the
    pilot and grid L0 configs, which differ only in `phase`/`run_tag` and share a recipe)
    is a hygiene issue worth reporting but must not block a pipeline whose queue does not
    contain them — otherwise the gate cries wolf and gets ignored.
    """
    from obtune.train_sft import adapter_dir

    queued = _queued_config_names()
    seen: dict[str, list[str]] = defaultdict(list)
    for rel in train_cfgs:
        try:
            cfg = load_config(str(rel))
            seen[str(adapter_dir(cfg))].append(str(rel))
        except Exception:  # noqa: BLE001
            continue
    for d, cfgs in seen.items():
        if len(cfgs) <= 1:
            continue
        live = [c for c in cfgs if Path(c).name in queued]
        msg = f"adapter collision: {cfgs} all train into {d}"
        if live:
            err(f"{msg} — and {live} is QUEUED, so it will overwrite the other's adapter")
        else:
            warn(f"{msg} (none queued: latent, not live)")


def check_queued_jobs() -> None:
    q = RUNS_DIR / "manifest" / "queued"
    done_ids = set()
    for state in ("done", "running"):
        base = RUNS_DIR / "manifest" / state
        for p in base.rglob("*.json"):
            try:
                done_ids.add(json.loads(p.read_text())["job_id"])
            except Exception:  # noqa: BLE001
                pass
    queued: dict[str, dict] = {}
    for p in sorted(q.glob("*.json")):
        try:
            j = json.loads(p.read_text())
        except Exception as exc:  # noqa: BLE001
            err(f"{p.name}: unreadable job file: {exc}")
            continue
        queued[j["job_id"]] = j

    for jid, j in queued.items():
        argv = [str(a) for a in j.get("argv", [])]
        if not j.get("raw") and argv[:1] == ["-m"]:
            mod = argv[1]
            try:
                importlib.import_module(mod)
            except Exception as exc:  # noqa: BLE001
                err(f"{jid}: entry module {mod!r} does not import: {exc}")
        if "--config" in argv:
            c = argv[argv.index("--config") + 1]
            if not (CONFIG_DIR / c).exists() and not Path(c).exists():
                err(f"{jid}: --config {c} does not exist")
        # An eval_vllm job against a MULTI-model / multi-language config must pin both, or
        # it silently runs the entire cross-product. That is how a 1.5b job came to load a
        # qwen25c-7b adapter. The emitter was fixed, but job files are written to disk and
        # outlive the emitter: a stale one requeued after a worker died reintroduced the
        # bug hours later. Validate the argv on disk, not the code that produced it.
        if not j.get("raw") and argv[:2] == ["-m", "obtune.eval_vllm"] and "--config" in argv:
            cname = argv[argv.index("--config") + 1]
            try:
                ecfg = load_config(cname)
            except Exception:  # noqa: BLE001
                ecfg = {}
            multi = len(ecfg.get("models") or []) > 1 or len(ecfg.get("languages") or []) > 1
            missing = [f for f in ("--model", "--language") if f not in argv]
            if multi and missing:
                err(f"{jid}: config {cname} declares "
                    f"{len(ecfg.get('models') or [])} model(s) x "
                    f"{len(ecfg.get('languages') or [])} language(s) but the job omits "
                    f"{missing} — it will run the whole cross-product and load another "
                    f"model's adapters")

        dep = (j.get("meta") or {}).get("depends_on")
        deps = [dep] if isinstance(dep, str) else list(dep or [])
        for d in deps:
            if d not in queued and d not in done_ids:
                err(f"{jid}: depends_on {d!r} which is neither queued nor finished — "
                    "it will never become ready")


def check_cross_model_adapters() -> None:
    """An adapter path whose model segment contradicts the config's `model:`.

    THE FAILURE THIS CATCHES, which actually happened. `configs/unlearn/negation_qwen25c-7b_*`
    extends the 1.5B `cft/eval/bidir_v1.yaml` and inherited its `cft` path unchanged — so a
    1.5B LoRA was loaded onto a 7B base and scored under a real arm's label. It did not crash;
    it produced 86.5% base-identical outputs in the 2026-08-10 run and looked like a weak arm.
    `assert_adapter_effective` did not fire because 13.5% of outputs did differ.

    This scans EVERY config, not just `/eval/` and `/train/`. That breadth is the point: the
    three affected files live under `configs/unlearn/`, which no other check walks, which is
    exactly why the defect survived a preflight that reported 0 errors.
    """
    import re

    for path in sorted(CONFIG_DIR.rglob("*.yaml")):
        if path.name.startswith("_"):
            continue
        rel = path.relative_to(CONFIG_DIR)
        try:
            cfg = load_config(str(rel))
        except Exception:
            continue
        model = cfg.get("model")
        if not isinstance(model, str):
            continue
        systems = cfg.get("systems")
        if not isinstance(systems, dict):
            continue
        for name, val in systems.items():
            if not isinstance(val, str) or "$" in val:
                continue
            hit = re.search(r"qwen25c-[\w.]+", val)
            if hit and hit.group(0) != model:
                err(f"{rel}: model={model} but system {name!r} points at a "
                    f"{hit.group(0)} adapter ({val}) — that loads one model's LoRA onto "
                    f"another's base and reports it under a real arm's label")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queued", action="store_true", help="only validate queued jobs")
    args = ap.parse_args()

    if not args.queued:
        eval_cfgs = sorted(
            p.relative_to(CONFIG_DIR)
            for p in CONFIG_DIR.rglob("*.yaml")
            if "/eval/" in str(p) and not p.name.startswith("_")
        )
        train_cfgs = sorted(
            p.relative_to(CONFIG_DIR)
            for p in CONFIG_DIR.rglob("*.yaml")
            if "/train/" in str(p) and not p.name.startswith("_")
        )
        for rel in eval_cfgs:
            check_eval_config(rel)
        check_output_collisions(eval_cfgs)
        check_cell_path_grid_collisions(eval_cfgs)
        for rel in train_cfgs:
            check_train_config(rel)
        check_adapter_dir_collisions(train_cfgs)
        check_pipeline_stage_configs()
        check_cross_model_adapters()
        print(f"checked {len(eval_cfgs)} eval + {len(train_cfgs)} train configs")

    check_queued_jobs()
    n_q = len(list((RUNS_DIR / "manifest" / "queued").glob("*.json")))
    print(f"checked {n_q} queued job(s)")

    for w in WARNS:
        print(f"  WARN  {w}")
    for e in ERRORS:
        print(f"  ERROR {e}")
    print(f"\n{len(ERRORS)} error(s), {len(WARNS)} warning(s)")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
