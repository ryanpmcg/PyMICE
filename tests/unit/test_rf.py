"""Tests for Random Forest (rf) imputation method."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import mice
from pymice.methods.registry import get_method, registered_methods
from pymice.methods.rf import impute_rf

pytest.importorskip("sklearn")


def test_rf_registered():
    assert "rf" in registered_methods()
    assert get_method("rf") is impute_rf


def test_rf_regression_runs():
    rng = np.random.default_rng(7)
    n = 50
    x = np.column_stack([np.linspace(0, 1, n), rng.normal(size=n)])
    y = x[:, 0] * 10 + rng.normal(scale=0.5, size=n)
    y[rng.random(n) < 0.2] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_rf(y=y, ry=ry, x=x, wy=wy, rng=rng, rfiter=5, minbucket=3)
    assert out.shape == (int(np.sum(wy)),)
    assert np.all(np.isfinite(out))


def test_rf_classification_binary():
    rng = np.random.default_rng(2)
    n = 60
    x = rng.normal(size=(n, 2))
    y = (x[:, 0] + rng.normal(scale=0.5, size=n) > 0).astype(float)
    y[rng.random(n) < 0.2] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_rf(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        rng=rng,
        levels=(0.0, 1.0),
        classification=True,
        rfiter=5,
        minbucket=3,
    )
    assert np.all(np.isin(out, [0.0, 1.0]))


def test_rf_constant_class_shortcut():
    rng = np.random.default_rng(0)
    y = np.array([2.0, 2.0, 2.0, np.nan, np.nan])
    x = np.arange(5.0).reshape(-1, 1)
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_rf(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        rng=rng,
        levels=(1.0, 2.0),
        classification=True,
    )
    assert np.all(out == 2.0)


def test_mice_runs_with_rf_method():
    rng = np.random.default_rng(42)
    n = 40
    x1 = rng.normal(size=n)
    y = x1 * 2.0 + rng.normal(scale=0.1, size=n)
    x2 = rng.normal(size=n)
    data = np.column_stack([x1, x2, y])
    data[rng.random(n) < 0.2, 2] = np.nan
    names = ["x1", "x2", "y"]
    result = mice(
        data,
        column_names=names,
        method={"y": "rf"},
        m=2,
        maxit=2,
        seed=1,
    )
    imp = result.imp["y"]
    assert imp.shape == (int(np.sum(np.isnan(data[:, 2]))), 2)
    assert np.all(np.isfinite(imp))


def test_rf_import_error_without_sklearn(monkeypatch):
    import pymice.methods.rf as rf_mod

    def _boom():
        raise ImportError(
            "The rf method requires scikit-learn. Install with: pip install pymice-fcs[ml]"
        )

    monkeypatch.setattr(rf_mod, "_sklearn_ensemble", _boom)
    with pytest.raises(ImportError, match="pymice-fcs\\[ml\\]"):
        impute_rf(
            y=np.array([1.0, np.nan]),
            ry=np.array([True, False]),
            x=np.array([[0.0], [1.0]]),
            wy=np.array([False, True]),
            rng=np.random.default_rng(0),
        )
