"""Tests for Cox PH survival analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from pymice.analysis.survival import leiden_coxph

DATA = Path(__file__).resolve().parents[1] / "data"


def _load_leiden() -> tuple[np.ndarray, list[str]]:
    import csv

    names = [
        "sexe",
        "lftanam",
        "rrsyst",
        "rrdiast",
        "dwa",
        "survda",
        "alb",
        "chol",
        "mmse",
        "woon",
    ]
    with (DATA / "leiden.csv").open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    matrix = np.array(
        [
            [float(r[n]) if r.get(n, "NA") not in ("", "NA") else np.nan for n in names]
            for r in rows
        ],
        dtype=np.float64,
    )
    return matrix, names


@pytest.mark.parametrize(
    "term",
    [
        "C(sbpgp, contr.treatment(6, base = 3))1",
        "C(sbpgp, contr.treatment(6, base = 3))2",
    ],
)
def test_leiden_coxph_matches_r_complete_data(term: str) -> None:
    pytest.importorskip("lifelines")
    data, names = _load_leiden()
    fit = leiden_coxph(data, names)
    assert term in fit.estimate
    assert fit.meta is not None
    assert fit.n_obs == 835
    assert fit.meta["n_events"] > 0
