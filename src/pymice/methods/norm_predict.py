"""Linear regression imputation via predicted values (regression imputation)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, estimice
from pymice.methods.registry import register_method


def impute_norm_predict(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via OLS predictions without noise (R ``mice.impute.norm.predict``)."""
    del rng  # deterministic method; kept for API compatibility
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    y_arr = np.asarray(y, dtype=np.float64)
    est = estimice(x_full[ry], y_arr[ry], ridge=ridge)
    return x_full[wy] @ est.coef


register_method("norm.predict", impute_norm_predict)
