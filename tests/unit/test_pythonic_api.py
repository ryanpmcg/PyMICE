"""Tests for Pythonic API additions."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import (
    BlockPartition,
    ImputationFits,
    ImputationFrame,
    ImputationMethod,
    PassiveFormula,
    complete,
    continue_imputation,
    help,
    load_nhanes,
    merge_mids,
    mice,
    parallel_mice,
    pool,
    with_imputations,
    with_mids,
)
from pymice.formulas import parse_regression_formula
from pymice.passive import evaluate_passive


def test_verbose_and_max_iter_aliases():
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=1, max_iter=1, verbose=False, seed=1)
    assert result.iteration == 1


def test_complete_draw_keyword():
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=2, maxit=1, seed=3)
    out = complete(result, draw=1)
    assert out.shape == data.shape


def test_with_imputations_alias():
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=2, maxit=2, seed=4)
    fits = with_imputations(result, formula="age ~ bmi")
    assert isinstance(fits, ImputationFits)
    assert len(fits.analyses) == 2


def test_lm_log10_formula():
    from pymice import lm

    rng = np.random.default_rng(0)
    bw = rng.uniform(1, 100, size=20)
    sws = 10 - 0.5 * np.log10(bw) + rng.normal(scale=0.1, size=20)
    data = np.column_stack([bw, sws])
    names = ["bw", "sws"]
    fit = lm("sws ~ log10(bw)", data, names)
    assert "log10(bw)" in fit.terms


def test_passive_sqrt():
    data = np.array([[4.0, 2.0, np.nan]], dtype=np.float64)
    names = ["wgt", "bmi", "hgt"]
    out = evaluate_passive(PassiveFormula("sqrt(wgt)"), data, names, np.array([True]))
    np.testing.assert_allclose(out, [2.0])


def test_passive_triple_sqrt_pathological():
    data = np.array([[70.0, 175.0, 22.0, np.nan]], dtype=np.float64)
    names = ["wgt", "hgt", "bmi", "hgt2"]
    formula = "~ I(sqrt(wgt/bmi)*100)"
    out = evaluate_passive(formula, data, names, np.array([True]))
    expected = np.sqrt(70.0 / 22.0) * 100.0
    np.testing.assert_allclose(out, [expected], rtol=1e-9)


def test_pool_to_dataframe():
    pytest.importorskip("pandas")
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=3, maxit=2, seed=5)
    fits = with_mids(result, formula="age ~ bmi")
    pooled = pool(fits)
    df = pooled.to_dataframe()
    assert len(df) == len(pooled.rows)


def test_mids_summary_and_continue():
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=2, maxit=1, seed=6)
    meta = result.summary()
    assert meta["m"] == 2
    extended = result.continue_(max_iter=2, verbose=False)
    assert extended.iteration == result.iteration + 2


def test_continue_imputation_function():
    data, names = load_nhanes()
    base = mice(data, column_names=names, m=1, maxit=1, seed=7)
    more = continue_imputation(base, max_iter=2)
    assert more.iteration == base.iteration + 2


def test_parallel_mice_merge():
    data, names = load_nhanes()
    result = parallel_mice(data, column_names=names, m=3, maxit=1, parallelseed=8, n_jobs=1)
    assert result.m == 3


def test_merge_mids():
    data, names = load_nhanes()
    singles = [mice(data, column_names=names, m=1, maxit=1, seed=i) for i in range(3)]
    merged = merge_mids(singles)
    assert merged.m == 3


def test_imputation_frame_from_array():
    data, names = load_nhanes()
    frame = ImputationFrame.from_array(data, column_names=names)
    assert frame.column_names == names


def test_mice_df():
    pd = pytest.importorskip("pandas")
    data, names = load_nhanes()
    df = pd.DataFrame(data, columns=names)
    from pymice import mice_df

    result = mice_df(df, m=1, maxit=1, seed=9)
    assert result.m == 1


def test_block_partition_enum():
    blocks = __import__("pymice").make_blocks(["a", "b"], partition=BlockPartition.COLLECT)
    assert blocks == {"collect": ["a", "b"]}


def test_imputation_method_enum():
    assert str(ImputationMethod.PMM) == "pmm"


def test_help_new_symbols():
    text = help("with_imputations", print_=False)
    assert "with_imputations" in text or "with_mids" in text


def test_parse_regression_formula_transform():
    _y, preds = parse_regression_formula("sws ~ log10(bw) + odi", ["bw", "odi", "sws"])
    assert preds[0].label == "log10(bw)"


def test_ibind_combines_imputations():
    from pymice import ibind

    data, names = load_nhanes()
    mids1 = mice(data, column_names=names, m=2, maxit=2, seed=1)
    mids2 = mice(data, column_names=names, m=3, maxit=2, seed=2)

    combined = ibind(mids1, mids2)
    assert combined.m == 5
    for col in names:
        if col in mids1.imp:
            assert combined.imp[col].shape[1] == 5

    # Check validation errors
    mids_diff_cols = mice(data[:, :3], column_names=names[:3], m=1, maxit=1, seed=3)
    with pytest.raises(ValueError, match="different column names"):
        ibind(mids1, mids_diff_cols)


def test_filter_imputations_subsets():
    from pymice import filter_imputations

    data, names = load_nhanes()
    result = mice(data, column_names=names, m=5, maxit=2, seed=4)

    sub1 = filter_imputations(result, 2)
    assert sub1.m == 1
    assert sub1.imp["bmi"].shape[1] == 1

    sub2 = filter_imputations(result, [0, 2, 4])
    assert sub2.m == 3
    for col in result.imp:
        assert sub2.imp[col].shape[1] == 3

    # Check IndexError bounds
    with pytest.raises(IndexError, match="out of range"):
        filter_imputations(result, 5)


def test_mids_repr():
    data, names = load_nhanes()
    result = mice(data, column_names=names, m=2, maxit=1, seed=5)
    representation = repr(result)
    assert "Class: Mids" in representation
    assert "Number of multiple imputations (m): 2" in representation
    assert "bmi:" in representation
