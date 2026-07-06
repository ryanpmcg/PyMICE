"""R help pager snapshots for vignette parity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.help_format import R_HELP_BOYS, R_HELP_MAMMAL, R_HELP_NHANES, format_help_r  # noqa: E402


def test_format_help_r_topics() -> None:
    assert format_help_r("nhanes") == R_HELP_NHANES
    assert format_help_r("boys") == R_HELP_BOYS
    assert format_help_r("mammalsleep") == R_HELP_MAMMAL
    assert format_help_r("?boys") == R_HELP_BOYS
