"""Optional R lme4 and scikit-learn backend helpers."""

from __future__ import annotations

import numpy as np
import pytest

from pymice.methods.r_lme4_backend import r_lme4_available, use_r_lme4_backend
from pymice.methods.sklearn_backend import sklearn_available, use_sklearn_backend


def test_use_r_lme4_backend_respects_env_disable(monkeypatch):
    monkeypatch.setenv("PYMICE_R_LMER", "0")
    assert use_r_lme4_backend() is False
    assert use_r_lme4_backend(explicit=True) is False


def test_use_sklearn_backend_respects_env_disable(monkeypatch):
    monkeypatch.setenv("PYMICE_SKLEARN", "0")
    assert use_sklearn_backend() is False
    assert use_sklearn_backend(explicit=True) is False


@pytest.mark.skipif(not sklearn_available(), reason="scikit-learn not installed")
def test_sklearn_available_when_installed():
    assert use_sklearn_backend() is True


@pytest.mark.r_backend
@pytest.mark.skipif(not r_lme4_available(), reason="R+lme4+mice not available")
def test_lme4_impute_r_smoke():
    from pymice.methods.r_lme4_backend import lme4_impute_r

    rng = np.random.default_rng(42)
    n = 40
    cluster = np.repeat(np.arange(4), n // 4)
    x_fix = rng.standard_normal((n, 1))
    y = 0.5 * x_fix[:, 0] + rng.standard_normal(n) * 0.3
    y[::5] = np.nan
    ry = np.isfinite(y)
    wy = ~ry
    x = np.column_stack([cluster.astype(np.float64), x_fix])
    type_vec = np.array([-2, 2], dtype=np.int_)

    out = lme4_impute_r(
        y,
        ry,
        x,
        type_vec,
        wy,
        method="lmer",
        seed=123,
    )
    assert out.shape == (int(np.sum(wy)),)
    assert np.all(np.isfinite(out))
