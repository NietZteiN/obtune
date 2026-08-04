"""Sandboxed program execution + the canonical output contract.

`pool.run_batch` is the only way programs are executed in this project; `canon.py`
and `canon.mjs` define what an "output" is, identically in both languages.
"""
from obtune.exec.canon import Unserializable, canon, canon_or_none
from obtune.exec.pool import BatchItem, CaseResult, ProgramResult, run_batch, run_one

__all__ = [
    "BatchItem", "CaseResult", "ProgramResult", "run_batch", "run_one",
    "canon", "canon_or_none", "Unserializable",
]
