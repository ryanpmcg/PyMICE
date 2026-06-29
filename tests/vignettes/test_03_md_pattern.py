"""Vignette 03 missingness inspection: md.pattern on nhanes."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice import md_pattern

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tests" / "data" / "nhanes.csv"


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    with DATA.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    matrix = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return matrix, names


def test_nhanes_md_pattern_vignette_counts():
    """Vignette 01/03: nhanes has 5 missingness patterns; complete cases = 13."""
    data, names = _load_nhanes()
    result = md_pattern(data, names)
    assert result.n_patterns == 5
    assert result.pattern_counts[0] == 13
    assert result.column_missing["age"] == 0
    assert result.column_missing["chl"] == 10
    assert int(result.matrix[-1, -1]) == 27
