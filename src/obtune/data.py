"""Dataset contract + loaders for training and evaluation.

This module is where the two silent failures that would invalidate the whole transfer
matrix get caught (CLAUDE.md §4):

  #1 split leakage — splits must partition by `program_id`, never by row. An L1b
     variant of a program whose L0 form is in the test set inflates every cell.
     `validate_pairs` refuses a corpus where a program_id appears in two splits, and
     `assert_train_eval_disjoint` refuses one that overlaps the test programs.
  H1 quarantine — every training read goes through `paths.load_training_jsonl`, which
     is the only function permitted to open a training file (CLAUDE.md §3.2 layer 1).
     Eval-side H1 reads go through `load_h1_items`, which *requires* an access purpose
     and appends to data/quarantine/h1/ACCESS_LOG.md.

`output_repr` round-trip: gold labels are canon (exec/canon.py) output, which is valid
JSON by construction. `json.loads` then re-`canon` must reproduce the string byte for
byte. A gold label that does not round-trip means the label and the grader disagree
about what "the output" is, which would show up as an unexplained accuracy ceiling.
"""
from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from obtune import paths, prompts
from obtune.config import GLOBAL_SEED
from obtune.exec.canon import Unserializable, canon
from obtune.schema import EvalItem, TrainPair

PAIRS_SUBDIR = "pairs"
# Evaluation reads the materialized EvalItem rows (variant x input case with gold),
# not the Variant rows the gate emits into testset/variants/. Separate directories
# mean re-running 05_build_variants.py never clobbers eval inputs and vice versa.
EVAL_VARIANTS_SUBDIR = "testset/items"
H1_ACCESS_LOG = paths.QUARANTINE_ROOT / "h1" / "ACCESS_LOG.md"

#: Named evaluation sets. `testset` is the 70 ICSE programs, kept because they carry
#: human accuracy labels; `heldout` is the corpus programs reserved by the `test`
#: split — far more of them, and the only set with enough power to call an
#: off-diagonal transfer cell zero. Each has its own H1 quarantine subset.
EVAL_SOURCES = {
    "testset": {"items": "testset/items", "h1_subset": "testset"},
    "heldout": {"items": "heldout/items", "h1_subset": "heldout"},
}
DEFAULT_EVAL_SOURCE = "testset"


class DataContractError(RuntimeError):
    """A corpus violates the dataset contract (split leakage, bad gold, H1 present)."""


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

def pairs_path(condition: str, language: str, aug_tag: Optional[str] = None) -> Path:
    if aug_tag:
        return paths.TRAIN_ROOT / "pairs_aug" / aug_tag / condition / f"{language}.jsonl"
    return paths.TRAIN_ROOT / PAIRS_SUBDIR / condition / f"{language}.jsonl"


def _source_spec(source: str) -> dict[str, str]:
    if source not in EVAL_SOURCES:
        raise ValueError(f"unknown eval source {source!r}; expected one of {sorted(EVAL_SOURCES)}")
    return EVAL_SOURCES[source]


def eval_variants_path(condition: str, language: str, source: str = DEFAULT_EVAL_SOURCE) -> Path:
    return paths.EVAL_ROOT / _source_spec(source)["items"] / condition / f"{language}.jsonl"


def h1_path(language: str, source: str = DEFAULT_EVAL_SOURCE) -> Path:
    subset = _source_spec(source)["h1_subset"]
    return paths.QUARANTINE_ROOT / "h1" / subset / "items" / f"{language}.jsonl"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def _trainable_composites() -> set[str]:
    """Composite codes the composite ladder declares trainable, excluding anything H1.

    Read from the ladder rather than hard-coded, so a composite cannot become trainable by
    being mentioned in a call site — it has to be declared, gate-validated and non-H1.
    """
    from obtune.config import load_config

    try:
        cfg = load_config("conditions_composite.yaml")
    except Exception:  # noqa: BLE001 — absent ladder simply means no composites
        return set()
    out: set[str] = set()
    for code, spec in (cfg.get("composite_conditions") or {}).items():
        if not spec.get("trainable", False):
            continue
        parts = [str(x) for x in (spec.get("parts") or [])]
        if "H1" in code or any("H1" in x for x in parts):
            continue  # unreachable today; the ladder is data, and this is cheap
        out.add(code)
    return out


