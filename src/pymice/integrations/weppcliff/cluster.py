"""Temporal cluster construction and granularity selection for WEPPCLIFF."""

from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

Granularity = Literal["seasonal", "month", "half_month", "quarter_month"]

GRANULARITY_ORDER: tuple[Granularity, ...] = (
    "quarter_month",
    "half_month",
    "month",
    "seasonal",
)

_COARSEST: Granularity = "seasonal"


def season_from_month(month: int, lat: float = 45.0) -> int:
    """Meteorological season 1–4 (DJF, MAM, JJA, SON), lat-aware."""
    m = int(month)
    if lat < 0.0:
        m = ((m + 5) % 12) + 1
    if m in (12, 1, 2):
        return 1
    if m in (3, 4, 5):
        return 2
    if m in (6, 7, 8):
        return 3
    return 4


def _month_quarter(day: int) -> int:
    q = int(day)
    if q <= 7:
        return 1
    if q >= 24:
        return 4
    if q >= 16:
        return 3
    if q >= 8:
        return 2
    return q


def _vectors_for_dates(
    dates_yyyymmdd: list[str],
    *,
    lat: float = 45.0,
) -> dict[Granularity, NDArray[np.int_]]:
    """Build cluster-id vectors for each granularity candidate."""
    mns = np.array([int(d[4:6]) for d in dates_yyyymmdd], dtype=np.int_)
    days = np.array([int(d[6:8]) for d in dates_yyyymmdd], dtype=np.int_)
    qtr = np.array([_month_quarter(d) for d in days], dtype=np.int_)
    sns = np.array([season_from_month(m, lat) for m in mns], dtype=np.int_)
    hmn = 2 * mns
    hmn = np.where(qtr <= 2, hmn - 1, hmn)
    qmn = 2 * hmn
    qmn = np.where((qtr == 1) | (qtr == 3), qmn - 1, qmn)
    return {
        "seasonal": sns,
        "month": mns,
        "half_month": hmn.astype(np.int_),
        "quarter_month": qmn.astype(np.int_),
    }


def build_cluster_candidates(
    dates_yyyymmdd: list[str],
    *,
    lat: float = 45.0,
) -> dict[Granularity, NDArray[np.int_]]:
    """Return cluster label arrays for all granularity tiers."""
    return _vectors_for_dates(dates_yyyymmdd, lat=lat)


def _min_complete_per_cluster(
    cluster_ids: NDArray[np.int_],
    complete_row: NDArray[np.bool_],
) -> int:
    counts: list[int] = []
    for cid in np.unique(cluster_ids):
        mask = cluster_ids == cid
        counts.append(int(np.sum(complete_row[mask])))
    return min(counts) if counts else 0


def _mean_within_cluster_cv(
    values: NDArray[np.float64],
    cluster_ids: NDArray[np.int_],
    complete_row: NDArray[np.bool_],
) -> float:
    cvs: list[float] = []
    for j in range(values.shape[1]):
        col = values[:, j]
        for cid in np.unique(cluster_ids):
            mask = (cluster_ids == cid) & complete_row
            obs = col[mask]
            obs = obs[np.isfinite(obs)]
            if obs.size < 3:
                continue
            mu = float(np.mean(obs))
            if abs(mu) < 1e-12:
                continue
            cvs.append(float(np.std(obs) / abs(mu)))
    return float(np.median(cvs)) if cvs else 0.0


def _quickpred_stability(
    values: NDArray[np.float64],
    *,
    mincor: float = 0.2,
    n_boot: int = 25,
    seed: int = 42,
) -> float:
    """Fraction of predictor edges that persist across bootstrap resamples."""
    from pymice.quickpred import quickpred

    n_obs, n_var = values.shape
    if n_obs < 10 or n_var < 2:
        return 1.0
    rng = np.random.default_rng(seed)
    base = quickpred(values, mincor=mincor)
    base_edges = base > 0
    hits = np.zeros_like(base_edges, dtype=np.float64)
    for _ in range(n_boot):
        idx = rng.integers(0, n_obs, size=n_obs)
        sample = values[idx]
        boot = quickpred(sample, mincor=mincor) > 0
        hits += (boot & base_edges).astype(np.float64)
    denom = float(np.sum(base_edges))
    if denom == 0:
        return 1.0
    return float(np.mean(hits[base_edges] / n_boot))


def select_cluster_granularity(
    dates_yyyymmdd: list[str],
    value_matrix: NDArray[np.float64] | None = None,
    *,
    lat: float = 45.0,
    n_vars: int | None = None,
    min_stability: float = 0.6,
    seed: int = 42,
) -> tuple[Granularity, NDArray[np.int_]]:
    """
    Choose the finest feasible cluster granularity.

    Never returns a single global cluster; coarsest tier is seasonal (4).
    """
    candidates = build_cluster_candidates(dates_yyyymmdd, lat=lat)
    p = n_vars or (value_matrix.shape[1] if value_matrix is not None else 1)
    n_min = max(30, 5 * p)

    complete_row: NDArray[np.bool_] | None = None
    if value_matrix is not None and value_matrix.size:
        complete_row = np.all(np.isfinite(value_matrix), axis=1)

    chosen: Granularity = _COARSEST
    for gran in GRANULARITY_ORDER:
        labels = candidates[gran]
        if complete_row is None:
            counts = [int(np.sum(labels == cid)) for cid in np.unique(labels)]
            if min(counts) >= n_min:
                chosen = gran
                break
            continue

        min_n = _min_complete_per_cluster(labels, complete_row)
        if min_n < n_min:
            continue

        obs = value_matrix[complete_row]
        if obs.shape[0] < n_min:
            continue

        noise = _mean_within_cluster_cv(value_matrix, labels, complete_row)
        adjusted_min = int(n_min * (1.0 + min(noise, 1.0)))
        if min_n < adjusted_min:
            continue

        stability = _quickpred_stability(obs, seed=seed)
        if stability < min_stability and gran != _COARSEST:
            continue

        chosen = gran
        break

    return chosen, candidates[chosen]


def assign_cluster_labels(
    dates_yyyymmdd: list[str],
    value_matrix: NDArray[np.float64] | None = None,
    *,
    lat: float = 45.0,
    n_vars: int | None = None,
) -> NDArray[np.int_]:
    """Convenience: select granularity and return cluster ids."""
    _, labels = select_cluster_granularity(
        dates_yyyymmdd,
        value_matrix,
        lat=lat,
        n_vars=n_vars,
    )
    return labels
