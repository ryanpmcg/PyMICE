"""Survival models for complete imputed datasets (requires lifelines)."""

from __future__ import annotations

import re

import numpy as np
from numpy.typing import NDArray

from pymice.types import FitResult


def coxph(
    formula: str,
    data: NDArray[np.float64],
    column_names: list[str],
) -> FitResult:
    """Fit a Cox Proportional Hazards model on a numeric matrix (requires lifelines)."""
    try:
        import pandas as pd
        from lifelines import CoxPHFitter
    except ImportError as exc:
        raise ImportError(
            "The coxph method requires pandas and lifelines. Install with: pip install lifelines pandas"
        ) from exc

    # Parse formula: Surv(time, status) ~ x1 + x2
    match = re.match(
        r"^\s*Surv\s*\(\s*([^,\s]+)\s*,\s*([^)\s]+)\s*\)\s*~\s*(.+)$", formula
    )
    if not match:
        raise ValueError(
            "Cox PH formula must be in the format 'Surv(time, status) ~ predictors'"
        )

    time_col = match.group(1).strip()
    status_col = match.group(2).strip()
    pred_str = match.group(3).strip()

    from pymice.formulas import parse_regression_formula

    # Dummy formula to reuse existing parser
    dummy_formula = f"dummy ~ {pred_str}"
    _, predictors = parse_regression_formula(dummy_formula, column_names)

    from pymice.formulas import build_design_matrix, term_labels

    pred_names = term_labels(predictors)

    # Build design matrix (without intercept!)
    x = build_design_matrix(data, column_names, predictors)
    if pred_names[0] == "(Intercept)" or np.allclose(x[:, 0], 1.0):
        x = x[:, 1:]
        pred_names = pred_names[1:]

    time_idx = column_names.index(time_col)
    status_idx = column_names.index(status_col)

    df = pd.DataFrame(x, columns=pred_names)
    df[time_col] = data[:, time_idx]
    df[status_col] = data[:, status_idx]

    df = df.dropna()
    n = len(df)

    cph = CoxPHFitter()
    cph.fit(df, duration_col=time_col, event_col=status_col)

    summary = cph.summary
    estimate = {t: float(summary.loc[t, "coef"]) for t in pred_names}
    variance = {t: float(summary.loc[t, "se"] ** 2) for t in pred_names}

    df_residual = float(n - len(pred_names))

    # Log-likelihood can act as pseudo-RSS or deviance
    log_lik = float(cph.log_likelihood_)

    return FitResult(
        terms=pred_names,
        estimate=estimate,
        variance=variance,
        df_residual=df_residual,
        n_obs=int(n),
        rss=float(-2.0 * log_lik),  # Use -2 * log-likelihood for LRT
    )