def load_pairs(
    conditions: Sequence[str],
    language: str,
    splits: Optional[Sequence[str]] = None,
    validate: bool = True,
    allow_composites: bool = False,
    augment_tags: Optional[Sequence[str]] = None,
) -> list[TrainPair]:
    """Load training pairs for `conditions`. The ONLY training-data entry point.

    `augment_tags` adds the re-seeded variant builds under data/train/pairs_aug/<tag>/ for
    the SAME conditions (scripts/05_build_variants.py --aug-tag). A condition whose
    transform is deterministic (L0, L2) has no augmented file and is silently taken once;
    everything else is loaded K+1 times with distinct item_ids. Still under TRAIN_ROOT,
    so every quarantine layer applies unchanged.

    `paths.load_training_jsonl` enforces the quarantine guard (path root + H1 label);
    `TrainPair` re-enforces it in its validator. Both layers are intentional.

    `allow_composites` is an OPT-IN, defaulting to the strict behaviour every existing
    caller already has. Composite `C_` codes are deliberately outside
    `TRAINABLE_CONDITIONS` so that adding them cannot shift the RQ1 grid, the transfer
    matrix, the router's class count, or any other consumer of that tuple — but the
    RouterLoRA gate genuinely needs them, because a stacked variant is the only case where
    no single expert is correct. Rather than widening the tuple (which ripples into
    `merge_adapters`, `transfer`, `cft/` and `router.features`), the narrow allowance is
    requested explicitly by the one caller that needs it.

    The allowance is NOT a bypass. A composite is accepted only if the composite ladder
    itself declares it `trainable: true`, and never if H1 appears in the code or in any of
    its parts. Both other quarantine layers still run unchanged on every row loaded.
    """
    allowed = set(paths.TRAINABLE_CONDITIONS)
    if allow_composites:
        allowed |= _trainable_composites()
    bad = [c for c in conditions if c not in allowed]
    if bad:
        raise paths.QuarantineViolation(
            f"conditions {bad} are not trainable (allowed: {sorted(allowed)})"
        )
    rows: list[TrainPair] = []
    for cond in conditions:
        p = pairs_path(cond, language)
        if not p.exists():
            raise FileNotFoundError(f"missing training pairs for {cond}/{language}: {p}")
        for raw in paths.load_training_jsonl(p):
            rows.append(TrainPair(**raw))
        for tag in (augment_tags or []):
            pa = pairs_path(cond, language, aug_tag=tag)
            if not pa.exists():
                continue  # deterministic transform: nothing to augment with
            for raw in paths.load_training_jsonl(pa):
                rows.append(TrainPair(**raw))
    if splits is not None:
        keep = set(splits)
        rows = [r for r in rows if r.split in keep]
    if validate:
        validate_pairs(rows)
    return rows


def load_eval_items(
    conditions: Sequence[str],
    language: str,
    h1_access_purpose: Optional[str] = None,
    script: str = "unknown",
    source: str = DEFAULT_EVAL_SOURCE,
) -> list[EvalItem]:
    """Load evaluation rows from a named set. H1 is routed to quarantine and logged."""
    items: list[EvalItem] = []
    for cond in conditions:
        if cond == "H1":
            items.extend(load_h1_items(language, purpose=h1_access_purpose,
                                       script=script, source=source))
            continue
        p = eval_variants_path(cond, language, source)
        if not p.exists():
            raise FileNotFoundError(f"missing eval items for {cond}/{language} in {source!r}: {p}")
        items.extend(EvalItem(**raw) for raw in paths.iter_jsonl(p))
    return items


