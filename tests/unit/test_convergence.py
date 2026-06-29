"""Tests for MICE sampler convergence diagnostics."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import mice
from pymice.diagnostics.convergence import convergence

ROOT = Path(__file__).resolve().parents[2]
NHANES = ROOT / "tests" / "data" / "nhanes.csv"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    with NHANES.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    matrix = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return matrix, names


def test_convergence_requires_multiple_imputations():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=1, maxit=3, seed=123)
    with pytest.raises(ValueError, match="m must be at least 2"):
        convergence(mids)


def test_convergence_requires_min_iterations():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=2, seed=123)
    with pytest.raises(ValueError, match="maxit must be at least 3"):
        convergence(mids)


def test_convergence_chain_mean_matches_r_nhanes_mean():
    """chainMean for mean imputation is constant across chains (R nhanes golden)."""
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)

    np.testing.assert_allclose(
        mids.chain_mean["bmi"],
        np.full((3, 2), 26.5625),
        rtol=0,
        atol=1e-6,
    )
    np.testing.assert_allclose(
        mids.chain_mean["hyp"],
        np.full((3, 2), 1.23529412),
        rtol=0,
        atol=1e-6,
    )
    np.testing.assert_allclose(
        mids.chain_mean["chl"],
        np.full((3, 2), 191.4),
        rtol=0,
        atol=1e-6,
    )


def test_convergence_returns_rows_per_variable_iteration():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    rows = convergence(mids)

    imputed = {"bmi", "hyp", "chl"}
    assert {r.variable for r in rows} == imputed
    assert len(rows) == len(imputed) * mids.iteration

    for var in imputed:
        var_rows = [r for r in rows if r.variable == var]
        assert [r.iteration for r in var_rows] == [1, 2, 3]
        assert var_rows[0].psrf is None
        assert all(r.psrf == 1.0 for r in var_rows[1:])
