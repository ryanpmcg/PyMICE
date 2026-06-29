"""Tests for jomoImpute and panImpute multivariate methods."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice
from pymice.methods.jomo_impute import impute_jomo
from pymice.methods.mvn_joint import mvn_da_impute
from pymice.methods.pan_impute import impute_pan
from pymice.methods.registry import (
    get_multivariate_method,
    is_multivariate_method,
    registered_methods,
)

ROOT = Path(__file__).resolve().parents[2]


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    age_map = {"20-39": 1.0, "40-59": 2.0, "60-99": 3.0}
    hyp_map = {"no": 1.0, "yes": 2.0}

    def _cell(column: str, raw: str) -> float:
        val = raw.strip().strip('"')
        if val in ("", "NA"):
            return np.nan
        if column == "age" and val in age_map:
            return age_map[val]
        if column == "hyp" and val in hyp_map:
            return hyp_map[val]
        return float(val)

    with (ROOT / "tests" / "data" / "nhanes.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[_cell(n, r[n]) for n in names] for r in rows],
        dtype=np.float64,
    )
    return data, names


def test_jomo_pan_registered():
    assert is_multivariate_method("jomoImpute")
    assert is_multivariate_method("panImpute")
    assert "jomoImpute" in registered_methods()
    assert get_multivariate_method("jomoImpute") is impute_jomo
    assert get_multivariate_method("panImpute") is impute_pan


def test_mvn_da_impute_fills_missing():
    rng = np.random.default_rng(7)
    y = np.array(
        [
            [1.0, 2.0, 3.0],
            [1.5, np.nan, 3.2],
            [np.nan, 2.1, np.nan],
            [0.8, 2.4, 2.9],
        ],
        dtype=np.float64,
    )
    out = mvn_da_impute(y, n_burn=20, n_iter=5, rng=rng)
    assert not np.any(np.isnan(out))


def test_jomo_impute_block_smoke():
    data = np.array(
        [
            [1.0, 10.0, 1.0, 100.0],
            [2.0, np.nan, 2.0, np.nan],
            [1.0, 22.0, 1.0, 120.0],
            [3.0, np.nan, 2.0, 200.0],
        ],
        dtype=np.float64,
    )
    names = ["age", "bmi", "hyp", "chl"]
    observed = ~np.isnan(data)
    where = np.isnan(data)
    type_row = np.array([1, 1, 1, 1], dtype=np.int_)
    out = impute_jomo(
        data=data,
        column_names=names,
        block_vars=["bmi", "chl", "hyp"],
        type_row=type_row,
        observed=observed,
        where=where,
        rng=np.random.default_rng(1),
        n_burn=10,
        n_iter=5,
    )
    assert set(out) == {"bmi", "chl"}
    assert np.all(np.isfinite(out["bmi"]))
    assert np.all(np.isfinite(out["chl"]))


def test_pan_requires_cluster():
    data = np.ones((6, 3), dtype=np.float64)
    data[1, 1] = np.nan
    names = ["y1", "y2", "id"]
    with pytest.raises(ValueError, match="cluster indicator"):
        impute_pan(
            data=data,
            column_names=names,
            block_vars=["y1", "y2"],
            type_row=np.array([1, 1, 0], dtype=np.int_),
            observed=~np.isnan(data),
            where=np.isnan(data),
            rng=np.random.default_rng(0),
            n_burn=5,
            n_iter=2,
        )


def test_jomo_mice_nhanes_end_to_end():
    data, names = _load_nhanes()
    blocks = {"B1": ["bmi", "chl", "hyp"], "age": ["age"]}
    result = mice(
        data,
        column_names=names,
        blocks=blocks,
        method={"B1": "jomoImpute", "age": "pmm"},
        m=1,
        maxit=1,
        seed=42,
        n_burn=30,
        n_iter=10,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
    assert result.method["B1"] == "jomoImpute"


def test_pan_mice_multilevel_smoke():
    rng = np.random.default_rng(0)
    n = 20
    clusters = np.repeat(np.arange(4), 5)
    y1 = clusters + rng.normal(scale=0.2, size=n)
    y2 = 2 * clusters + rng.normal(scale=0.2, size=n)
    y1[rng.random(n) < 0.2] = np.nan
    y2[rng.random(n) < 0.25] = np.nan
    data = np.column_stack([y1, y2, clusters.astype(float)])
    names = ["y1", "y2", "id"]
    blocks = {"B1": ["y1", "y2"]}
    block_pred = {"B1": np.array([1, 1, -2], dtype=np.int_)}
    result = mice(
        data,
        column_names=names,
        blocks=blocks,
        method="panImpute",
        block_predictor_matrix=block_pred,
        m=1,
        maxit=1,
        seed=7,
        n_burn=20,
        n_iter=5,
    )
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled[:, :2]))
