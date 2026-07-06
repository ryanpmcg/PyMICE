"""LASSO-penalized imputation methods."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, norm_draw
from pymice.methods.logreg import impute_logreg
from pymice.methods.registry import register_method
from pymice.methods.sklearn_backend import use_sklearn_backend


def _lasso_coef(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    *,
    logistic: bool = False,
    use_sklearn: bool | None = None,
) -> NDArray[np.float64]:
    if not use_sklearn_backend(use_sklearn):
        if logistic:
            from pymice.methods.logreg import _fit_logistic_irls

            beta, _ = _fit_logistic_irls(x, y, np.ones(y.size))
            return beta
        from pymice.methods.linear import estimice

        return estimice(x, y).coef
    try:
        if logistic:
            from sklearn.linear_model import LogisticRegression

            clf = LogisticRegression(penalty="l1", solver="liblinear", C=1.0, max_iter=200)
            clf.fit(x, y)
            return np.concatenate([[float(clf.intercept_[0])], clf.coef_.ravel()])
        from sklearn.linear_model import Lasso

        clf = Lasso(alpha=0.01, max_iter=500)
        clf.fit(x, y)
        return np.concatenate([[float(clf.intercept_)], clf.coef_.ravel()])
    except Exception:
        return _lasso_coef(x, y, logistic=logistic, use_sklearn=False)


def _impute_lasso_norm(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    *,
    select: bool = False,
) -> NDArray[np.floating]:
    del select
    x_full = add_intercept(np.asarray(x, dtype=np.float64))
    coef = _lasso_coef(x_full[ry], np.asarray(y, dtype=np.float64)[ry], logistic=False)
    _, beta_star, sigma_star = norm_draw(
        np.asarray(y, dtype=np.float64),
        ry,
        x_full,
        rng=rng,
    )
    beta_star = coef + (beta_star - coef) * 0.5  # blend LASSO point estimate with Bayes draw
    preds = x_full[wy] @ beta_star
    noise = rng.standard_normal(int(np.sum(wy))) * sigma_star
    return preds + noise


def _impute_lasso_logreg(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    *,
    select: bool = False,
) -> NDArray[np.floating]:
    del select
    try:
        x_full = add_intercept(np.asarray(x, dtype=np.float64))
        coef = _lasso_coef(x_full[ry], np.asarray(y, dtype=np.float64)[ry], logistic=True)
        eta = x_full[wy] @ coef
        prob = 1.0 / (1.0 + np.exp(-eta))
        return (rng.random(int(np.sum(wy))) <= prob).astype(np.float64)
    except Exception:
        return impute_logreg(y, ry, x, wy, rng)


register_method("lasso.norm", lambda *a, **k: _impute_lasso_norm(*a, **k, select=False))
register_method("lasso.logreg", lambda *a, **k: _impute_lasso_logreg(*a, **k, select=False))
register_method("lasso.select.norm", lambda *a, **k: _impute_lasso_norm(*a, **k, select=True))
register_method("lasso.select.logreg", lambda *a, **k: _impute_lasso_logreg(*a, **k, select=True))
