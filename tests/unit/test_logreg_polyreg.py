"""Tests for categorical imputation methods."""

from __future__ import annotations

import numpy as np

from pymice import complete, mice
from pymice.methods.logreg import impute_logreg
from pymice.methods.polyreg import impute_polyreg
from pymice.types import VariableKind, VariableSpec


def test_logreg_binary_output():
    rng = np.random.default_rng(7)
    y = np.array([0.0, 1.0, 0.0, 1.0, np.nan, np.nan])
    x = np.array([[1.0], [2.0], [1.5], [3.0], [2.5], [0.5]])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_logreg(y=y, ry=ry, x=x, wy=wy, rng=rng)
    assert set(np.unique(out)).issubset({0.0, 1.0})


def test_polyreg_multiclass_output():
    rng = np.random.default_rng(11)
    y = np.array([1.0, 2.0, 3.0, 1.0, np.nan, np.nan])
    x = np.arange(6.0).reshape(-1, 1)
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_polyreg(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        rng=rng,
        levels=(1.0, 2.0, 3.0),
    )
    assert set(np.unique(out)).issubset({1.0, 2.0, 3.0})


def test_mice_with_explicit_factor_specs():
    data = np.array(
        [
            [1.0, 10.0, 1.0],
            [2.0, np.nan, 2.0],
            [3.0, 12.0, np.nan],
        ],
        dtype=np.float64,
    )
    specs = [
        VariableSpec("age", VariableKind.UNORDERED, levels=(1.0, 2.0, 3.0)),
        VariableSpec("score", VariableKind.NUMERIC),
        VariableSpec("flag", VariableKind.BINARY, levels=(1.0, 2.0)),
    ]
    result = mice(
        data,
        column_names=["age", "score", "flag"],
        variable_specs=specs,
        method={"age": "sample", "score": "norm", "flag": "logreg"},
        m=1,
        maxit=2,
        seed=5,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
