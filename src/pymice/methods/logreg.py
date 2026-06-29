"""Binary logistic regression imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.augment import augment
from pymice.methods.linear import _chol_safe, add_intercept
from pymice.methods.registry import register_method


def _fit_logistic_irls(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    weights: NDArray[np.float64],
    max_iter: int = 25,
    tol: float = 1e-8,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Weighted logistic regression via IRLS (R ``glm.fit`` quasibinomial)."""
    _n, p = x.shape
    beta = np.zeros(p, dtype=np.float64)
    y = np.clip(y, 1e-9, 1 - 1e-9)

    for _ in range(max_iter):
        eta = x @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        w = weights * mu * (1.0 - mu)
        z = eta + (y - mu) / np.maximum(mu * (1.0 - mu), 1e-9)

        wx = x * w[:, None]
        lhs = x.T @ wx
        rhs = x.T @ (w * z)
        try:
            beta_new = np.linalg.solve(lhs, rhs)
        except np.linalg.LinAlgError:
            beta_new = np.linalg.lstsq(lhs, rhs, rcond=None)[0]

        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new

    eta = x @ beta
    mu = 1.0 / (1.0 + np.exp(-eta))
    w = weights * mu * (1.0 - mu)
    wx = x * w[:, None]
    fisher = x.T @ wx
    try:
        cov = np.linalg.inv(fisher)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(fisher)

    return beta, cov


def impute_logreg(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    **_: object,
) -> NDArray[np.floating]:
    """Impute binary outcomes via Bayesian logistic regression."""
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)

    ya, rya, xa, wya, wa = augment(y_arr, ry, x_arr, wy)
    x_aug = add_intercept(xa)

    beta, cov = _fit_logistic_irls(x_aug[rya], ya[rya], wa[rya])
    chol = _chol_safe((cov + cov.T) / 2.0)
    beta_star = beta + chol @ rng.standard_normal(beta.size)

    eta = x_aug[wya] @ beta_star
    prob = 1.0 / (1.0 + np.exp(-eta))
    draws = rng.random(int(np.sum(wya))) <= prob
    return draws.astype(np.float64)


register_method("logreg", impute_logreg)
