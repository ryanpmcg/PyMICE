"""Full JOMO feature tests: random slopes, groups, priors, formula helpers."""

from __future__ import annotations

import numpy as np

from pymice import complete, mice
from pymice.methods.jomo_core import JomoPrior, ml_jomo_impute
from pymice.methods.jomo_formula import type_row_from_roles
from pymice.methods.jomo_impute import impute_jomo


def test_type_row_from_roles_builds_mitml_codes():
    names = ["y1", "y2", "x", "z", "id", "grp"]
    row = type_row_from_roles(
        names,
        targets=["y1", "y2"],
        fixed=["x"],
        random=["z"],
        cluster="id",
        group="grp",
    )
    assert row.tolist() == [1, 1, 2, 3, -2, -1]


def test_ml_jomo_random_slope_fills_missing():
    rng = np.random.default_rng(1)
    n = 60
    clusters = np.repeat(np.arange(6), 10)
    z = rng.normal(size=n)
    y1 = clusters + 0.5 * z + rng.normal(scale=0.2, size=n)
    y2 = 2 * clusters - z + rng.normal(scale=0.2, size=n)
    y1[rng.choice(n, 12, replace=False)] = np.nan
    y2[rng.choice(n, 10, replace=False)] = np.nan
    y = np.column_stack([y1, y2])
    x = np.ones((n, 1))
    z_mat = z.reshape(-1, 1)
    out = ml_jomo_impute(
        y,
        clusters.astype(np.int_),
        x=x,
        z=z_mat,
        n_burn=15,
        n_iter=8,
        rng=rng,
    )
    assert not np.any(np.isnan(out))


def test_jomo_group_stratification_smoke():
    rng = np.random.default_rng(2)
    n = 80
    grp = np.repeat([1, 2], n // 2)
    y = grp[:, None] * 2 + rng.normal(scale=0.5, size=(n, 1))
    y[rng.choice(n, 15, replace=False), 0] = np.nan
    data = np.column_stack([y[:, 0], grp.astype(float)])
    names = ["y", "grp"]
    observed = ~np.isnan(data)
    where = np.isnan(data)
    type_row = type_row_from_roles(names, targets=["y"], group="grp")
    out = impute_jomo(
        data=data,
        column_names=names,
        block_vars=["y"],
        type_row=type_row,
        observed=observed,
        where=where,
        rng=rng,
        n_burn=10,
        n_iter=5,
    )
    assert "y" in out
    assert np.all(np.isfinite(out["y"]))


def test_jomo_mice_with_random_predictor():
    rng = np.random.default_rng(3)
    n = 50
    clusters = np.repeat(np.arange(5), 10)
    z = rng.normal(size=n)
    y = clusters + z + rng.normal(scale=0.3, size=n)
    y[rng.choice(n, 10, replace=False)] = np.nan
    data = np.column_stack([y, z, clusters.astype(float)])
    names = ["y", "z_pred", "id"]
    block_pred = {
        "B1": np.array([1, 3, -2], dtype=np.int_),
    }
    result = mice(
        data,
        column_names=names,
        blocks={"B1": ["y"]},
        method="jomoImpute",
        block_predictor_matrix=block_pred,
        m=1,
        maxit=1,
        seed=9,
        n_burn=8,
        n_iter=4,
        prior={"Binv": np.eye(1)},
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled[:, 0]))


def test_jomo_prior_object_accepted():
    rng = np.random.default_rng(4)
    y = np.array([[1.0, 2.0], [np.nan, 3.0], [2.0, np.nan]], dtype=np.float64)
    out = ml_jomo_impute(
        y,
        np.zeros(3, dtype=np.int_),
        n_burn=5,
        n_iter=3,
        rng=rng,
        prior=JomoPrior(b_inv=np.eye(2)),
    )
    assert not np.any(np.isnan(out))
