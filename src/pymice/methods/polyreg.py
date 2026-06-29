"""Polytomous logistic regression for unordered categorical imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize

from pymice.methods.augment import augment
from pymice.methods.linear import add_intercept
from pymice.methods.registry import register_method


def _softmax(logits: NDArray[np.float64]) -> NDArray[np.float64]:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    expv = np.exp(shifted)
    return expv / np.sum(expv, axis=1, keepdims=True)


def _fit_multinomial(
    x: NDArray[np.float64],
    y_codes: NDArray[np.int_],
    weights: NDArray[np.float64],
    n_classes: int,
) -> NDArray[np.float64]:
    """Fit multinomial logit with reference category 0 (nnet::multinom style)."""
    n, p = x.shape
    k = n_classes - 1
    if k == 0:
        return np.zeros((p, 0), dtype=np.float64)

    def nll(params: NDArray[np.float64]) -> float:
        beta = params.reshape(k, p)
        logits = np.zeros((n, n_classes))
        logits[:, 1:] = x @ beta.T
        probs = _softmax(logits)
        idx = np.arange(n)
        p_y = probs[idx, y_codes]
        return -float(np.sum(weights * np.log(np.maximum(p_y, 1e-12))))

    x0 = np.zeros(k * p, dtype=np.float64)
    result = minimize(nll, x0, method="L-BFGS-B")
    return result.x.reshape(k, p)


def _predict_multinomial(
    x: NDArray[np.float64], beta: NDArray[np.float64], n_classes: int
) -> NDArray[np.float64]:
    k = n_classes - 1
    logits = np.zeros((x.shape[0], n_classes))
    if k > 0:
        logits[:, 1:] = x @ beta.T
    return _softmax(logits)


def impute_polyreg(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    levels: tuple[float, ...] | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute unordered categorical values via polytomous regression."""
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)

    if levels is None:
        levels_tuple = tuple(float(v) for v in np.unique(y_arr[~np.isnan(y_arr)]))
    else:
        levels_tuple = tuple(float(v) for v in levels)
    level_to_code = {lv: i for i, lv in enumerate(levels_tuple)}
    np.array([level_to_code.get(v, 0) for v in y_arr], dtype=np.int_)
    n_classes = len(levels_tuple)

    ya, rya, xa, wya, wa = augment(y_arr, ry, x_arr, wy)
    ya_codes = np.array([level_to_code.get(v, 0) for v in ya], dtype=np.int_)

    counts = {level_to_code[lv]: int(np.sum(ya[rya] == lv)) for lv in levels_tuple}
    for code, count in counts.items():
        if count == int(np.sum(rya)):
            return np.full(int(np.sum(wy)), levels_tuple[code], dtype=np.float64)

    x_aug = add_intercept(xa)
    beta = _fit_multinomial(x_aug[rya], ya_codes[rya], wa[rya], n_classes)
    post = _predict_multinomial(x_aug[wya], beta, n_classes)

    n_wy = post.shape[0]
    un = np.repeat(rng.random(n_wy), n_classes).reshape(n_wy, n_classes)
    cum = np.cumsum(post, axis=1)
    draws = un > cum
    idx = np.sum(draws, axis=1)
    return np.array([levels_tuple[min(i, n_classes - 1)] for i in idx], dtype=np.float64)


register_method("polyreg", impute_polyreg)
