#!/usr/bin/env python3
"""
Semantic entropy based evaluation of model attention against human eye-tracking data.

Usage:
    python3 evaluation.py --instruction "Simulate ..." --snippet Ackerman
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import re

import numpy as np

from models import DEFAULT_MODEL_NAME, DEFAULT_CACHE_DIR
from render.util import AttentionRenderer, RenderConfig
from paths import (
    model_dir_name,
    resolve_artifact_path,
    resolve_attn_root,
    resolve_eyetracking_source_root,
    resolve_eval_root,
    resolve_obf_result_read_root,
)

try:
    from transformers import AutoTokenizer  # type: ignore
except ImportError as exc:  # pragma: no cover - informative
    raise SystemExit(
        "The evaluation module requires the Hugging Face 'transformers' package.\n"
        "Install it via: pip install transformers accelerate safetensors"
    ) from exc


PHASES = ("reading", "answering", "reasoning")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_prob(vec: np.ndarray) -> np.ndarray:
    total = float(vec.sum())
    if total > 0:
        return vec / total
    if vec.size == 0:
        return vec
    return np.full_like(vec, 1.0 / vec.size)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _rankdata(vec: np.ndarray) -> np.ndarray:
    order = np.argsort(vec)
    ranks = np.zeros_like(order, dtype=float)
    ranks[order] = np.arange(1, len(vec) + 1)
    return ranks


def spearman_correlation(a: np.ndarray, b: np.ndarray) -> float:
    if a.size != b.size or a.size == 0:
        return 0.0
    ra = _rankdata(a)
    rb = _rankdata(b)
    return cosine_similarity(ra - ra.mean(), rb - rb.mean())


def entropy(probs: np.ndarray) -> float:
    probs = probs[np.nonzero(probs)]
    if probs.size == 0:
        return 0.0
    return float(-np.sum(probs * np.log(probs)))


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = normalize_prob(p)
    q = normalize_prob(q)
    m = 0.5 * (p + q)
    return entropy(m) - 0.5 * (entropy(p) + entropy(q))


def js_divergence_multi(distributions: Sequence[np.ndarray]) -> float:
    if not distributions:
        return 0.0
    dists = [normalize_prob(np.asarray(vec, dtype=float)) for vec in distributions]
    mu = np.mean(dists, axis=0)
    return entropy(mu) - np.mean([entropy(vec) for vec in dists])


def vector_from_fixation_tokens(tokens: Sequence[Dict[str, Any]], size: int) -> np.ndarray:
    vec = np.zeros(size, dtype=float)
    for entry in tokens:
        idx = entry.get("token_idx")
        if idx is None or idx < 0 or idx >= size:
            continue
        vec[int(idx)] = float(entry.get("score", 0.0))
    return normalize_prob(vec)


def cluster_outputs(outputs: Sequence[str]) -> Tuple[List[int], Dict[int, float], float]:
    K = len(outputs)
    if K == 0:
        return [], {}, 0.0
    canonical_to_cluster: Dict[str, int] = {}
    cluster_counts: Dict[int, int] = defaultdict(int)
    cluster_ids: List[int] = []
    for out in outputs:
        key = " ".join(out.strip().split()).lower()
        if key not in canonical_to_cluster:
            canonical_to_cluster[key] = len(canonical_to_cluster)
        cid = canonical_to_cluster[key]
        cluster_ids.append(cid)
        cluster_counts[cid] += 1
    q: Dict[int, float] = {cid: count / K for cid, count in cluster_counts.items()}
    H_sem = -sum(prob * math.log(prob) for prob in q.values() if prob > 0)
    return cluster_ids, q, H_sem


def split_into_bins(items: Sequence[np.ndarray], n_bins: int) -> List[np.ndarray]:
    if n_bins <= 0:
        return []
    if not items:
        return [np.zeros(0)] * n_bins
    indices = np.array_split(np.arange(len(items)), n_bins)
    bins: List[np.ndarray] = []
    for idxs in indices:
        if len(idxs) == 0:
            bins.append(np.zeros_like(items[0]))
        else:
            chunk = np.mean([items[i] for i in idxs], axis=0)
            bins.append(chunk)
    return bins


@dataclass
class RunPhaseData:
    mean_vector: np.ndarray
    step_vectors: List[np.ndarray]


@dataclass
class RunRecord:
    run_id: str
    cluster_id: int
    weight: float
    phases: Dict[str, RunPhaseData]


class SemanticEntropyEvaluator:
    def __init__(
        self,
        root: Path,
        instruction: str,
        code_snippet: str,
        vocab_tokens: Sequence[Dict[str, Any]],
        cache_dir: Optional[str] = None,
        model_dir: Optional[str] = None,
    ) -> None:
        self.root = root
        self.attn_root = resolve_attn_root(root, model_dir)
        self.instruction = instruction
        self.code_snippet = code_snippet
        self.vocab_tokens = vocab_tokens
        self.vocab_size = len(vocab_tokens)
        tokenizer_kwargs: Dict[str, Any] = {"local_files_only": True}
        effective_cache = cache_dir or str(DEFAULT_CACHE_DIR)
        if effective_cache:
            tokenizer_kwargs["cache_dir"] = effective_cache
        self.tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL_NAME, **tokenizer_kwargs)
        self.renderer = AttentionRenderer(self.tokenizer, RenderConfig(pool="all_layers_mean"))

    def _classify_generation_phases(
        self, result: Dict[str, Any]
    ) -> Tuple[Dict[int, str], Dict[str, Tuple[int, int]]]:
        completion = result.get("generated_completion", "") or ""
        lower = completion.lower()
        reading_end = next(
            (
                idx
                for idx in (
                    lower.find("answer:"),
                    lower.find("explanation"),
                    lower.find("```text"),
                )
                if idx != -1
            ),
            len(completion),
        )

        answer_start = lower.find("```text", reading_end)
        if answer_start == -1:
            answer_start = lower.find("```", reading_end)
        if answer_start == -1:
            answer_start = len(completion)

        answer_end = lower.find("```", answer_start + 3) if answer_start < len(completion) else -1
        if answer_end != -1:
            answer_end += 3
        else:
            answer_end = len(completion)

        reading_range = (0, min(answer_start, reading_end))
        answer_range = (answer_start, answer_end)
        reasoning_range = (answer_end, len(completion))

        spans = self._compute_generated_token_spans(
            result.get("token_ids_all", []), result.get("prompt_length_tokens", 0)
        )

        phase_by_step: Dict[int, str] = {}
        for idx, (start_char, _) in enumerate(spans):
            if answer_range[0] <= start_char < answer_range[1]:
                phase = "answering"
            elif reasoning_range[0] <= start_char:
                phase = "reasoning"
            else:
                phase = "reading"
            phase_by_step[idx] = phase

        return phase_by_step, {
            "reading": reading_range,
            "answering": answer_range,
            "reasoning": reasoning_range,
        }

    def _compute_generated_token_spans(
        self, token_ids_all: Sequence[int], prompt_len: int
    ) -> List[Tuple[int, int]]:
        generated_ids = token_ids_all[prompt_len:]
        spans: List[Tuple[int, int]] = []
        if not generated_ids:
            return spans
        decoded_prev = ""
        for idx in range(len(generated_ids)):
            current = self.tokenizer.decode(generated_ids[: idx + 1], skip_special_tokens=True)
            spans.append((len(decoded_prev), len(current)))
            decoded_prev = current
        return spans

    def _prompt_scores_to_vector(self, prompt_scores: Sequence[float]) -> np.ndarray:
        attn_map = self.renderer.map_attention_from_prompt_scores(
            code_snippet=self.code_snippet,
            instruction=self.instruction,
            prompt_scores=prompt_scores,
            pool_name="all_layers_mean",
            human_vocabulary=self.vocab_tokens,
        )
        return vector_from_fixation_tokens(attn_map.get("fixation_tokens", []), self.vocab_size)

    def load_model_runs(
        self,
        snippet: str,
        variant_label: Optional[str] = None,
        prior_label: Optional[str] = None,
    ) -> Tuple[List[RunRecord], float]:
        snippet_dir = self.attn_root / snippet
        if not snippet_dir.exists():
            raise FileNotFoundError(f"No model outputs found for snippet '{snippet}'.")
        variant_dir = resolve_child_dir(snippet_dir, variant_label, "variant")
        prior_dir = resolve_child_dir(variant_dir, prior_label, "prior")

        run_records: List[RunRecord] = []
        outputs: List[str] = []
        run_metadata: List[Tuple[str, Dict[str, RunPhaseData]]] = []

        for band in ("EM", "Mismatch"):
            band_dir = prior_dir / band
            if not band_dir.exists():
                continue
            for run_dir in sorted(band_dir.iterdir()):
                model_output_path = run_dir / "model_output.json"
                if not model_output_path.is_file():
                    continue
                with model_output_path.open("r", encoding="utf-8") as fh:
                    result = json.load(fh)
                outputs.append(result.get("generated_text", "") or "")

                phase_assignments, _ = self._classify_generation_phases(result)
                per_phase_vectors: Dict[str, List[np.ndarray]] = {phase: [] for phase in PHASES}

                for entry in result.get("pooled_attention_by_generated_token", []):
                    step = entry.get("generated_step")
                    if step is None:
                        continue
                    phase = phase_assignments.get(step)
                    if not phase:
                        continue
                    prompt_scores = entry.get("prompt_scores", {}).get("all_layers_mean")
                    if not prompt_scores:
                        continue
                    vec = self._prompt_scores_to_vector(prompt_scores)
                    per_phase_vectors.setdefault(phase, []).append(vec)

                phase_data: Dict[str, RunPhaseData] = {}
                for phase, vectors in per_phase_vectors.items():
                    if vectors:
                        stacked = np.vstack(vectors)
                        mean_vector = normalize_prob(stacked.mean(axis=0))
                        vectors_norm = [normalize_prob(vec) for vec in vectors]
                    else:
                        mean_vector = np.zeros(self.vocab_size, dtype=float)
                        vectors_norm = []
                    phase_data[phase] = RunPhaseData(mean_vector=mean_vector, step_vectors=vectors_norm)

                run_metadata.append((run_dir.name, phase_data))

        cluster_ids, cluster_mass, H_sem = cluster_outputs(outputs)
        if not run_metadata:
            return [], 0.0

        weights = []
        for idx, (run_id, phase_data) in enumerate(run_metadata):
            cid = cluster_ids[idx] if idx < len(cluster_ids) else 0
            w = cluster_mass.get(cid, 0.0) or 0.0
            weights.append(w)
            run_records.append(RunRecord(run_id=run_id, cluster_id=cid, weight=w, phases=phase_data))

        if sum(weights) == 0:
            uniform = 1.0 / len(run_records)
            for record in run_records:
                record.weight = uniform

        return run_records, H_sem

    def aggregate_phase_vectors(
        self, run_records: Sequence[RunRecord], phase: str
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        vectors = []
        weights = []
        for record in run_records:
            phase_data = record.phases.get(phase)
            if not phase_data:
                continue
            vectors.append(phase_data.mean_vector)
            weights.append(record.weight)
        if not vectors:
            return np.zeros(self.vocab_size, dtype=float), []
        weights_arr = np.asarray(weights, dtype=float)
        weights_sum = weights_arr.sum()
        if weights_sum == 0:
            weights_arr = np.full_like(weights_arr, 1.0 / len(weights_arr))
            weights_sum = 1.0
        weighted = np.average(np.vstack(vectors), axis=0, weights=weights_arr)
        return normalize_prob(weighted), vectors

    def aggregate_phase_matrices(
        self, run_records: Sequence[RunRecord], phase: str, n_bins: int
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        matrices: List[np.ndarray] = []
        weights: List[float] = []
        for record in run_records:
            phase_data = record.phases.get(phase)
            if not phase_data or not phase_data.step_vectors:
                continue
            binned = split_into_bins(phase_data.step_vectors, n_bins)
            if not binned:
                continue
            mat = np.column_stack([normalize_prob(col) for col in binned])
            matrices.append(mat)
            weights.append(record.weight)
        if not matrices:
            return np.zeros((self.vocab_size, n_bins), dtype=float), []
        weights_arr = np.asarray(weights, dtype=float)
        weights_sum = weights_arr.sum()
        if weights_sum == 0:
            weights_arr = np.full_like(weights_arr, 1.0 / len(weights_arr))
            weights_sum = 1.0
        stacked = np.stack(matrices)
        weighted = np.tensordot(weights_arr / weights_sum, stacked, axes=(0, 0))
        for t in range(weighted.shape[1]):
            weighted[:, t] = normalize_prob(weighted[:, t])
        return weighted, matrices


def load_participant_files(snippet_dir: Path) -> List[Path]:
    return sorted(p for p in snippet_dir.iterdir() if p.name.startswith("participant") and p.suffix == ".json")


def _build_token_index_map(vocab_tokens: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for idx, entry in enumerate(vocab_tokens):
        token = entry.get("Token")
        if token is None:
            continue
        mapping[token] = int(entry.get("TokenIdx", idx))
    return mapping


def load_participant_data(
    path: Path,
    vocab_tokens: Sequence[Dict[str, Any]],
) -> Tuple[np.ndarray, np.ndarray]:
    vocab_size = len(vocab_tokens)
    token_map = _build_token_index_map(vocab_tokens)

    data = json.loads(path.read_text(encoding="utf-8"))
    for entry in data.get("vocabulary", []):
        token = entry.get("Token")
        if token is None:
            continue
        idx = entry.get("TokenIdx")
        if idx is not None:
            token_map.setdefault(token, int(idx))
    total_scores = np.zeros(vocab_size, dtype=float)
    for entry in data.get("total_scores", []):
        idx = entry.get("TokenIdx")
        if idx is None:
            idx = token_map.get(entry.get("Token"))
        if idx is None or idx < 0 or idx >= vocab_size:
            continue
        total_scores[int(idx)] = float(entry.get("score", 0.0))
    total_scores = normalize_prob(total_scores)

    timeline = data.get("timeline", [])
    if timeline:
        n_bins = len(timeline)
        matrix = np.zeros((vocab_size, n_bins), dtype=float)
        for t, column in enumerate(timeline):
            col_vec = np.zeros(vocab_size, dtype=float)
            for entry in column:
                idx = entry.get("TokenIdx")
                if idx is None:
                    idx = token_map.get(entry.get("Token"))
                if idx is None or idx < 0 or idx >= vocab_size:
                    continue
                col_vec[int(idx)] = float(entry.get("score", 0.0))
            matrix[:, t] = normalize_prob(col_vec)
    else:
        matrix = np.zeros((vocab_size, 0), dtype=float)
    return total_scores, matrix


def resolve_child_dir(base: Path, preferred: Optional[str], label: str) -> Path:
    if preferred:
        target = base / preferred
        if not target.is_dir():
            raise FileNotFoundError(f"{label} '{preferred}' not found under {base}")
        return target
    candidates = sorted([p for p in base.iterdir() if p.is_dir()])
    if not candidates:
        raise FileNotFoundError(f"No {label} directories found under {base}")
    return candidates[-1]


def columnwise_metric(
    model: np.ndarray, human: np.ndarray, func
) -> float:
    if model.shape != human.shape or model.size == 0:
        return 0.0
    scores = []
    for t in range(model.shape[1]):
        scores.append(func(model[:, t], human[:, t]))
    return float(np.mean(scores)) if scores else 0.0

def output_prediction_eval(
    project_root: Path,
    output_root: Path,
    snippets_filter: Optional[Sequence[str]] = None,
    model_dir: Optional[str] = None,
    model_name: Optional[str] = None,
    expected_runs: int = 200,
    variant_filter: Optional[Sequence[str]] = None,
    prior_filter: Optional[Sequence[str]] = None,
    run_tag_filter: Optional[Sequence[str]] = None,
    run_tag_contains: Optional[str] = None,
    run_tag_regex: Optional[str] = None,
    prediction_root: Optional[Path] = None,
) -> None:
    """
    Scan prediction run artifacts and report output-prediction accuracy (EM rate)
    per snippet/variant/prior.
    """
    attn_root = prediction_root if prediction_root is not None else resolve_attn_root(project_root, model_dir)
    if not attn_root.exists():
        raise FileNotFoundError(f"Prediction root missing: {attn_root}. Run the pipeline first.")

    targets = set(s.lower() for s in snippets_filter) if snippets_filter else None
    variant_targets = (
        set(v.strip().lower() for v in variant_filter if v.strip())
        if variant_filter
        else None
    )
    prior_targets = (
        set(p.strip().lower() for p in prior_filter if p.strip())
        if prior_filter
        else None
    )
    run_tag_targets = (
        set(t.strip().lower() for t in run_tag_filter if t.strip())
        if run_tag_filter
        else None
    )
    run_tag_contains_lc = run_tag_contains.lower() if run_tag_contains else None
    run_tag_regex_compiled = re.compile(run_tag_regex) if run_tag_regex else None
    rows: List[Tuple[str, str, str, str, int, int, int, float]] = []
    tag_rows: List[Tuple[str, str, str, str, str, str, str, str, int, int, int, float]] = []
    snippet_variant_stats: Dict[str, Dict[str, Dict[str, Any]]] = {}
    overall_em: Dict[Tuple[str, str], int] = {}
    overall_total: Dict[Tuple[str, str], int] = {}
    setting_totals: Dict[Tuple[str, str, str, str], Dict[str, int]] = defaultdict(
        lambda: {"em": 0, "total": 0}
    )
    setting_snippets: Dict[Tuple[str, str, str, str], set[str]] = defaultdict(set)
    true_baseline_totals: Dict[str, int] = {"em": 0, "total": 0}
    true_baseline_snippets: set[str] = set()

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

    def tag_matches(tag_name: str) -> bool:
        tag_lc = tag_name.lower()
        if run_tag_targets is not None and tag_lc not in run_tag_targets:
            return False
        if run_tag_contains_lc is not None and run_tag_contains_lc not in tag_lc:
            return False
        if run_tag_regex_compiled is not None and not run_tag_regex_compiled.search(tag_name):
            return False
        return True

    def count_runs(root: Path) -> Tuple[int, int]:
        em_dir = root / "EM"
        mismatch_dir = root / "Mismatch"
        em_runs = (
            sum(
                1
                for run in em_dir.iterdir()
                if run.is_dir() and (run / "model_output.json").is_file()
            )
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

    for snippet_dir in sorted(p for p in attn_root.iterdir() if p.is_dir()):
        snippet_name = snippet_dir.name
        if targets and snippet_name.lower() not in targets:
            continue
        for variant_dir in sorted(p for p in snippet_dir.iterdir() if p.is_dir()):
            variant = variant_dir.name
            if variant_targets and variant.lower() not in variant_targets:
                continue
            for prior_dir in sorted(p for p in variant_dir.iterdir() if p.is_dir()):
                prior = prior_dir.name
                if prior_targets and prior.lower() not in prior_targets:
                    continue
                run_tag_dirs = [
                    d
                    for d in prior_dir.iterdir()
                    if d.is_dir() and d.name not in {"EM", "Mismatch"}
                ]
                if run_tag_dirs:
                    run_tags = [(d.name, d) for d in sorted(run_tag_dirs)]
                else:
                    run_tags = []
                    if (prior_dir / "EM").exists() or (prior_dir / "Mismatch").exists():
                        run_tags.append(("grouped", prior_dir))

                if variant.lower() == "baseline" and prior.lower() == "none":
                    # Baseline aggregates across all baseline run-tags and does
                    # NOT apply expected-runs filtering.
                    baseline_has_runs = False
                    for tag_name, tag_dir in run_tags:
                        b_em, b_mm = count_runs(tag_dir)
                        b_total = b_em + b_mm
                        if b_total <= 0:
                            continue
                        baseline_has_runs = True
                        true_baseline_totals["em"] += b_em
                        true_baseline_totals["total"] += b_total
                    if baseline_has_runs:
                        true_baseline_snippets.add(snippet_name)

                total_em = 0
                total_mm = 0
                valid_tags = 0
                for tag_name, tag_dir in run_tags:
                    if not tag_matches(tag_name):
                        continue
                    em_runs, mm_runs = count_runs(tag_dir)
                    total = em_runs + mm_runs
                    if total != expected_runs:
                        print(
                            f"[SKIP] {snippet_name}/{variant}/{prior}/{tag_name} "
                            f"runs={total} (expected {expected_runs})"
                        )
                        continue
                    valid_tags += 1
                    total_em += em_runs
                    total_mm += mm_runs
                    step, level, beta = parse_step_level_beta(tag_name, variant)
                    tag_acc = em_runs / total if total else 0.0
                    tag_rows.append(
                        (
                            snippet_name,
                            variant,
                            prior,
                            tag_name,
                            step,
                            level,
                            beta,
                            model_name or "",
                            total,
                            em_runs,
                            mm_runs,
                            tag_acc,
                        )
                    )
                    setting_key = (step, level, prior, beta)
                    setting_totals[setting_key]["em"] += em_runs
                    setting_totals[setting_key]["total"] += total
                    setting_snippets[setting_key].add(snippet_name)

                total = total_em + total_mm
                if total == 0:
                    continue
                accuracy = total_em / total
                rows.append((snippet_name, variant, prior, model_name or "", total, total_em, total_mm, accuracy))

                stats = snippet_variant_stats.setdefault(snippet_name, {}).setdefault(
                    variant,
                    {
                        "em": 0,
                        "total": 0,
                        "priors": [],
                    },
                )
                stats["em"] += total_em
                stats["total"] += total
                stats["priors"].append(
                    {
                        "prior": prior,
                        "total": total,
                        "em": total_em,
                        "mm": total_mm,
                        "acc": accuracy,
                        "valid_tags": valid_tags,
                    }
                )
                # overall_em += em_runs
                # overall_total += total

    if not rows:
        print("[WARN] No completed runs found for prediction accuracy evaluation.")
        return

    def format_variant_label(name: str) -> str:
        if name == "baseline":
            return "--baseline"
        if name.startswith("levels-"):
            suffix = name[len("levels-") :]
            levels = re.findall(r"L(\d+)", suffix)
            if levels:
                return ", ".join(f"--level{lvl}" for lvl in levels)
        return name

    display_model = model_name or (model_dir or "default")
    print("\n[Prediction Accuracy]")
    print(f"Model: {display_model}")
    print(
        "Filters: "
        f"snippets={','.join(sorted(targets)) if targets else 'all'} | "
        f"variant={','.join(sorted(variant_targets)) if variant_targets else 'all'} | "
        f"prior={','.join(sorted(prior_targets)) if prior_targets else 'all'} | "
        f"run_tag={','.join(sorted(run_tag_targets)) if run_tag_targets else '*'} | "
        f"contains={run_tag_contains or '*'} | "
        f"regex={run_tag_regex or '*'} | "
        f"expected_runs={expected_runs}"
    )
    for snippet in sorted(snippet_variant_stats.keys()):
        print(f"{snippet}")
        variants = snippet_variant_stats[snippet]
        for variant in sorted(variants.keys()):
            stats = variants[variant]
            total = stats["total"]
            em_runs = stats["em"]
            mm_runs = total - em_runs
            acc = em_runs / total if total else 0.0
            label = format_variant_label(variant)
            for prior_stats in sorted(stats["priors"], key=lambda p: p["prior"]):
                prior = prior_stats["prior"]
                key = (label, prior)
                overall_total[key] = overall_total.get(key, 0) + prior_stats["total"]
                overall_em[key] = overall_em.get(key, 0) + prior_stats["em"]
            print(
                f"  {label:<25}: {acc*100:6.2f}%  (runs={total}, EM={em_runs}, Mismatch={mm_runs})"
            )
            for prior_stats in sorted(stats["priors"], key=lambda p: p["prior"]):
                prior = prior_stats["prior"]
                p_total = prior_stats["total"]
                p_em = prior_stats["em"]
                p_mm = prior_stats["mm"]
                p_acc = prior_stats["acc"]
                p_tags = prior_stats.get("valid_tags", 0)
                print(
                    f"      [prior={prior:<8}] {p_acc*100:6.2f}%  (runs={p_total}, EM={p_em}, Mismatch={p_mm}, tags={p_tags})"
                )
        print()


    print("\n[Overall Accuracy by Level/Prior]")
    if true_baseline_totals["total"] > 0:
        b_total = true_baseline_totals["total"]
        b_em = true_baseline_totals["em"]
        b_mm = b_total - b_em
        b_acc = b_em / b_total if b_total else 0.0
        print(
            f"  {'--baseline':<25} | prior={'none':<8} : "
            f"{b_acc*100:6.2f}%  (runs={b_total}, EM={b_em}, Mismatch={b_mm})"
        )
    for (label, prior) in sorted(overall_total.keys()):
        total = overall_total[(label, prior)]
        em = overall_em.get((label, prior), 0)
        acc = em / total if total else 0.0
        mm = total - em
        print(f"  {label:<25} | prior={prior:<8} : {acc*100:6.2f}%  (runs={total}, EM={em}, Mismatch={mm})")

    if setting_totals or true_baseline_totals["total"] > 0:
        print("\n[Accuracy by Step/Level/Prior/Beta]")
        if true_baseline_totals["total"] > 0:
            b_total = true_baseline_totals["total"]
            b_em = true_baseline_totals["em"]
            b_mm = b_total - b_em
            b_acc = b_em / b_total if b_total else 0.0
            b_tags = len(true_baseline_snippets)
            print(
                f"  {'baseline':<8} | {'baseline':<12} | prior={'none':<8} | beta={'-':<6} "
                f": {b_acc*100:6.2f}%  (runs={b_total}, EM={b_em}, Mismatch={b_mm}, tags={b_tags})"
            )
        for step, level, prior, beta in sorted(setting_totals.keys()):
            total = setting_totals[(step, level, prior, beta)]["total"]
            em = setting_totals[(step, level, prior, beta)]["em"]
            tags = len(setting_snippets[(step, level, prior, beta)])
            mm = total - em
            acc = em / total if total else 0.0
            print(
                f"  {step:<8} | {level:<12} | prior={prior:<8} | beta={beta:<6} "
                f": {acc*100:6.2f}%  (runs={total}, EM={em}, Mismatch={mm}, tags={tags})"
            )

    ensure_dir(output_root)
    csv_path = output_root / "prediction_accuracy.csv"
    with csv_path.open("w", encoding="utf-8") as fh:
        fh.write("model,snippet,variant,prior,total_runs,exact_matches,mismatches,accuracy\n")
        for snippet, variant, prior, model, total, em_runs, mm_runs, acc in sorted(rows):
            fh.write(f"{model},{snippet},{variant},{prior},{total},{em_runs},{mm_runs},{acc:.6f}\n")
    print(f"[INFO] Saved accuracy summary to {csv_path}")

    if tag_rows:
        tag_csv_path = output_root / "prediction_accuracy_by_tag.csv"
        with tag_csv_path.open("w", encoding="utf-8") as fh:
            fh.write(
                "model,snippet,variant,prior,run_tag,step,level,beta,total_runs,exact_matches,mismatches,accuracy\n"
            )
            for (
                snippet,
                variant,
                prior,
                tag_name,
                step,
                level,
                beta,
                model,
                total,
                em_runs,
                mm_runs,
                acc,
            ) in sorted(tag_rows):
                fh.write(
                    f"{model},{snippet},{variant},{prior},{tag_name},{step},{level},{beta},"
                    f"{total},{em_runs},{mm_runs},{acc:.6f}\n"
                )
        print(f"[INFO] Saved run-tag accuracy summary to {tag_csv_path}")

    if setting_totals or true_baseline_totals["total"] > 0:
        setting_csv_path = output_root / "prediction_accuracy_by_setting.csv"
        with setting_csv_path.open("w", encoding="utf-8") as fh:
            fh.write("model,step,level,prior,beta,total_runs,exact_matches,mismatches,tags,accuracy\n")
            if true_baseline_totals["total"] > 0:
                b_total = true_baseline_totals["total"]
                b_em = true_baseline_totals["em"]
                b_mm = b_total - b_em
                b_acc = b_em / b_total if b_total else 0.0
                b_tags = len(true_baseline_snippets)
                fh.write(
                    f"{model_name or ''},baseline,baseline,none,-,{b_total},{b_em},{b_mm},{b_tags},{b_acc:.6f}\n"
                )
            for step, level, prior, beta in sorted(setting_totals.keys()):
                total = setting_totals[(step, level, prior, beta)]["total"]
                em = setting_totals[(step, level, prior, beta)]["em"]
                tags = len(setting_snippets[(step, level, prior, beta)])
                mm = total - em
                acc = em / total if total else 0.0
                fh.write(
                    f"{model_name or ''},{step},{level},{prior},{beta},{total},{em},{mm},{tags},{acc:.6f}\n"
                )
        print(f"[INFO] Saved setting-level accuracy summary to {setting_csv_path}")



def evaluate_snippet(
    project_root: Path,
    instruction: str,
    snippet: str,
    output_root: Path,
    cache_dir: Optional[str] = None,
    model_dir: Optional[str] = None,
    phase_summary_tables: Optional[
        Dict[str, Dict[str, Dict[str, Tuple[float, float, float, float]]]]
    ] = None,
    variant_label: Optional[str] = None,
    prior_label: Optional[str] = None,
) -> None:
    fixation_dir = project_root / "fixation_dump" / snippet
    vocab_path = fixation_dir / "vocabulary.json"
    if not vocab_path.is_file():
        raise FileNotFoundError(f"Vocabulary file missing for snippet '{snippet}'.")
    vocab_tokens = json.loads(vocab_path.read_text(encoding="utf-8"))

    source_root = resolve_eyetracking_source_root(project_root)
    source_path = source_root / f"{snippet}.java"
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file missing for snippet '{snippet}'.")
    code_text = source_path.read_text(encoding="utf-8")

    if cache_dir and not Path(cache_dir).expanduser().exists():
        raise FileNotFoundError(
            f"Tokenizer cache directory '{cache_dir}' not found. "
            "Pass --cache-dir pointing to your local CodeLlama cache."
        )

    evaluator = SemanticEntropyEvaluator(
        root=project_root,
        instruction=instruction,
        code_snippet=code_text,
        vocab_tokens=vocab_tokens,
        cache_dir=cache_dir,
        model_dir=model_dir,
    )

    run_records, semantic_entropy_value = evaluator.load_model_runs(
        snippet,
        variant_label=variant_label,
        prior_label=prior_label,
    )
    if not run_records:
        print(f"[WARN] No model runs found for snippet '{snippet}'.")
        return

    participant_files = load_participant_files(fixation_dir)
    if not participant_files:
        print(f"[WARN] No participant files found for snippet '{snippet}'.")
        return

    for participant_file in participant_files:
        participant_id = participant_file.stem.split("_")[-1]
        human_vector, human_matrix = load_participant_data(
            participant_file, vocab_tokens
        )
        n_bins = human_matrix.shape[1] if human_matrix.size else 0

        phase_vectors: Dict[str, np.ndarray] = {}
        phase_vector_sets: Dict[str, List[np.ndarray]] = {}
        phase_matrices: Dict[str, np.ndarray] = {}
        phase_matrix_sets: Dict[str, List[np.ndarray]] = {}

        for phase in PHASES:
            mean_vec, vec_set = evaluator.aggregate_phase_vectors(run_records, phase)
            phase_vectors[phase] = mean_vec
            phase_vector_sets[phase] = vec_set
            if n_bins > 0:
                mean_mat, mat_set = evaluator.aggregate_phase_matrices(
                    run_records, phase, n_bins
                )
                phase_matrices[phase] = mean_mat
                phase_matrix_sets[phase] = mat_set
            else:
                phase_matrices[phase] = np.zeros((evaluator.vocab_size, 0))
                phase_matrix_sets[phase] = []

        for phase in PHASES:
            cosine_vec = cosine_similarity(phase_vectors[phase], human_vector)
            spearman_vec = spearman_correlation(phase_vectors[phase], human_vector)
            js_vec = js_divergence(phase_vectors[phase], human_vector)
            dispersion_vec = js_divergence_multi(phase_vector_sets[phase])
            metrics = {
                "semantic_entropy": semantic_entropy_value,
                "cosine_vector": cosine_vec,
                "spearman_vector": spearman_vec,
                "js_divergence_vector": js_vec,
                "vector_dispersion_js": dispersion_vec,
                "vector_elements": phase_vectors[phase].tolist(),
            }

            if human_matrix.size and phase_matrices[phase].shape[1] == human_matrix.shape[1]:
                matrix_dispersion = 0.0
                if phase_matrix_sets[phase]:
                    mats = [mat for mat in phase_matrix_sets[phase] if mat.shape[1] == human_matrix.shape[1]]
                    if mats:
                        mats_stack = np.stack(mats)
                        dispersions = []
                        for t in range(human_matrix.shape[1]):
                            column_vectors = [mats_stack[i, :, t] for i in range(mats_stack.shape[0])]
                            dispersions.append(js_divergence_multi(column_vectors))
                        matrix_dispersion = float(np.mean(dispersions)) if dispersions else 0.0
                metrics.update(
                    {
                        "cosine_matrix": columnwise_metric(
                            phase_matrices[phase], human_matrix, cosine_similarity
                        ),
                        "spearman_matrix": columnwise_metric(
                            phase_matrices[phase], human_matrix, spearman_correlation
                        ),
                        "js_divergence_matrix": columnwise_metric(
                            phase_matrices[phase], human_matrix, js_divergence
                        ),
                        "matrix_dispersion_js": matrix_dispersion,
                    }
                )

            target_dir = (
                output_root
                / f"participant_{participant_id}"
                / snippet
                / f"phase_{phase}"
            )
            ensure_dir(target_dir)
            (target_dir / "metrics.json").write_text(
                json.dumps(metrics, indent=2), encoding="utf-8"
            )
            if phase_summary_tables is not None:
                tuple_value = (cosine_vec, spearman_vec, js_vec, dispersion_vec)
                phase_table = phase_summary_tables.setdefault(phase, {})
                phase_table.setdefault(f"participant_{participant_id}", {})[snippet] = tuple_value


def main(argv: Optional[Sequence[str]] = None) -> None:
    default_instruction = (
        "Simulate the execution of the Java program provided below and reproduce exactly what "
        "would appear on standard output. Return only the raw console output characters, preserving "
        "line breaks and spacing. Do not add explanations, commentary, or formatting such as code "
        "fences or quotes. If the program prints nothing, respond with an empty string."
    )

    parser = argparse.ArgumentParser(description="Semantic entropy based evaluation pipeline.")
    parser.add_argument(
        "--prediction-accuracy",
        type=str,
        nargs="?",
        const="all",
        default=None,
        help=(
            "Compute output-prediction accuracy. "
            "Optionally supply comma-separated snippets (default: all)."
        ),
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Root directory of the eyetracking project.",
    )
    parser.add_argument(
        "--snippet",
        type=str,
        default=None,
        help="Specific snippet to evaluate (default: all snippets found in attn_viz).",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default=default_instruction,
        help="Instruction string used during model prompting.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=str(DEFAULT_CACHE_DIR),
        help=f"Hugging Face cache directory containing tokenizer files (default: {DEFAULT_CACHE_DIR}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=resolve_eval_root(Path(__file__).resolve().parent),
        help="Directory where evaluation results will be stored.",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Model name used to select attn_viz/<model> directory.",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default=None,
        help="Explicit attn_viz/<model_dir> override.",
    )
    parser.add_argument(
        "--variant-label",
        type=str,
        default=None,
        help="Variant directory under attn_viz/<snippet> (e.g., baseline, levels-L1L2). Defaults to latest.",
    )
    parser.add_argument(
        "--prior-label",
        type=str,
        default=None,
        help="Prior directory under the variant (e.g., none, human). Defaults to latest.",
    )
    parser.add_argument(
        "--expected-runs",
        type=int,
        default=200,
        help="Expected number of runs per run-tag. Tags with different counts are skipped.",
    )
    parser.add_argument(
        "--run-tag",
        type=str,
        default=None,
        help="Run-tag filter (comma-separated exact names).",
    )
    parser.add_argument(
        "--run-tag-contains",
        type=str,
        default=None,
        help="Run-tag substring filter (e.g., step1-l1-cfg-b0p5). If it contains 'obf', read from obfuscation/result.",
    )
    parser.add_argument(
        "--run-tag-regex",
        type=str,
        default=None,
        help="Run-tag regex filter. If it contains 'obf', read from obfuscation/result.",
    )
    args = parser.parse_args(argv)

    project_root = args.project_root
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = resolve_artifact_path(project_root, output_dir)
    model_dir = args.model_dir or (model_dir_name(args.model_name) if args.model_name else None)

    if args.prediction_accuracy is not None:
        arg_value = args.prediction_accuracy or "all"
        tokens = [
            token.strip()
            for token in arg_value.split(",")
            if token.strip()
        ]
        if tokens and tokens[0].lower() in {"all", "*"}:
            tokens = []
        variant_tokens = (
            [token.strip() for token in args.variant_label.split(",") if token.strip()]
            if args.variant_label
            else None
        )
        prior_tokens = (
            [token.strip() for token in args.prior_label.split(",") if token.strip()]
            if args.prior_label
            else None
        )
        run_tag_tokens = (
            [token.strip() for token in args.run_tag.split(",") if token.strip()]
            if args.run_tag
            else None
        )
        tag_hints: List[str] = []
        if run_tag_tokens:
            tag_hints.extend(run_tag_tokens)
        if args.run_tag_contains:
            tag_hints.append(args.run_tag_contains)
        if args.run_tag_regex:
            tag_hints.append(args.run_tag_regex)
        use_obf_prediction_root = any("obf" in hint.lower() for hint in tag_hints)
        prediction_root = None
        if use_obf_prediction_root:
            prediction_root = resolve_obf_result_read_root(project_root, model_dir)
            print(f"[INFO] Detected obf run-tag filter; reading prediction runs from: {prediction_root}")
        output_prediction_eval(
            project_root=project_root,
            output_root=output_dir,
            snippets_filter=tokens or None,
            model_dir=model_dir,
            model_name=args.model_name,
            expected_runs=args.expected_runs,
            variant_filter=variant_tokens,
            prior_filter=prior_tokens,
            run_tag_filter=run_tag_tokens,
            run_tag_contains=args.run_tag_contains,
            run_tag_regex=args.run_tag_regex,
            prediction_root=prediction_root,
        )
        return

        return

    attn_root = resolve_attn_root(project_root, model_dir)
    if not attn_root.exists():
        raise FileNotFoundError("Run the main pipeline first to generate attn_viz artifacts.")

    snippets = (
        [args.snippet]
        if args.snippet
        else sorted([p.name for p in attn_root.iterdir() if p.is_dir()])
    )

    ensure_dir(output_dir)
    phase_summary_tables: Dict[
        str, Dict[str, Dict[str, Tuple[float, float, float, float]]]
    ] = {phase: {} for phase in PHASES}

    for snippet in snippets:
        try:
            evaluate_snippet(
                project_root=project_root,
                instruction=args.instruction,
                snippet=snippet,
                output_root=output_dir,
                cache_dir=args.cache_dir,
                model_dir=model_dir,
                phase_summary_tables=phase_summary_tables,
                variant_label=args.variant_label,
                prior_label=args.prior_label,
            )
            print(f"[INFO] Evaluation completed for snippet '{snippet}'.")
        except Exception as exc:
            print(f"[ERROR] Failed to evaluate snippet '{snippet}': {exc}")
    for phase, table in phase_summary_tables.items():
        if not table:
            continue
        participants = sorted(table.keys())
        snippets_sorted = sorted({snip for mapping in table.values() for snip in mapping.keys()})
        summary_path = output_dir / f"summary_phase_{phase}.csv"
        with summary_path.open("w", encoding="utf-8") as csv_file:
            header = ["participant"] + snippets_sorted
            csv_file.write(",".join(header) + "\n")
            for participant in participants:
                row = [participant]
                for snippet in snippets_sorted:
                    metrics = table.get(participant, {}).get(snippet)
                    if metrics:
                        cos, spear, jsd, disp = metrics
                        row.append(f"({cos:.3f};{spear:.3f};{jsd:.3f};{disp:.3f})")
                    else:
                        row.append("")
                csv_file.write(",".join(row) + "\n")


if __name__ == "__main__":
    main()
