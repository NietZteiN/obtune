from __future__ import annotations

import numpy as np


class RunningMean:
    def __init__(self, shape: tuple[int, ...], *, dtype=np.float64) -> None:
        self.sum = np.zeros(shape, dtype=dtype)
        self.count = np.zeros(shape, dtype=np.int64)

    def update(self, value: np.ndarray, mask: np.ndarray | None = None) -> None:
        if mask is None:
            finite = np.isfinite(value)
        else:
            finite = np.asarray(mask, dtype=bool) & np.isfinite(value)
        self.sum[finite] += value[finite]
        self.count[finite] += 1

    def mean(self) -> np.ndarray:
        out = np.full(self.sum.shape, np.nan, dtype=np.float64)
        nz = self.count > 0
        out[nz] = self.sum[nz] / self.count[nz]
        return out

