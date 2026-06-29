"""Bayesian normal linear regression imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, norm_draw
from pymice.methods.registry import register_method


def impute_norm(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via Bayesian linear regression (R ``mice.impute.norm``)."""
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    y_arr = np.asarray(y, dtype=np.float64)
    _, beta_star, sigma_star = norm_draw(y_arr, ry, x_full, rng=rng, ridge=ridge)
    preds = x_full[wy] @ beta_star
    noise = rng.standard_normal(int(np.sum(wy))) * sigma_star
    return preds + noise


register_method("norm", impute_norm)
