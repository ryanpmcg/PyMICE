"""Predictive mean matching."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, matchindex, norm_draw
from pymice.methods.registry import register_method


def impute_pmm(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    donors: int = 5,
    matchtype: int = 1,
    ridge: float = 1e-5,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via predictive mean matching (R ``mice.impute.pmm``)."""
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    y_arr = np.asarray(y, dtype=np.float64)

    coef, beta_star, _ = norm_draw(y_arr, ry, x_full, rng=rng, ridge=ridge)

    if matchtype == 0:
        yhat_obs = x_full[ry] @ coef
        yhat_mis = x_full[wy] @ coef
    elif matchtype == 1:
        yhat_obs = x_full[ry] @ coef
        yhat_mis = x_full[wy] @ beta_star
    elif matchtype == 2:
        yhat_obs = x_full[ry] @ beta_star
        yhat_mis = x_full[wy] @ beta_star
    else:
        raise ValueError(f"matchtype must be 0, 1, or 2; got {matchtype}")

    idx = matchindex(yhat_obs, yhat_mis, k=donors, rng=rng)
    y_obs = y_arr[ry]
    out = np.full(int(np.sum(wy)), np.nan, dtype=np.float64)
    out[:] = y_obs[idx]
    return out


register_method("pmm", impute_pmm)
