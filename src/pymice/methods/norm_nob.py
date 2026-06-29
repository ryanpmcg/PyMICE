"""Linear regression imputation without parameter uncertainty."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, norm_fix
from pymice.methods.registry import register_method


def impute_norm_nob(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via OLS + residual noise (R ``mice.impute.norm.nob``)."""
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    y_arr = np.asarray(y, dtype=np.float64)
    beta, sigma = norm_fix(y_arr, ry, x_full, ridge=ridge)
    preds = x_full[wy] @ beta
    noise = rng.standard_normal(int(np.sum(wy))) * sigma
    return preds + noise


register_method("norm.nob", impute_norm_nob)
