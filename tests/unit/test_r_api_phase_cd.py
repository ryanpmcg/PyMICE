"""Phase C/D R-familiar API: complete layouts, continue state, plots."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from pymice import complete, data, mice, mice_mids


def test_complete_long_dataframe():
    pd = pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=3, maxit=1, seed=1)
    long = complete(imp, "long")
    assert isinstance(long, pd.DataFrame)
    assert list(long.columns[:2]) == [".imp", ".id"]
    assert set(long.columns[2:]) == set(nhanes.columns)
    assert long[".imp"].tolist() == [1] * imp.n_obs + [2] * imp.n_obs + [3] * imp.n_obs
    assert long[".id"].tolist() == list(range(1, imp.n_obs + 1)) * 3


def test_complete_broad_dataframe():
    pd = pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=2, maxit=1, seed=2)
    broad = complete(imp, "broad")
    assert isinstance(broad, pd.DataFrame)
    assert list(broad.columns) == [
        "age.1",
        "bmi.1",
        "hyp.1",
        "chl.1",
        "age.2",
        "bmi.2",
        "hyp.2",
        "chl.2",
    ]
    assert broad.shape == (imp.n_obs, len(nhanes.columns) * imp.m)


def test_complete_long_ndarray_backward_compat():
    nhanes = data("nhanes")
    imp = mice(nhanes, m=2, maxit=1, seed=3)
    stacked = complete(imp, "long", as_dataframe=False)
    assert isinstance(stacked, np.ndarray)
    assert stacked.shape == (imp.n_obs * imp.m, imp.n_vars)


def test_mice_mids_preserves_chain_state():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=2, maxit=2, seed=4)
    prior_len = imp.chain_mean["bmi"].shape[0]
    more = mice_mids(imp, maxit=3, print=False)
    assert more.iteration == imp.iteration + 3
    assert more.chain_mean["bmi"].shape[0] == prior_len + 3
    assert np.allclose(more.chain_mean["bmi"][:prior_len], imp.chain_mean["bmi"])


def test_logged_events_on_collinear_predictors():
    pytest.importorskip("pandas")
    # Perfect collinearity: x2 = 2 * x1 forces predictor removal events.
    arr = np.array(
        [
            [1.0, 1.0, 2.0],
            [np.nan, 2.0, 4.0],
            [3.0, 3.0, 6.0],
            [np.nan, 4.0, 8.0],
        ],
        dtype=np.float64,
    )
    pred = np.array(
        [
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 0],
        ],
        dtype=np.int_,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        imp = mice(
            arr,
            column_names=["y", "x1", "x2"],
            predictor_matrix=pred,
            method={"y": "norm", "x1": "", "x2": ""},
            m=1,
            maxit=2,
            seed=5,
        )
    assert imp.logged_events
    assert imp.loggedEvents is imp.logged_events
    event = imp.logged_events[0]
    assert {"iteration", "imp", "method", "dep", "out"} <= set(event.keys())


def test_post_round_string():
    data_arr = np.array([[100.4], [np.nan], [120.7]], dtype=np.float64)
    result = mice(
        data_arr,
        column_names=["y"],
        method="norm",
        m=1,
        maxit=1,
        seed=6,
        post={"y": "imp[[j]][, i] <- round(imp[[j]][, i])"},
    )
    filled = complete(result, 1)[:, 0]
    miss = np.isnan(data_arr[:, 0])
    assert np.all(filled[miss] == np.round(filled[miss]))


def test_plot_dispatch_smoke():
    plt = pytest.importorskip("matplotlib.pyplot")
    pytest.importorskip("pandas")
    from pymice import bwplot, densityplot, plot, stripplot, xyplot

    nhanes = data("nhanes")
    imp = mice(nhanes, m=2, maxit=2, seed=7)
    fig = plot(imp, variables="bmi")
    assert fig is not None
    plt.close("all")

    fig = densityplot(imp)
    plt.close(fig)

    fig = densityplot(imp, "~ bmi")
    plt.close(fig)

    fig = densityplot(imp, "~ bmi | .imp")
    plt.close(fig)

    fig = stripplot(imp, "chl ~ .imp")
    plt.close(fig)

    fig = xyplot(imp, "bmi ~ age")
    plt.close(fig)

    fig = bwplot(imp)
    plt.close(fig)

    fig = bwplot(imp, "chl ~ .imp")
    plt.close(fig)
