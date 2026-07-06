"""Tests for jomo1cat, jomo1mix, random.L1, and 2l.* methods."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice
from pymice.methods.jomo_categorical import jomo1cat_impute
from pymice.methods.jomo_mixed import jomo1mix_impute
from pymice.methods.registry import get_method, registered_methods
from pymice.methods.twol_norm import impute_2l_norm
from pymice.methods.twol_pan import impute_2l_pan
from pymice.methods.twolonly_mean import impute_2lonly_mean
from pymice.types import VariableKind, VariableSpec

ROOT = Path(__file__).resolve().parents[2]


def test_extended_methods_registered():
    for name in ("2l.norm", "2l.pan", "2lonly.mean", "2lonly.norm", "2lonly.pmm", "2logreg"):
        assert name in registered_methods()
        assert get_method(name) is not None
    assert get_method("2logreg") is get_method("logreg")


def test_jomo1cat_impute_smoke():
    y = np.array([[1.0, 1.0], [2.0, np.nan], [np.nan, 2.0], [1.0, 1.0]], dtype=np.float64)
    specs = [
        VariableSpec("a", VariableKind.BINARY, levels=(1.0, 2.0)),
        VariableSpec("b", VariableKind.BINARY, levels=(1.0, 2.0)),
    ]
    out = jomo1cat_impute(y, specs, n_burn=10, n_iter=5, rng=np.random.default_rng(3))
    assert not np.any(np.isnan(out))
    assert set(np.unique(out[:, 0])).issubset({1.0, 2.0})


def test_jomo1mix_impute_smoke():
    y_con = np.array([[1.0], [np.nan], [3.0], [2.0]], dtype=np.float64)
    y_cat = np.array([[1.0], [2.0], [np.nan], [1.0]], dtype=np.float64)
    con_specs = [VariableSpec("y", VariableKind.NUMERIC)]
    cat_specs = [VariableSpec("c", VariableKind.BINARY, levels=(1.0, 2.0))]
    yc, yk = jomo1mix_impute(
        y_con,
        y_cat,
        con_specs,
        cat_specs,
        n_burn=10,
        n_iter=5,
        rng=np.random.default_rng(4),
    )
    assert not np.any(np.isnan(yc))
    assert not np.any(np.isnan(yk))


def test_jomo_random_l1_requires_cluster():
    data = np.ones((10, 2), dtype=np.float64)
    data[2, 0] = np.nan
    with pytest.raises(ValueError, match="cluster"):
        mice(
            data,
            column_names=["y", "g"],
            blocks={"B1": ["y"]},
            method="jomoImpute",
            block_predictor_matrix={"B1": np.array([1, 0], dtype=int)},
            random_l1="mean",
            m=1,
            maxit=1,
            seed=1,
        )


def test_jomo_random_l1_mean_smoke():
    rng = np.random.default_rng(0)
    n = 40
    clusters = np.repeat(np.arange(4), n // 4)
    y = rng.normal(clusters, 0.5)
    y[rng.choice(n, size=8, replace=False)] = np.nan
    data = np.column_stack([y, clusters.astype(np.float64)])
    result = mice(
        data,
        column_names=["y", "g"],
        blocks={"B1": ["y"]},
        method="jomoImpute",
        block_predictor_matrix={"B1": np.array([1, -2], dtype=int)},
        random_l1="mean",
        m=1,
        maxit=1,
        seed=7,
        n_burn=5,
        n_iter=3,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled[:, 0]))


def test_2l_norm_smoke():
    rng = np.random.default_rng(0)
    n = 30
    clusters = np.repeat(np.arange(6), n // 6)
    x = np.column_stack([clusters.astype(float), rng.normal(size=n)])
    y = rng.normal(clusters, 0.5)
    y[rng.choice(n, size=8, replace=False)] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    type_vec = np.array([-2, 2], dtype=np.int_)
    out = impute_2l_norm(y=y, ry=ry, x=x, wy=wy, type=type_vec, rng=np.random.default_rng(0))
    assert out.shape == (int(np.sum(wy)),)
    assert np.all(np.isfinite(out))
    assert np.std(out) > 0.0


def _load_popncr2() -> tuple[np.ndarray, list[str], list[VariableSpec]]:
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    specs = [
        VariableSpec("pupil", VariableKind.NUMERIC),
        VariableSpec("class", VariableKind.UNORDERED, levels=tuple(range(1, 101))),
        VariableSpec("extrav", VariableKind.NUMERIC),
        VariableSpec("sex", VariableKind.BINARY, levels=(0.0, 1.0)),
        VariableSpec("texp", VariableKind.NUMERIC),
        VariableSpec("popular", VariableKind.NUMERIC),
        VariableSpec("popteach", VariableKind.NUMERIC),
    ]
    with (ROOT / "tests" / "data" / "popNCR2.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[float(r[n]) if r[n] not in ("", "NA") else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return data, names, specs


def test_2l_norm_popncr2_mice():
    data, names, specs = _load_popncr2()
    pred = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, -2, 0, 0, 0, 0, 0],
            [0, -2, 0, 2, 2, 0, 2],
            [0, 1, 1, 0, 1, 1, 1],
            [0, -2, 1, 1, 0, 1, 1],
            [0, -2, 2, 2, 2, 0, 2],
            [0, 1, 1, 1, 1, 1, 0],
        ],
        dtype=np.int_,
    )
    methods = {
        "pupil": "",
        "class": "",
        "extrav": "",
        "sex": "",
        "texp": "",
        "popular": "2l.norm",
        "popteach": "",
    }
    result = mice(
        data,
        column_names=names,
        variable_specs=specs,
        method=methods,
        predictor_matrix=pred,
        m=1,
        maxit=1,
        seed=42,
        n_iter=20,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled[:, names.index("popular")]))


def test_2l_pan_smoke():
    rng = np.random.default_rng(1)
    n = 30
    clusters = np.repeat(np.arange(6), n // 6)
    x = np.column_stack(
        [
            clusters.astype(float),
            rng.normal(size=n),
            rng.integers(0, 2, size=n).astype(float),
        ]
    )
    y = rng.normal(clusters, 0.5)
    y[rng.choice(n, size=8, replace=False)] = np.nan
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    type_vec = np.array([-2, 2, 1], dtype=np.int_)
    out = impute_2l_pan(
        y=y, ry=ry, x=x, wy=wy, type=type_vec, rng=np.random.default_rng(1), paniter=50
    )
    assert out.shape == (int(np.sum(wy)),)
    assert np.all(np.isfinite(out))
    assert np.std(out) > 0.0


def test_2l_norm_popncr2_r_parity_stats():
    """Direct 2l.norm on popNCR2: moments within tolerance of R mice (seed=123)."""
    data, names, _specs = _load_popncr2()
    y = data[:, names.index("popular")]
    x = data[
        :, [names.index("class"), names.index("extrav"), names.index("sex"), names.index("texp")]
    ]
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_2l_norm(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        type=np.array([-2, 2, 2, 2], dtype=np.int_),
        rng=np.random.default_rng(123),
        n_iter=100,
    )
    # R mice:::mice.impute.2l.norm(..., seed=123): mean=5.506497, sd=1.273668
    assert abs(float(np.mean(out)) - 5.506497) < 0.15
    assert abs(float(np.std(out)) - 1.273668) < 0.15


def test_2lonly_mean_class_mean_and_empty_class():
    y = np.array([1.0, 2.0, np.nan, np.nan], dtype=np.float64)
    x = np.array([[1.0], [1.0], [1.0], [3.0]], dtype=np.float64)
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_2lonly_mean(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        type=np.array([-2], dtype=np.int_),
        rng=np.random.default_rng(0),
    )
    assert out[0] == 1.5
    assert np.isnan(out[1])


@pytest.mark.r_backend
def test_2l_pan_popncr2_r_parity_stats():
    """Direct 2l.pan on popNCR2: moments within tolerance of R mice (seed=123)."""
    from pymice.methods.r_pan_backend import r_pan_available

    if not r_pan_available():
        pytest.skip("R pan backend unavailable")

    data, names, _specs = _load_popncr2()
    y = data[:, names.index("popular")]
    x = data[:, [names.index(c) for c in ("class", "extrav", "sex", "texp", "popteach")]]
    ry = ~np.isnan(y)
    wy = np.isnan(y)
    out = impute_2l_pan(
        y=y,
        ry=ry,
        x=x,
        wy=wy,
        type=np.array([-2, 2, 2, 1, 2], dtype=np.int_),
        rng=np.random.default_rng(123),
        paniter=500,
        mice_seed=123,
    )
    # R mice:::mice.impute.2l.pan(..., seed=123): mean=5.722624, sd=1.312215
    assert abs(float(np.mean(out)) - 5.722624) < 0.15
    sd_tol = 0.15 if r_pan_available() else 0.5
    assert abs(float(np.std(out)) - 1.312215) < sd_tol


def test_imp8_class_factor_pmm_smoke():
    """popNCR3 PMM with unordered ``class`` uses dummy-coded predictors."""
    names = ["pupil", "class", "extrav", "sex", "texp", "popular", "popteach"]
    with (ROOT / "tests" / "data" / "popNCR3.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[float(r[n]) if r[n] not in ("", "NA") else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    class_vals = data[:, names.index("class")]
    class_levels = tuple(float(v) for v in np.unique(class_vals[~np.isnan(class_vals)]))
    specs = [
        VariableSpec("pupil", VariableKind.NUMERIC),
        VariableSpec("class", VariableKind.UNORDERED, levels=class_levels),
        VariableSpec("extrav", VariableKind.NUMERIC),
        VariableSpec("sex", VariableKind.BINARY, levels=(0.0, 1.0)),
        VariableSpec("texp", VariableKind.NUMERIC),
        VariableSpec("popular", VariableKind.NUMERIC),
        VariableSpec("popteach", VariableKind.NUMERIC),
    ]
    result = mice(
        data,
        column_names=names,
        variable_specs=specs,
        m=2,
        maxit=2,
        seed=123,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
    assert set(np.unique(filled[:, names.index("class")])).issubset(set(class_levels))
