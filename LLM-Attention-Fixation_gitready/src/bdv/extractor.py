from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

from .schema import GLOBAL_FEATURE_NAMES, HEAD_FEATURE_NAMES, LAYER_FEATURE_NAMES


@dataclass(frozen=True)
class _RegionMasks:
    instr: np.ndarray
    code: np.ndarray
    other: np.ndarray


def _bucket_index(step: int, total: int, bucket_count: int) -> int:
    if bucket_count <= 1 or total <= 1:
        return 0
    return min(bucket_count - 1, int(step * bucket_count / max(total, 1)))


def _safe_entropy(prob: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    p = torch.clamp(prob, min=0.0)
    z = p.sum(dim=-1, keepdim=True)
    p = torch.where(z > eps, p / z, torch.zeros_like(p))
    return -(p * torch.log(torch.clamp(p, min=eps))).sum(dim=-1)


def _build_region_masks(
    tokenizer,
    *,
    prompt: str,
    instruction: str,
    code_snippet: str,
    language: str,
    prompt_len: int,
) -> _RegionMasks:
    prompt_no_special = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    instr_text = f"{instruction}\n\n"
    code_text = f"```{language}\n{code_snippet}\n```"
    instr_ids = tokenizer(instr_text, add_special_tokens=False)["input_ids"]
    code_ids = tokenizer(code_text, add_special_tokens=False)["input_ids"]

    bos_offset = max(0, int(prompt_len - len(prompt_no_special)))
    instr_start = bos_offset
    instr_end = min(prompt_len, instr_start + len(instr_ids))
    code_end = min(prompt_len, instr_end + len(code_ids))

    instr_mask = np.zeros((prompt_len,), dtype=bool)
    code_mask = np.zeros((prompt_len,), dtype=bool)
    instr_mask[instr_start:instr_end] = True
    code_mask[instr_end:code_end] = True
    other_mask = ~(instr_mask | code_mask)
    return _RegionMasks(instr=instr_mask, code=code_mask, other=other_mask)


def _capture_layer_norms(
    model,
    *,
    num_heads: int,
) -> Tuple[List[torch.utils.hooks.RemovableHandle], Dict[int, torch.Tensor], Dict[int, torch.Tensor], Dict[int, torch.Tensor]]:
    hooks: List[torch.utils.hooks.RemovableHandle] = []
    head_out_norm: Dict[int, torch.Tensor] = {}
    attn_delta_norm: Dict[int, torch.Tensor] = {}
    mlp_delta_norm: Dict[int, torch.Tensor] = {}

    layers = getattr(getattr(model, "model", None), "layers", None)
    if layers is None:
        return hooks, head_out_norm, attn_delta_norm, mlp_delta_norm

    for layer_idx, layer in enumerate(layers):
        attn = getattr(layer, "self_attn", None)
        mlp = getattr(layer, "mlp", None)
        o_proj = getattr(attn, "o_proj", None)
        down_proj = getattr(mlp, "down_proj", None)

        if o_proj is not None:
            def _o_proj_hook(mod, inputs, output, *, li=layer_idx):
                if not inputs:
                    return
                x = inputs[0]
                if x is None or x.ndim != 3:
                    return
                with torch.no_grad():
                    bsz, steps, dim = x.shape
                    if bsz <= 0 or dim <= 0 or num_heads <= 0 or dim % num_heads != 0:
                        return
                    head_dim = dim // num_heads
                    xh = x.detach().to(torch.float32).reshape(bsz, steps, num_heads, head_dim)
                    head_norm = torch.linalg.vector_norm(xh, dim=-1)[0].cpu()  # [T, H]
                    head_out_norm[li] = head_norm
                    y = output.detach().to(torch.float32)
                    attn_norm = torch.linalg.vector_norm(y, dim=-1)[0].cpu()  # [T]
                    attn_delta_norm[li] = attn_norm

            hooks.append(o_proj.register_forward_hook(_o_proj_hook))

        if down_proj is not None:
            def _down_proj_hook(mod, inputs, output, *, li=layer_idx):
                if output is None or output.ndim != 3:
                    return
                with torch.no_grad():
                    y = output.detach().to(torch.float32)
                    mlp_norm = torch.linalg.vector_norm(y, dim=-1)[0].cpu()  # [T]
                    mlp_delta_norm[li] = mlp_norm

            hooks.append(down_proj.register_forward_hook(_down_proj_hook))

    return hooks, head_out_norm, attn_delta_norm, mlp_delta_norm


def build_bdv_features(
    *,
    model,
    tokenizer,
    code_snippet: str,
    instruction: str,
    target_text: str,
    language: str = "java",
    bucket_count: int = 1,
    pair_id: str = "",
    variant_type: str = "plain",
    is_correct: bool = False,
) -> Dict[str, Any]:
    bucket_count = 1 if bucket_count <= 1 else 3
    prompt = f"{instruction}\n\n```{language}\n{code_snippet}\n```"

    model_device = getattr(model, "device", None)
    if model_device is None:
        model_device = next(model.parameters()).device

    enc_prompt = tokenizer(prompt, return_tensors="pt")
    prompt_ids = enc_prompt["input_ids"].to(model_device)
    prompt_len = int(prompt_ids.shape[-1])

    target_ids = tokenizer(target_text or "", add_special_tokens=False, return_tensors="pt")["input_ids"].to(model_device)
    out_len = int(target_ids.shape[-1])
    full_ids = torch.cat([prompt_ids, target_ids], dim=-1)
    full_mask = torch.ones_like(full_ids, dtype=torch.long)

    num_layers = int(getattr(model.config, "num_hidden_layers", 0))
    num_heads = int(getattr(model.config, "num_attention_heads", 0))
    f_head = len(HEAD_FEATURE_NAMES)
    f_layer = len(LAYER_FEATURE_NAMES)
    f_global = len(GLOBAL_FEATURE_NAMES)

    head_sum = np.zeros((num_layers, num_heads, bucket_count, f_head), dtype=np.float64)
    head_count = np.zeros_like(head_sum, dtype=np.int64)
    layer_sum = np.zeros((num_layers, bucket_count, f_layer), dtype=np.float64)
    layer_count = np.zeros_like(layer_sum, dtype=np.int64)
    bucket_counts = np.zeros((bucket_count,), dtype=np.int64)

    availability = {
        "attention_available": False,
        "head_out_norm_available": False,
        "attn_delta_norm_available": False,
        "mlp_delta_norm_available": False,
        "head_logit_correct_available": False,
        "hidden_post_norm_available": False,
    }

    hooks, head_out_norm, attn_delta_norm, mlp_delta_norm = _capture_layer_norms(model, num_heads=num_heads)
    try:
        with torch.no_grad():
            out = model(
                input_ids=full_ids,
                attention_mask=full_mask,
                use_cache=False,
                output_attentions=True,
                output_hidden_states=False,
                return_dict=True,
            )
    finally:
        for h in hooks:
            h.remove()

    attentions = getattr(out, "attentions", None)
    logits = out.logits.detach().to(torch.float32).cpu()  # [1, T, V]
    availability["attention_available"] = isinstance(attentions, (tuple, list))
    availability["head_out_norm_available"] = len(head_out_norm) > 0
    availability["attn_delta_norm_available"] = len(attn_delta_norm) > 0
    availability["mlp_delta_norm_available"] = len(mlp_delta_norm) > 0

    region_masks = _build_region_masks(
        tokenizer,
        prompt=prompt,
        instruction=instruction,
        code_snippet=code_snippet,
        language=language,
        prompt_len=prompt_len,
    )
    code_mask_t = torch.from_numpy(region_masks.code)
    instr_mask_t = torch.from_numpy(region_masks.instr)
    other_mask_t = torch.from_numpy(region_masks.other)

    seq_nll = 0.0
    final_layer_entropy_values: List[float] = []

    for step in range(out_len):
        q_pos = prompt_len + step - 1
        y_pos = prompt_len + step
        if q_pos < 0 or y_pos >= int(full_ids.shape[-1]):
            continue
        bucket = _bucket_index(step, out_len, bucket_count)
        bucket_counts[bucket] += 1

        step_logits = logits[0, q_pos]
        correct_id = int(full_ids[0, y_pos].item())
        log_probs = torch.log_softmax(step_logits, dim=-1)
        lp = float(log_probs[correct_id].item())
        seq_nll += -lp
        correct_logit = float(step_logits[correct_id].item())
        masked = step_logits.clone()
        masked[correct_id] = float("-inf")
        best_incorrect = float(torch.max(masked).item())
        rank = int((step_logits > correct_logit).sum().item()) + 1
        margin = correct_logit - best_incorrect

        for li in range(num_layers):
            # Layer-level features
            layer_vals = np.array(
                [
                    lp,
                    float(rank),
                    margin,
                    float(attn_delta_norm[li][q_pos].item()) if li in attn_delta_norm and q_pos < attn_delta_norm[li].shape[0] else np.nan,
                    float(mlp_delta_norm[li][q_pos].item()) if li in mlp_delta_norm and q_pos < mlp_delta_norm[li].shape[0] else np.nan,
                    np.nan,
                ],
                dtype=np.float64,
            )
            finite_layer = np.isfinite(layer_vals)
            layer_sum[li, bucket, :] += np.where(finite_layer, layer_vals, 0.0)
            layer_count[li, bucket, :] += finite_layer.astype(np.int64)

            if not availability["attention_available"] or li >= len(attentions):
                continue

            layer_attn = attentions[li][0, :, q_pos, :prompt_len].detach().to(torch.float32).cpu()  # [H, prompt_len]
            denom = torch.clamp(layer_attn.sum(dim=-1, keepdim=True), min=1e-12)
            prompt_prob = layer_attn / denom
            code_mass = prompt_prob[:, code_mask_t].sum(dim=-1) if code_mask_t.any() else torch.zeros((num_heads,), dtype=torch.float32)
            instr_mass = prompt_prob[:, instr_mask_t].sum(dim=-1) if instr_mask_t.any() else torch.zeros((num_heads,), dtype=torch.float32)
            other_mass = prompt_prob[:, other_mask_t].sum(dim=-1) if other_mask_t.any() else torch.zeros((num_heads,), dtype=torch.float32)
            entropy = _safe_entropy(prompt_prob)
            if li == num_layers - 1:
                final_layer_entropy_values.extend([float(x) for x in entropy.tolist()])

            if li in head_out_norm and q_pos < head_out_norm[li].shape[0]:
                h_norm = head_out_norm[li][q_pos].to(torch.float32)
            else:
                h_norm = torch.full((num_heads,), float("nan"), dtype=torch.float32)

            head_features = torch.stack(
                [
                    code_mass,
                    instr_mass,
                    other_mass,
                    entropy,
                    h_norm,
                    torch.full((num_heads,), float("nan"), dtype=torch.float32),
                ],
                dim=-1,
            ).numpy()  # [H, F_head]

            finite_head = np.isfinite(head_features)
            head_sum[li, :, bucket, :] += np.where(finite_head, head_features, 0.0)
            head_count[li, :, bucket, :] += finite_head.astype(np.int64)

    head_denom = np.maximum(head_count, 1)
    layer_denom = np.maximum(layer_count, 1)
    phi_head = np.zeros_like(head_sum, dtype=np.float64)
    phi_layer = np.zeros_like(layer_sum, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        np.divide(head_sum, head_denom, out=phi_head, where=head_count > 0)
        np.divide(layer_sum, layer_denom, out=phi_layer, where=layer_count > 0)
    phi_head[head_count == 0] = np.nan
    phi_layer[layer_count == 0] = np.nan

    avg_final_entropy = float(np.mean(final_layer_entropy_values)) if final_layer_entropy_values else np.nan
    phi_global = np.array(
        [
            float(seq_nll),
            avg_final_entropy,
            float(prompt_len),
            float(out_len),
        ],
        dtype=np.float32,
    )

    return {
        "schema_version": "bdv_v1",
        "bucket_count": int(bucket_count),
        "phi_head": phi_head.astype(np.float16),
        "phi_layer": phi_layer.astype(np.float16),
        "phi_global": phi_global.astype(np.float32),
        "bucket_counts": bucket_counts.astype(np.int32),
        "availability": availability,
        "pair_id": str(pair_id),
        "variant_type": str(variant_type),
        "is_correct": bool(is_correct),
    }
