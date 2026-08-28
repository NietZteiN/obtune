"""RQ3 attention metrics: class mass, entropy, and the anchoring shift.

WHY these particular numbers
---------------------------
RQ3 asks *where* obfuscation-tuning moves a model's attention. The naive metric —
"fraction of attention on identifier tokens" over the whole prompt — is dominated by
two things that have nothing to do with the code: the BOS/first-token attention sink
(routinely 20-60% of the mass in a decoder-only LM) and the instruction boilerplate,
which is byte-identical across every condition. Both would swamp a real per-condition
effect and would make the metric depend on prompt length rather than on the program.

PRE-REGISTERED METRIC DECISIONS (do not change without a design-doc update):

  D1. Query rows: the LAST prompt token only. That is the position from which the first
      answer token is produced, so it is the only row whose attention is causally on the
      path to the prediction. Averaging over all query rows would mix in the model's
      own left-to-right encoding of the code.
  D2. Key columns: restricted to the CODE-TOKEN REGION and RENORMALIZED over it, i.e.
      mass_c = sum_{k in class c} a_k / sum_{k in code} a_k. The denominator makes the
      six masses a proper probability decomposition of *attention within the program*.
      `attn_to_code` (the un-renormalized share of the full row that reaches the code)
      is reported alongside so the renormalization is auditable, never hidden.
  D3. Heads: mean over heads within a layer. Per-head analysis is a follow-up; the
      pre-registered unit is the layer.
  D4. Entropy is computed on the SAME renormalized code distribution, and reported raw
      (nats) and normalized by log(n_code_tokens) so programs of different length are
      comparable.

anchoring_shift(post, pre) = D[mass_control_kw + mass_dataflow_critical]
                             - D[mass_identifier]
with D[x] = x_post - x_pre and `mass_identifier` counting only OFF-slice identifiers
(the decoy surface). Positive = tuning moved attention from name surface onto control
structure and the def-use closure of the return value. The two halves are disjoint by
construction (see token_classes) so the difference is not double-counting.

Output: results/attn/attention_metrics.parquet
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

from obtune.attention.token_classes import CLASSES, Classification, classify_code
from obtune.config import RESULTS_DIR

__all__ = [
    "AttentionRecord", "save_attention_npz", "load_attention_npz",
    "resolve_spans_to_tokens", "token_class_assignment", "metrics_for_record",
    "metrics_table", "anchoring_shift", "ATTN_DIR",
]

ATTN_DIR = RESULTS_DIR / "attn"

# Ties in token->class assignment resolve in this order. dataflow_critical wins so a
# subword shared between a sliced name and a delimiter counts toward the slice; `other`
# loses everything, so a token that touches any real code character is never `other`.
_CLASS_PRIORITY = ("dataflow_critical", "identifier", "control_kw", "literal", "operator", "other")


@dataclass
class AttentionRecord:
    """One saved forward pass. This dataclass IS the npz contract.

    `attn` is [n_saved_layers, n_heads, K]: the attention row of the LAST prompt query
    token, per layer, per head. Saving only that row keeps a 1.5k-token prompt at ~5 MB
    instead of ~7 GB, which is what makes a 3-model x 7-condition x 70-item sweep
    storable at all.
    """

    attn: np.ndarray
    layers: np.ndarray
    offsets: np.ndarray  # [T,2] char offsets into `text`
    code_char_start: int
    code_char_end: int
    text: str
    code: str
    language: str
    entry_point: Optional[str]
    item_id: str
    program_id: str
    condition: str
    base_model: str
    model_state: str  # "pre" | "post" | adapter identifier
    adapter_id: Optional[str] = None
    seed: int = 17
    run_id: str = ""
    span_resolution_rate: float = float("nan")
    extra: dict[str, Any] = field(default_factory=dict)

    def meta(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("attn", "layers", "offsets"):
            d.pop(k)
        return d


def save_attention_npz(rec: AttentionRecord, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        p,
        attn=np.asarray(rec.attn, dtype=np.float32),
        layers=np.asarray(rec.layers, dtype=np.int32),
        offsets=np.asarray(rec.offsets, dtype=np.int32),
        meta_json=np.array(json.dumps(rec.meta()), dtype=object),
    )
    return p


def load_attention_npz(path: str | Path) -> AttentionRecord:
    """Read a dump written by `eval_hf.py --mode attn`, the documented on-disk contract.

    TWO FORMATS EXIST AND THIS READS BOTH. `results/attn/SCHEMA.md` specifies the one the
    capture path actually writes: an npz of `rows / layers / token_offsets / code_span /
    input_ids` beside a `.json` sidecar carrying the metadata. `save_attention_npz` above
    writes a DIFFERENT, older layout (`attn / layers / offsets / meta_json`) that no
    writer in the project emits.

    Until 2026-08-17 this function only understood the second one, so `metrics_table`,
    `anchoring_shift` and the `metrics.py` CLI raised `KeyError: meta_json` on the first
    real dump they were handed. Nothing caught it because no one had run the analysis end
    to end on captured data. The legacy branch is kept so any old dump still loads.
    """
    p = Path(path)
    z = np.load(p, allow_pickle=True)
    if "meta_json" in z.files:                      # legacy save_attention_npz layout
        meta = json.loads(str(z["meta_json"].item()))
        return AttentionRecord(attn=z["attn"], layers=z["layers"], offsets=z["offsets"], **meta)

    side = p.with_suffix(".json")
    if not side.exists():
        raise FileNotFoundError(
            f"{p.name} is in the SCHEMA.md layout but its .json sidecar is missing; the "
            "metadata (prompt_text, condition, item_id ...) lives there, not in the npz"
        )
    m = json.loads(side.read_text())
    cs, ce = (int(x) for x in np.asarray(z["code_span"]).reshape(2))
    text = m["prompt_text"]
    return AttentionRecord(
        attn=np.asarray(z["rows"]),
        layers=np.asarray(z["layers"]),
        offsets=np.asarray(z["token_offsets"]),
        code_char_start=cs,
        code_char_end=ce,
        text=text,
        # `code` is not stored separately; that is precisely what `code_span` is for, and
        # recovering it here keeps the two provably consistent.
        code=text[cs:ce],
        language=m["language"],
        entry_point=m.get("entry_point"),
        item_id=m["item_id"],
        program_id=m["program_id"],
        condition=m["condition"],
        base_model=m["base_model"],
        # SCHEMA.md calls this `system` (base | tuned_S2 | ...); AttentionRecord calls the
        # same thing `model_state`. One concept, two names, mapped in one place.
        model_state=m.get("system", "base"),
        adapter_id=m.get("adapter"),
        seed=int(m.get("seed", 17)),
        extra={k: m[k] for k in ("prompt_id", "prompt_sha") if k in m},
    )


# ---------------------------------------------------------------------------
# char-span -> token-index resolution
# ---------------------------------------------------------------------------
def resolve_spans_to_tokens(
    spans: Sequence[tuple[int, int]],
    offsets: Sequence[tuple[int, int]],
    *,
    char_base: int = 0,
    tokenizer: Any = None,
    input_ids: Optional[Sequence[int]] = None,
    code: Optional[str] = None,
) -> tuple[list[int], int, int]:
    """Map character spans (into `code`) onto token indices via offset overlap.

    Ported from transcoders/src/extract_activations.resolve_spans_to_positions, which
    was validated at rate 1.0 on the same stimuli. `char_base` shifts code-relative
    spans into prompt-relative offsets. When a tokenizer + input_ids + code are supplied
    the decode check is applied: the concatenated decode of the hit tokens must contain
    the span text. That check is what catches BOS shifts and off-by-one offset bugs that
    a pure range filter silently passes.

    Returns (sorted unique token indices, n_spans_resolved, n_spans_total).
    """
    positions: list[int] = []
    resolved = 0
    for a, b in spans:
        a2, b2 = a + char_base, b + char_base
        hit = [i for i, (s, e) in enumerate(offsets) if e > s and s < b2 and e > a2]
        if not hit:
            continue
        if tokenizer is not None and input_ids is not None and code is not None:
            text = tokenizer.decode([int(input_ids[i]) for i in hit])
            if code[a:b] not in text:
                continue
        positions.extend(hit)
        resolved += 1
    return sorted(set(positions)), resolved, len(spans)


def token_class_assignment(
    cls: Classification,
    offsets: Sequence[tuple[int, int]],
    code_char_start: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Assign every token a partition class by maximal character overlap.

    Returns (token_class[T] as an index into CLASSES, code_mask[T] bool). Subword
    tokenizers routinely merge `):` or ` return` into one token, so a majority-overlap
    rule with an explicit tie-break (see _CLASS_PRIORITY) is required; the reference
    implementation's ">50% of characters" rule leaves such tokens unassigned.
    """
    char_cls = cls.char_classes()
    n_code = len(cls.code)
    T = len(offsets)
    tok_cls = np.full(T, CLASSES.index("other"), dtype=np.int8)
    code_mask = np.zeros(T, dtype=bool)
    prio = {c: i for i, c in enumerate(_CLASS_PRIORITY)}

    for i, (s, e) in enumerate(offsets):
        if e <= s:
            continue  # (0,0) special tokens
        a = max(s - code_char_start, 0)
        b = min(e - code_char_start, n_code)
        if b <= a:
            continue
        code_mask[i] = True
        overlap: dict[str, int] = {}
        for j in range(a, b):
            c = char_cls[j]
            overlap[c] = overlap.get(c, 0) + 1
        best = max(overlap.items(), key=lambda kv: (kv[1], -prio[kv[0]]))[0]
        tok_cls[i] = CLASSES.index(best)
    return tok_cls, code_mask


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------
def metrics_for_record(
    rec: AttentionRecord,
    *,
    classification: Optional[Classification] = None,
) -> list[dict[str, Any]]:
    """One row per (model_state, item, condition, layer)."""
    cls = classification or classify_code(rec.code, rec.language, rec.entry_point)
    offsets = [(int(a), int(b)) for a, b in np.asarray(rec.offsets).tolist()]
    tok_cls, code_mask = token_class_assignment(cls, offsets, rec.code_char_start)

    n_code = int(code_mask.sum())
    # span_resolution_rate: fraction of classified non-`other` spans that reach >=1 token.
    real_spans = [(s.start, s.end) for s in cls.spans if s.base_cls != "other"]
    _, n_res, n_tot = resolve_spans_to_tokens(real_spans, offsets, char_base=rec.code_char_start)
    span_rate = (n_res / n_tot) if n_tot else float("nan")
    if not math.isnan(rec.span_resolution_rate):
        span_rate = float(rec.span_resolution_rate)  # capture-time value (decode-checked) wins

    A = np.asarray(rec.attn, dtype=np.float64)
    if A.ndim == 4:  # [L,H,Q,K] handed straight from output_attentions
        A = A[:, :, -1, :]
    if A.ndim == 2:  # [L,K] already head-averaged
        A = A[:, None, :]
    n_layers, _, K = A.shape
    if K != len(offsets):
        raise ValueError(f"attention K={K} != n_tokens={len(offsets)} for {rec.item_id}")

    idx_ident = CLASSES.index("identifier")
    idx_slice = CLASSES.index("dataflow_critical")
    rows: list[dict[str, Any]] = []
    for li in range(n_layers):
        a = A[li].mean(axis=0)  # D3: mean over heads
        total = float(a.sum())
        code_sum = float(a[code_mask].sum())
        if n_code == 0 or code_sum <= 0:
            masses = {c: float("nan") for c in CLASSES}
            ent = ent_norm = float("nan")
        else:
            p = np.where(code_mask, a, 0.0) / code_sum  # D2: renormalize over the code region
            masses = {c: float(p[tok_cls == CLASSES.index(c)].sum()) for c in CLASSES}
            pos = p[p > 0]
            ent = float(-(pos * np.log(pos)).sum())
            ent_norm = ent / math.log(n_code) if n_code > 1 else float("nan")
        rows.append({
            "run_id": rec.run_id,
            "seed": rec.seed,
            "base_model": rec.base_model,
            "model_state": rec.model_state,
            "adapter_id": rec.adapter_id,
            "item_id": rec.item_id,
            "program_id": rec.program_id,
            "condition": rec.condition,
            "language": rec.language,
            "entry_point": rec.entry_point,
            "layer": int(rec.layers[li]),
            "head_agg": "mean",
            "mass_identifier": masses["identifier"],
            "mass_identifier_incl_slice": (
                masses["identifier"] + masses["dataflow_critical"]
                if not math.isnan(masses["identifier"]) else float("nan")
            ),
            "mass_control_kw": masses["control_kw"],
            "mass_operator": masses["operator"],
            "mass_literal": masses["literal"],
            "mass_dataflow_critical": masses["dataflow_critical"],
            "mass_other": masses["other"],
            "attn_to_code": (code_sum / total) if total > 0 else float("nan"),
            "entropy": ent,
            "entropy_norm": ent_norm,
            "n_code_tokens": n_code,
            "n_prompt_tokens": len(offsets),
            "n_slice_tokens": int((tok_cls == idx_slice).sum()),
            "n_identifier_tokens": int((tok_cls == idx_ident).sum()),
            "span_resolution_rate": span_rate,
            "class_coverage": cls.coverage(),
            "partition_ok": bool(cls.partition_ok()),
            "parse_ok": bool(cls.parse_ok),
        })
    return rows


