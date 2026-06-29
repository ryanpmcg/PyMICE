"""Tests for missing-data pattern diagnostics."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice.diagnostics.md_pattern import md_pattern

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


def test_md_pattern_shape():
    data = np.array(
        [
            [1.0, 2.0, 3.0],
            [np.nan, 2.0, 3.0],
            [1.0, np.nan, 3.0],
        ],
        dtype=np.float64,
    )
    result = md_pattern(data)
    assert result.matrix.ndim == 2
    assert result.matrix.shape[1] == data.shape[1] + 1
    assert result.n_patterns == 3


def test_md_pattern_nhanes_matches_r():
    """R md.pattern(nhanes): 5 patterns; footer 0 8 9 10 27."""
    data, names = _load_nhanes()
    result = md_pattern(data, names)

    assert result.n_patterns == 5
    assert result.column_names == ["age", "hyp", "bmi", "chl"]
    assert result.pattern_counts == [13, 3, 1, 1, 7]
    assert result.column_missing == {"age": 0, "hyp": 8, "bmi": 9, "chl": 10}

    expected = np.array(
        [
            [1, 1, 1, 1, 0],
            [1, 1, 1, 0, 1],
            [1, 1, 0, 1, 1],
            [1, 0, 0, 1, 2],
            [1, 0, 0, 0, 3],
            [0, 8, 9, 10, 27],
        ],
        dtype=np.int_,
    )
    np.testing.assert_array_equal(result.matrix, expected)
