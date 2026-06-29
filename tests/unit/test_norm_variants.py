"""Unit tests for norm.boot and norm.predict."""

from __future__ import annotations

import numpy as np

from pymice import complete, mice
from pymice.methods.linear import add_intercept, estimice
from pymice.methods.norm_boot import impute_norm_boot
from pymice.methods.norm_predict import impute_norm_predict
from pymice.methods.registry import get_method, registered_methods

# Fixed arrays cross-checked against R mice v3.19.0 (mice.impute.norm.predict).
_R_NORM_PREDICT_Y = np.array(
    [
        1.7168957072809565,
        2.5428673125225147,
        np.nan,
        3.5270128400927923,
        4.30984618254784,
        np.nan,
        4.891853050244579,
        5.81674870559215,
        np.nan,
        6.4787602295835365,
        7.014552406289615,
        np.nan,
        8.465052893427693,
        8.337935181905493,
        9.300592257180737,
    ],
    dtype=np.float64,
)
_R_NORM_PREDICT_X = np.column_stack(
    [
        np.arange(15, dtype=np.float64),
        np.array(
            [
                -0.9891213503478509,
                -0.3677866514678832,
                1.2879252612892487,
                0.1939744191326132,
                0.9202308996398569,
                0.5771037912572513,
                -0.6364636463709805,
                0.5419522204102933,
                -0.3165954511658161,
                -0.32238911615896015,
                0.09716731867045719,
                -1.5259304065189514,
                1.1921661041016585,
                -0.6710896751741096,
                1.0002694196594604,
            ],
            dtype=np.float64,
        ),
    ]
)
_R_NORM_PREDICT_RY = ~np.isnan(_R_NORM_PREDICT_Y)
_R_NORM_PREDICT_WY = np.isnan(_R_NORM_PREDICT_Y)
_R_NORM_PREDICT_GOLDEN = np.array(
    [3.4580347544023, 4.73554846260578, 5.95710896972075, 7.08209771589735],
    dtype=np.float64,
)


def test_norm_variants_registered():
    assert {"norm.boot", "norm.predict"}.issubset(set(registered_methods()))
    assert get_method("norm.boot") is impute_norm_boot
    assert get_method("norm.predict") is impute_norm_predict


def test_norm_predict_is_deterministic():
    y = np.array([1.0, 2.0, 3.0, np.nan, 5.0, np.nan])
    x = np.column_stack([np.arange(6, dtype=float), np.ones(6)])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out1 = impute_norm_predict(y=y, ry=ry, x=x, wy=wy, rng=np.random.default_rng(0))
    out2 = impute_norm_predict(y=y, ry=ry, x=x, wy=wy, rng=np.random.default_rng(99))
    assert np.array_equal(out1, out2)


def test_norm_predict_matches_manual_ols():
    y = np.array([1.0, 2.0, 3.0, np.nan, 5.0, np.nan])
    x = np.column_stack([np.arange(6, dtype=float), np.ones(6)])
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    x_full = add_intercept(x)
    est = estimice(x_full[ry], y[ry])
    expected = x_full[wy] @ est.coef
    out = impute_norm_predict(y=y, ry=ry, x=x, wy=wy, rng=np.random.default_rng(0))
    np.testing.assert_allclose(out, expected)


def test_norm_predict_matches_r_reference():
    out = impute_norm_predict(
        y=_R_NORM_PREDICT_Y,
        ry=_R_NORM_PREDICT_RY,
        x=_R_NORM_PREDICT_X,
        wy=_R_NORM_PREDICT_WY,
        rng=np.random.default_rng(0),
    )
    np.testing.assert_allclose(out, _R_NORM_PREDICT_GOLDEN, rtol=0, atol=1e-5)


def test_norm_boot_is_reproducible():
    y = _R_NORM_PREDICT_Y
    x = _R_NORM_PREDICT_X
    ry = _R_NORM_PREDICT_RY
    wy = _R_NORM_PREDICT_WY
    kwargs = dict(y=y, ry=ry, x=x, wy=wy)
    out1 = impute_norm_boot(**kwargs, rng=np.random.default_rng(42))
    out2 = impute_norm_boot(**kwargs, rng=np.random.default_rng(42))
    np.testing.assert_allclose(out1, out2)


def test_norm_boot_differs_from_norm_predict():
    y = _R_NORM_PREDICT_Y
    x = _R_NORM_PREDICT_X
    ry = _R_NORM_PREDICT_RY
    wy = _R_NORM_PREDICT_WY
    kwargs = dict(y=y, ry=ry, x=x, wy=wy)
    pred = impute_norm_predict(**kwargs, rng=np.random.default_rng(0))
    boot = impute_norm_boot(**kwargs, rng=np.random.default_rng(99))
    assert not np.allclose(pred, boot)


def test_norm_boot_r_bootstrap_indices_match_coef_sigma():
    """Bootstrap fit matches R when using the same resampled rows."""
    x_full = add_intercept(_R_NORM_PREDICT_X)
    x_obs = x_full[_R_NORM_PREDICT_RY]
    y_obs = _R_NORM_PREDICT_Y[_R_NORM_PREDICT_RY]
    boot_idx = np.array([0, 5, 5, 4, 2, 9, 1, 5, 3, 3, 3])
    est = estimice(x_obs[boot_idx], y_obs[boot_idx])
    n1 = int(np.sum(_R_NORM_PREDICT_RY))
    sigma = float(np.sqrt(np.sum(est.residuals**2) / max(n1 - x_full.shape[1] - 1, 1)))
    np.testing.assert_allclose(
        est.coef,
        [2.05179743846724, 0.504197186945949, 0.308723999327491],
        rtol=0,
        atol=1e-6,
    )
    np.testing.assert_allclose(sigma, 0.07908219, rtol=0, atol=1e-6)


def test_norm_predict_mice_end_to_end():
    """Full MICE run with norm.predict fills all missing cells."""
    data = _R_NORM_PREDICT_X.copy()
    names = ["x0", "x1"]
    data[2, 0] = np.nan
    data[5, 1] = np.nan
    result = mice(data, column_names=names, method="norm.predict", m=1, maxit=1, seed=1)
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
