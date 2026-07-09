"""Tests for predictor design-matrix construction."""

from __future__ import annotations

import numpy as np

from devtools.lib.data import load_popncr, popncr_variable_specs
from pymice import mice
from pymice.design import expand_predictors, obtain_design


def test_predictor_matrix_type_one_uses_numeric_class():
    """R flag 1 treats factors as continuous (V05 imp2 texp ~ class)."""
    data, names = load_popncr()
    specs = popncr_variable_specs(data, names)
    class_i = names.index("class")
    texp_i = names.index("texp")
    pred_idx = [class_i, names.index("extrav"), names.index("sex")]

    expanded = expand_predictors(
        data,
        pred_idx,
        specs,
        predictor_types=[1, 1, 1],
    )
    assert expanded.shape == (data.shape[0], 3)

    numeric = obtain_design(
        data,
        texp_i,
        pred_idx,
        specs,
        predictor_types=[1, 1, 1],
    )
    assert numeric.shape == (data.shape[0], 3)
    np.testing.assert_array_equal(numeric[:, 0], data[:, class_i])


def test_predictor_matrix_type_two_dummy_codes_class():
    data, names = load_popncr()
    specs = popncr_variable_specs(data, names)
    class_i = names.index("class")
    texp_i = names.index("texp")

    expanded = expand_predictors(
        data,
        [class_i],
        specs,
        predictor_types=[2],
    )
    n_levels = len(specs[class_i].levels or ())
    assert expanded.shape == (data.shape[0], max(n_levels - 1, 0))


def test_v05_imp2_texp_chain_mean_varies_across_chains():
    """Norm imputation with class flag 1 must not collapse texp chains."""
    data, names = load_popncr()
    specs = popncr_variable_specs(data, names)
    ini = mice(data, column_names=names, maxit=0, print_flag=False, variable_specs=specs)
    meth = dict(ini.method)
    for var in ("extrav", "texp", "popular", "popteach"):
        meth[var] = "norm"
    pred2 = ini.predictor_matrix.copy()
    pred2[:, names.index("pupil")] = 0

    imp2 = mice(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred2,
        m=5,
        maxit=5,
        print_flag=False,
        variable_specs=specs,
        seed=123,
    )

    texp_imp = imp2.imp["texp"]
    assert not np.allclose(texp_imp[:, 0], texp_imp[:, 1])

    chain_means = imp2.chain_mean["texp"]
    assert chain_means.shape == (5, 5)
    for row in chain_means:
        assert len(np.unique(np.round(row, 6))) > 1