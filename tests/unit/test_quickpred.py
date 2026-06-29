"""Tests for quickpred predictor selection."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice.quickpred import quickpred

ROOT = Path(__file__).resolve().parents[2]


def _load_nhanes() -> np.ndarray:
    names = ["age", "bmi", "hyp", "chl"]
    with (ROOT / "tests" / "data" / "nhanes.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    return np.array(
        [[float(r[n]) if r[n] not in ("", "NA") else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )


def test_quickpred_nhanes_mincor_03():
    data = _load_nhanes()
    pred = quickpred(data, mincor=0.3, column_names=["age", "bmi", "hyp", "chl"])
    expected = np.array(
        [
            [0, 0, 0, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 0],
        ],
        dtype=np.int_,
    )
    assert np.array_equal(pred, expected)
