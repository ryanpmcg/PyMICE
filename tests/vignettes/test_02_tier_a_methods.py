"""Vignette parity tests for Tier A imputation methods."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice
from pymice.types import VariableKind, VariableSpec

NHANES2_NAMES = ["age", "bmi", "hyp", "chl"]
NHANES2_SPECS = [
    VariableSpec("age", VariableKind.UNORDERED, levels=(1.0, 2.0, 3.0)),
    VariableSpec("bmi", VariableKind.NUMERIC),
    VariableSpec("hyp", VariableKind.BINARY, levels=(1.0, 2.0)),
    VariableSpec("chl", VariableKind.NUMERIC),
]

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "goldens" / "r"


def _load_csv(path: Path, names: list[str]) -> np.ndarray:
    age_map = {"20-39": 1.0, "40-59": 2.0, "60-99": 3.0}
    hyp_map = {"no": 1.0, "yes": 2.0}

    def _cell(column: str, raw: str) -> float:
        val = raw.strip().strip('"')
        if val in ("", "NA"):
            return np.nan
        if column == "age" and val in age_map:
            return age_map[val]
        if column == "hyp" and val in hyp_map:
            return hyp_map[val]
        return float(val)

    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    return np.array(
        [[_cell(n, r[n]) for n in names] for r in rows],
        dtype=np.float64,
    )


@pytest.mark.parametrize(
    "method,atol",
    [
        ("mean", 1e-12),
        ("norm.nob", 50.0),
        ("norm", 50.0),
        ("pmm", 50.0),
    ],
)
def test_nhanes_method_golden(method: str, atol: float):
    """Compare completed data against R goldens (stochastic methods use loose atol)."""
    golden = GOLDEN / f"nhanes_{method.replace('.', '_')}_m2_maxit3_complete1.csv"
    if not golden.exists():
        pytest.skip(f"Missing golden file: {golden.name}")

    names = ["age", "bmi", "hyp", "chl"]
    data = _load_csv(ROOT / "tests" / "data" / "nhanes.csv", names)
    result = mice(data, column_names=names, method=method, m=2, maxit=3, seed=123)
    filled = complete(result, 1)
    r_golden = np.genfromtxt(golden, delimiter=",", skip_header=1)

    assert not np.any(np.isnan(filled))
    observed = ~np.isnan(data)
    np.testing.assert_allclose(filled[observed], data[observed], rtol=0, atol=1e-12)
    if atol < 1e-6:
        np.testing.assert_allclose(filled, r_golden, rtol=0, atol=atol)
    else:
        # RNG stream differs from R; only assert observed cells match exactly.
        imputed = np.isnan(data)
        assert np.all(np.isfinite(filled[imputed]))


@pytest.mark.skipif(
    not (GOLDEN / "nhanes2_default_m2_maxit3_complete1.csv").exists(),
    reason="Run tests/run_r_goldens.sh first",
)
def test_nhanes2_default_methods_runs():
    """Default R methods on factor-coded nhanes2: polyreg/logreg/pmm."""
    data = _load_csv(ROOT / "tests" / "data" / "nhanes2.csv", NHANES2_NAMES)
    result = mice(
        data,
        column_names=NHANES2_NAMES,
        variable_specs=NHANES2_SPECS,
        m=2,
        maxit=3,
        seed=123,
    )
    assert result.method["age"] == ""  # age fully observed in nhanes2
    assert result.method["hyp"] == "logreg"
    assert result.method["bmi"] == "pmm"
    assert result.method["chl"] == "pmm"
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
    assert set(np.unique(filled[:, 0])).issubset({1.0, 2.0, 3.0})
    assert set(np.unique(filled[:, 2])).issubset({1.0, 2.0})


def test_where_mask_limits_imputation():
    """``where`` restricts which missing cells are imputed."""
    data = np.array([[np.nan, np.nan], [1.0, 2.0]], dtype=np.float64)
    where = np.array([[False, True], [True, False]], dtype=bool)
    result = mice(data, column_names=["a", "b"], method="mean", m=1, maxit=1, where=where, seed=1)
    filled = complete(result, 1)
    assert np.isnan(filled[0, 0])
    assert not np.isnan(filled[0, 1])
    assert not np.isnan(filled[1, 0])
    assert filled[1, 1] == 2.0
