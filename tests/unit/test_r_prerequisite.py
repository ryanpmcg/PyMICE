"""Tests for R prerequisite checking and vignette RNG wiring."""

from __future__ import annotations

import pytest

from pymice.r_prerequisite import (
    check_r_prerequisites,
    ensure_r_prerequisites,
    find_rscript,
    needs_r_rng,
)
from pymice.rng import make_rng, resolve_rng_backend_name

from tests.r_support import r_backend_available, r_backend_skip_reason


def test_needs_r_rng():
    assert needs_r_rng("r") is True
    assert needs_r_rng("R") is True
    assert needs_r_rng("numpy") is False
    assert needs_r_rng(None) is False


def test_check_r_prerequisites_when_r_available():
    if find_rscript() is None:
        pytest.skip("Rscript not available")
    status = check_r_prerequisites(("mice", "pan"))
    assert status.rscript is not None
    assert status.r_version is not None


def test_make_rng_numpy_unaffected():
    rng, backend = make_rng(1, "numpy")
    assert resolve_rng_backend_name(backend) == "numpy"
    assert rng.random() >= 0.0


@pytest.mark.r_backend
@pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason())
def test_ensure_r_prerequisites_without_install():
    status = ensure_r_prerequisites(install=False, packages=("mice", "pan"))
    assert status.ok
    rng, backend = make_rng(123, "r")
    assert backend == "r"
    close = getattr(rng, "close", None)
    if callable(close):
        close()
