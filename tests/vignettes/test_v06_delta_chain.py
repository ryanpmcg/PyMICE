"""V06 leiden δ-chain uses R vignette seeds and ``rng='r'``."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.data import load_leiden  # noqa: E402
from lib.vignette_rng import (  # noqa: E402
    run_v06_leiden_delta_chain,
    start_vignette_rng_session,
)

from pymice.rng import RSession  # noqa: E402

from tests.r_support import r_backend_available, r_backend_skip_reason  # noqa: E402

pytestmark = [
    pytest.mark.r_backend,
    pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason()),
]


def test_v06_leiden_delta_chain_seeds() -> None:
    RSession.close()
    start_vignette_rng_session(123)
    data, names = load_leiden()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        imp_all = run_v06_leiden_delta_chain(data, names)
    assert len(imp_all) == 5
    assert all(imp.m == 5 for imp in imp_all)
    assert imp_all[0].seed == 1
    assert imp_all[4].seed == 5
    assert all(imp.rng_backend == "r" for imp in imp_all)
