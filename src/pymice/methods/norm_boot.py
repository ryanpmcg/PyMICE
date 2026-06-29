"""Linear regression imputation with bootstrap resampling."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, estimice
from pymice.methods.registry import register_method


def impute_norm_boot(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via bootstrap OLS + normal residuals (R ``mice.impute.norm.boot``)."""
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    y_arr = np.asarray(y, dtype=np.float64)
    x_obs = x_full[ry]
    y_obs = y_arr[ry]
    n1 = int(np.sum(ry))
    boot_idx = rng.integers(0, n1, size=n1)
    est = estimice(x_obs[boot_idx], y_obs[boot_idx], ridge=ridge)
    ncol = x_full.shape[1]
    denom = max(n1 - ncol - 1, 1)
    sigma = float(np.sqrt(np.sum(est.residuals**2) / denom))
    preds = x_full[wy] @ est.coef
    noise = rng.standard_normal(int(np.sum(wy))) * sigma
    return preds + noise


register_method("norm.boot", impute_norm_boot)
