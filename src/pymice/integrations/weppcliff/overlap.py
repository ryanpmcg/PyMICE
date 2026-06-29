"""Interval-aware overlap resolution for sub-daily precipitation breakpoints."""

from __future__ import annotations

import pandas as pd


def _merge_duplicate_times(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("DT_1").reset_index(drop=True)
    if out.empty:
        return out
    keep_rows: list[dict] = []
    for dt, grp in out.groupby("DT_1", sort=True):
        row = grp.iloc[0].to_dict()
        row["PRECIP"] = float(grp["PRECIP"].sum())
        row["DUR"] = float(grp["DUR"].max())
        keep_rows.append(row)
    return pd.DataFrame(keep_rows).sort_values("DT_1").reset_index(drop=True)


def _resolve_day_intervals(day_df: pd.DataFrame, *, min_gap_min: float = 0.5) -> pd.DataFrame:
    """Retime breakpoints within a day to remove duration-interval overlap."""
    if len(day_df) <= 1:
        return day_df

    out = day_df.sort_values("DT_1").reset_index(drop=True).copy()
    starts = pd.to_datetime(out["DT_1"])
    durs = out["DUR"].astype(float).to_numpy()
    starts + pd.to_timedelta(durs, unit="m")

    new_starts = [starts.iloc[0]]
    for i in range(1, len(out)):
        prev_end = new_starts[-1] + pd.Timedelta(minutes=float(durs[i - 1]))
        desired = starts.iloc[i]
        if desired < prev_end + pd.Timedelta(minutes=min_gap_min):
            desired = prev_end + pd.Timedelta(minutes=min_gap_min)
        new_starts.append(desired)

    out["DT_1"] = new_starts
    if "HOUR" in out.columns:
        out["HOUR"] = out["DT_1"].dt.hour
        out["MINUTE"] = out["DT_1"].dt.minute
        out["SECOND"] = out["DT_1"].dt.second
    return out


def resolve_overlaps(
    df: pd.DataFrame,
    *,
    date_col: str = "YYYYMMDD",
    min_gap_min: float = 0.5,
) -> pd.DataFrame:
    """
    Replace duplicate-merge + DUR-trim loop with explicit interval scheduling.

    Preserves daily ``PRECIP`` totals; retimes within day when intervals overlap.
    """
    if df.empty or "DT_1" not in df.columns:
        return df

    work = df.copy()
    work["DT_1"] = pd.to_datetime(work["DT_1"])
    work = _merge_duplicate_times(work)

    if date_col not in work.columns:
        work[date_col] = work["DT_1"].dt.strftime("%Y%m%d")

    parts = [
        _resolve_day_intervals(grp, min_gap_min=min_gap_min)
        for _, grp in work.groupby(work[date_col].astype(str), sort=False)
    ]
    return pd.concat(parts, ignore_index=True).sort_values("DT_1").reset_index(drop=True)


def trim_overlap_durations(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy-compatible duration trim when next event starts before current ends."""
    out = df.sort_values("DT_1").reset_index(drop=True).copy()
    if len(out) < 2:
        return out
    lap_time = out["DT_1"] + pd.to_timedelta(out["DUR"], unit="m")
    lap_diff = (lap_time - out["DT_1"].shift(-1)).dt.total_seconds() / 60.0
    lap_diff = lap_diff.fillna(0.0).clip(lower=0.0)
    locs = lap_diff[lap_diff > 0].index
    if len(locs):
        out.loc[locs, "DUR"] = out.loc[locs, "DUR"] - lap_diff.loc[locs]
        out["DUR"] = out["DUR"].clip(lower=0.1)
    return out
