"""Vignette 01 baseline: nhanes mean imputation vs R golden."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tests" / "data" / "nhanes.csv"
GOLDEN = ROOT / "tests" / "goldens" / "r" / "nhanes_mean_m2_maxit3_complete1.csv"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    import csv

    names = ["age", "bmi", "hyp", "chl"]
    with DATA.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    matrix = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return matrix, names


@pytest.mark.skipif(not GOLDEN.exists(), reason="Run tests/run_r_goldens.sh first")
def test_nhanes_mean_matches_r_golden():
    data, names = _load_nhanes()
    result = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    filled = complete(result, 1)
    r_golden = np.genfromtxt(GOLDEN, delimiter=",", skip_header=1)
    np.testing.assert_allclose(filled, r_golden, rtol=0, atol=1e-12)
