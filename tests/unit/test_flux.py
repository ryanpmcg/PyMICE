"""Flux diagnostics parity with R mice::flux."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from pymice.diagnostics.flux import flux

ROOT = Path(__file__).resolve().parents[2]
LEIDEN = ROOT / "tests" / "data" / "leiden.csv"


def _load_leiden() -> tuple[np.ndarray, list[str]]:
    names = ["sexe", "lftanam", "rrsyst", "rrdiast", "dwa", "survda", "alb", "chol", "mmse", "woon"]
    with LEIDEN.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    data = np.array(
        [[float(r[n]) if r[n] != "NA" else np.nan for n in names] for r in rows],
        dtype=np.float64,
    )
    return data, names


def test_flux_rrsyst_matches_r():
    data, names = _load_leiden()
    fx = flux(data, names)
    i = names.index("rrsyst")
    np.testing.assert_allclose(fx.pobs[i], 0.8734310, rtol=0, atol=1e-6)
    np.testing.assert_allclose(fx.influx[i], 0.09798107, rtol=0, atol=1e-6)
    np.testing.assert_allclose(fx.outflux[i], 0.5573770, rtol=0, atol=1e-6)
    np.testing.assert_allclose(fx.ainb[i], 0.7887971, rtol=0, atol=1e-5)
    np.testing.assert_allclose(fx.aout[i], 0.05881570, rtol=0, atol=1e-6)
    np.testing.assert_allclose(fx.fico[i], 0.2562874, rtol=0, atol=1e-6)