def metrics_table(npz_paths: Iterable[str | Path]) -> "Any":
    """pandas.DataFrame of every metric row across a directory of saved records."""
    import pandas as pd

    rows: list[dict[str, Any]] = []
    for p in npz_paths:
        rows.extend(metrics_for_record(load_attention_npz(p)))
    return pd.DataFrame(rows)


_KEY = ["base_model", "item_id", "program_id", "condition", "language", "layer"]


def anchoring_shift(df: "Any", post: str = "post", pre: str = "pre") -> "Any":
    """anchoring_shift = D[control + dataflow] - D[identifier], per item/condition/layer.

    `post`/`pre` name values of the `model_state` column. Only cells present in BOTH
    states are returned — a one-sided cell would otherwise contribute a spurious shift.
    """
    import pandas as pd

    a = df[df["model_state"] == post].set_index(_KEY)
    b = df[df["model_state"] == pre].set_index(_KEY)
    common = a.index.intersection(b.index)
    a, b = a.loc[common], b.loc[common]
    out = pd.DataFrame(index=common).reset_index()
    out["d_control_kw"] = (a["mass_control_kw"] - b["mass_control_kw"]).to_numpy()
    out["d_dataflow_critical"] = (a["mass_dataflow_critical"] - b["mass_dataflow_critical"]).to_numpy()
    out["d_identifier"] = (a["mass_identifier"] - b["mass_identifier"]).to_numpy()
    out["d_entropy_norm"] = (a["entropy_norm"] - b["entropy_norm"]).to_numpy()
    out["anchoring_shift"] = (
        out["d_control_kw"] + out["d_dataflow_critical"] - out["d_identifier"]
    )
    out["model_state_post"] = post
    out["model_state_pre"] = pre
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build results/attn/attention_metrics.parquet")
    ap.add_argument("--npz-dir", default=str(ATTN_DIR / "records"),
                    help="directory of *.npz saved by attention.capture")
    ap.add_argument("--out", default=str(ATTN_DIR / "attention_metrics.parquet"))
    ap.add_argument("--shift-out", default=str(ATTN_DIR / "anchoring_shift.parquet"))
    ap.add_argument("--post", default="post")
    ap.add_argument("--pre", default="pre")
    args = ap.parse_args(argv)

    paths = sorted(Path(args.npz_dir).glob("*.npz"))
    if not paths:
        raise SystemExit(f"no .npz records under {args.npz_dir}")
    df = metrics_table(paths)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"wrote {out}  ({len(df)} rows, {df['item_id'].nunique()} items, "
          f"{df['layer'].nunique()} layers)")

    if {args.pre, args.post} <= set(df["model_state"].unique()):
        sh = anchoring_shift(df, post=args.post, pre=args.pre)
        sh.to_parquet(args.shift_out, index=False)
        print(f"wrote {args.shift_out}  ({len(sh)} paired cells, "
              f"mean anchoring_shift={sh['anchoring_shift'].mean():+.4f})")
    else:
        print(f"model_state values {sorted(df['model_state'].unique())} do not contain "
              f"both {args.pre!r} and {args.post!r}; anchoring shift not computed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