def load_h1_items(
    language: str, purpose: Optional[str], script: str = "unknown", note: str = "",
    source: str = DEFAULT_EVAL_SOURCE,
) -> list[EvalItem]:
    """Read the held-out condition. CLAUDE.md §3.2 rule 3: every read is logged.

    `purpose` is mandatory and constrained to the two sanctioned passes so that an
    accidental extra H1 evaluation is a crash, not a silently-appended log line.
    """
    if purpose not in ("pilot_eval", "final_eval"):
        raise paths.QuarantineViolation(
            "H1 may only be read with h1_access_purpose in {'pilot_eval','final_eval'}; "
            f"got {purpose!r}. H1 is never used for training, checkpoint selection, "
            "router training or merge tuning (CLAUDE.md §3.2)."
        )
    p = h1_path(language, source)
    if not p.exists():
        raise FileNotFoundError(f"missing H1 quarantine file: {p}")
    items = [EvalItem(**raw) for raw in paths.iter_jsonl(p)]
    record_h1_access(purpose=purpose, script=script, n_items=len(items), language=language, note=note)
    return items


def record_h1_access(
    purpose: str, script: str, n_items: int, language: str, note: str = ""
) -> Path:
    H1_ACCESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not H1_ACCESS_LOG.exists():
        H1_ACCESS_LOG.write_text(
            "# H1 quarantine access log\n\n"
            "Append-only. Every read of data/quarantine/h1/ appends a row here "
            "(CLAUDE.md §3.2 rule 3).\n\n"
            "| utc | purpose | script | language | n_items | note |\n"
            "|---|---|---|---|---|---|\n"
        )
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(H1_ACCESS_LOG, "a") as f:
        f.write(f"| {ts} | {purpose} | {script} | {language} | {n_items} | {note} |\n")
    return H1_ACCESS_LOG


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #

@dataclass
class CorpusReport:
    n_rows: int
    n_programs: int
    by_condition: dict[str, int] = field(default_factory=dict)
    by_split: dict[str, int] = field(default_factory=dict)
    bad_gold: list[str] = field(default_factory=list)
    leaked_programs: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "n_programs": self.n_programs,
            "by_condition": self.by_condition,
            "by_split": self.by_split,
            "n_bad_gold": len(self.bad_gold),
            "n_leaked_programs": len(self.leaked_programs),
        }


def check_output_repr(output_repr: str) -> bool:
    """Gold must be canon output: valid JSON that re-canonicalizes to itself."""
    try:
        value = json.loads(output_repr)
    except (json.JSONDecodeError, RecursionError):
        return False
    try:
        return canon(value) == output_repr
    except Unserializable:
        return False


def validate_pairs(rows: Sequence[TrainPair], strict_gold: bool = True) -> CorpusReport:
    """Enforce the training-corpus contract. Raises DataContractError on violation."""
    if not rows:
        raise DataContractError("empty training corpus")

    split_of: dict[str, set[str]] = defaultdict(set)
    seen_item_ids: set[str] = set()
    dupes: list[str] = []
    for r in rows:
        if r.condition == "H1":  # belt and braces: TrainPair already rejects it
            raise paths.QuarantineViolation(f"H1 row in training corpus: {r.item_id}")
        if r.item_id in seen_item_ids:
            dupes.append(r.item_id)
        seen_item_ids.add(r.item_id)
        split_of[r.program_group_id].add(r.split)
        if r.program_group_id != r.program_id:
            raise DataContractError(
                f"{r.item_id}: program_group_id {r.program_group_id!r} != program_id "
                f"{r.program_id!r} — the split unit must be the program"
            )

    if dupes:
        raise DataContractError(f"duplicate item_id(s): {sorted(set(dupes))[:5]} ...")

    leaked = sorted(pid for pid, s in split_of.items() if len(s) > 1)
    if leaked:
        raise DataContractError(
            f"{len(leaked)} program_id(s) appear in more than one split "
            f"(e.g. {leaked[:5]}). Splits partition by program_id — CLAUDE.md §4.1."
        )

    bad_gold = [r.item_id for r in rows if not check_output_repr(r.output_repr)]
    if bad_gold and strict_gold:
        raise DataContractError(
            f"{len(bad_gold)} row(s) whose output_repr is not canonical "
            f"(e.g. {bad_gold[:5]}); the grader and the labels disagree"
        )

    return CorpusReport(
        n_rows=len(rows),
        n_programs=len(split_of),
        by_condition=dict(Counter(r.condition for r in rows)),
        by_split=dict(Counter(r.split for r in rows)),
        bad_gold=bad_gold,
        leaked_programs=leaked,
    )


