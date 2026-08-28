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

__all__ = ["KnockoutSpec", "identifier_key_mask", "inert_key_mask", "attention_knockout", "layer_set",
           "evaluate_with_knockout", "score_with_knockout"]

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
        # `inert` is a PSEUDO-CLASS: it is not a lexical category but a static-analysis verdict
        # ("this code cannot affect the result"), so it cuts across `CLASSES` rather than being one
        # of them. It is resolved by `_key_mask` via `inert_key_mask`, and may be combined with
        # lexical classes — the masks are unioned.
        bad = [c for c in self.classes if c not in CLASSES and c != "inert"]
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


def inert_key_mask(
    code: str,
    language: str,
    entry_point: Optional[str],
    offsets: Sequence[tuple[int, int]],
    code_char_start: int,
) -> np.ndarray:
    """Boolean [T] mask of the tokens a static analysis PROVES cannot affect the result.

    THE QUESTION THIS EXISTS TO ANSWER. Deleting inert code helps: symbolic DCE is worth
    **+4.74 pts** to `base` on `S2` [+3.12, +6.24]. But deletion changes two things at once — the
    distracting tokens are gone, AND the sequence is shorter, so every live token sits closer to
    the answer position and the model has fewer positions to spread attention over. Every
    normalization result in this project confounds those. Masking separates them: the program the
    model sees is byte-identical, every token keeps its position, and the ONLY thing that changes
    is that attention to the inert keys is suppressed. If the +4.74 survives, the benefit is
    attention allocation and it can be had at inference with no training and no rewrite. If it
    vanishes, the benefit was length and position, and "stop attending to it" is not the same as
    "it is not there" — which would also mean the 2026-08-26 knockout result is about something
    narrower than it appears.

    PRE-REGISTERED DIRECTION, and note it is the OPPOSITE of the identifier knockout. There,
    suppressing tokens the answer depends on HURT `base` (delta_logp −0.089 [−0.158, −0.023]).
    Here the suppressed tokens are provably irrelevant, so a model that was being distracted by
    them should get BETTER: delta_logp > 0. A null is informative and a negative would falsify the
    distraction account outright.

    Spans come from `normalize.inert.inert_spans`, the same analysis that drives the `dse`
    normalization pass — so "delete them" and "stop attending to them" are the same set of
    characters by construction, which is what makes the two arms comparable. It is
    execution-gated at 1200/1200 parity (`scripts/analysis/25_validate_inert.py`).

    A token is masked when the MAJORITY of its code characters are inert. Subword tokenizers merge
    across boundaries, so a strict all-or-nothing rule would leave the tokens straddling the edge
    of a dead block unmasked; the majority rule matches `token_class_assignment`'s convention.
    """
    from obtune.normalize.inert import inert_spans

    if language != "python":
        return np.zeros(len(offsets), dtype=bool)
    spans = inert_spans(code, entry_point or "")
    if not spans:
        return np.zeros(len(offsets), dtype=bool)

    dead = np.zeros(len(code), dtype=bool)
    for lo, hi in spans:
        dead[max(lo, 0):min(hi, len(code))] = True

    out = np.zeros(len(offsets), dtype=bool)
    for i, (st, en) in enumerate(offsets):
        if en <= st:
            continue                                  # (0,0) special tokens
        a = max(st - code_char_start, 0)
        b = min(en - code_char_start, len(code))
        if b <= a:
            continue                                  # outside the code region
        out[i] = dead[a:b].mean() > 0.5
    return out


def _key_mask(it: dict, offsets, code_char_start: int, spec: "KnockoutSpec") -> np.ndarray:
    """Union of the lexical-class mask and (if requested) the static-analysis inert mask."""
    lexical = tuple(c for c in spec.classes if c != "inert")
    mask = np.zeros(len(offsets), dtype=bool)
    if lexical or spec.include_slice:
        mask |= identifier_key_mask(it["code"], it["language"], it["entry_point"], offsets,
                                    code_char_start, classes=lexical or (),
                                    include_slice=spec.include_slice)
    if "inert" in spec.classes:
        mask |= inert_key_mask(it["code"], it["language"], it["entry_point"], offsets,
                               code_char_start)
    return mask


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

    # NO FALLBACK GRADER. This used to fall back to `output.strip() == gold.strip()` if
    # `obtune.scoring` failed to import ("keep the module importable before scoring.py
    # lands" — it has long since landed). A silently substituted grader is CLAUDE.md
    # silent-failure #5: strict string equality is not the project's normalized exact
    # match, so every knockout number would have been graded by a different rule than
    # every accuracy number it is compared against, with nothing in the output saying so.
    from obtune.scoring import grade

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
        km = _key_mask(it, offsets, cs, spec)
        enc = {k: v.to(model.device) for k, v in enc.items()}

        def _gen() -> str:
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                                     pad_token_id=tokenizer.eos_token_id)
            return tokenizer.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)

        clean = _gen()
        with attention_knockout(model, km, spec):
            knocked = _gen()

        # `grade(pred, gold, language) -> Grade`, a frozen dataclass. This previously called
        # it with two positional args and unpacked two values, so it raised TypeError on the
        # first item — twice over, since `Grade` has six fields and is not a 2-tuple. Never
        # caught because the knockout had never been run.
        ok_c = grade(clean, it["output_repr"], it["language"]).correct
        ok_k = grade(knocked, it["output_repr"], it["language"]).correct
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


