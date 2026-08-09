"""Four-axis budget accounting — the number that decides how Experiment 1 is read.

The source paper compares its contrastive objective against forward-only fine-tuning
without ever stating what is held constant, and "same data budget" turns out not to be
one quantity. Four of them move independently here:

  `instances`         rows in the mixture — what "10 000 each" (§5.0.2) counts
  `supervised_tokens` tokens the loss is actually computed on (`completion_only_loss`)
  `sequence_tokens`   prompt + completion — proportional to FLOPs and wall-clock
  `steps`             optimizer steps at the configured effective batch

They diverge because the three task formats have wildly different shapes. A `gen` target
is a whole obfuscated program (~197 supervised tokens); a `pos`/`neg` target is the single
token YES or NO (3 with the template) — yet its *prompt* carries two whole programs, so it
costs a full `gen`-sized forward/backward pass. A `rev` example is the same two programs
with the roles swapped, so it costs exactly what its `gen` twin costs while supervising
the shorter of the two.

The consequence, measured on the Python corpus with the Qwen2.5-Coder tokenizer:

    arm      instances  supervised tok  sequence tok  steps
    FWD        1.00x        1.00x          1.00x      1.00x
    REV        1.00x        0.52x          1.00x      1.00x
    FLIP       2.00x        1.52x          2.00x      2.00x
    MIX50      1.00x        0.76x          1.00x      1.00x
    CFT        2.52x        1.02x          2.60x      2.53x

**CFT already costs more than FLIP on every axis a practitioner pays for, while adding
almost no supervised signal.** So the honest frame is not budget-matching but dominance:
if FLIP beats CFT on the reverse direction, no budget account rescues CFT. And MIX50 —
matched to FWD on instances, sequence tokens and steps simultaneously, with strictly less
supervision — is what turns "FLIP had more data" from an objection into a measurement.

Every arm publishes its realised row here before training starts, so the comparison is
made against recorded numbers rather than against an assumption.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from obtune.cft import train as cft_train
from obtune.cft.dataset import CFTInstance

AXES = ("instances", "supervised_tokens", "sequence_tokens", "steps")


def budget_row(
    rows: Sequence[CFTInstance],
    tokenizer: Any,
    max_seq_len: int,
    effective_batch: int,
    epochs: float = 1.0,
    build_example: Optional[Any] = None,
) -> dict[str, Any]:
    """The four axes for one arm, plus the per-task detail that explains them.

    Measured on the LENGTH-FILTERED mixture — the rows that will actually be trained on —
    because a dropped overlong example costs nothing and must not be counted.
    """
    keep, stats = cft_train.measure_lengths(rows, tokenizer, max_seq_len, build_example)
    kept = [rows[i] for i in keep]

    examples = [(build_example or _default_builder())(r.model_dump()) for r in kept]
    full_texts = [
        tokenizer.apply_chat_template(list(e["prompt"]) + list(e["completion"]), tokenize=False)
        for e in examples
    ]
    seq_tokens = sum(
        len(x) for x in tokenizer(full_texts, add_special_tokens=False)["input_ids"]
    )
    supervised = sum(stats["supervised_tokens_by_task"].values())
    n = len(kept)
    steps = int(round(epochs * n / max(1, effective_batch)))

    # All four axes are TOTALS OVER TRAINING, i.e. multiplied by epochs. Mixing
    # conventions — per-epoch tokens against total steps — makes `fwd2x` read as using
    # FWD's compute when matching FLIP's compute is the arm's entire purpose.
    return {
        "instances": int(round(n * epochs)),
        "supervised_tokens": int(round(supervised * epochs)),
        "sequence_tokens": int(round(seq_tokens * epochs)),
        "steps": steps,
        "epochs": epochs,
        "instances_per_epoch": n,
        "supervised_tokens_per_epoch": supervised,
        "sequence_tokens_per_epoch": seq_tokens,
        "effective_batch": effective_batch,
        "by_task": stats["kept_by_task"],
        "supervised_tokens_by_task": stats["supervised_tokens_by_task"],
        "task_token_share": stats["task_token_share"],
        "mean_supervised_tokens_by_task": stats["mean_supervised_tokens_by_task"],
        "n_dropped": stats["n_dropped"],
        "drop_rate": stats["drop_rate"],
        "len_p95": stats["len_p95"],
        "len_max": stats["len_max"],
    }


def _default_builder():
    from obtune.cft import prompts as cft_prompts

    return cft_prompts.build_example


def budget_table(
    arms: Mapping[str, Sequence[CFTInstance]],
    tokenizer: Any,
    max_seq_len: int,
    effective_batch: int,
    epochs: Mapping[str, float] | float = 1.0,
    baseline: str = "fwd",
    build_example: Optional[Any] = None,
) -> dict[str, Any]:
    """Budget rows for several arms plus their ratios against `baseline`.

    The ratio block is the deliverable: absolute token counts are corpus-specific, but
    "CFT costs 2.60x FWD's compute for 1.02x its supervised signal" is the claim, and it
    should be readable straight off the table without arithmetic.
    """
    rows: dict[str, Any] = {}
    for name, mixture in arms.items():
        ep = epochs.get(name, 1.0) if isinstance(epochs, Mapping) else float(epochs)
        rows[name] = budget_row(
            mixture, tokenizer, max_seq_len, effective_batch, ep, build_example
        )

    ratios: dict[str, Any] = {}
    if baseline in rows:
        base = rows[baseline]
        for name, row in rows.items():
            ratios[name] = {
                axis: (row[axis] / base[axis] if base[axis] else None) for axis in AXES
            }
    return {"baseline": baseline, "arms": rows, "ratios_vs_baseline": ratios}


def format_table(table: Mapping[str, Any]) -> str:
    """Render `budget_table` as the markdown block that goes in the log entry."""
    base = table.get("baseline", "fwd")
    lines = [
        f"| arm | instances | supervised tok | sequence tok (FLOPs) | steps |",
        "|---|---|---|---|---|",
    ]
    for name, r in table["arms"].items():
        ratio = table["ratios_vs_baseline"].get(name, {})
        def cell(axis: str) -> str:
            v = ratio.get(axis)
            return f"{r[axis]:,} ({v:.2f}x)" if v is not None else f"{r[axis]:,}"
        lines.append(
            f"| {name} | {cell('instances')} | {cell('supervised_tokens')} "
            f"| {cell('sequence_tokens')} | {cell('steps')} |"
        )
    lines.append("")
    lines.append(f"*Ratios are against `{base}`. Measured on the length-filtered mixture.*")
    return "\n".join(lines)
