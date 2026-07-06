"""Previously unimplemented R methods and mids utilities are now registered."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import as_mids, cbind_mids, mice, rbind_mids, unimplemented_imputation_methods
from pymice.methods.registry import (
    get_method,
    get_multivariate_method,
    is_multivariate_method,
    registered_methods,
)


def test_no_unimplemented_imputation_methods_remain():
    assert unimplemented_imputation_methods() == []


@pytest.mark.parametrize(
    "name",
    [
        "2l.bin",
        "2l.lmer",
        "2lonly.norm",
        "2lonly.pmm",
        "micemean",
        "quadratic",
        "logreg.boot",
        "lda",
        "lasso.norm",
        "lasso.logreg",
        "mnar",
        "ri",
        "jomo2con",
        "jomo2ran",
    ],
)
def test_former_gap_methods_registered(name: str):
    assert name in registered_methods()
    if is_multivariate_method(name):
        assert get_multivariate_method(name) is not None
    else:
        assert get_method(name) is not None


def test_as_mids_roundtrip():
    data = np.array([[1.0, 2.0], [np.nan, 4.0]])
    imp = {"V1": np.array([[3.0], [5.0]])}
    mids = as_mids(data, imp, column_names=["V1", "V2"], m=1)
    assert mids.m == 1
    assert mids.n_obs == 2


def test_cbind_and_rbind_mids():
    pytest.importorskip("pandas")
    imp1 = mice(
        {"a": [1.0, np.nan], "b": [2.0, 3.0]},
        m=2,
        maxit=1,
        seed=1,
    )
    imp2 = mice(
        {"a": [4.0, np.nan], "c": [6.0, np.nan]},
        m=2,
        maxit=1,
        seed=2,
    )
    bound = cbind_mids(imp1, imp2)
    assert "c" in bound.column_names
    assert bound.n_obs == imp1.n_obs

    stacked = rbind_mids(imp1, imp1)
    assert stacked.n_obs == imp1.n_obs * 2
