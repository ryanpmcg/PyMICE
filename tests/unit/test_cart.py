"""Tests for cart (CART) imputation method."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import mice
from pymice.methods.cart import impute_cart
from pymice.methods.registry import get_method, registered_methods
from pymice.types import VariableKind, VariableSpec

pytest.importorskip("sklearn")


def test_cart_registered():
    assert "cart" in registered_methods()
    assert get_method("cart") is impute_cart


def test_cart_regression_samples_leaf_donors():
    rng = np.random.default_rng(7)
    n = 40
    x = np.column_stack([np.linspace(0, 1, n), rng.normal(size=n)])
    y = x[:, 0] * 10 + rng.normal(scale=0.5, size=n)
    y[rng.random(n) < 0.3] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_cart(y=y, ry=ry, x=x, wy=wy, rng=rng, minbucket=3)
    assert out.shape == (int(np.sum(wy)),)
    assert np.all(np.isin(out, y[ry]))


def test_cart_classification_binary():
    rng = np.random.default_rng(2)
    n = 50
    x = rng.normal(size=(n, 2))
    y = (x[:, 0] + rng.normal(scale=0.5, size=n) > 0).astype(float)
    y[rng.random(n) < 0.25] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    specs = VariableSpec("y", VariableKind.BINARY, levels=(0.0, 1.0))
    out = impute_cart(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        rng=rng,
        levels=specs.levels,
        classification=True,
        minbucket=3,
    )
    assert np.all(np.isin(out, [0.0, 1.0]))


def test_cart_constant_class_shortcut():
    rng = np.random.default_rng(0)
    y = np.array([1.0, 1.0, 1.0, np.nan, np.nan])
    x = np.arange(5.0).reshape(-1, 1)
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_cart(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        rng=rng,
        levels=(1.0, 2.0),
        classification=True,
    )
    assert np.all(out == 1.0)


def test_cart_empty_predictors_uses_intercept():
    rng = np.random.default_rng(11)
    y = np.array([1.0, 2.0, 3.0, np.nan])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_cart(y=y, ry=ry, x=np.empty((4, 0)), wy=wy, rng=rng)
    assert np.isin(out[0], y[ry])


def test_mice_runs_with_cart_method():
    rng = np.random.default_rng(5)
    n = 30
    x1 = rng.normal(size=n)
    y = (x1 > 0).astype(float)
    x2 = rng.normal(size=n)
    data = np.column_stack([x1, x2, y])
    data[rng.random(n) < 0.2, 2] = np.nan
    names = ["x1", "x2", "event"]
    result = mice(
        data,
        column_names=names,
        method={"event": "cart"},
        m=2,
        maxit=2,
        seed=99,
    )
    imp = result.imp["event"]
    assert imp.shape == (int(np.sum(np.isnan(data[:, 2]))), 2)
    assert np.all(np.isin(imp, [0.0, 1.0]))


def test_cart_import_error_without_sklearn(monkeypatch):
    import pymice.methods.cart as cart_mod

    def _boom():
        raise ImportError(
            "The cart method requires scikit-learn. Install with: pip install pymice[ml]"
        )

    monkeypatch.setattr(cart_mod, "_sklearn_trees", _boom)
    with pytest.raises(ImportError, match="pymice\\[ml\\]"):
        impute_cart(
            y=np.array([1.0, np.nan]),
            ry=np.array([True, False]),
            x=np.array([[0.0], [1.0]]),
            wy=np.array([False, True]),
            rng=np.random.default_rng(0),
        )
