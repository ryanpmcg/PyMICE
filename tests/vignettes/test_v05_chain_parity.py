"""V05 session-chain parity: factor class + R remove.lindep logged events."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.data import load_popncr, popncr_variable_specs  # noqa: E402
from lib.golden import golden_output as g  # noqa: E402
from lib.r_style import compare_output, format_logged_events_warning_r  # noqa: E402
from lib.vignette_rng import (  # noqa: E402
    _v05_norm_setup,
    mice_vignette,
    start_vignette_rng_session,
)

from pymice.rng import RSession  # noqa: E402
from tests.r_support import r_backend_available, r_backend_skip_reason  # noqa: E402

pytestmark = [
    pytest.mark.r_backend,
    pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason()),
]


@pytest.fixture
def popncr_imp2():
    """imp2 on session stream with R-style factor ``class`` (steps 11–12)."""
    RSession.close()
    start_vignette_rng_session(123)
    data, names = load_popncr()
    specs = popncr_variable_specs(data, names)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        ini = mice_vignette(
            data,
            column_names=names,
            variable_specs=specs,
            maxit=0,
            print_flag=False,
        )
        meth, pred_nc, _ = _v05_norm_setup(ini, names)
        mice_vignette(
            data,
            column_names=names,
            variable_specs=specs,
            method=meth,
            predictor_matrix=pred_nc,
            m=5,
            maxit=5,
            print_flag=False,
        )
        pred2 = ini.predictor_matrix.copy()
        pred2[:, names.index("pupil")] = 0
        imp2 = mice_vignette(
            data,
            column_names=names,
            variable_specs=specs,
            method=meth,
            predictor_matrix=pred2,
            m=5,
            maxit=5,
            print_flag=False,
        )
    return imp2


def test_v05_imp2_logged_events_match_r(popncr_imp2) -> None:
    act = format_logged_events_warning_r(len(popncr_imp2.logged_events))
    match, _ = compare_output(g("05", 11, 27), act, exact=True)
    assert match
    assert len(popncr_imp2.logged_events) == 90