def assert_train_eval_disjoint(
    train_rows: Iterable[TrainPair], eval_items: Iterable[EvalItem]
) -> None:
    """No training program may also be a test program (contamination check #1)."""
    tr = {r.program_id for r in train_rows}
    ev = {i.program_id for i in eval_items}
    overlap = sorted(tr & ev)
    if overlap:
        raise DataContractError(
            f"{len(overlap)} program_id(s) present in BOTH train and eval "
            f"(e.g. {overlap[:5]}). This silently inflates every transfer cell."
        )


def validate_eval_items(items: Sequence[EvalItem], strict_gold: bool = True) -> CorpusReport:
    if not items:
        raise DataContractError("empty eval set")
    ids = [i.item_id for i in items]
    if len(set(ids)) != len(ids):
        d = [k for k, v in Counter(ids).items() if v > 1]
        raise DataContractError(f"duplicate eval item_id(s): {d[:5]}")
    prompts.assert_demo_disjoint(i.program_id for i in items)
    bad = [i.item_id for i in items if not check_output_repr(i.output_repr)]
    if bad and strict_gold:
        raise DataContractError(f"{len(bad)} eval row(s) with non-canonical output_repr: {bad[:5]}")
    return CorpusReport(
        n_rows=len(items),
        n_programs=len({i.program_id for i in items}),
        by_condition=dict(Counter(i.condition for i in items)),
        by_split={"test": len(items)},
        bad_gold=bad,
    )


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #

def stratified_subset(
    rows: Sequence[Any],
    n_per_cell: int,
    key_fn: Callable[[Any], Any],
    seed: int = GLOBAL_SEED,
) -> list[Any]:
    """Deterministic balanced subset: up to `n_per_cell` rows per `key_fn` cell.

    Used for the attention subset (RQ3) — attention extraction is ~100x slower per
    item than vLLM generation, so it runs on a stratified subset, and that subset must
    be balanced across (condition, language) or Δ-attention would be confounded with
    cell size. Output order is a seeded shuffle of the union, so any downstream
    truncation is still balanced in expectation.
    """
    if n_per_cell <= 0:
        raise ValueError("n_per_cell must be positive")
    buckets: dict[Any, list[Any]] = defaultdict(list)
    for r in rows:
        buckets[key_fn(r)].append(r)
    rng = random.Random(seed)
    out: list[Any] = []
    for key in sorted(buckets, key=repr):  # sorted: dict order must not leak into results
        bucket = list(buckets[key])
        rng.shuffle(bucket)
        out.extend(bucket[:n_per_cell])
    rng.shuffle(out)
    return out


def _balanced_take(rows: Sequence[TrainPair], n: int, seed: int) -> list[TrainPair]:
    """Take `n` rows, balanced across conditions, deterministically.

    A monolithic (multi-condition) run must not be dominated by whichever condition
    happened to produce more gate-passing variants; S1/S2 bail on some programs by
    design (CLAUDE.md §4 coverage honesty), so raw concatenation would be skewed.
    """
    if n >= len(rows):
        rng = random.Random(seed)
        out = list(rows)
        rng.shuffle(out)
        return out
    by_cond: dict[str, list[TrainPair]] = defaultdict(list)
    for r in rows:
        by_cond[r.condition].append(r)
    rng = random.Random(seed)
    for v in by_cond.values():
        rng.shuffle(v)
    conds = sorted(by_cond)
    out: list[TrainPair] = []
    idx = {c: 0 for c in conds}
    while len(out) < n:
        progressed = False
        for c in conds:
            if len(out) >= n:
                break
            i = idx[c]
            if i < len(by_cond[c]):
                out.append(by_cond[c][i])
                idx[c] = i + 1
                progressed = True
        if not progressed:
            break
    rng.shuffle(out)
    return out


