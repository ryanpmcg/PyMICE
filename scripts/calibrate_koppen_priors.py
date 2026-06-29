#!/usr/bin/env python3
"""
Calibrate Köppen prior JSON from a CSV of station daily weather.

Expected columns: KOPPEN (or KG), YYYYMMDD, and WEPPCLIFF variable names.
Writes versioned JSON compatible with ``KoppenPriorStore``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from pymice.integrations.weppcliff.cluster import season_from_month


def _seasons_for_frame(df: pd.DataFrame, lat: float) -> pd.Series:
    months = df["YYYYMMDD"].astype(str).str[4:6].astype(int)
    return months.map(lambda m: season_from_month(m, lat))


def calibrate(
    path: Path,
    *,
    zone_col: str = "KOPPEN",
    lat_col: str = "LAT",
    variables: list[str],
    out: Path,
) -> None:
    df = pd.read_csv(path)
    if zone_col not in df.columns:
        raise ValueError(f"column {zone_col!r} required")

    zones: dict = {"version": 1, "zones": {}}
    for zone, grp in df.groupby(zone_col):
        lat = float(grp[lat_col].iloc[0]) if lat_col in grp.columns else 45.0
        seasons = _seasons_for_frame(grp, lat)
        zone_entry: dict = {"seasons": {}}
        for season in sorted(seasons.unique()):
            sub = grp.loc[seasons == season]
            var_stats: dict = {}
            for var in variables:
                if var not in sub.columns:
                    continue
                vals = pd.to_numeric(sub[var], errors="coerce").dropna()
                if vals.empty:
                    continue
                var_stats[var] = {
                    "mean": float(vals.mean()),
                    "std": float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
                }
            zone_entry["seasons"][str(int(season))] = var_stats
        zones["zones"][str(zone)] = zone_entry

    out.write_text(json.dumps(zones, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({len(zones['zones'])} zones)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("-o", "--out", type=Path, default=Path("koppen_priors.json"))
    parser.add_argument(
        "--vars",
        nargs="+",
        default=["MIN_TEMP", "MAX_TEMP", "SO_RAD", "W_VEL", "DP_TEMP", "PRECIP"],
    )
    args = parser.parse_args()
    calibrate(args.csv, variables=args.vars, out=args.out)


if __name__ == "__main__":
    main()
