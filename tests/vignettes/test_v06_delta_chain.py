"""V06 leiden δ-chain uses R vignette seeds and ``rng='r'``."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# devtools on path via tests/conftest.py

from lib.data import load_leiden  # noqa: E402
from lib.vignette_rng import (  # noqa: E402
    ensure_vignette_r_prerequisites,
    run_v06_leiden_delta_chain,
    start_vignette_rng_session,
)

from pymice.rng import RSession  # noqa: E402


def test_v06_leiden_delta_chain_seeds() -> None:
    ensure_vignette_r_prerequisites()
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
