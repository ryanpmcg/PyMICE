"""Tests for R mice diagnostic colors (``mdc``)."""

from __future__ import annotations

from pymice.diagnostics.theme import (
    COLOR_MISSING,
    COLOR_OBSERVED,
    mdc,
)


def test_mdc_numeric_codes():
    obs = mdc(1)
    miss = mdc(2)
    assert len(obs) == 4
    assert len(miss) == 4
    assert obs[2] > obs[0]  # blue dominates over red
    assert miss[0] > miss[2]  # red dominates over blue


def test_mdc_named_aliases():
    assert mdc("observed", "line") == mdc(4)
    assert mdc("missing", "symbol") == mdc(2)


def test_mdc_hex():
    hex_obs = mdc(1, as_hex=True)
    assert isinstance(hex_obs, str)
    assert hex_obs.startswith("#")
    assert len(hex_obs) in {7, 9}


def test_module_constants():
    assert COLOR_OBSERVED == mdc(1)
    assert COLOR_MISSING == mdc(2)
