"""RQ2 router: frozen-base prompt features -> 6-way obfuscation-condition classifier.

H1 is NEVER one of the classes (see features.CONDITION_TO_LABEL). Only the CPU-safe
symbols are re-exported; `features.extract_features` needs torch/transformers and is
imported explicitly.
"""
from obtune.router.features import (
    CONDITION_TO_LABEL,
    LABEL_TO_CONDITION,
    FeatureSet,
    load_features,
    save_features,
)

__all__ = [
    "CONDITION_TO_LABEL", "LABEL_TO_CONDITION", "FeatureSet",
    "load_features", "save_features",
]
