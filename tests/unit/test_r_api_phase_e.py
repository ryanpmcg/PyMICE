"""Phase E: honest NotImplemented boundaries and R gap helpers."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import (
    data,
    filter_mids,
    fluxplot,
    mice,
    unimplemented_features,
    unimplemented_imputation_methods,
)
from pymice.methods.registry import get_method


def test_unimplemented_method_registry_empty():
    assert unimplemented_imputation_methods() == []


def test_get_method_returns_2l_lmer():
    assert get_method("2l.lmer") is not None


def test_unimplemented_features_empty():
    assert unimplemented_features() == []


def test_filter_mids_uses_r_style_indices():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=5, maxit=1, seed=1)
    sub = filter_mids(imp, [1, 3, 5])
    assert sub.m == 3
    for name in imp.imp:
        np.testing.assert_array_equal(sub.imp[name][:, 0], imp.imp[name][:, 0])
        np.testing.assert_array_equal(sub.imp[name][:, 1], imp.imp[name][:, 2])
        np.testing.assert_array_equal(sub.imp[name][:, 2], imp.imp[name][:, 4])


def test_filter_mids_rejects_zero_based_indices():
    pytest.importorskip("pandas")
    imp = mice(data("nhanes"), m=2, maxit=1, seed=2)
    with pytest.raises(IndexError, match="1-based"):
        filter_mids(imp, [0, 1])


def test_fluxplot_smoke():
    plt = pytest.importorskip("matplotlib.pyplot")
    pytest.importorskip("pandas")
    leiden = data("leiden")
    fig = fluxplot(leiden)
    assert fig is not None
    plt.close(fig)

    table, fig2 = fluxplot(leiden, return_table=True)
    assert len(table.column_names) == leiden.shape[1]
    plt.close(fig2)
