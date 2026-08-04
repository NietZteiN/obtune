"""RQ3 stretch intervention: causally knock out attention to identifier-class keys.

The mass/entropy metrics in metrics.py are CORRELATIONAL — they say attention moved,
not that the movement mattered. The knockout closes that gap: suppress the model's
ability to attend to identifier-surface tokens at a chosen layer set and measure the
accuracy drop. If obfuscation-tuning really re-anchors the model off name surface, the
tuned model should lose LESS accuracy under identifier knockout than the untuned one
(interaction: knockout x tuning), which is a directional prediction the mass metric
alone cannot make.

Mechanism — additive attention bias, not head ablation:
    logits[b, h, q, k] += BIAS   for k in the knocked-out key set
with BIAS a large negative number (default -1e4 in the mask dtype). This is the PASTA /
attention-steering construction reused from reallocation/src/attention_editing.py's
post-hoc log-bias wrapper, reduced to the one case we need. It is applied by rewriting
the 4-D float `attention_mask` in a `forward_pre_hook` on each target `self_attn` module,
so it composes with the causal mask, needs no re-implementation of the attention kernel,
and works under SDPA (which accepts an additive float mask) as well as eager.

Rejected alternatives:
  * Zeroing the post-softmax probabilities and renormalizing — requires wrapping the
    kernel itself and silently changes the value-vector mixture in a way that is not a
    valid attention distribution under SDPA/flash.
  * Deleting the identifier tokens from the input — changes position ids, sequence
    length and the causal structure, so any accuracy drop is unattributable.
  * Scaling Q/K projections — affects every query/key pair, not the identifier columns.

This module is written against the HF path and is NOT run here (it needs a free GPU).
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence

import numpy as np

from obtune.attention.metrics import token_class_assignment
from obtune.attention.token_classes import CLASSES, classify_code

__all__ = ["KnockoutSpec", "identifier_key_mask", "attention_knockout", "layer_set"]

DEFAULT_BIAS = -1e4


@dataclass(frozen=True)
class KnockoutSpec:
    """What to suppress, where, and how hard."""

    layers: tuple[int, ...]
    classes: tuple[str, ...] = ("identifier",)
    bias: float = DEFAULT_BIAS
    heads: Optional[tuple[int, ...]] = None  # None => all heads
    include_slice: bool = False  # also suppress dataflow_critical identifier keys

    def validate(self) -> "KnockoutSpec":
        bad = [c for c in self.classes if c not in CLASSES]
        if bad:
            raise ValueError(f"unknown token classes: {bad}")
        return self


def layer_set(n_layers: int, spec: int | Sequence[int] | str) -> tuple[int, ...]:
    """Resolve a layer specification. Negative indices count from the end.

    `"early"`/`"mid"`/`"late"` select the first/middle/last third — the pre-registered
    depth bands, so a result cannot be produced by fishing over 28 individual layers.
    """
    if isinstance(spec, str):
        third = max(1, n_layers // 3)
        return {
            "early": tuple(range(0, third)),
            "mid": tuple(range(third, 2 * third)),
            "late": tuple(range(2 * third, n_layers)),
            "all": tuple(range(n_layers)),
        }[spec]
    idxs = [spec] if isinstance(spec, int) else list(spec)
    return tuple(sorted({i if i >= 0 else n_layers + i for i in idxs
                         if -n_layers <= i < n_layers}))


def identifier_key_mask(
    code: str,
    language: str,
    entry_point: Optional[str],
    offsets: Sequence[tuple[int, int]],
    code_char_start: int,
    *,
    classes: Iterable[str] = ("identifier",),
    include_slice: bool = False,
) -> np.ndarray:
    """Boolean [T] mask of key positions to suppress.

    Only tokens inside the code region can be masked: knocking out the instruction
    boilerplate would confound the intervention with a prompt-comprehension effect.
    """
    cls = classify_code(code, language, entry_point)
    tok_cls, code_mask = token_class_assignment(cls, offsets, code_char_start)
    wanted = set(classes)
    if include_slice:
        wanted.add("dataflow_critical")
    idxs = {CLASSES.index(c) for c in wanted}
    return np.array([code_mask[i] and int(tok_cls[i]) in idxs for i in range(len(offsets))])


def _attn_modules(model) -> list[Any]:
    """Per-layer self-attention modules, unwrapping a PEFT wrapper if present."""
    core = getattr(model, "base_model", model)
    core = getattr(core, "model", core)
    while hasattr(core, "model") and not hasattr(core, "layers"):
        core = core.model
    if not hasattr(core, "layers"):
        raise RuntimeError(f"cannot locate decoder layers on {type(model).__name__}")
    return [layer.self_attn for layer in core.layers]


@contextmanager
def attention_knockout(model, key_mask: "np.ndarray | Any", spec: KnockoutSpec):
    """Additively suppress `key_mask` columns at `spec.layers` for the duration.

    `key_mask` is a boolean array/tensor of length K (the prompt length). The hook
    rewrites the float `attention_mask` argument in place of the module call; if the
    model was built without a float mask (mask=None, e.g. a fully-causal fast path) the
    hook synthesizes one of shape [B, 1, Q, K] so the intervention still applies.
    """
    import torch

    spec.validate()
    mask_t = torch.as_tensor(np.asarray(key_mask, dtype=bool))
    handles = []
    mods = _attn_modules(model)
    targets = {i for i in spec.layers if 0 <= i < len(mods)}
    if not targets:
        raise ValueError(f"no valid layers in {spec.layers} for a {len(mods)}-layer model")

    def make_hook(module):
        def hook(mod, args, kwargs):
            am = kwargs.get("attention_mask")
            pos = None
            if am is None and len(args) >= 3:
                am, pos = args[2], 2
            hs = kwargs.get("hidden_states", args[0] if args else None)
            if hs is None:
                return None
            B, Q, _ = hs.shape
            device, dtype = hs.device, hs.dtype
            if am is None:
                K = Q
                am_new = torch.zeros((B, 1, Q, K), device=device, dtype=dtype)
            else:
                am_new = am.clone()
                K = am_new.shape[-1]
            m = mask_t.to(device)
            if m.numel() < K:
                m = torch.cat([m, torch.zeros(K - m.numel(), dtype=torch.bool, device=device)])
            else:
                m = m[:K]
            bias = torch.zeros((K,), device=device, dtype=am_new.dtype)
            bias[m] = spec.bias
            if spec.heads is None or am_new.shape[1] == 1:
                am_new = am_new + bias.view(1, 1, 1, K)
            else:
                H = am_new.shape[1]
                per_head = torch.zeros((H, K), device=device, dtype=am_new.dtype)
                for h in spec.heads:
                    if 0 <= h < H:
                        per_head[h] = bias
                am_new = am_new + per_head.view(1, H, 1, K)
            if pos is not None:
                args = list(args)
                args[pos] = am_new
                return tuple(args), kwargs
            kwargs = dict(kwargs)
            kwargs["attention_mask"] = am_new
            return args, kwargs

        return hook

    try:
        for i in sorted(targets):
            handles.append(mods[i].register_forward_pre_hook(make_hook(mods[i]), with_kwargs=True))
        yield
    finally:
        for h in handles:
            h.remove()


def evaluate_with_knockout(
    model,
    tokenizer,
    items: Sequence[dict[str, Any]],
    spec: KnockoutSpec,
    *,
    max_new_tokens: int = 64,
    max_length: int = 1536,
) -> list[dict[str, Any]]:
    """Greedy-decode each item twice (clean / knocked out) and grade both.

    Returns one row per item with `correct_clean` and `correct_knockout`, which is the
    paired unit the RQ3 permutation test in stats/R/05_rq3_attention.R consumes. Grading
    goes through the project's scoring module (peer-owned); the assumed interface is
    `obtune.scoring.grade(output_raw, gold) -> (correct: bool, parsed: str | None)`.
    """
    import torch

    from obtune.attention.capture import build_prompt_text

    try:
        from obtune.scoring import grade  # peer-owned
    except Exception:  # keep the module importable before scoring.py lands
        def grade(output_raw: str, gold: str):
            return output_raw.strip() == gold.strip(), output_raw.strip()

    rows: list[dict[str, Any]] = []
    for it in items:
        text, _ = build_prompt_text(
            tokenizer, code=it["code"], entry_point=it["entry_point"],
            args_repr=it.get("args_repr", "()"), language=it["language"],
            condition=it["condition"],
        )
        cs = text.find(it["code"])
        enc = tokenizer(text, return_offsets_mapping=True, truncation=True,
                        max_length=max_length, return_tensors="pt", add_special_tokens=False)
        offsets = [tuple(map(int, o)) for o in enc.pop("offset_mapping")[0].tolist()]
        km = identifier_key_mask(it["code"], it["language"], it["entry_point"], offsets, cs,
                                 classes=spec.classes, include_slice=spec.include_slice)
        enc = {k: v.to(model.device) for k, v in enc.items()}

        def _gen() -> str:
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                                     pad_token_id=tokenizer.eos_token_id)
            return tokenizer.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)

        clean = _gen()
        with attention_knockout(model, km, spec):
            knocked = _gen()

        ok_c, _ = grade(clean, it["output_repr"])
        ok_k, _ = grade(knocked, it["output_repr"])
        rows.append({
            "item_id": it["item_id"], "program_id": it["program_id"],
            "condition": it["condition"], "language": it["language"],
            "n_knocked_keys": int(km.sum()), "n_tokens": len(offsets),
            "knockout_layers": ",".join(map(str, spec.layers)),
            "knockout_classes": ",".join(spec.classes), "knockout_bias": spec.bias,
            "output_clean": clean, "output_knockout": knocked,
            "correct_clean": int(bool(ok_c)), "correct_knockout": int(bool(ok_k)),
        })
    return rows
