"""Proportional odds (ordered logistic) imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize

from pymice.methods.augment import augment
from pymice.methods.linear import add_intercept
from pymice.methods.polyreg import _fit_multinomial, _predict_multinomial
from pymice.methods.registry import register_method


def _cumulative_probs(eta: NDArray[np.float64], zetas: NDArray[np.float64]) -> NDArray[np.float64]:
    """P(Y <= j) for j = 0..K-1."""
    logits = zetas[None, :] - eta[:, None]
    return 1.0 / (1.0 + np.exp(-logits))


def _category_probs(cum: NDArray[np.float64]) -> NDArray[np.float64]:
    k = cum.shape[1]
    probs = np.empty((cum.shape[0], k), dtype=np.float64)
    probs[:, 0] = cum[:, 0]
    for j in range(1, k - 1):
        probs[:, j] = cum[:, j] - cum[:, j - 1]
    probs[:, k - 1] = 1.0 - cum[:, k - 2]
    return np.clip(probs, 1e-12, 1.0)


def _fit_polr(
    x: NDArray[np.float64],
    y_codes: NDArray[np.int_],
    weights: NDArray[np.float64],
    n_classes: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    n, p = x.shape
    k = n_classes - 1
    if k == 0:
        return np.zeros(0, dtype=np.float64), np.zeros(p, dtype=np.float64)

    def nll(params: NDArray[np.float64]) -> float:
        zetas = params[:k]
        beta = params[k:]
        eta = x @ beta
        cum = _cumulative_probs(eta, zetas)
        cat = _category_probs(cum)
        idx = np.arange(n)
        p_y = cat[idx, y_codes]
        return -float(np.sum(weights * np.log(p_y)))

    x0 = np.zeros(k + p, dtype=np.float64)
    x0[:k] = np.linspace(-1.0, 1.0, k)
    result = minimize(nll, x0, method="L-BFGS-B")
    zetas = result.x[:k]
    beta = result.x[k:]
    return zetas, beta


def _predict_polr(
    x: NDArray[np.float64],
    zetas: NDArray[np.float64],
    beta: NDArray[np.float64],
    n_classes: int,
) -> NDArray[np.float64]:
    eta = x @ beta
    cum = _cumulative_probs(eta, zetas)
    return _category_probs(cum)


def impute_polr(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    levels: tuple[float, ...] | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute ordered categorical values via proportional odds model."""
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)

    if levels is None:
        levels_tuple = tuple(float(v) for v in np.unique(y_arr[~np.isnan(y_arr)]))
    else:
        levels_tuple = tuple(float(v) for v in levels)
    level_to_code = {lv: i for i, lv in enumerate(levels_tuple)}
    n_classes = len(levels_tuple)

    ya, rya, xa, wya, wa = augment(y_arr, ry, x_arr, wy)
    ya_codes = np.array([level_to_code.get(v, 0) for v in ya], dtype=np.int_)
    x_aug = add_intercept(xa)

    try:
        zetas, beta = _fit_polr(x_aug[rya], ya_codes[rya], wa[rya], n_classes)
        post = _predict_polr(x_aug[wya], zetas, beta, n_classes)
    except Exception:
        beta = _fit_multinomial(x_aug[rya], ya_codes[rya], wa[rya], n_classes)
        post = _predict_multinomial(x_aug[wya], beta, n_classes)

    n_wy = post.shape[0]
    un = np.repeat(rng.random(n_wy), n_classes).reshape(n_wy, n_classes)
    cum = np.cumsum(post, axis=1)
    draws = un > cum
    idx = np.sum(draws, axis=1)
    return np.array([levels_tuple[min(i, n_classes - 1)] for i in idx], dtype=np.float64)


register_method("polr", impute_polr)
