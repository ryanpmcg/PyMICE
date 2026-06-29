"""Tests for passive imputation."""

from __future__ import annotations

import numpy as np

from pymice import complete, mice
from pymice.passive import evaluate_passive, is_passive


def test_is_passive_detects_formula():
    assert is_passive("~ I(sws + ps)")
    assert not is_passive("pmm")


def test_evaluate_passive_sum():
    data = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 9.0]], dtype=np.float64)
    names = ["sws", "ps", "ts"]
    wy = np.array([True, True])
    out = evaluate_passive("~ I(sws + ps)", data, names, wy)
    np.testing.assert_allclose(out, [3.0, 9.0])


def test_evaluate_passive_r_caret_power():
    data = np.array([[70.0, 175.0, np.nan]], dtype=np.float64)
    names = ["wgt", "hgt", "bmi"]
    wy = np.array([True])
    out = evaluate_passive("~ I(wgt / (hgt / 100)^2)", data, names, wy)
    np.testing.assert_allclose(out, [70.0 / (175.0 / 100.0) ** 2], rtol=1e-9)


def test_mice_passive_imputes_sum():
    rng = np.random.default_rng(7)
    n = 12
    sws = rng.random(n) * 5
    ps = rng.random(n) * 3
    ts = sws + ps
    data = np.column_stack([sws, ps, ts])
    names = ["sws", "ps", "ts"]
    data[2:6, 2] = np.nan

    result = mice(
        data,
        column_names=names,
        method={"ts": "~ I(sws + ps)"},
        m=1,
        maxit=2,
        seed=11,
    )
    filled = complete(result, 1)
    expected = filled[:, 0] + filled[:, 1]
    np.testing.assert_allclose(filled[2:6, 2], expected[2:6], rtol=0, atol=1e-9)
