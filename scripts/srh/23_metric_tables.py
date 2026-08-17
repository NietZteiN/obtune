#!/usr/bin/env python
"""Workshop-paper derived tables E7 (prompting) and E8 (metric artifact).

    python scripts/srh/23_metric_tables.py --table all \
        --run results/2026-08-09_cft-bidirectional/qwen25c-7b/python/bidir_qwen7b

Both tables are RE-SCORINGS of trials already on disk. Neither needs a GPU: every field
they read (`reverse_success_strict`, `reverse_success_paper`, `identifier_recall_original`,
`identity_output`) is written per trial by `obtune.cft.evaluate`. Writes
`e7_prompting.{json,md}` / `e8_metric_artifact.{json,md}` into the run directory.

E7 — WHAT PROMPTING BUYS WITHOUT TRAINING
The source paper reports that prompting cannot rescue the reverse direction (ΔR ≈
0.01–0.05, §4.3.3) and reports SFT at 0 %. Both claims are strategy-dependent, and the
comparison a reviewer will actually make is between a *fine-tuned* model and an *untuned*
one that was merely prompted better. This table puts all of them in one grid so the
paper's "sft below base" claim can be stated at its weakest defensible form: the
fine-tuned arm under its BEST strategy against the untuned base under its WORST.

E8 — WHAT THE PAPER'S CRITERION ACTUALLY CERTIFIES
§4 of the workshop paper claims the source paper's renaming "success" is an artifact of a
criterion that rewards plausible names over recovered ones. The honest form of that claim
is NOT "passes have near-zero identifier recall" — measured, they run ~0.43 — but that the
criterion is *uninformative*: id-recall among passes is indistinguishable from id-recall
among all outputs, so passing it predicts nothing about recovery.

That comparison is unreadable without a floor, because identifier recall is never zero:
builtins, the entry point and library calls survive any renaming. So this table computes
the ECHO FLOOR directly — `identifier_recall(obfuscated_source, original_source)` over the
same program set — i.e. what a model scores by copying its input straight back out. Two
independent estimates are reported:

  floor_corpus    computed from the corpus variants via load_eval_programs, so it covers
                  every evaluated program regardless of what any model emitted;
  floor_observed  the mean id-recall of trials the harness flagged `identity_output` —
                  the same quantity measured on real generations, as a cross-check.

If they agree, the floor is trustworthy and the "criterion is uninformative" claim can be
read straight off the table.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from obtune.cft import metrics  # noqa: E402
from obtune.cft.evaluate import load_eval_programs  # noqa: E402
from obtune.config import GLOBAL_SEED, load_config  # noqa: E402
from obtune.paths import iter_jsonl  # noqa: E402


def _load_report_helpers():
    """Import `cluster_bootstrap`/`rate` from scripts/cft/12_report.py.

    Imported rather than reimplemented on purpose. These tables sit beside numbers that
    script already published, and a second copy of the estimator is a second chance for
    the two to drift — a different resample count or a different seed would show up as a
    changed CI on an unchanged result. The module name starts with a digit, so it cannot
    be imported by name and needs the loader dance.
    """
    path = ROOT / "scripts" / "cft" / "12_report.py"
    spec = importlib.util.spec_from_file_location("_cft_report", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.cluster_bootstrap, mod.rate


cluster_bootstrap, rate = _load_report_helpers()

STRATEGY_ORDER = ("simple", "few_shot", "cot", "augmented")


def _discover_config(run: Path) -> str | None:
    """Recover the eval config for runs written before it was recorded in summary.json.

    `evaluate.py` derives its output directory name from the config's filename stem
    (`run_tag`), so the mapping is invertible — but only if the stem is unique across
    `configs/`. Ambiguity is returned as None rather than guessed: picking the wrong
    config would compute the E8 floor over a different program set and quietly produce a
    table whose reference column does not belong to its rates.
    """
    hits = sorted((ROOT / "configs").rglob(f"{run.name}.yaml"))
    if len(hits) != 1:
        return None
    return str(hits[0].relative_to(ROOT / "configs"))


def _pct(x: float) -> str:
    return "—" if x != x else f"{100 * x:.1f}"


def _mean(vals: Sequence[float]) -> float:
    return statistics.mean(vals) if vals else float("nan")


def _f3(x: float, signed: bool = False) -> str:
    """Format a rate to 3 dp, rendering NaN as an em dash.

    NaN is a real outcome here, not an error: a cell with zero paper-criterion passes has
    no mean id-recall to report, and printing `nan` in a paper table invites the reader to
    treat it as a measured zero.
    """
    if x != x:
        return "—"
    return f"{x:+.3f}" if signed else f"{x:.3f}"


# ---------------------------------------------------------------- E7


def e7_table(trials: list[dict[str, Any]], n_boot: int) -> dict[str, Any]:
    rev = [t for t in trials if t["direction"] == "reverse"]
    systems = sorted({t["system"] for t in rev})
    strategies = [s for s in STRATEGY_ORDER if s in {t["strategy"] for t in rev}]

    cells: dict[str, dict[str, Any]] = {}
    for sysname in systems:
        for strat in strategies:
            sub = [t for t in rev if t["system"] == sysname and t["strategy"] == strat]
            if not sub:
                continue
            strict = rate("reverse_success_strict")(sub)
            lo, hi = cluster_bootstrap(sub, rate("reverse_success_strict"),
                                       n_boot=n_boot, seed=GLOBAL_SEED)
            cells[f"{sysname}|{strat}"] = {
                "system": sysname, "strategy": strat, "n": len(sub),
                "strict": strict, "strict_ci": [lo, hi],
                "paper": rate("reverse_success_paper")(sub),
                "exec": rate("reverse_success_exec")(sub),
                "identity": rate("identity_output")(sub),
            }

    # The headline contrast: best fine-tuned cell vs worst untuned-base cell.
    def best(sysname: str) -> dict[str, Any] | None:
        got = [c for c in cells.values() if c["system"] == sysname]
        return max(got, key=lambda c: c["strict"]) if got else None

    def worst(sysname: str) -> dict[str, Any] | None:
        got = [c for c in cells.values() if c["system"] == sysname]
        return min(got, key=lambda c: c["strict"]) if got else None

    contrast = {}
    base_worst = worst("base")
    if base_worst:
        for sysname in systems:
            if sysname == "base":
                continue
            b = best(sysname)
            if b:
                contrast[sysname] = {
                    "best_strategy": b["strategy"], "best_strict": b["strict"],
                    "base_worst_strategy": base_worst["strategy"],
                    "base_worst_strict": base_worst["strict"],
                    "below_base_worst": b["strict"] < base_worst["strict"],
                }
    return {"cells": cells, "systems": systems, "strategies": strategies,
            "headline_contrast": contrast}


def e7_markdown(res: dict[str, Any]) -> list[str]:
    L = ["## E7 — what prompting buys, with and without fine-tuning\n",
         "Reverse direction, **strict** (execution-correct AND genuinely de-obfuscated), "
         "with cluster-bootstrap 95 % CIs by `program_id`.\n"]
    strategies = res["strategies"]
    L.append("| system | " + " | ".join(strategies) + " |")
    L.append("|---|" + "---|" * len(strategies))
    for sysname in res["systems"]:
        cs = []
        for strat in strategies:
            c = res["cells"].get(f"{sysname}|{strat}")
            if not c:
                cs.append("—"); continue
            lo, hi = c["strict_ci"]
            cs.append(f"{_pct(c['strict'])} [{_pct(lo)}, {_pct(hi)}]")
        L.append(f"| `{sysname}` | " + " | ".join(cs) + " |")
    L.append("")
    for sysname, c in res["headline_contrast"].items():
        verdict = ("BELOW" if c["below_base_worst"] else "above")
        L.append(
            f"- `{sysname}` at its best strategy (`{c['best_strategy']}`, "
            f"{_pct(c['best_strict'])} %) is **{verdict}** the untuned base at its worst "
            f"(`{c['base_worst_strategy']}`, {_pct(c['base_worst_strict'])} %)."
        )
    L.append("")
    return L


# ---------------------------------------------------------------- E8


def echo_floor_from_corpus(cfg: dict[str, Any]) -> dict[str, float]:
    """`identifier_recall(obfuscated, original)` per condition — the copy-the-input score.

    Uses the eval config's own program-set parameters so the floor is computed on exactly
    the programs the trials were scored on. Any drift here (a different `limit`, a
    different seed) would make the floor incomparable to the rates it is meant to anchor.
    """
    language = cfg.get("language", "python")
    conditions = [c for c in cfg["conditions"] if c != "L0"]
    progs = load_eval_programs(
        language=language, conditions=cfg["conditions"], source=cfg.get("eval_source", "heldout"),
        limit=cfg.get("limit"), seed=cfg.get("seed", GLOBAL_SEED),
        program_set=cfg.get("eval_program_set", "common_subset"),
    )
    out: dict[str, float] = {}
    for cond in conditions:
        vals = [
            metrics.identifier_recall(p.variants[cond]["code"], p.original_code, language)
            for p in progs if cond in p.variants
        ]
        out[cond] = _mean(vals)
    out["_n_programs"] = float(len(progs))
    return out


def e8_table(trials: list[dict[str, Any]], floor: dict[str, float],
             strategy: str, n_boot: int) -> dict[str, Any]:
    rev = [t for t in trials if t["direction"] == "reverse" and t["strategy"] == strategy]
    systems = sorted({t["system"] for t in rev})
    conditions = sorted({t["condition"] for t in rev})

    rows = {}
    for sysname in systems:
        for cond in conditions:
            sub = [t for t in rev if t["system"] == sysname and t["condition"] == cond]
            if not sub:
                continue
            passes = [t for t in sub if t["reverse_success_paper"] == 1]
            ident = [t for t in sub if t.get("identity_output")]
            ir_pass = _mean([t["identifier_recall_original"] for t in passes])
            ir_all = _mean([t["identifier_recall_original"] for t in sub])
            rows[f"{sysname}|{cond}"] = {
                "system": sysname, "condition": cond, "n": len(sub),
                "paper": rate("reverse_success_paper")(sub),
                "strict": rate("reverse_success_strict")(sub),
                "n_paper_pass": len(passes),
                "idrec_among_passes": ir_pass,
                "idrec_among_all": ir_all,
                # THE claim: if this is ~0, passing the criterion tells you nothing about
                # whether identifiers were actually recovered.
                "idrec_lift_of_passing": ir_pass - ir_all,
                "floor_corpus": floor.get(cond, float("nan")),
                "floor_observed": _mean([t["identifier_recall_original"] for t in ident]),
                "n_identity": len(ident),
                # How much the paper's criterion over-counts relative to strict.
                "criterion_inflation": rate("reverse_success_paper")(sub)
                                       - rate("reverse_success_strict")(sub),
            }
    return {"strategy": strategy, "rows": rows, "systems": systems,
            "conditions": conditions, "floor_corpus": floor}


def e8_markdown(res: dict[str, Any]) -> list[str]:
    L = ["## E8 — what the paper's reverse criterion certifies\n",
         f"Reverse direction, `{res['strategy']}` strategy. `floor` is the identifier "
         "recall of the **obfuscated input itself** — what copying the input scores, and "
         "the only reference against which the other two columns mean anything.\n"]
    L.append("| system | cond | paper % | strict % | inflation | id-rec passes | id-rec all "
             "| **lift of passing** | floor (corpus) | floor (observed) | n pass |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for sysname in res["systems"]:
        for cond in res["conditions"]:
            r = res["rows"].get(f"{sysname}|{cond}")
            if not r:
                continue
            L.append(
                f"| `{sysname}` | `{cond}` "
                f"| {_pct(r['paper'])} "
                f"| {_pct(r['strict'])} "
                f"| {_pct(r['criterion_inflation'])} "
                f"| {_f3(r['idrec_among_passes'])} "
                f"| {_f3(r['idrec_among_all'])} "
                f"| **{_f3(r['idrec_lift_of_passing'], signed=True)}** "
                f"| {_f3(r['floor_corpus'])} "
                f"| {_f3(r['floor_observed'])} ({r['n_identity']}) "
                f"| {r['n_paper_pass']} |"
            )
    L.append("")
    L.append("Read the **lift of passing** column: it is the id-recall of outputs that "
             "satisfy the paper's criterion minus the id-recall of all outputs. A lift near "
             "zero means the criterion certifies nothing about identifier recovery.\n")
    return L


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="an obtune.cft.evaluate output directory")
    ap.add_argument("--table", default="all", choices=["e7", "e8", "all"])
    ap.add_argument("--config", default=None,
                    help="eval config used for the run (default: read from summary.json)")
    ap.add_argument("--e8-strategy", default="simple",
                    help="E8 is a per-condition table; it needs one fixed strategy")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    run = Path(args.run)
    trials = list(iter_jsonl(run / "trials.jsonl"))
    if not trials:
        raise SystemExit(f"no trials in {run}")
    summary = json.loads((run / "summary.json").read_text())

    cfg_rel = args.config or summary.get("meta", {}).get("config") or _discover_config(run)
    if not cfg_rel:
        raise SystemExit(
            "cannot locate the eval config for this run; pass --config explicitly. "
            "It is needed to recompute the E8 echo floor on the SAME program set.")
    cfg = load_config(cfg_rel)

    out: dict[str, Any] = {"run": str(run), "config": str(cfg_rel),
                           "model": summary.get("meta", {}).get("model"),
                           "n_trials": len(trials)}
    md: list[str] = [f"# Derived metric tables — `{run.name}`\n",
                     f"*Generated by `scripts/srh/23_metric_tables.py` from `{run}`. "
                     f"No GPU: these are re-scorings of trials already on disk.*\n"]

    if args.table in ("e7", "all"):
        res = e7_table(trials, args.n_boot)
        out["e7"] = res
        md += e7_markdown(res)
        (run / "e7_prompting.json").write_text(json.dumps(res, indent=2))

    if args.table in ("e8", "all"):
        floor = echo_floor_from_corpus(cfg)
        res = e8_table(trials, floor, args.e8_strategy, args.n_boot)
        out["e8"] = res
        md += e8_markdown(res)
        (run / "e8_metric_artifact.json").write_text(json.dumps(res, indent=2))

    (run / "metric_tables.md").write_text("\n".join(md))
    print("\n".join(md))
    print(f"\n[23_metric_tables] wrote {run}/metric_tables.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
