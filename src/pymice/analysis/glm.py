"""Generalized linear models for complete imputed datasets."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.formulas import build_design_matrix, parse_regression_formula, term_labels
from pymice.types import FitResult


def glm(
    formula: str,
    data: NDArray[np.float64],
    column_names: list[str],
    family: str = "binomial",
) -> FitResult:
    """Fit Generalized Linear Models (e.g. logistic regression) on a numeric matrix."""
    if family == "gaussian":
        from pymice.analysis.ols import lm

        return lm(formula, data, column_names)

    if family != "binomial":
        raise ValueError(
            f"Family '{family}' is not supported. Supported families: 'binomial', 'gaussian'"
        )

    y_name, predictors = parse_regression_formula(formula, column_names)
    y_idx = column_names.index(y_name)

    y = data[:, y_idx]
    x = build_design_matrix(data, column_names, predictors)
    mask = np.isfinite(y) & np.isfinite(x).all(axis=1)
    y = y[mask]
    x = x[mask]
    n, p = x.shape

    from pymice.methods.logreg import _fit_logistic_irls

    weights = np.ones(n, dtype=np.float64)
    beta, cov = _fit_logistic_irls(x, y, weights)

    df_residual = float(n - p)
    terms = term_labels(predictors)
    estimate = {t: float(v) for t, v in zip(terms, beta, strict=True)}
    variance = {t: float(v) for t, v in zip(terms, np.diag(cov), strict=True)}

    # For binomial, deviance can act as RSS (or deviance residuals)
    # R: deviance = 2 * sum(y * log(y/mu) + (1-y) * log((1-y)/(1-mu)))
    # We can approximate with sum of squared residuals for simplicity or deviance
    eta = x @ beta
    mu = 1.0 / (1.0 + np.exp(-eta))
    mu = np.clip(mu, 1e-9, 1.0 - 1e-9)
    y_clip = np.clip(y, 1e-9, 1.0 - 1e-9)
    deviance = 2.0 * np.sum(
        y_clip * np.log(y_clip / mu) + (1.0 - y_clip) * np.log((1.0 - y_clip) / (1.0 - mu))
    )

    return FitResult(
        terms=terms,
        estimate=estimate,
        variance=variance,
        df_residual=df_residual,
        n_obs=int(n),
        rss=float(deviance),
    )