def score_with_knockout(
    model,
    tokenizer,
    items: Sequence[dict[str, Any]],
    spec: KnockoutSpec,
    *,
    max_length: int = 1536,
) -> list[dict[str, Any]]:
    """Teacher-forced log P(gold answer) under clean vs knocked-out attention.

    WHY THIS EXISTS, AND WHY `evaluate_with_knockout` IS THE WRONG INSTRUMENT HERE.
    The 2026-08-26 manipulation check showed the knockout hook works exactly as intended:
    attention mass at masked key positions drops to 0.0000 at every layer, and masking all six
    token classes across all 28 layers changes 68 % of generated outputs (only 48/150 identical,
    against 62 % identical at 6 layers -- a clean dose-response). The intervention is real.

    What did NOT move was exact-match ACCURACY: every cell of a 12-condition sweep landed inside
    -2.7 to +2.7 points. The reason is a floor, not a failure. `base` scores ~22 % on obfuscated
    `S2`, close enough to guessing that scrambling what it can attend to changes WHICH answers it
    emits without changing how often they happen to be right. A binary hit/miss on a 22 %-accurate
    task has no headroom to register the manipulation.

    Log-probability of the gold answer has no floor. It is continuous, it is defined for every
    item including the ones the model gets wrong, and it measures the quantity the mechanism claim
    is actually about: how much the answer DEPENDS on being able to read those tokens.

    Returns one row per item with `logp_clean`, `logp_knockout` and `delta_logp`
    (= knocked - clean, so NEGATIVE means the knockout hurt). Per-token means are included
    because gold answers differ in length and a sum would confound effect with answer length.
    """
    import torch

    from obtune.attention.capture import build_prompt_text

    rows: list[dict[str, Any]] = []
    for it in items:
        text, _ = build_prompt_text(
            tokenizer, code=it["code"], entry_point=it["entry_point"],
            args_repr=it.get("args_repr", "()"), language=it["language"],
            condition=it["condition"],
        )
        enc = tokenizer(text, return_offsets_mapping=True, truncation=True,
                        max_length=max_length, return_tensors="pt", add_special_tokens=False)
        offsets = enc.pop("offset_mapping")[0].numpy().astype(np.int32)
        cs = text.find(it["code"])
        if cs < 0:
            continue
        km = _key_mask(it, offsets, cs, spec)

        prompt_ids = enc["input_ids"]
        gold_ids = tokenizer(str(it["output_repr"]), add_special_tokens=False,
                             return_tensors="pt")["input_ids"]
        if gold_ids.shape[-1] == 0:
            continue
        full = torch.cat([prompt_ids, gold_ids], dim=1).to(model.device)
        n_prompt = int(prompt_ids.shape[-1])
        n_gold = int(gold_ids.shape[-1])

        def _logp() -> float:
            with torch.no_grad():
                out = model(input_ids=full, use_cache=False)
            # Position t's logits predict token t+1, so the gold tokens (which occupy
            # n_prompt .. n_prompt+n_gold-1) are predicted from logits at n_prompt-1 onward.
            # float32 for the log_softmax: summing bf16 log-probs over a long answer loses
            # more precision than the effect being measured.
            lsm = out.logits[0, n_prompt - 1: -1].float().log_softmax(-1)
            tgt = full[0, n_prompt:]
            return float(lsm.gather(-1, tgt.unsqueeze(-1)).sum())

        clean = _logp()
        with attention_knockout(model, km, spec):
            knocked = _logp()

        rows.append({
            "item_id": it["item_id"], "program_id": it["program_id"],
            "condition": it["condition"], "language": it["language"],
            "n_knocked_keys": int(km.sum()), "n_tokens": len(offsets), "n_gold_tokens": n_gold,
            "logp_clean": clean, "logp_knockout": knocked,
            "delta_logp": knocked - clean,
            "delta_logp_per_token": (knocked - clean) / n_gold,
        })
    return rows
