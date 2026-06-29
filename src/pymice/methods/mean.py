"""Unconditional mean imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method


def impute_mean(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute missing values with the unconditional mean of observed ``y``."""
    observed = y[ry]
    if observed.size == 0:
        raise ValueError("No observed values available for mean imputation")
    mu = float(np.nanmean(observed))
    return np.full(int(np.sum(wy)), mu, dtype=np.float64)


register_method("mean", impute_mean)