# --------------------------------------------------------------------------- #
# SFT dataset
# --------------------------------------------------------------------------- #

def to_sft_records(
    rows: Sequence[TrainPair], oracle: bool = False, one_shot: bool = False,
    completions: Optional[Sequence[str]] = None,
) -> list[dict[str, Any]]:
    """`completions` (trace arm) supplies one assistant turn per row in order; None keeps
    the plain `output_repr` completion."""
    if completions is None:
        return [
            prompts.build_example(r.model_dump(), oracle=oracle, one_shot=one_shot) for r in rows
        ]
    if len(completions) != len(rows):
        raise DataContractError("completions must be parallel to rows")
    return [
        prompts.build_example(r.model_dump(), oracle=oracle, one_shot=one_shot, completion=c)
        for r, c in zip(rows, completions)
    ]


def _attach_trace_completions(
    rows: list[TrainPair], language: str, pcfg: Mapping[str, Any], seed: int
) -> tuple[list[TrainPair], list[str], dict[str, Any]]:
    """Trace arm: replace each row's completion with its execution trace (trace.py).

    Rows whose trace fails or whose traced answer disagrees with the gold are DROPPED,
    not kept with a plain completion — a mixed dataset would teach the model that the
    trace is optional. The drop counts land in meta so the size loss is visible next to
    n_train. Order is preserved, so the shuffle above still governs batch order.
    """
    from obtune import trace as _trace

    kept, report = _trace.attach_traces(
        rows, language, cfg=pcfg.get("trace_cfg"),
        workers=int(pcfg.get("trace_workers", 8)),
    )
    return [r for r, _ in kept], [c for _, c in kept], report


