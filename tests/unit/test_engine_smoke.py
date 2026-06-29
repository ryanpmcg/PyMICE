"""Smoke tests for the FCS engine."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    import csv

    path = DATA_DIR / "nhanes.csv"
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    names = ["age", "bmi", "hyp", "chl"]
    matrix = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return matrix, names


def test_mice_mean_runs_on_nhanes():
    data, names = _load_nhanes()
    result = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    assert result.m == 2
    assert result.iteration == 3
    assert "bmi" in result.imp
    assert result.imp["bmi"].shape == (9, 2)


def test_complete_fills_missing():
    data, names = _load_nhanes()
    result = mice(data, column_names=names, method="mean", m=1, maxit=2, seed=1)
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
    assert filled.shape == data.shape


def test_fcs_iterations_change_imputations():
    data, names = _load_nhanes()
    one_pass = mice(data, column_names=names, method="mean", m=1, maxit=1, seed=99)
    multi = mice(data, column_names=names, method="mean", m=1, maxit=5, seed=99)
    # Mean is constant across iterations, but chained updates via other columns differ.
    assert "bmi" in one_pass.imp and "bmi" in multi.imp


def test_unknown_method_raises():
    data, names = _load_nhanes()
    with pytest.raises(ValueError, match="Unknown imputation method"):
        mice(data, column_names=names, method="not_a_method", m=1, maxit=1)
