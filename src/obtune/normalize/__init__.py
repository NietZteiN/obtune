"""Symbolic normalization — the zero-training deobfuscation baseline.

The question this answers is the one an FSE reviewer asks first: *before you fine-tune
anything, what does a plain static normalizer already recover?* Every pass here is
deterministic source-to-source rewriting with no model, no training and no GPU.

See `py_norm` for the passes and `PROFILES` for the arms actually evaluated.
"""
from obtune.normalize.py_norm import (  # noqa: F401
    PASSES,
    PROFILES,
    NormResult,
    normalize,
    normalize_python,
)
