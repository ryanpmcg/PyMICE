"""Factor-aware R summary / head formatters."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.data import load_boys_full_matrix, load_mammalsleep_full, load_nhanes2  # noqa: E402
from lib.golden import golden_output as g  # noqa: E402
from lib.r_style import compare_output  # noqa: E402
from lib.summary_format import (  # noqa: E402
    format_boys_head_r,
    format_mammalsleep_head_r,
    format_summary_boys_r,
    format_summary_mammalsleep_r,
    format_summary_nhanes2_r,
)


@pytest.mark.parametrize(
    ("loader", "formatter", "golden_key", "kwargs"),
    [
        (load_nhanes2, format_summary_nhanes2_r, ("02", 4, 10), {}),
        (load_boys_full_matrix, format_summary_boys_r, ("03", 3, 4), {}),
        (load_mammalsleep_full, format_summary_mammalsleep_r, ("03", 9, 18), {}),
    ],
)
def test_summary_formatters_match_golden(loader, formatter, golden_key, kwargs) -> None:
    data, names = loader()
    actual = formatter(data, names, **kwargs)
    match, _ = compare_output(g(*golden_key), actual, exact=True)
    assert match


def test_boys_head_matches_golden() -> None:
    match, _ = compare_output(g("03", 3, 2), format_boys_head_r(), exact=True)
    assert match


def test_mammalsleep_head_matches_golden() -> None:
    match, _ = compare_output(g("03", 9, 17), format_mammalsleep_head_r(), exact=True)
    assert match
