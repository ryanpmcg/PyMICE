"""Shrink local estimates toward Köppen regional priors."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.priors.store import KoppenPriorStore, VarPrior


def prior_weight(n_complete: int, n_min: int) -> float:
    """
    Weight on local data in [0, 1]. More complete cases → more local weight.

    Returns 0 when no local data; approaches 1 as n_complete >> n_min.
    """
    if n_complete <= 0:
        return 0.0
    if n_min <= 0:
        return 1.0
    return float(min(1.0, n_complete / (2.0 * n_min)))


def blend_series(
    local: float | None,
    prior: VarPrior,
    *,
    weight: float,
    rng: np.random.Generator | None = None,
) -> float:
    """Blend local estimate with prior mean; add prior noise when local is absent."""
    w = float(np.clip(weight, 0.0, 1.0))
    if local is None or (isinstance(local, float) and np.isnan(local)):
        base = prior.mean
        if rng is not None and prior.std > 0:
            return float(rng.normal(base, prior.std * 0.25))
        return base
    return float(w * local + (1.0 - w) * prior.mean)


def impute_from_prior(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    store: KoppenPriorStore,
    zone: str,
    lat: float,
    lon: float = 0.0,
    granularity: str = "seasonal",
    weight: float = 0.0,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Fill remaining NA using zone × season marginals (6b fallback)."""
    out = df.copy()
    if "CLUSTER" not in out.columns:
        return out

    for cid in out["CLUSTER"].dropna().unique():
        locs = out.index[out["CLUSTER"] == cid]
        season = store.season_for_cluster(int(cid), granularity)
        n_complete = int(out.loc[locs, value_cols].notna().all(axis=1).sum())
        w = prior_weight(n_complete, max(30, 5 * len(value_cols))) if weight <= 0 else weight

        for col in value_cols:
            if col not in out.columns:
                continue
            prior = store.variable_prior(zone, season, col, lat=lat, lon=lon)
            if prior is None:
                continue
            missing = locs[out.loc[locs, col].isna()]
            if len(missing) == 0:
                continue
            local_mean = out.loc[locs, col].mean()
            local_val = None if pd.isna(local_mean) else float(local_mean)
            for idx in missing:
                out.loc[idx, col] = blend_series(local_val, prior, weight=w, rng=rng)
    return out
