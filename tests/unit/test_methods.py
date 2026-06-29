"""Unit tests for Tier A imputation methods."""

from __future__ import annotations

import numpy as np
import pytest

from pymice.methods.linear import matchindex, norm_draw
from pymice.methods.mean import impute_mean
from pymice.methods.pmm import impute_pmm
from pymice.methods.registry import get_method, registered_methods
from pymice.methods.sample import impute_sample


def test_all_tier_a_methods_registered():
    expected = {
        "mean",
        "sample",
        "pmm",
        "norm",
        "norm.nob",
        "norm.boot",
        "norm.predict",
        "logreg",
        "polyreg",
    }
    assert expected.issubset(set(registered_methods()))


def test_mean_imputation():
    y = np.array([1.0, np.nan, 3.0, np.nan, 5.0])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_mean(y=y, ry=ry, x=np.empty((5, 0)), wy=wy)
    assert np.allclose(out, 3.0)


def test_sample_imputation_reproducible():
    y = np.array([1.0, 2.0, 3.0, np.nan, np.nan])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    rng = np.random.default_rng(42)
    out1 = impute_sample(y=y, ry=ry, x=np.empty((5, 0)), wy=wy, rng=rng)
    rng = np.random.default_rng(42)
    out2 = impute_sample(y=y, ry=ry, x=np.empty((5, 0)), wy=wy, rng=rng)
    assert np.array_equal(out1, out2)
    assert set(out1).issubset({1.0, 2.0, 3.0})


def test_pmm_returns_observed_donors():
    rng = np.random.default_rng(1)
    y = np.array([1.0, 2.0, 3.0, 4.0, np.nan, np.nan])
    x = np.arange(6.0).reshape(-1, 1)
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_pmm(y=y, ry=ry, x=x, wy=wy, rng=rng, donors=3)
    assert np.all(np.isin(out, y[ry]))


def test_norm_draw_is_stochastic():
    from pymice.methods.linear import add_intercept

    y = np.array([1.2, 2.1, 2.8, 4.3, 5.1])
    x = add_intercept(np.arange(5.0).reshape(-1, 1))
    ry = np.ones(5, dtype=bool)
    betas = [norm_draw(y, ry, x, rng=np.random.default_rng(s))[1] for s in range(50)]
    assert any(not np.allclose(betas[0], b) for b in betas[1:])


def test_matchindex_bounds():
    rng = np.random.default_rng(99)
    d = np.array([-5.0, 5.0, 0.0, 10.0, 12.0])
    t = np.array([-6.0, -4.0, 0.0, 2.0, 4.0])
    idx = matchindex(d, t, k=1, rng=rng)
    assert idx.min() >= 0
    assert idx.max() < d.size


def test_unknown_method_raises():
    with pytest.raises(ValueError, match="Unknown"):
        get_method("not_real")
