#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from paths import (  # noqa: E402
    model_dir_name,
    resolve_attn_root,
    resolve_alignment_outputs_root,
    resolve_artifact_path,
)


@dataclass
class TagStats:
    em: int = 0
    total: int = 0
    snippets: set[str] = field(default_factory=set)
    step: str = "-"
    level: str = "-"
    prior: str = "-"
    beta: str = "-"

    @property
    def acc(self) -> float:
        return (self.em / self.total) if self.total else 0.0

    @property
    def mismatch(self) -> int:
        return self.total - self.em


def parse_step_level_beta(tag_name: str, variant_name: str) -> Tuple[str, str, str]:
    tag_lc = tag_name.lower()
    variant_lc = variant_name.lower()
    step = "-"
    level = "-"
    beta = "-"

    step_m = re.search(r"(step\d+)", tag_lc)
    if step_m:
        step = step_m.group(1)

    level_m = re.search(r"-(l\d+(?:l\d+)*)($|-)", tag_lc)
    if level_m:
        level = level_m.group(1)
    elif variant_lc.startswith("levels-"):
        level = variant_lc[len("levels-") :].lower()
    elif variant_lc == "baseline":
        level = "baseline"

    beta_m = re.search(r"-b(\d+(?:p\d+)?)($|-)", tag_lc)
    if beta_m:
        beta = beta_m.group(1).replace("p", ".")

    return step, level, beta


def count_runs(root: Path) -> Tuple[int, int]:
    em_dir = root / "EM"
    mismatch_dir = root / "Mismatch"
    em_runs = (
        sum(1 for run in em_dir.iterdir() if run.is_dir() and (run / "model_output.json").is_file())
        if em_dir.exists()
        else 0
    )
    mm_runs = (
        sum(
            1
            for run in mismatch_dir.iterdir()
            if run.is_dir() and (run / "model_output.json").is_file()
        )
        if mismatch_dir.exists()
        else 0
    )
    return em_runs, mm_runs


def iter_run_tags(prior_dir: Path) -> Iterable[Tuple[str, Path]]:
    run_tag_dirs = [d for d in prior_dir.iterdir() if d.is_dir() and d.name not in {"EM", "Mismatch"}]
    if run_tag_dirs:
        for d in sorted(run_tag_dirs):
            yield d.name, d
    elif (prior_dir / "EM").exists() or (prior_dir / "Mismatch").exists():
        yield "grouped", prior_dir


def collect_baseline_stats(
    model_root: Path,
    expected_runs: Optional[int],
    required_snippets: int,
    tag_regex: Optional[re.Pattern[str]],
) -> Dict[str, TagStats]:
    baseline: Dict[str, TagStats] = {}
    snippet_dirs = sorted([p for p in model_root.iterdir() if p.is_dir()])

    for snippet_dir in snippet_dirs:
        snippet = snippet_dir.name
        prior_dir = snippet_dir / "baseline" / "none"
        if not prior_dir.is_dir():
            continue
        for tag_name, tag_dir in iter_run_tags(prior_dir):
            if tag_regex and not tag_regex.search(tag_name):
                continue
            em, mm = count_runs(tag_dir)
            total = em + mm
            if total <= 0:
                continue
            if expected_runs is not None and total != expected_runs:
                continue
            stats = baseline.setdefault(tag_name, TagStats(step="baseline", level="baseline", prior="none", beta="-"))
            stats.em += em
            stats.total += total
            stats.snippets.add(snippet)

    return {
        tag: stats
        for tag, stats in baseline.items()
        if stats.total > 0 and len(stats.snippets) >= required_snippets
    }


def collect_struct_stats(
    model_root: Path,
    expected_runs: int,
    required_snippets: int,
    struct_priors: Sequence[str],
    variant_regex: re.Pattern[str],
    tag_regex: Optional[re.Pattern[str]],
) -> Dict[str, TagStats]:
    struct: Dict[str, TagStats] = {}
    prior_targets = {p.lower() for p in struct_priors}
    snippet_dirs = sorted([p for p in model_root.iterdir() if p.is_dir()])

    for snippet_dir in snippet_dirs:
        snippet = snippet_dir.name
        variant_dirs = [p for p in snippet_dir.iterdir() if p.is_dir() and variant_regex.search(p.name)]
        for variant_dir in sorted(variant_dirs):
            variant = variant_dir.name
            for prior_dir in sorted([p for p in variant_dir.iterdir() if p.is_dir()]):
                prior = prior_dir.name
                if prior.lower() not in prior_targets:
                    continue
                for tag_name, tag_dir in iter_run_tags(prior_dir):
                    if tag_regex and not tag_regex.search(tag_name):
                        continue
                    em, mm = count_runs(tag_dir)
                    total = em + mm
                    if total != expected_runs:
                        continue

                    step, level, beta = parse_step_level_beta(tag_name, variant)
                    stats = struct.get(tag_name)
                    if stats is None:
                        stats = TagStats(step=step, level=level, prior=prior, beta=beta)
                        struct[tag_name] = stats
                    stats.em += em
                    stats.total += total
                    stats.snippets.add(snippet)

    return {
        tag: stats
        for tag, stats in struct.items()
        if stats.total > 0 and len(stats.snippets) >= required_snippets
    }


