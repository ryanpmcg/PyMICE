"""Ordinary least squares for complete imputed datasets."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.formulas import build_design_matrix, parse_regression_formula, term_labels
from pymice.types import FitResult


def lm(
    formula: str,
    data: NDArray[np.float64],
    column_names: list[str],
) -> FitResult:
    """Fit OLS model ``y ~ x1 + log10(x2) + ...`` on a numeric matrix."""
    y_name, predictors = parse_regression_formula(formula, column_names)
    y_idx = column_names.index(y_name)

    y = data[:, y_idx]
    x = build_design_matrix(data, column_names, predictors)
    mask = np.isfinite(y) & np.isfinite(x).all(axis=1)
    y = y[mask]
    x = x[mask]
    n, p = x.shape

    coef, _residuals, rank, _sing = np.linalg.lstsq(x, y, rcond=None)
    if rank < p:
        raise ValueError("Model matrix is rank deficient")

    df_residual = float(n - p)
    rss = float(np.sum((y - x @ coef) ** 2))
    sigma2 = rss / df_residual if df_residual > 0 else float("nan")

    xtx_inv = np.linalg.inv(x.T @ x)
    var_coef = sigma2 * xtx_inv
    se = np.sqrt(np.diag(var_coef))

    terms = term_labels(predictors)
    estimate = {t: float(v) for t, v in zip(terms, coef, strict=True)}
    variance = {t: float(v) for t, v in zip(terms, se**2, strict=True)}

    return FitResult(
        terms=terms,
        estimate=estimate,
        variance=variance,
        df_residual=df_residual,
        n_obs=int(n),
    )
