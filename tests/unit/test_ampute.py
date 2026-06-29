"""Tests for ampute missing-data simulation."""

from __future__ import annotations

import numpy as np

from pymice import ampute


def test_ampute_mcar_by_cases():
    rng = np.random.default_rng(0)
    data = rng.normal(size=(50, 3))
    result = ampute(data, prop=0.2, seed=1)
    assert result.amp.shape == data.shape
    assert np.isnan(result.amp).sum() > 0
    assert result.mech == "MCAR"
    assert result.bycases is True


def test_ampute_custom_pattern():
    data = np.ones((20, 2), dtype=np.float64)
    patterns = np.array([[1, 0], [0, 1]], dtype=np.int_)
    result = ampute(data, prop=0.5, patterns=patterns, freq=np.array([1.0, 0.0]), seed=2)
    miss1 = np.isnan(result.amp[:, 1])
    assert np.any(miss1)
    assert np.all(np.isfinite(result.amp[miss1, 0]))


def test_ampute_mar_smoke():
    rng = np.random.default_rng(0)
    data = rng.normal(size=(500, 3))
    result = ampute(data, mech="MAR", prop=0.3, seed=11)
    assert result.mech == "MAR"
    assert result.weights is not None
    assert np.isnan(result.amp).sum() > 0


def test_ampute_mnar_smoke():
    rng = np.random.default_rng(1)
    data = rng.normal(size=(500, 3))
    result = ampute(data, mech="MNAR", prop=0.3, seed=12)
    assert result.mech == "MNAR"
    assert np.isnan(result.amp).sum() > 0
