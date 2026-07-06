"""R ``print(imp)`` formatter parity for default ``mice(nhanes)``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.r_style import format_mids_print_r  # noqa: E402
from lib.vignette_rng import run_v01_mice_chain, start_vignette_rng_session  # noqa: E402
from runners.v01_ad_hoc_mice import R_MIDS_PRINT  # noqa: E402

from pymice import data  # noqa: E402
from pymice.rng import RSession  # noqa: E402


@pytest.mark.skipif(
    __import__("subprocess").run(["which", "Rscript"], capture_output=True).returncode != 0,
    reason="Rscript not available",
)
def test_format_mids_print_r_matches_r_golden() -> None:
    RSession.close()
    start_vignette_rng_session(123)
    nhanes = data("nhanes")
    *_, imp_pmm = run_v01_mice_chain(nhanes, plot_bmi_density=False)
    actual = format_mids_print_r(imp_pmm)
    assert actual == R_MIDS_PRINT
