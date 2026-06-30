"""Tests for multivariate pooling statistics (D1, D2, D3), GLM, and Cox PH."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import (
    D1,
    D2,
    D3,
    coxph,
    glm,
    load_nhanes,
    mice,
    pool,
    summary_pool,
    with_mids,
)


def test_glm_binomial_fit():
    rng = np.random.default_rng(0)
    n = 100
    x = rng.normal(size=n)
    # Binary target
    y = (x + rng.normal(scale=0.5, size=n) > 0).astype(float)
    data = np.column_stack([y, x])
    names = ["y", "x"]

    # Test single glm fit
    fit = glm("y ~ x", data, names, family="binomial")
    assert fit.terms == ["(Intercept)", "x"]
    assert "(Intercept)" in fit.estimate
    assert fit.rss is not None  # binomial deviance
    assert fit.n_obs == n

    # Test gaussian family fallback
    fit_gauss = glm("y ~ x", data, names, family="gaussian")
    assert fit_gauss.terms == ["(Intercept)", "x"]


def test_glm_binomial_pooling_workflow():
    data, names = load_nhanes()
    # Recode hyp to 0 and 1 (from 1 and 2) for standard logistic regression
    hyp_col = names.index("hyp")
    # Observed values are 1 and 2, NAs are nan
    hyp_vals = data[:, hyp_col]
    mask = ~np.isnan(hyp_vals)
    data[mask, hyp_col] = hyp_vals[mask] - 1.0

    imp = mice(data, column_names=names, method="mean", m=3, maxit=2, seed=123)

    # Fit logistic models on mids
    fit = with_mids(imp, formula="hyp ~ bmi + age", family="binomial")
    assert fit.m == 3
    pooled = pool(fit)
    summary = summary_pool(pooled)

    for row in summary:
        assert np.isfinite(row["estimate"])
        assert np.isfinite(row["std_error"])


def test_multivariate_statistics_d1_d2_d3():
    data, names = load_nhanes()
    imp = mice(data, column_names=names, method="mean", m=3, maxit=2, seed=123)

    # Fit nested models
    fit_s = with_mids(imp, formula="bmi ~ age")
    fit_l = with_mids(imp, formula="bmi ~ age + hyp")

    # D1 (Wald test / anova)
    res_d1 = D1(fit_s, fit_l)
    assert "F" in res_d1
    assert res_d1["df1"] == 1
    assert res_d1["p_value"] >= 0.0

    # D2 (averaged F)
    res_d2 = D2(fit_s, fit_l)
    assert "F" in res_d2
    assert res_d2["df1"] == 1
    assert res_d2["p_value"] >= 0.0

    # D3 (likelihood ratio test)
    res_d3 = D3(fit_s, fit_l)
    assert "statistic" in res_d3
    assert res_d3["df"] == 1
    assert res_d3["p_value"] >= 0.0


def test_coxph_importer_or_run():
    # Attempt to import lifelines to determine if we run or mock
    try:
        import lifelines  # noqa: F401

        has_lifelines = True
    except ImportError:
        has_lifelines = False

    if not has_lifelines:
        # Verify it raises ImportError when lifelines is missing
        data = np.array([[10.0, 1.0, 1.5], [12.0, 0.0, 2.0]], dtype=np.float64)
        names = ["time", "status", "x"]
        with pytest.raises(ImportError, match="requires pandas and lifelines"):
            coxph("Surv(time, status) ~ x", data, names)
    else:
        # Run test fit if lifelines is installed
        rng = np.random.default_rng(0)
        n = 50
        time = rng.exponential(scale=10, size=n)
        status = rng.binomial(1, 0.8, size=n)
        x = rng.normal(size=n)
        data = np.column_stack([time, status, x])
        names = ["time", "status", "x"]

        fit = coxph("Surv(time, status) ~ x", data, names)
        assert fit.terms == ["x"]
        assert "x" in fit.estimate
        assert fit.df_residual == 49.0

        # Verify automatic routing in with_mids
        imp = mice(data, column_names=names, method="mean", m=2, maxit=1, seed=12)
        fit_mids = with_mids(imp, formula="Surv(time, status) ~ x")
        assert fit_mids.m == 2
        assert fit_mids.analyses[0].terms == ["x"]