def build_sft_splits(config: Mapping[str, Any]) -> dict[str, Any]:
    """Materialize train/val `datasets.Dataset`s in TRL prompt-completion form.

    Config keys consumed: `language`, `train_conditions`, `train.{train_size, val_size,
    seed, l0_replay_fraction}`, and optionally `prompt.{oracle, one_shot}`.
    """
    from datasets import Dataset  # imported lazily: keeps `import obtune.data` cheap

    language = config["language"]
    train_conditions = list(config["train_conditions"])
    tcfg = config.get("train", {})
    seed = int(tcfg.get("seed", GLOBAL_SEED))
    train_size = int(tcfg.get("train_size") or 0) or None  # null = take everything
    val_size = int(tcfg.get("val_size", 0)) or None
    replay = float(tcfg.get("l0_replay_fraction", 0.0) or 0.0)
    pcfg = config.get("prompt", {}) or {}
    oracle = bool(pcfg.get("oracle", False))
    one_shot = bool(pcfg.get("one_shot", False))
    trace = bool(pcfg.get("trace", False))
    if trace and bool(tcfg.get("shuffle_labels", False)):
        raise DataContractError("prompt.trace and train.shuffle_labels are incompatible")

    augment_tags = [str(t) for t in (tcfg.get("augment_tags") or [])]
    rows = load_pairs(train_conditions, language,
                      allow_composites=bool(config.get('allow_composites', False)),
                      augment_tags=augment_tags)
    report = validate_pairs(rows)

    train_rows = [r for r in rows if r.split == "train"]
    val_rows = [r for r in rows if r.split == "val"]
    if not train_rows:
        raise DataContractError("no rows with split == 'train'")

    if replay > 0.0 and "L0" not in train_conditions:
        # L0 replay is the mitigation for in-domain forgetting (configs/train/_base_lora.yaml
        # raises it to 0.1 only if the pilot shows delta-L0 < -3 pts). Replay rows come
        # from the same train split, so no leakage is introduced.
        l0_rows = [r for r in load_pairs(["L0"], language) if r.split == "train"]
        n_replay = int(round(replay * len(train_rows)))
        train_rows = train_rows + _balanced_take(l0_rows, n_replay, seed + 1)

    if train_size:
        train_rows = _balanced_take(train_rows, train_size, seed)
    else:
        rng = random.Random(seed)
        rng.shuffle(train_rows)

    # FORMAT-ONLY ABLATION. `train.shuffle_labels` permutes `output_repr` ACROSS the training rows
    # THAT WERE ACTUALLY SELECTED (it runs after size-matching, so it is a strict permutation of
    # the arm's own answer multiset), leaving code, prompts, answer distribution and row count
    # untouched. The model
    # then sees perfectly well-formed answers that are uncorrelated with their input, so it can
    # learn the ANSWER FORMAT and the marginal distribution of answers, and nothing about the task.
    #
    # Why this arm exists: the project's central finding is that `tuned_L0` — an adapter trained on
    # 4,689 rows of CLEAN code — matches every obfuscation-trained system on the held-out
    # obfuscator. MASTER_REPORT §6 notes the untuned base fails the output format 17.3 % of the
    # time against 2-6 % for adapters, which raises an obvious alternative reading nobody has
    # tested: that "fine-tuning helps on obfuscated code" is substantially "fine-tuning teaches the
    # answer format". If a label-shuffled adapter recovers most of `tuned_L0`'s gain, that reading
    # is right and it reframes the headline. If it recovers little, the gain is real task
    # acquisition and the finding is safe from the objection.
    #
    # The VAL split is deliberately NOT shuffled: checkpoint selection then picks the checkpoint
    # with the best genuine accuracy, exactly as it does for every other arm. That is a small
    # asymmetry (this arm cannot improve on the task, so selection is closer to "least damaged"
    # than "best"), and it is recorded here rather than hidden.
    if bool(tcfg.get("shuffle_labels", False)):
        import random as _random
        _rng = _random.Random(seed)
        golds = [r.output_repr for r in train_rows]
        _rng.shuffle(golds)
        train_rows = [r.model_copy(update={"output_repr": g}) for r, g in zip(train_rows, golds)]

    if val_size and val_rows:
        val_rows = _balanced_take(val_rows, val_size, seed + 2)

    train_completions = val_completions = None
    trace_meta: dict[str, Any] = {}
    if trace:
        train_rows, train_completions, trace_meta["train"] = _attach_trace_completions(
            train_rows, language, pcfg, seed
        )
        if val_rows:
            val_rows, val_completions, trace_meta["val"] = _attach_trace_completions(
                val_rows, language, pcfg, seed
            )
        if not train_rows:
            raise DataContractError("trace arm: every training row was dropped")

    out = {
        "train": Dataset.from_list(
            to_sft_records(train_rows, oracle, one_shot, completions=train_completions)
        ),
        "meta": {
            "language": language,
            "train_conditions": train_conditions,
            "seed": seed,
            "n_train": len(train_rows),
            "n_val": len(val_rows),
            "n_train_programs": len({r.program_id for r in train_rows}),
            "augment_tags": augment_tags,
            "l0_replay_fraction": replay,
            "corpus": report.as_dict(),
            "trace": trace_meta if trace else None,
            **prompts.provenance_block(oracle=oracle, one_shot=one_shot, trace=trace),
        },
        "train_rows": train_rows,
        "val_rows": val_rows,
    }
    out["val"] = (
        Dataset.from_list(
            to_sft_records(val_rows, oracle, one_shot, completions=val_completions)
        )
        if val_rows else None
    )
    return out


def build_sft_dataset(config: Mapping[str, Any], split: str = "train") -> Any:
    """`datasets.Dataset` in prompt-completion form for `split` in {train, val}."""
    bundle = build_sft_splits(config)
    ds = bundle.get(split)
    if ds is None:
        raise DataContractError(f"no {split!r} dataset available for this config")
    return ds
