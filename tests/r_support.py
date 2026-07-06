"""Helpers for optional R-backed pytest modules."""

from __future__ import annotations

from pymice.r_prerequisite import check_r_prerequisites
from pymice.rng import r_rng_available


def r_backend_available() -> bool:
    """True when ``rng='r'`` prerequisites are satisfied (Rscript + CRAN mice + pan)."""
    return check_r_prerequisites(("mice", "pan")).ok


def r_backend_skip_reason() -> str:
    return check_r_prerequisites(("mice", "pan")).message


def r_rng_skip_reason() -> str:
    if r_rng_available():
        return ""
    return "Rscript or pymice R RNG server unavailable"