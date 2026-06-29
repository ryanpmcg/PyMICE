"""Tests for midastouch and polr methods."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice import mice
from pymice.methods.registry import registered_methods
from pymice.types import VariableKind, VariableSpec

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


def test_methods_registered():
    methods = registered_methods()
    assert "midastouch" in methods
    assert "polr" in methods


def test_midastouch_runs_on_nhanes():
    data, names = _load_nhanes()
    result = mice(
        data,
        column_names=names,
        method="midastouch",
        m=2,
        maxit=2,
        seed=99,
    )
    bmi_imp = result.imp["bmi"]
    assert bmi_imp.shape[1] == 2
    assert np.all(np.isfinite(bmi_imp))


def test_polr_runs_on_ordered_variable():
    rng = np.random.default_rng(3)
    n = 40
    x = rng.normal(size=n)
    y = np.clip(np.round(x * 0.8 + 2), 1, 4)
    data = np.column_stack([x, y])
    names = ["x", "y"]
    data[rng.random(n) < 0.25, 1] = np.nan
    specs = [
        VariableSpec("x", VariableKind.NUMERIC),
        VariableSpec("y", VariableKind.ORDERED, levels=(1.0, 2.0, 3.0, 4.0)),
    ]
    result = mice(
        data,
        column_names=names,
        method={"y": "polr"},
        variable_specs=specs,
        m=1,
        maxit=2,
        seed=5,
    )
    imp = result.imp["y"]
    assert np.all(np.isin(imp, [1.0, 2.0, 3.0, 4.0]))
