"""Tests for Rubin pooling."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import mice, pool, pool_scalar, summary_pool, with_mids

ROOT = Path(__file__).resolve().parents[2]
NHANES = ROOT / "tests" / "data" / "nhanes.csv"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    with NHANES.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return data, names


def test_pool_scalar_matches_r_reference():
    """R: pool.scalar(Q=c(-1.5457,-1.428), U=c(0.9723^2,1.041^2), n=25, k=2)."""
    result = pool_scalar(
        q=[-1.5457, -1.428],
        u=[0.9723**2, 1.041**2],
        n=25,
        k=2,
    )
    assert result.m == 2
    np.testing.assert_allclose(result.qbar, -1.48685, rtol=0, atol=1e-4)
    np.testing.assert_allclose(result.ubar, 1.014524, rtol=0, atol=1e-4)
    np.testing.assert_allclose(result.b, 0.006926645, rtol=0, atol=1e-6)
    np.testing.assert_allclose(result.t, 1.024914, rtol=0, atol=1e-4)
    np.testing.assert_allclose(result.df, 20.97025, rtol=0, atol=1e-3)
    np.testing.assert_allclose(result.r, 0.01024122, rtol=0, atol=1e-5)
    np.testing.assert_allclose(result.fmi, 0.09272831, rtol=0, atol=1e-4)


def test_pool_workflow_nhanes_mean():
    """Full MICE → lm → pool workflow; mean imputation for stable comparison."""
    data, names = _load_nhanes()
    imp = mice(data, column_names=names, method="mean", m=3, maxit=3, seed=123)
    fits = with_mids(imp, formula="bmi ~ hyp + chl")
    assert fits.m == 3
    pooled = pool(fits)
    summary = summary_pool(pooled)

    # R reference (mice 3.19, seed=123, mean, m=3, maxit=3)
    r_est = {
        "(Intercept)": 20.30719251,
        "hyp": -0.93064108,
        "chl": 0.03868821,
    }
    for row in summary:
        term = row["term"]
        if term in r_est:
            np.testing.assert_allclose(row["estimate"], r_est[term], rtol=0, atol=1e-2)


def test_pool_requires_multiple_fits():
    from pymice.types import FitResult

    fit = FitResult(
        terms=["(Intercept)"],
        estimate={"(Intercept)": 1.0},
        variance={"(Intercept)": 0.1},
        df_residual=10.0,
        n_obs=12,
    )
    result = pool([fit])
    assert result.m == 1


def test_anova_workflow_nhanes():
    from pymice import anova

    data, names = _load_nhanes()
    imp = mice(data, column_names=names, method="mean", m=3, maxit=3, seed=123)

    # Nested models
    fit1 = with_mids(imp, formula="bmi ~ hyp")
    fit2 = with_mids(imp, formula="bmi ~ hyp + chl")

    res = anova(fit1, fit2)
    assert "F" in res
    assert res["df1"] == 1
    assert "chl" in res["extra_terms"]
    assert res["p_value"] >= 0.0

    # Test error when not nested
    fit3 = with_mids(imp, formula="bmi ~ age")
    with pytest.raises(ValueError, match="strictly nested"):
        anova(fit1, fit3)
