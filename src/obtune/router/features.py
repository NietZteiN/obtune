"""Frozen-base prompt features for the RQ2 router.

WHY frozen mid-layer mean-pooling: the router's job is to say *which obfuscation
condition this prompt is* so the right per-type adapter can be loaded. If the router
were trained end-to-end with the base model, RQ2 would no longer be comparing "per-type
adapters + a cheap dispatcher" against "one monolithic adapter" — the dispatcher would
itself be a tuned model and the parameter budgets would stop matching. Freezing the base
and reading one hidden state keeps the router's cost at ~1 MB of MLP weights.

Layer: `configs/models.yaml::router_layer` (mid depth, 14/28 on Qwen-Coder). Mid-depth
because obfuscation family is a syntactic/lexical property that is linearly decodable
well before the final layers, and the last layers are specialized for next-token
prediction of the *answer*, which is exactly the signal we do not want the router to key
on (it would leak the task instead of the transform).

Pooling: mean over real (non-pad, non-special) prompt tokens. Last-token pooling was
rejected: the prompt ends in the chat template's assistant header, which is byte-
identical across all conditions, so the last position is the one place where the
condition signal is weakest.

H1 IS NEVER A CLASS. H1 prompts may be featurized (its routing-entropy distribution is a
reported RQ2 result) but they are written with label -1 and `train_router.py` refuses to
train on them.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

from obtune.config import RUNS_DIR, load_config
from obtune.paths import TRAINABLE_CONDITIONS, iter_jsonl, load_training_jsonl
from obtune.seedutil import set_seed

__all__ = ["FeatureSet", "CONDITION_TO_LABEL", "LABEL_TO_CONDITION",
           "extract_features", "save_features", "load_features"]

# Class index order is frozen here so a router trained today can be scored tomorrow.
CONDITION_TO_LABEL: dict[str, int] = {c: i for i, c in enumerate(TRAINABLE_CONDITIONS)}
LABEL_TO_CONDITION: dict[int, str] = {i: c for c, i in CONDITION_TO_LABEL.items()}
H1_LABEL = -1

FEATURE_DIR = RUNS_DIR / "router" / "features"


@dataclass
class FeatureSet:
    X: np.ndarray  # [N, hidden] float32
    y: np.ndarray  # [N] int16 (-1 for H1)
    item_ids: np.ndarray
    program_ids: np.ndarray
    conditions: np.ndarray
    languages: np.ndarray
    meta: dict[str, Any]

    def __len__(self) -> int:
        return int(self.X.shape[0])

    def trainable_mask(self) -> np.ndarray:
        return self.y >= 0

    def subset(self, mask: np.ndarray) -> "FeatureSet":
        return FeatureSet(
            X=self.X[mask], y=self.y[mask], item_ids=self.item_ids[mask],
            program_ids=self.program_ids[mask], conditions=self.conditions[mask],
            languages=self.languages[mask], meta=dict(self.meta),
        )


def save_features(fs: FeatureSet, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        p, X=fs.X.astype(np.float32), y=fs.y.astype(np.int16),
        item_ids=fs.item_ids, program_ids=fs.program_ids,
        conditions=fs.conditions, languages=fs.languages,
        meta_json=np.array(json.dumps(fs.meta), dtype=object),
    )
    return p


def load_features(path: str | Path) -> FeatureSet:
    z = np.load(path, allow_pickle=True)
    return FeatureSet(
        X=z["X"], y=z["y"], item_ids=z["item_ids"], program_ids=z["program_ids"],
        conditions=z["conditions"], languages=z["languages"],
        meta=json.loads(str(z["meta_json"].item())),
    )


def _prompt_texts(tokenizer, rows: Sequence[dict[str, Any]]) -> list[str]:
    """Render prompts through the project's ONE prompt builder.

    ASSUMED INTERFACE (peer-owned `obtune.prompts`):
        build_prompt(code, entry_point, args_repr, language, condition, oracle=False)
            -> list[{"role": str, "content": str}]
    Falling back to a local template would make the router features incomparable with the
    eval distribution (CLAUDE.md §4 silent-failure #3), so the fallback is loud.
    """
    try:
        from obtune.prompts import build_prompt
    except Exception as exc:  # pragma: no cover - exercised only before prompts.py lands
        raise RuntimeError(
            "obtune.prompts.build_prompt is required so router features are computed on "
            f"the same prompt distribution as training/eval; import failed: {exc}"
        ) from exc
    texts = []
    for r in rows:
        msgs = build_prompt(code=r["code"], entry_point=r["entry_point"],
                            args_repr=r.get("args_repr", "()"), language=r["language"],
                            condition=r["condition"], oracle=False)
        texts.append(tokenizer.apply_chat_template(msgs, tokenize=False,
                                                   add_generation_prompt=True))
    return texts


def extract_features(
    rows: Sequence[dict[str, Any]],
    *,
    model_key: str = "qwen25c-1.5b",
    layer: Optional[int] = None,
    batch_size: int = 32,
    max_length: int = 1536,
    seed: int = 17,
    device: Optional[str] = None,
) -> FeatureSet:
    """Mean-pooled hidden states at `layer` for every row. GPU strongly preferred."""
    import torch
    from transformers import AutoModel, AutoTokenizer

    models_cfg = load_config("models.yaml")["models"]
    mcfg = models_cfg[model_key]
    if layer is None:
        layer = int(mcfg["router_layer"])
    set_seed(seed)

    tok = AutoTokenizer.from_pretrained(mcfg["hf_id"])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    # AutoModel, NOT AutoModelForCausalLM: we only ever read `hidden_states`, but the
    # causal-LM head still computes [batch, seq, vocab] logits — 32 x 1536 x 151936 in
    # bf16 is ~14 GB of pure waste, and it OOM'd the 1.5B feature job on a 48 GB card.
    # Dropping the head also frees its ~0.6 GB of weights. Hidden-state indexing is
    # unchanged: index 0 is still the embedding output.
    model = AutoModel.from_pretrained(
        mcfg["hf_id"], dtype=torch.bfloat16, attn_implementation="sdpa")
    model.eval()
    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model.to(dev)

    texts = _prompt_texts(tok, rows)
    feats = np.zeros((len(rows), int(mcfg["hidden_size"])), dtype=np.float32)
    special = set(tok.all_special_ids)

    for i in range(0, len(texts), batch_size):
        chunk = texts[i:i + batch_size]
        enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                  max_length=max_length, add_special_tokens=False)
        enc = {k: v.to(dev) for k, v in enc.items()}
        with torch.no_grad():
            out = model(**enc, output_hidden_states=True, use_cache=False, return_dict=True)
        h = out.hidden_states[layer]  # [B, T, D]; index 0 is the embedding output
        mask = enc["attention_mask"].bool()
        if special:
            ids = enc["input_ids"]
            sp = torch.zeros_like(mask)
            for s in special:
                sp |= ids == s
            mask = mask & ~sp
        m = mask.unsqueeze(-1).to(h.dtype)
        pooled = (h * m).sum(dim=1) / m.sum(dim=1).clamp(min=1.0)
        feats[i:i + len(chunk)] = pooled.float().cpu().numpy()

    y = np.array([CONDITION_TO_LABEL.get(r["condition"], H1_LABEL) for r in rows], dtype=np.int16)
    return FeatureSet(
        X=feats, y=y,
        item_ids=np.array([r["item_id"] for r in rows]),
        program_ids=np.array([r.get("program_group_id", r["program_id"]) for r in rows]),
        conditions=np.array([r["condition"] for r in rows]),
        languages=np.array([r["language"] for r in rows]),
        meta={"model_key": model_key, "hf_id": mcfg["hf_id"], "layer": int(layer),
              "pooling": "mean_nonspecial", "seed": seed, "max_length": max_length,
              "hidden_size": int(mcfg["hidden_size"]),
              "class_order": list(TRAINABLE_CONDITIONS)},
    )


def _read_rows(paths: Iterable[str | Path], *, allow_h1: bool) -> list[dict[str, Any]]:
    """Training rows go through paths.load_training_jsonl (the quarantine entry point).

    H1 prompts are read ONLY through the explicit `--h1` flag and only ever end up with
    label -1, so they can never become a router class.
    """
    rows: list[dict[str, Any]] = []
    for p in paths:
        rows.extend(iter_jsonl(p) if allow_h1 else load_training_jsonl(p))
    return rows


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Cache frozen-base router features")
    ap.add_argument("--config", default="router/router_v1.yaml")
    # No default: a forgotten --model must fail loudly, not silently run the wrong base.
    ap.add_argument("--model", required=True, help="key in configs/models.yaml")
    ap.add_argument("--train-jsonl", nargs="*", default=[],
                    help="data/train/pairs/<cond>/<lang>.jsonl (quarantine-guarded read)")
    ap.add_argument("--h1-jsonl", nargs="*", default=[],
                    help="H1 eval rows for the routing-entropy report; labelled -1, never trained on")
    # Routing happens on EVAL items, but the only non-training read used to be the H1
    # flag -- so the emitted job had no way to featurize the items it needed to route,
    # and the router's train set and route set were silently the same rows. Eval rows are
    # labelled from `condition` exactly as training rows are (H1 still falls to -1), so
    # `correct_route` stays meaningful; they are simply never passed to train_router.
    ap.add_argument("--eval-jsonl", nargs="*", default=[],
                    help="eval items to be ROUTED (data/eval/<src>/items/<cond>/<lang>.jsonl)")
    ap.add_argument("--out", default=str(FEATURE_DIR / "router_features.npz"))
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    rows = _read_rows(args.train_jsonl, allow_h1=False)
    n_train = len(rows)
    rows += _read_rows(list(args.eval_jsonl) + list(args.h1_jsonl), allow_h1=True)
    if not rows:
        raise SystemExit("no rows: pass --train-jsonl, --eval-jsonl and/or --h1-jsonl")

    fs = extract_features(
        rows, model_key=args.model,
        layer=cfg["features"].get("layer"),
        batch_size=int(cfg["features"].get("batch_size", 32)),
        seed=int(cfg["train"].get("seed", 17)),
    )
    p = save_features(fs, args.out)
    print(f"wrote {p}  X={fs.X.shape} trainable={int(fs.trainable_mask().sum())}/{len(fs)} "
          f"(from {n_train} trainable rows + {len(rows) - n_train} H1 report rows), "
          f"layer={fs.meta['layer']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
