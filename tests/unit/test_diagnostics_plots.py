"""Smoke tests for optional diagnostic plots."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np

from pymice import mice
from pymice.diagnostics.md_pattern import md_pattern
from pymice.diagnostics.plots import plot_density, plot_md_pattern, plot_mids

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


def test_plot_md_pattern_returns_figure():
    data, _ = _load_nhanes()
    result = md_pattern(data)
    fig = plot_md_pattern(result)
    assert fig is not None
    fig.clf()


def test_plot_mids_returns_figure():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_mids(mids, variables=["bmi"])
    assert fig is not None
    fig.clf()


def test_plot_density_returns_figure():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_density(mids, "bmi")
    assert fig is not None
    fig.clf()
