"""Tests for parallel MICE / futuremice fidelity."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import futuremice, load_nhanes, merge_mids, mice, parallel_mice
from pymice.parallel import distribute_imputations, worker_seeds


@pytest.mark.parametrize(
    ("m", "n_core", "expected"),
    [
        (5, 3, [2, 1, 2]),
        (10, 4, [3, 2, 2, 3]),
        (5, 1, [5]),
        (3, 5, [1, 1, 1]),
    ],
)
def test_distribute_imputations_matches_r_cut(m: int, n_core: int, expected: list[int]) -> None:
    pytest.importorskip("pandas")
    got = distribute_imputations(m, n_core)
    assert got == [c for c in expected if c > 0]


def test_parallel_mice_reproducible_with_parallelseed():
    data, names = load_nhanes()
    kwargs = dict(column_names=names, m=5, maxit=1, parallelseed=123, n_jobs=2, print=False)
    a = parallel_mice(data, **kwargs)
    b = parallel_mice(data, **kwargs)
    assert a.parallelseed == 123
    assert b.parallelseed == 123
    assert a.m == b.m == 5
    for col in names:
        if col in a.imp:
            np.testing.assert_allclose(a.imp[col], b.imp[col])


def test_futuremice_stores_parallelseed():
    data, names = load_nhanes()
    result = futuremice(
        data, column_names=names, m=3, maxit=1, parallelseed=42, n_core=1, print=False
    )
    assert result.parallelseed == 42
    assert result.m == 3


def test_parallel_matches_sequential_chunks():
    data, names = load_nhanes()
    chunks = distribute_imputations(5, 3)
    seeds = worker_seeds(77, len(chunks), duplicate=False)
    singles = [
        mice(data, column_names=names, m=chunk, maxit=1, seed=seed, print=False)
        for chunk, seed in zip(chunks, seeds, strict=True)
    ]
    expected = merge_mids(singles)
    actual = parallel_mice(
        data,
        column_names=names,
        m=5,
        maxit=1,
        parallelseed=77,
        n_jobs=3,
        print=False,
    )
    for col in names:
        if col in expected.imp:
            np.testing.assert_allclose(expected.imp[col], actual.imp[col])


def test_seed_warning_with_multiple_workers():
    data, names = load_nhanes()
    with pytest.warns(UserWarning, match="duplicate imputations"):
        parallel_mice(
            data,
            column_names=names,
            m=4,
            maxit=1,
            seed=99,
            n_jobs=2,
            print=False,
        )
