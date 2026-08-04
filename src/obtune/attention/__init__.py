"""RQ3 attention analysis: token classes, backward slices, mass/entropy metrics.

Only the CPU-safe surface is re-exported here. `capture` and `knockout` pull in
torch/transformers and are imported explicitly from a GPU entrypoint, so that
`import obtune.attention` stays cheap for the stats/validation paths.
"""
from obtune.attention.slicer_js import slice_javascript
from obtune.attention.slicer_py import Slice, slice_python
from obtune.attention.token_classes import (
    BASE_CLASSES,
    CLASSES,
    ClassSpan,
    Classification,
    classify_code,
)

__all__ = [
    "CLASSES", "BASE_CLASSES", "ClassSpan", "Classification", "classify_code",
    "Slice", "slice_python", "slice_javascript",
]
