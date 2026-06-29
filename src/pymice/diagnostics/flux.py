"""Flux diagnostics (R ``mice:::flux`` / ``fluxplot``)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class FluxResult:
    """Per-variable flux statistics."""

    column_names: list[str]
    pobs: NDArray[np.float64]
    influx: NDArray[np.float64]
    outflux: NDArray[np.float64]
    ainb: NDArray[np.float64]
    aout: NDArray[np.float64]
    fico: NDArray[np.float64]


def _md_pairs(missing: NDArray[np.bool_]) -> tuple[NDArray[np.int_], ...]:
    """Pairwise missingness counts (R ``md.pairs``)."""
    r = ~missing
    rr = r.T.astype(np.int_) @ r.astype(np.int_)
    mm = (~r).T.astype(np.int_) @ (~r).astype(np.int_)
    mr = (~r).T.astype(np.int_) @ r.astype(np.int_)
    rm = r.T.astype(np.int_) @ (~r).astype(np.int_)
    return rr, rm, mr, mm


def _avg_r(row: NDArray[np.floating]) -> float:
    """R ``.avg``: sum(row, na.rm=TRUE) / (length(row) - 1)."""
    finite = np.isfinite(row)
    if len(row) <= 1:
        return 0.0
    return float(np.sum(row[finite]) / (len(row) - 1))


def flux(
    data: NDArray[np.floating],
    column_names: list[str] | None = None,
) -> FluxResult:
    """Compute flux table for incomplete data (R ``flux()``)."""
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError("data must be a matrix with at least two columns")

    names = column_names or [f"V{j + 1}" for j in range(data.shape[1])]
    missing = np.isnan(data)
    pobs = np.mean(~missing, axis=0)

    rr, rm, mr, mm = _md_pairs(missing)
    with np.errstate(divide="ignore", invalid="ignore"):
        influx = np.sum(mr, axis=1) / np.sum(mr + rr, axis=1)
        outflux = np.sum(rm, axis=1) / np.sum(rm + mm, axis=1)
        ainb_ratio = mr / (mr + mm)
        aout_ratio = rm / (rm + rr)
    ainb = np.array([_avg_r(ainb_ratio[j]) for j in range(data.shape[1])])
    aout = np.array([_avg_r(aout_ratio[j]) for j in range(data.shape[1])])

    incomplete_rows = np.any(missing, axis=1)
    fico = np.array(
        [
            np.sum((~missing[:, j]) & incomplete_rows) / np.sum(~missing[:, j])
            if np.any(~missing[:, j])
            else 0.0
            for j in range(data.shape[1])
        ]
    )

    return FluxResult(
        column_names=names,
        pobs=pobs,
        influx=np.nan_to_num(influx, nan=0.0),
        outflux=np.nan_to_num(outflux, nan=0.0),
        ainb=np.nan_to_num(ainb, nan=0.0),
        aout=np.nan_to_num(aout, nan=0.0),
        fico=fico,
    )
