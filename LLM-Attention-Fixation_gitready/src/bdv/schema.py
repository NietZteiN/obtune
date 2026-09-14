from __future__ import annotations

from typing import Dict, List

BDV_SCHEMA_VERSION = "bdv_v1"

HEAD_FEATURE_NAMES: List[str] = [
    "attn_mass_code",
    "attn_mass_instr",
    "attn_mass_other",
    "attn_entropy",
    "head_out_norm",
    "head_logit_correct",
]

LAYER_FEATURE_NAMES: List[str] = [
    "logprob_correct",
    "rank_correct",
    "margin_correct",
    "attn_delta_norm",
    "mlp_delta_norm",
    "hidden_post_norm",
]

GLOBAL_FEATURE_NAMES: List[str] = [
    "seq_nll",
    "avg_entropy_final_layer",
    "len_prompt_tokens",
    "len_output_tokens",
]

BDV_SCHEMA: Dict[str, object] = {
    "schema_version": BDV_SCHEMA_VERSION,
    "head_feature_names": HEAD_FEATURE_NAMES,
    "layer_feature_names": LAYER_FEATURE_NAMES,
    "global_feature_names": GLOBAL_FEATURE_NAMES,
    "notes": {
        "nan_semantics": "NaN indicates unavailable feature on this backend/run.",
        "bucketing": "B=1 uses all decode steps; B=3 uses early/mid/late split.",
    },
}

