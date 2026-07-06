"""Native ``run_ampute_chain`` parity with optional R backend."""

from __future__ import annotations

import numpy as np
import pytest

from pymice import run_ampute_chain
from pymice.methods.r_ampute_backend import r_ampute_available, run_ampute_chain_r


def _v07_chain() -> list[dict[str, object]]:
    patterns = np.array([[0, 1, 1], [0, 0, 1], [1, 1, 0], [0, 1, 0]], dtype=np.int_)
    freq = np.array([0.7, 0.1, 0.1, 0.1], dtype=np.float64)
    weights = np.array(
        [[0.0, 0.8, 0.4], [0.0, 0.0, 1.0], [3.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        dtype=np.float64,
    )
    return [
        {"prop": 0.5},
        {"prop": 0.2, "bycases": False},
        {"freq": freq, "patterns": patterns, "mech": "MAR"},
        {"freq": freq, "patterns": patterns, "mech": "MNAR"},
        {
            "freq": freq,
            "patterns": patterns,
            "weights": weights,
            "cont": True,
            "type": ["RIGHT", "TAIL", "MID", "LEFT"],
            "mech": "MAR",
        },
    ]


@pytest.fixture
def testdata() -> np.ndarray:
    from pathlib import Path

    import pandas as pd

    path = Path(__file__).resolve().parents[2] / "tests" / "data" / "ampute_testdata.csv"
    return pd.read_csv(path).to_numpy(dtype=np.float64)


def test_run_ampute_chain_prop_adjustment(testdata: np.ndarray) -> None:
    chain = _v07_chain()
    results = run_ampute_chain(testdata, chain[:2], seed=2016)
    assert results[0].prop == 0.5
    assert results[1].prop == pytest.approx(0.6)


@pytest.mark.r_backend
@pytest.mark.skipif(not r_ampute_available(), reason="R ampute backend unavailable")
def test_run_ampute_chain_matches_r_backend(testdata: np.ndarray) -> None:
    chain = _v07_chain()
    py_results = run_ampute_chain(testdata, chain, seed=2016)
    r_results = run_ampute_chain_r(
        [
            {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in spec.items()}
            for spec in chain
        ],
        seed=2016,
    )
    for i, (py_res, r_res) in enumerate(zip(py_results, r_results, strict=True)):
        assert py_res.prop == pytest.approx(r_res.prop)
        if i >= 2:
            assert py_res.mech == r_res.mech
        if py_res.amp is not None and r_res.amp is not None:
            py_miss = int(np.sum(np.isnan(py_res.amp)))
            r_miss = int(np.sum(np.isnan(r_res.amp)))
            assert py_miss == pytest.approx(r_miss, rel=0.08)
