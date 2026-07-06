"""Tests for pluggable RNG backends."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from pymice import complete, mice
from pymice.methods.linear import matchindex, norm_draw
from pymice.rng import (
    RngBackend,
    RRandomGenerator,
    RSession,
    make_rng,
    r_rng_available,
    resolve_rng_backend_name,
)

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "goldens" / "r"


def test_resolve_rng_backend_defaults():
    _, backend = make_rng(1, None)
    assert backend == RngBackend.NUMPY.value
    assert resolve_rng_backend_name("pcg64") == RngBackend.NUMPY.value
    assert resolve_rng_backend_name("legacy") == RngBackend.LEGACY.value
    assert resolve_rng_backend_name("r") == RngBackend.R.value


def test_make_rng_custom_generator():
    gen = np.random.default_rng(9)
    out, backend = make_rng(None, gen)
    assert out is gen
    assert backend == RngBackend.NUMPY.value


@pytest.mark.skipif(not r_rng_available(), reason="Rscript not available")
def test_r_rng_matches_r_runif_rnorm():
    import subprocess

    rscript = "Rscript"
    code = "set.seed(123); cat(paste(runif(5), collapse=' '))"
    r_runif = np.asarray(
        subprocess.check_output([rscript, "-e", code], text=True).strip().split(),
        dtype=np.float64,
    )
    code = "set.seed(123); cat(paste(rnorm(5), collapse=' '))"
    r_rnorm = np.asarray(
        subprocess.check_output([rscript, "-e", code], text=True).strip().split(),
        dtype=np.float64,
    )

    rng = RRandomGenerator(123)
    try:
        np.testing.assert_allclose(rng.random(5), r_runif, rtol=0, atol=1e-12)
    finally:
        rng.close()

    rng = RRandomGenerator(123)
    try:
        np.testing.assert_allclose(rng.standard_normal(5), r_rnorm, rtol=0, atol=1e-12)
    finally:
        rng.close()


@pytest.mark.skipif(not r_rng_available(), reason="Rscript not available")
def test_norm_draw_and_matchindex_use_r_stream():
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, np.nan, np.nan], dtype=np.float64)
    x = np.column_stack([np.ones(7), np.arange(7, dtype=np.float64)])
    ry = ~np.isnan(y)
    rng = RRandomGenerator(42)
    try:
        coef, beta_star, sigma = norm_draw(y, ry, x, rng=rng)
        assert np.all(np.isfinite(coef))
        assert np.all(np.isfinite(beta_star))
        assert sigma > 0
        idx = matchindex(y[ry], np.array([2.5, 4.5]), k=3, rng=rng)
        assert idx.shape == (2,)
    finally:
        rng.close()


def _load_nhanes() -> tuple[np.ndarray, list[str]]:
    names = ["age", "bmi", "hyp", "chl"]
    with (ROOT / "tests" / "data" / "nhanes.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[float(r[n]) if r[n] not in ("", "NA") else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return data, names


@pytest.mark.parametrize("method", ["mean", "pmm", "norm", "norm.nob"])
@pytest.mark.skipif(not GOLDEN.exists(), reason="Missing golden directory")
def test_nhanes_rng_backends_run(method: str):
    data, names = _load_nhanes()
    result = mice(data, column_names=names, method=method, m=2, maxit=3, seed=123, rng="numpy")
    filled = complete(result, 1)
    assert not np.any(np.isnan(filled))
    assert result.rng_backend == "numpy"


@pytest.mark.skipif(not r_rng_available(), reason="Rscript not available")
def test_r_session_survives_sequential_mice_calls():
    data, names = _load_nhanes()
    RSession.start(123)
    try:
        mice(data, column_names=names, method="mean", m=1, maxit=1, seed=None, rng="r")
        result = mice(data, column_names=names, method="pmm", m=2, maxit=1, seed=None, rng="r")
        assert result.rng_backend == "r"
        assert RSession.is_active()
    finally:
        RSession.close()


@pytest.mark.skipif(not r_rng_available(), reason="Rscript not available")
def test_r_session_continues_stream_across_make_rng():
    RSession.start(123)
    try:
        rng1, _ = make_rng(None, "r")
        draw1 = float(rng1.random())
        rng2, _ = make_rng(None, "r")
        float(rng2.random())
        assert rng1 is rng2
        RSession.acquire(123)
        assert float(rng1.random()) == draw1
    finally:
        RSession.close()


@pytest.mark.parametrize("method,atol", [("pmm", 1e-6), ("norm", 1e-6), ("norm.nob", 1e-6)])
@pytest.mark.skipif(not r_rng_available(), reason="Rscript not available")
@pytest.mark.skipif(
    not (GOLDEN / "nhanes_pmm_m2_maxit3_complete1.csv").exists(), reason="Missing R goldens"
)
def test_nhanes_stochastic_methods_match_r_with_rng_r(method: str, atol: float):
    golden = GOLDEN / f"nhanes_{method.replace('.', '_')}_m2_maxit3_complete1.csv"
    if not golden.exists():
        pytest.skip(f"Missing golden file: {golden.name}")

    data, names = _load_nhanes()
    result = mice(data, column_names=names, method=method, m=2, maxit=3, seed=123, rng="r")
    filled = complete(result, 1)
    r_golden = np.genfromtxt(golden, delimiter=",", skip_header=1)

    observed = ~np.isnan(data)
    np.testing.assert_allclose(filled[observed], data[observed], rtol=0, atol=1e-12)
    np.testing.assert_allclose(filled, r_golden, rtol=0, atol=atol)
    assert result.rng_backend == "r"
