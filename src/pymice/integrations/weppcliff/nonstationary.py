"""Time-varying relationship support (year blocks)."""

from __future__ import annotations

import pandas as pd


def year_block_from_dates(
    dates_yyyymmdd: pd.Series | list[str], *, block_years: int = 5
) -> pd.Series:
    """Assign each date to a ``block_years`` calendar-year bin (for ``-ns t``)."""
    if isinstance(dates_yyyymmdd, list):
        dates = pd.Series(dates_yyyymmdd)
    else:
        dates = dates_yyyymmdd.astype(str)
    years = dates.str[:4].astype(int)
    base = int(years.min()) if len(years) else 2000
    return ((years - base) // block_years).astype(int)


def attach_year_block(
    df: pd.DataFrame,
    date_index: pd.Index,
    dates_yyyymmdd: list[str] | None = None,
    *,
    block_years: int = 5,
) -> pd.DataFrame:
    """
    Add ``_YEAR_BLOCK_`` predictor column (fully observed, not imputed).

    ``date_index`` maps ``df`` rows to positions in ``dates_yyyymmdd``.
    """
    if dates_yyyymmdd is None or not len(dates_yyyymmdd):
        out = df.copy()
        out["_YEAR_BLOCK_"] = 0
        return out

    blocks = year_block_from_dates(dates_yyyymmdd, block_years=block_years)
    out = df.copy()
    mapped = [int(blocks.iloc[i]) if i < len(blocks) else 0 for i in date_index]
    out["_YEAR_BLOCK_"] = mapped
    return out


def adjacent_cluster_ids(cluster_id: int, granularity: str = "month") -> list[int]:
    """Neighbors for pooling when a cluster has persistent missingness."""
    cid = int(cluster_id)
    if granularity == "seasonal":
        return [((cid - 2) % 4) + 1, (cid % 4) + 1]
    if granularity == "month":
        return [((cid - 2) % 12) + 1, (cid % 12) + 1]
    return [cid - 1, cid + 1]
