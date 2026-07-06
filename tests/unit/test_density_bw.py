"""Tests for R-compatible density bandwidth."""

from __future__ import annotations

import numpy as np
from scipy.stats import gaussian_kde

from pymice import data, densityplot
from pymice.diagnostics.density_bw import bw_nrd0, density_limits, nrd0_kde_factor


def test_density_limits_uses_three_bandwidth_pad():
    obs = __import__("numpy").array([20.4, 22.7, 26.3, 27.4, 30.1, 35.3], dtype=float)
    lo, hi = density_limits(obs)
    bw = bw_nrd0(obs)
    assert lo == obs.min() - 3.0 * bw
    assert hi == obs.max() + 3.0 * bw


def test_densityplot_xlim_matches_r_density_range():
    nhanes = data("nhanes")
    bmi = nhanes["bmi"].dropna().to_numpy()
    fig = densityplot(nhanes["bmi"], xlab="nhanes$bmi")
    lo, hi = density_limits(bmi)
    xlim = fig.axes[0].get_xlim()
    assert abs(xlim[0] - lo) < 1e-6
    assert abs(xlim[1] - hi) < 1e-6
    fig.clf()


def test_nrd0_kde_factor_scales_with_data():
    obs = np.array([20.4, 22.7, 26.3, 27.4, 30.1], dtype=np.float64)
    kde = gaussian_kde(obs, bw_method=nrd0_kde_factor)
    assert kde.factor > 0
    assert abs(kde.factor * np.std(obs, ddof=1) - bw_nrd0(obs)) < 1e-9