def pick_latest(tags: Dict[str, TagStats], k: int) -> List[Tuple[str, TagStats]]:
    return sorted(tags.items(), key=lambda x: x[0], reverse=True)[:k]


def mean_std(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.pstdev(values)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute delta acc_struct over N structural run-tags against baseline for each model."
        )
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-Coder-7B-Instruct"],
        help="Model names to compare. Each maps to attn_viz/<model_dir_name(model)>.",
    )
    parser.add_argument("--expected-runs", type=int, default=50, help="Expected runs per snippet/tag.")
    parser.add_argument(
        "--baseline-expected-runs",
        type=int,
        default=None,
        help="Optional expected runs filter for baseline tags. Default: no filter.",
    )
    parser.add_argument("--required-snippets", type=int, default=32, help="Minimum snippet coverage for a valid tag.")
    parser.add_argument("--num-runs", type=int, default=5, help="How many structural run-tags to include per model.")
    parser.add_argument(
        "--struct-priors",
        default="ast,cfg,slice",
        help="Comma-separated structural priors to include.",
    )
    parser.add_argument(
        "--variant-regex",
        default=r"^levels-L\d+",
        help="Regex for structural variant directories (default includes levels-L1/L2/L3...).",
    )
    parser.add_argument(
        "--struct-tag-regex",
        default=None,
        help="Optional regex to filter structural run-tags (e.g., '(step1|step2)-l2-.*').",
    )
    parser.add_argument(
        "--baseline-tag-regex",
        default=None,
        help="Optional regex to filter baseline run-tags.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(resolve_alignment_outputs_root(PROJECT_ROOT)),
        help="Directory to write CSV summaries.",
    )
    args = parser.parse_args()

    attn_root = resolve_attn_root(PROJECT_ROOT)
    struct_priors = [p.strip() for p in args.struct_priors.split(",") if p.strip()]
    variant_regex = re.compile(args.variant_regex)
    tag_regex = re.compile(args.struct_tag_regex) if args.struct_tag_regex else None
    baseline_tag_regex = re.compile(args.baseline_tag_regex) if args.baseline_tag_regex else None
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = resolve_artifact_path(PROJECT_ROOT, out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    micro_rows: List[Dict[str, str]] = []
    summary_rows: List[Dict[str, str]] = []

    for model_name in args.models:
        model_dir = model_dir_name(model_name)
        model_root = attn_root / model_dir
        if not model_root.is_dir():
            summary_rows.append(
                {
                    "model_name": model_name,
                    "model_dir": model_dir,
                    "baseline_acc": "",
                    "baseline_tags": "0",
                    "struct_runs_used": "0",
                    "struct_acc_mean": "",
                    "struct_acc_std": "",
                    "delta_acc_struct_mean": "",
                    "delta_acc_struct_std": "",
                    "note": "model_dir_missing",
                }
            )
            continue

        baseline = collect_baseline_stats(
            model_root=model_root,
            expected_runs=args.baseline_expected_runs,
            required_snippets=args.required_snippets,
            tag_regex=baseline_tag_regex,
        )
        struct = collect_struct_stats(
            model_root=model_root,
            expected_runs=args.expected_runs,
            required_snippets=args.required_snippets,
            struct_priors=struct_priors,
            variant_regex=variant_regex,
            tag_regex=tag_regex,
        )

        if not baseline:
            summary_rows.append(
                {
                    "model_name": model_name,
                    "model_dir": model_dir,
                    "baseline_acc": "",
                    "baseline_tags": "0",
                    "struct_runs_used": "0",
                    "struct_acc_mean": "",
                    "struct_acc_std": "",
                    "delta_acc_struct_mean": "",
                    "delta_acc_struct_std": "",
                    "note": "no_valid_baseline_tags",
                }
            )
            continue

        if not struct:
            baseline_total = sum(s.total for s in baseline.values())
            baseline_em = sum(s.em for s in baseline.values())
            baseline_acc = (baseline_em / baseline_total) if baseline_total else 0.0
            summary_rows.append(
                {
                    "model_name": model_name,
                    "model_dir": model_dir,
                    "baseline_acc": f"{baseline_acc:.6f}",
                    "baseline_tags": str(len(baseline)),
                    "struct_runs_used": "0",
                    "struct_acc_mean": "",
                    "struct_acc_std": "",
                    "delta_acc_struct_mean": "",
                    "delta_acc_struct_std": "",
                    "note": "no_valid_struct_tags",
                }
            )
            continue

        baseline_total = sum(s.total for s in baseline.values())
        baseline_em = sum(s.em for s in baseline.values())
        baseline_acc = (baseline_em / baseline_total) if baseline_total else 0.0

        selected = pick_latest(struct, args.num_runs)
        deltas: List[float] = []
        struct_accs: List[float] = []
        for idx, (tag_name, stats) in enumerate(selected, start=1):
            s_acc = stats.acc
            delta = s_acc - baseline_acc
            deltas.append(delta)
            struct_accs.append(s_acc)
            micro_rows.append(
                {
                    "model_name": model_name,
                    "model_dir": model_dir,
                    "run_index": str(idx),
                    "run_tag": tag_name,
                    "step": stats.step,
                    "level": stats.level,
                    "prior": stats.prior,
                    "beta": stats.beta,
                    "snippet_count": str(len(stats.snippets)),
                    "total_runs": str(stats.total),
                    "exact_matches": str(stats.em),
                    "mismatches": str(stats.mismatch),
                    "struct_acc": f"{s_acc:.6f}",
                    "baseline_acc": f"{baseline_acc:.6f}",
                    "delta_acc_struct": f"{delta:.6f}",
                }
            )

        struct_mean, struct_std = mean_std(struct_accs)
        delta_mean, delta_std = mean_std(deltas)
        summary_rows.append(
            {
                "model_name": model_name,
                "model_dir": model_dir,
                "baseline_acc": f"{baseline_acc:.6f}",
                "baseline_tags": str(len(baseline)),
                "struct_runs_used": str(len(selected)),
                "struct_acc_mean": f"{struct_mean:.6f}",
                "struct_acc_std": f"{struct_std:.6f}",
                "delta_acc_struct_mean": f"{delta_mean:.6f}",
                "delta_acc_struct_std": f"{delta_std:.6f}",
                "note": "",
            }
        )

    micro_csv = out_dir / "delta_acc_struct_micro.csv"
    summary_csv = out_dir / "delta_acc_struct_summary.csv"

    with micro_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "model_name",
            "model_dir",
            "run_index",
            "run_tag",
            "step",
            "level",
            "prior",
            "beta",
            "snippet_count",
            "total_runs",
            "exact_matches",
            "mismatches",
            "struct_acc",
            "baseline_acc",
            "delta_acc_struct",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in micro_rows:
            writer.writerow(row)

    with summary_csv.open("w", newline="", encoding="utf-8") as fh:
        fields = [
            "model_name",
            "model_dir",
            "baseline_acc",
            "baseline_tags",
            "struct_runs_used",
            "struct_acc_mean",
            "struct_acc_std",
            "delta_acc_struct_mean",
            "delta_acc_struct_std",
            "note",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    print("[delta_acc_struct summary]")
    print(
        "Model                               | Baseline | Struct Mean (n=5) | Delta Mean±Std    | Baseline Tags | Note"
    )
    print("-" * 112)
    for row in summary_rows:
        model = row["model_name"]
        b = row["baseline_acc"] or "-"
        sm = (
            "-"
            if not row["struct_acc_mean"]
            else f"{float(row['struct_acc_mean']):.4f}"
        )
        if row["delta_acc_struct_mean"]:
            ds = f"{float(row['delta_acc_struct_mean']):+.4f} ± {float(row['delta_acc_struct_std']):.4f}"
        else:
            ds = "-"
        n = row["baseline_tags"]
        note = row["note"] or ""
        print(f"{model:<35} | {b:<8} | {sm:<17} | {ds:<17} | {n:<13} | {note}")

    print(f"\n[INFO] Wrote micro stats:   {micro_csv}")
    print(f"[INFO] Wrote model summary: {summary_csv}")


if __name__ == "__main__":
    main()
