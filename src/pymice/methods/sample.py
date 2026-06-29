"""Random draw from observed values."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.registry import register_method


def impute_sample(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    **_: object,
) -> NDArray[np.floating]:
    """Impute by sampling observed ``y`` with replacement."""
    observed = y[ry]
    if observed.size == 0:
        raise ValueError("No observed values available for sample imputation")
    n = int(np.sum(wy))
    return rng.choice(observed, size=n, replace=True).astype(np.float64)


register_method("sample", impute_sample)
