"""Bootstrap logistic regression imputation (logreg.boot)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.logreg import _fit_logistic_irls
from pymice.methods.registry import register_method


def impute_logreg_boot(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    **_: object,
) -> NDArray[np.floating]:
    """Impute binary data via bootstrap logistic regression (R ``mice.impute.logreg.boot``)."""
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    x_full = add_intercept(x_arr)
    obs_idx = np.flatnonzero(ry)
    if obs_idx.size == 0:
        raise ValueError("No observed values for logreg.boot")
    boot_idx = rng.choice(obs_idx, size=obs_idx.size, replace=True)
    beta, cov = _fit_logistic_irls(x_full[boot_idx], y_arr[boot_idx], np.ones(boot_idx.size))
    chol = np.linalg.cholesky((cov + cov.T) / 2.0 + np.eye(cov.shape[0]) * 1e-6)
    beta_star = beta + chol @ rng.standard_normal(beta.size)
    eta = x_full[wy] @ beta_star
    prob = 1.0 / (1.0 + np.exp(-eta))
    return (rng.random(int(np.sum(wy))) <= prob).astype(np.float64)


register_method("logreg.boot", impute_logreg_boot)
