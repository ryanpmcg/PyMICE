"""Survival models for complete imputed datasets (requires lifelines)."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pymice.types import FitResult

COX_SBPGP_TERM = "C(sbpgp, contr.treatment(6, base = 3))"
LEIDEN_COX_FORMULA = (
    "Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, base = 3)) + strata(sexe, agegp)"
)
SBPGP_BREAKS = [50.0, 124.0, 144.0, 164.0, 184.0, 200.0, 500.0]
AGEGP_BREAKS = [85.0, 90.0, 95.0, 110.0]


def _cox_term_name(level: int) -> str:
    return f"{COX_SBPGP_TERM}{level}"


def _require_lifelines():
    try:
        import pandas as pd
        from lifelines import CoxPHFitter
    except ImportError as exc:
        raise ImportError(
            "The coxph method requires pandas and lifelines. Install with: pip install lifelines pandas"
        ) from exc
    return pd, CoxPHFitter


def _prepare_leiden_cox_frame(
    data: NDArray[np.float64],
    column_names: list[str],
) -> tuple[Any, list[str]]:
    """Cut ``rrsyst``/``lftanam`` and build treatment-coded sbpgp dummies (base level 3)."""
    pd, _ = _require_lifelines()

    idx = {
        name: column_names.index(name) for name in ("rrsyst", "lftanam", "dwa", "survda", "sexe")
    }
    sbpgp = pd.cut(
        data[:, idx["rrsyst"]],
        bins=SBPGP_BREAKS,
        right=True,
        include_lowest=True,
    )
    agegp = pd.cut(
        data[:, idx["lftanam"]],
        bins=AGEGP_BREAKS,
        right=True,
        include_lowest=True,
    )
    df = pd.DataFrame(
        {
            "survda": data[:, idx["survda"]],
            "dead": 1.0 - data[:, idx["dwa"]],
            "sexe": data[:, idx["sexe"]],
            "sbpgp": sbpgp,
            "agegp": agegp,
        }
    )
    df = df.dropna()
    categories = df["sbpgp"].cat.categories
    base_idx = 2
    pred_cols: list[str] = []
    for i, level in enumerate(categories):
        if i == base_idx:
            continue
        col = f"sbpgp_{i + 1}"
        df[col] = (df["sbpgp"] == level).astype(float)
        pred_cols.append(col)
    return df, pred_cols


def leiden_coxph(
    data: NDArray[np.float64] | Any,
    column_names: list[str] | None = None,
) -> FitResult:
    """Leiden sensitivity Cox model (``cda`` expression from vignette 06)."""
    from pymice.data_input import prepare_tabular_input

    matrix, column_names = prepare_tabular_input(data, column_names)
    _pd, CoxPHFitter = _require_lifelines()

    df, pred_cols = _prepare_leiden_cox_frame(matrix, column_names)
    n = len(df)
    cph = CoxPHFitter()
    cph.fit(
        df,
        duration_col="survda",
        event_col="dead",
        strata=["sexe", "agegp"],
        formula=" + ".join(pred_cols),
    )

    summary = cph.summary
    terms: list[str] = []
    estimate: dict[str, float] = {}
    variance: dict[str, float] = {}
    exp_coef: dict[str, float] = {}
    se_coef: dict[str, float] = {}
    z_vals: dict[str, float] = {}
    p_vals: dict[str, float] = {}

    level_map = [1, 2, 4, 5, 6]
    for i, row_name in enumerate(summary.index):
        term = _cox_term_name(level_map[i])
        terms.append(term)
        estimate[term] = float(summary.loc[row_name, "coef"])
        se = float(summary.loc[row_name, "se(coef)"])
        variance[term] = se * se
        exp_coef[term] = float(summary.loc[row_name, "exp(coef)"])
        se_coef[term] = se
        z_vals[term] = float(summary.loc[row_name, "z"])
        p_vals[term] = float(summary.loc[row_name, "p"])

    n_events = int(df["dead"].sum())
    lrt_p = float(cph.log_likelihood_ratio_test().p_value)

    return FitResult(
        terms=terms,
        estimate=estimate,
        variance=variance,
        df_residual=float(n - len(terms)),
        n_obs=int(n),
        rss=float(-2.0 * cph.log_likelihood_),
        meta={
            "model": "coxph",
            "formula": LEIDEN_COX_FORMULA,
            "exp_coef": exp_coef,
            "se_coef": se_coef,
            "z": z_vals,
            "p": p_vals,
            "lrt_stat": float(cph.log_likelihood_ratio_test().test_statistic),
            "lrt_df": float(len(terms)),
            "lrt_p": lrt_p,
            "n_events": n_events,
        },
    )


def coxph(
    formula: str,
    data: NDArray[np.float64] | Any,
    column_names: list[str] | None = None,
) -> FitResult:
    """Fit a Cox Proportional Hazards model on a matrix or DataFrame (requires lifelines)."""
    if "sbpgp" in formula or "strata(sexe" in formula.replace(" ", ""):
        return leiden_coxph(data, column_names)

    from pymice.data_input import prepare_tabular_input

    matrix, column_names = prepare_tabular_input(data, column_names)
    data = matrix
    pd, CoxPHFitter = _require_lifelines()

    match = re.match(r"^\s*Surv\s*\(\s*([^,\s]+)\s*,\s*([^)\s]+)\s*\)\s*~\s*(.+)$", formula)
    if not match:
        raise ValueError("Cox PH formula must be in the format 'Surv(time, status) ~ predictors'")

    time_col = match.group(1).strip()
    status_col = match.group(2).strip()
    pred_str = match.group(3).strip()

    from pymice.formulas import build_design_matrix, parse_regression_formula, term_labels

    _, predictors = parse_regression_formula(f"{time_col} ~ {pred_str}", column_names)
    pred_names = term_labels(predictors)

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
    se_col = "se(coef)" if "se(coef)" in summary.columns else "se"
    variance = {t: float(summary.loc[t, se_col] ** 2) for t in pred_names}
    df_residual = float(n - len(pred_names))
    log_lik = float(cph.log_likelihood_)

    return FitResult(
        terms=pred_names,
        estimate=estimate,
        variance=variance,
        df_residual=df_residual,
        n_obs=int(n),
        rss=float(-2.0 * log_lik),
    )
