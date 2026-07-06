"""Smoke tests for optional diagnostic plots."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np

from pymice import data, densityplot, mice
from pymice.diagnostics.density_bw import bw_nrd0
from pymice.diagnostics.md_pattern import md_pattern
from pymice.diagnostics.plots import (
    _bwplot_grid_variables,
    _density_grid_variables,
    plot_bwplot,
    plot_bwplot_grid,
    plot_density,
    plot_density_grid,
    plot_md_pattern,
    plot_mids,
)
from pymice.diagnostics.theme import mdc

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


def test_plot_md_pattern_r_layout():
    data, _ = _load_nhanes()
    result = md_pattern(data)
    fig = plot_md_pattern(result)
    ax = fig.axes[0]

    assert ax.get_title() == ""
    assert not ax.xaxis.get_label().get_text()
    patches = [c for c in ax.patches if c.get_label() != "_nolegend_"]
    assert len(patches) == result.n_patterns * len(result.column_names)

    texts = [t.get_text() for t in ax.texts]
    assert "13" in texts
    assert "27" in texts
    assert set(result.column_names).issubset(texts)
    fig.clf()


def test_md_pattern_plot_true_draws():
    data, _ = _load_nhanes()
    result = md_pattern(data, plot=True)
    assert result.n_patterns == 5
    import matplotlib.pyplot as plt

    assert plt.get_fignums()
    plt.close("all")


def test_plot_mids_returns_figure():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_mids(mids, variables=["bmi"])
    assert fig is not None
    assert len(fig.axes) == 2
    assert fig.axes[0].get_title(loc="left") == "mean"
    assert fig.axes[1].get_title(loc="left") == "sd"
    fig.clf()


def test_plot_mids_mean_sd_grid():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_mids(mids, variables=["bmi", "chl"])
    assert len(fig.axes) == 4
    assert fig.axes[0].get_title(loc="left") == "mean"
    assert fig.axes[1].get_title(loc="left") == "sd"
    assert fig.axes[2].get_title(loc="left") == "mean"
    assert fig.axes[3].get_title(loc="left") == "sd"
    assert fig.axes[2].get_xlabel() == ""
    assert fig.axes[3].get_xlabel() == ""
    assert fig.get_supxlabel() == "Iteration"
    fig.clf()


def test_densityplot_series_r_style():
    nhanes = data("nhanes")
    fig = densityplot(nhanes["bmi"], xlab="nhanes$bmi")
    ax = fig.axes[0]
    assert ax.get_xlabel() == "nhanes$bmi"
    assert ax.get_ylabel() == "Density"
    assert ax.get_title() == ""
    line = ax.lines[0]
    assert tuple(line.get_color()[:3]) == tuple(mdc(4)[:3])
    fig.clf()


def test_bw_nrd0_positive():
    data_arr, _ = _load_nhanes()
    bmi = data_arr[:, 1]
    bmi = bmi[np.isfinite(bmi)]
    assert bw_nrd0(bmi) > 0


def test_plot_density_returns_figure():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_density(mids, "bmi")
    assert fig is not None
    fig.clf()


def test_plot_density_grid_returns_figure():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    varlist = _density_grid_variables(mids)
    fig = plot_density_grid(mids)
    assert fig is not None
    assert len(fig.axes) == 4
    assert fig.axes[2].axis("off")
    assert [ax.get_title() for ax in fig.axes[:2]] == varlist[:2]
    assert fig.axes[0].get_ylabel() == "Density"
    assert fig.axes[1].get_ylabel() == ""
    fig.clf()


def test_densityplot_mids_no_formula():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    varlist = _density_grid_variables(mids)
    fig = densityplot(mids)
    assert len(fig.axes) == 4
    titled = [ax.get_title() for ax in fig.axes if ax.get_title()]
    assert titled == varlist
    fig.clf()


def test_plot_bwplot_includes_observed_draw():
    data, names = _load_nhanes()
    mids = mice(data, column_names=names, method="mean", m=2, maxit=3, seed=123)
    fig = plot_bwplot(mids, "bmi")
    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["0", "1", "2"]
    fig.clf()


def test_plot_bwplot_grid_returns_figure():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "devtools"))
    from lib.data import load_leiden

    data, names = load_leiden()
    mids = mice(
        data,
        column_names=names,
        post={"rrsyst": "imp[[j]][,i] <- imp[[j]][,i] + 0"},
        m=5,
        maxit=2,
        seed=1,
        print=False,
    )
    varlist = _bwplot_grid_variables(mids)
    fig = plot_bwplot_grid(mids)
    assert len(varlist) == 10
    assert len(fig.axes) == 12
    titled = [ax.get_title() for ax in fig.axes if ax.get_title()]
    assert titled == varlist
    assert fig.get_supxlabel() == "Imputation number"
    fig.clf()


def test_bwplot_mids_no_formula():
    import sys
    from pathlib import Path

    from pymice import bwplot

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "devtools"))
    from lib.data import load_leiden

    data, names = load_leiden()
    mids = mice(data, column_names=names, m=5, maxit=2, seed=1, print=False)
    varlist = _bwplot_grid_variables(mids)
    fig = bwplot(mids)
    titled = [ax.get_title() for ax in fig.axes if ax.get_title()]
    assert titled == varlist
    fig.clf()
