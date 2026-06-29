"""Tests for post-processing and squeeze."""

from __future__ import annotations

import numpy as np

from pymice import complete, mice
from pymice.postprocess import post_squeeze, squeeze


def test_squeeze_clips_values():
    x = np.array([-1.0, 1.5, 30.0], dtype=np.float64)
    out = squeeze(x, (1.0, 25.0))
    assert np.allclose(out, [1.0, 1.5, 25.0])


def test_post_squeeze_in_mice():
    data = np.array([[1.0, 10.0], [np.nan, 20.0], [3.0, np.nan]], dtype=np.float64)
    result = mice(
        data,
        column_names=["a", "b"],
        method={"a": "norm", "b": ""},
        m=1,
        maxit=2,
        seed=1,
        post={"a": post_squeeze(1.0, 25.0)},
    )
    filled = complete(result, 1)[:, 0]
    miss = np.isnan(data[:, 0])
    assert np.all(filled[miss] >= 1.0)
    assert np.all(filled[miss] <= 25.0)


def test_post_add_string_command():
    data = np.array([[100.0], [np.nan], [120.0]], dtype=np.float64)
    result = mice(
        data,
        column_names=["y"],
        method="norm",
        m=1,
        maxit=1,
        seed=2,
        post={"y": "imp[[j]][, i] <- imp[[j]][, i] + -20"},
    )
    base = mice(data, column_names=["y"], method="norm", m=1, maxit=1, seed=2)
    delta = complete(result, 1)[1, 0] - complete(base, 1)[1, 0]
    assert np.isclose(delta, -20.0, atol=1e-6)
