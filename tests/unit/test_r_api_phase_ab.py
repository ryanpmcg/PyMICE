"""Phase A/B R-familiar API: aliases, DataFrame-first paths."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from pymice import (
    data,
    futuremice,
    lm,
    md_pattern,
    mice,
    mice_mids,
    pool,
    summary,
    with_,
)
from pymice.analysis.ols import lm as lm_fn


def test_mice_print_kwarg():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    result = mice(nhanes, m=1, maxit=1, print=False, seed=1)
    assert result.m == 1


def test_mice_r_kwarg_aliases():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    pred = np.eye(4, dtype=np.int_)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = mice(
            nhanes,
            m=1,
            maxit=0,
            printFlag=False,
            predictorMatrix=pred,
            visitSequence=["age", "bmi", "hyp", "chl"],
        )
    assert result.iteration == 0
    np.testing.assert_array_equal(result.pred, pred)


def test_mids_r_slot_aliases():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=1, maxit=1, seed=2)
    assert imp.meth is imp.method
    assert imp.pred is imp.predictor_matrix
    assert imp.visitSequence == imp.visit_sequence


def test_with_and_summary_r_names():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=2, maxit=2, seed=3)
    fit = with_(imp, "age ~ bmi")
    fit2 = with_(imp, lm_fn, "age ~ bmi")
    assert len(fit.analyses) == 2
    assert len(fit2.analyses) == 2
    tab = summary(pool(fit))
    assert tab[0]["term"] in {"(Intercept)", "Intercept"}


def test_mice_mids_and_futuremice():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    imp = mice(nhanes, m=1, maxit=1, seed=4)
    more = mice_mids(imp, maxit=2, print=False)
    assert more.iteration == imp.iteration + 2
    par = futuremice(nhanes, m=2, maxit=1, parallelseed=5, n_core=1, print=False)
    assert par.m == 2


def test_data_registry():
    pd = pytest.importorskip("pandas")
    nhanes = data("nhanes")
    assert isinstance(nhanes, pd.DataFrame)
    assert list(nhanes.columns) == ["age", "bmi", "hyp", "chl"]


def test_md_pattern_dataframe():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    result = md_pattern(nhanes)
    assert result.n_patterns == 5


def test_lm_dataframe():
    pytest.importorskip("pandas")
    nhanes = data("nhanes")
    fit = lm("age ~ bmi", nhanes)
    assert "bmi" in fit.terms


def test_mice_df_deprecation():
    pytest.importorskip("pandas")
    from pymice import mice_df

    nhanes = data("nhanes")
    with pytest.warns(DeprecationWarning, match="mice_df"):
        result = mice_df(nhanes, m=1, maxit=1, seed=6)
    assert result.m == 1
