#!/usr/bin/env python
"""Render a bidirectional-eval run as a table beside the paper's numbers.

    python scripts/cft/12_report.py results/2026-08-08_cft-bidirectional/python

Reads `trials.jsonl` + `summary.json` from an `obtune.cft.evaluate` output directory and
writes `report.md` next to them. Cluster-bootstrap CIs are resampled by `program_id`
(CLAUDE.md §4): a program contributes one trial per condition x strategy, and those are
correlated, so bootstrapping trials would understate every interval.

The paper's numbers are quoted, never recomputed, and are tagged with the model they came
from — the paper's Qwen2.5-Coder-7B row is the only one directly comparable to ours, and
comparing a 1.5B run against GPT-4.1-Mini's 52 % would be meaningless.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from obtune.config import GLOBAL_SEED  # noqa: E402
from obtune.paths import iter_jsonl  # noqa: E402

#: Quoted from papers/nikiema2025contrastive.pdf. Values, not recomputations.
PAPER_NUMBERS = {
    "sft_reverse_success": ("0 %", "§4.3.3, Fig. 4 — universal across all models and transforms"),
    "cft_reverse_success_qwencoder": ("39.00 %", "Fig. 4, Qwen2.5-Coder-7B — our comparable model"),
    "cft_reverse_success_best": ("52.03 %", "Fig. 4, GPT-4.1-Mini — commercial, not comparable to ours"),
    "sft_similarity_to_obfuscated": ("0.61–0.79", "§4.3.3 — SFT echoes the obfuscated input back"),
    "prompting_delta": ("ΔR ≈ 0.01–0.05", "§4.3.3 — across simple / few-shot / CoT / augmented"),
    "forward_similarity_cft": ("0.42–0.51", "§5.0.3 — vs SFT's 0.42–0.50; CFT preserves forward"),
}


def cluster_bootstrap(
    rows: Sequence[dict[str, Any]],
    stat: Callable[[Sequence[dict[str, Any]]], float],
    n_boot: int = 2000,
    seed: int = GLOBAL_SEED,
) -> tuple[float, float]:
    """Percentile CI, resampling PROGRAMS with replacement (not trials)."""
    by_prog: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_prog[r["program_id"]].append(r)
    progs = sorted(by_prog)
    if len(progs) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    draws = []
    for _ in range(n_boot):
        picked = [by_prog[progs[rng.randrange(len(progs))]] for _ in progs]
        flat = [r for chunk in picked for r in chunk]
        try:
            draws.append(stat(flat))
        except ZeroDivisionError:
            continue
    draws.sort()
    if not draws:
        return (float("nan"), float("nan"))
    lo = draws[int(0.025 * len(draws))]
    hi = draws[min(len(draws) - 1, int(0.975 * len(draws)))]
    return (lo, hi)


def rate(field: str) -> Callable[[Sequence[dict[str, Any]]], float]:
    def _f(rows: Sequence[dict[str, Any]]) -> float:
        vals = [r[field] for r in rows if field in r]
        return sum(vals) / len(vals) if vals else float("nan")

    return _f


def _fmt_pct(x: float) -> str:
    return "—" if x != x else f"{100 * x:.1f} %"


def _fmt(x: float) -> str:
    return "—" if x != x else f"{x:.3f}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", help="an obtune.cft.evaluate output directory")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()

    run = Path(args.run_dir)
    trials = list(iter_jsonl(run / "trials.jsonl"))
    summary = json.loads((run / "summary.json").read_text())
    meta = summary["meta"]
    if not trials:
        raise SystemExit(f"no trials in {run}")

    systems = [s for s in ("base", "sft", "cft") if s in {t["system"] for t in trials}]
    conditions = sorted({t["condition"] for t in trials})
    strategies = sorted({t["strategy"] for t in trials if t["direction"] == "reverse"})

    L: list[str] = []
    L.append(f"# CFT bidirectional evaluation — {meta['language']}, {run.name}\n")
    L.append(f"*Generated from `{run}`. Model: `{meta.get('model', 'see run_manifest.json')}`.*\n")
    L.append(
        "Replication of `nikiema2025contrastive` (arXiv:2509.05553). Design and the full "
        "deviation list: [`../../docs/CFT_REPLICATION.md`](../../docs/CFT_REPLICATION.md).\n"
    )
    L.append(
        f"**{meta['n_programs']} test-split programs · {meta['n_trials']} generations · "
        f"conditions {', '.join(conditions)}.** The paper's third transformation (string "
        "encryption) maps onto our quarantined `H1` and is absent by design.\n"
    )
    L.append(
        "> `readability_*` is `metrics.readability_proxy`, **not** the Scalabrino et al. model "
        "the paper uses. Only within-run contrasts are interpretable; absolute values are not "
        "comparable to the paper's R.\n"
    )

    # ---- Reverse direction: the headline ------------------------------------
    L.append("\n## Reverse direction — the headline comparison\n")
    L.append(
        "`success_paper` is the paper's criterion (§4.3.2: similarity to the obfuscated input "
        "below the threshold AND readability restored). `success_exec` is obtune's: the "
        "recovered program actually reproduces the original's outputs. `strict` is both.\n"
    )
    L.append("| system | strategy | success_paper [95 % CI] | success_exec | strict | S(deobf,obf) | S(deobf,orig) | id-recall |")
    L.append("|---|---|---|---|---|---|---|---|")
    rev = [t for t in trials if t["direction"] == "reverse"]
    for s in systems:
        for strat in strategies:
            g = [t for t in rev if t["system"] == s and t["strategy"] == strat]
            if not g:
                continue
            p = rate("reverse_success_paper")(g)
            lo, hi = cluster_bootstrap(g, rate("reverse_success_paper"), args.n_boot)
            L.append(
                f"| `{s}` | {strat} | **{_fmt_pct(p)}** [{_fmt_pct(lo)}, {_fmt_pct(hi)}] "
                f"| {_fmt_pct(rate('reverse_success_exec')(g))} "
                f"| {_fmt_pct(rate('reverse_success_strict')(g))} "
                f"| {_fmt(rate('codebleu_other')(g))} "
                f"| {_fmt(rate('codebleu_target')(g))} "
                f"| {_fmt(rate('identifier_recall_original')(g))} |"
            )

    L.append("\n### Reverse success by condition (C3: is any gain renaming-only?)\n")
    L.append("| system | " + " | ".join(f"`{c}`" for c in conditions) + " |")
    L.append("|---" * (len(conditions) + 1) + "|")
    for s in systems:
        cells = []
        for c in conditions:
            g = [t for t in rev if t["system"] == s and t["condition"] == c]
            cells.append(_fmt_pct(rate("reverse_success_paper")(g)) if g else "—")
        L.append(f"| `{s}` | " + " | ".join(cells) + " |")

    # ---- Forward direction ---------------------------------------------------
    L.append("\n## Forward direction — did fine-tuning work at all?\n")
    L.append(
        "`exec_parity` is the check the paper could not run: does the obfuscated program the "
        "model produced still compute the original's outputs?\n"
    )
    L.append("| system | exec_parity [95 % CI] | S(gen,tool) | parse_ok | identity | empty |")
    L.append("|---|---|---|---|---|---|")
    fwd = [t for t in trials if t["direction"] == "forward"]
    for s in systems:
        g = [t for t in fwd if t["system"] == s]
        if not g:
            continue
        p = rate("forward_success_exec")(g)
        lo, hi = cluster_bootstrap(g, rate("forward_success_exec"), args.n_boot)
        L.append(
            f"| `{s}` | **{_fmt_pct(p)}** [{_fmt_pct(lo)}, {_fmt_pct(hi)}] "
            f"| {_fmt(rate('codebleu_target')(g))} "
            f"| {_fmt_pct(rate('parse_ok')(g))} "
            f"| {_fmt_pct(rate('identity_output')(g))} "
            f"| {_fmt_pct(rate('empty_output')(g))} |"
        )
    L.append(
        "\n`identity` is the failure the paper reports for StarCoder (§4.1.3, excluded from their "
        "analysis for reproducing its input exactly) and for every SFT model in reverse (§4.3.3: "
        "\"outputs nearly identical to the obfuscated input\"). A high rate here means the arm is "
        "echoing, not transforming.\n"
    )

    # ---- Arm contrast --------------------------------------------------------
    if "sft" in systems and "cft" in systems:
        L.append("\n## CFT − SFT (C2), pooled over strategies\n")
        L.append("| measure | SFT | CFT | difference [95 % CI] |")
        L.append("|---|---|---|---|")
        for label, subset, field in (
            ("reverse success (paper)", rev, "reverse_success_paper"),
            ("reverse success (exec)", rev, "reverse_success_exec"),
            ("reverse identifier recall", rev, "identifier_recall_original"),
            ("forward exec parity", fwd, "forward_success_exec"),
        ):
            a = [t for t in subset if t["system"] == "sft"]
            b = [t for t in subset if t["system"] == "cft"]
            if not a or not b:
                continue
            paired = a + b

            def diff(rows: Sequence[dict[str, Any]], _f=field) -> float:
                x = rate(_f)([r for r in rows if r["system"] == "cft"])
                y = rate(_f)([r for r in rows if r["system"] == "sft"])
                return x - y

            lo, hi = cluster_bootstrap(paired, diff, args.n_boot)
            L.append(
                f"| {label} | {_fmt_pct(rate(field)(a))} | {_fmt_pct(rate(field)(b))} "
                f"| **{_fmt_pct(diff(paired))}** [{_fmt_pct(lo)}, {_fmt_pct(hi)}] |"
            )

    # ---- Paper's numbers -----------------------------------------------------
    L.append("\n## The paper's reported numbers, for comparison\n")
    L.append("| quantity | paper | source |")
    L.append("|---|---|---|")
    for _, (value, where) in PAPER_NUMBERS.items():
        L.append(f"| {where.split('—')[-1].strip()} | **{value}** | {where.split('—')[0].strip()} |")

    L.append("\n## Provenance\n")
    L.append(f"- CodeBLEU: `{meta.get('codebleu_impl')}`")
    L.append(f"- prompt template: `{meta.get('cft_prompt_template_sha256', '?')[:16]}…` "
             f"(`{meta.get('cft_prompt_version')}`)")
    L.append(f"- reverse-success thresholds: `{json.dumps(meta.get('criteria', {}))}`")
    L.append(f"- adapter-effectiveness check: `{json.dumps(meta.get('adapter_effectiveness', {}))}`")
    L.append(f"- readability weights: `{json.dumps(meta.get('readability_weights', {}))}`")

    out = run / "report.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[cft.report] wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
