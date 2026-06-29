"""Sub-daily precipitation imputation via storm templates (Phase 6c)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.adapter import ImputeConfig, _config_from_any, _run_mice_on_frame
from pymice.integrations.weppcliff.diagnostics import ImputationReport
from pymice.integrations.weppcliff.ei_validate import (
    EIValidationResult,
    validate_i30_against_donors,
)
from pymice.integrations.weppcliff.overlap import resolve_overlaps, trim_overlap_durations
from pymice.integrations.weppcliff.storm_template import (
    apply_template_to_day,
    cluster_median_start,
    extract_day_templates,
    select_donor_template,
)


def impute_subdaily_timeseries(
    imp_df: pd.DataFrame,
    *,
    observed_ts: pd.DataFrame,
    daily_events: pd.DataFrame,
    config: ImputeConfig,
    imp_method: str = "midastouch",
) -> tuple[pd.DataFrame, ImputationReport, list[EIValidationResult]]:
    """
    Impute sub-daily ``DUR``/``PRECIP``/time fields using storm-template donors.

    Parameters
    ----------
    imp_df
        Rows with CLUSTER, DUR, PRECIP, HOUR, MINUTE, SECOND (NA where missing).
    observed_ts
        Original precipitation timeseries before NA masking (donor pool).
    daily_events
        Per wet-day metadata: YYYYMMDD, BPS, ELEN, PRECIP, CLUSTER.
    """
    config = _config_from_any(config)
    rep = ImputationReport(strategies=["storm_template"])
    ei_results: list[EIValidationResult] = []

    work = imp_df.copy()
    value_cols = [c for c in ("DUR", "PRECIP", "HOUR", "MINUTE", "SECOND") if c in work.columns]
    if not value_cols:
        return work, rep, ei_results

    templates = extract_day_templates(observed_ts)
    if not templates:
        rep.strategies.append("storm_template_no_donors")
        if work[value_cols].isna().any().any():
            filled = _run_mice_on_frame(work[value_cols], imp_method=imp_method, config=config)
            for col in value_cols:
                work[col] = filled[col].to_numpy()
        return work, rep, ei_results

    rng = np.random.default_rng(config.seed)
    dates = daily_events.copy()
    if "YYYYMMDD" not in dates.columns:
        raise ValueError("daily_events must contain YYYYMMDD")

    dates["YYYYMMDD"] = dates["YYYYMMDD"].astype(str)
    donor_frames: dict[str, list[pd.DataFrame]] = {}
    for tpl in templates:
        donor_frames.setdefault(tpl.yyyymmdd, []).append(
            observed_ts.loc[observed_ts["YYYYMMDD"].astype(str) == tpl.yyyymmdd].copy()
        )

    if "YYYYMMDD" not in work.columns and "DT_1" in work.columns:
        work["YYYYMMDD"] = pd.to_datetime(work["DT_1"]).dt.strftime("%Y%m%d")

    out_parts: list[pd.DataFrame] = []
    for ymd, day_idx in work.groupby(work["YYYYMMDD"].astype(str), sort=False):
        day_rows = day_idx.copy()
        needs_fill = day_rows[value_cols].isna().any(axis=1)
        if not needs_fill.any():
            out_parts.append(day_rows)
            continue

        meta = dates.loc[dates["YYYYMMDD"] == str(ymd)]
        if meta.empty:
            out_parts.append(day_rows)
            continue
        meta_row = meta.iloc[0]
        cluster = int(meta_row.get("CLUSTER", day_rows["CLUSTER"].iloc[0]))
        bps = int(meta_row.get("BPS", needs_fill.sum()) or needs_fill.sum())
        daily_p = float(meta_row.get("PRECIP", day_rows["PRECIP"].sum(skipna=True)) or 0.0)

        donor = select_donor_template(
            templates,
            cluster=cluster,
            bps=bps,
            daily_precip=daily_p,
            rng=rng,
        )
        if donor is None:
            rep.strategies.append(f"fcs_fallback_{ymd}")
            filled = _run_mice_on_frame(day_rows[value_cols], imp_method=imp_method, config=config)
            for col in value_cols:
                day_rows[col] = filled[col].to_numpy()
            out_parts.append(day_rows)
            continue

        start_min = cluster_median_start(templates, cluster)
        synth = apply_template_to_day(
            donor,
            yyyymmdd=str(ymd),
            daily_precip=daily_p,
            bps=bps,
            cluster=cluster,
            start_minute=start_min,
        )
        rep.strategies.append(f"template_{ymd}")

        fill_locs = day_rows.index[needs_fill]
        n_fill = min(len(fill_locs), len(synth))
        for i in range(n_fill):
            loc = fill_locs[i]
            for col in value_cols:
                if col in synth.columns:
                    day_rows.loc[loc, col] = synth.iloc[i][col]

        if "DT_1" in day_rows.columns:
            for i in range(n_fill):
                day_rows.loc[fill_locs[i], "DT_1"] = synth.iloc[i]["DT_1"]

        cluster_donors = [observed_ts.loc[observed_ts["CLUSTER"] == cluster].copy()]
        if "DT_1" in day_rows.columns:
            ei = validate_i30_against_donors(
                day_rows[needs_fill][["DT_1", "DUR", "PRECIP"]].dropna(subset=["DT_1"]),
                cluster_donors,
            )
            ei_results.append(ei)
            if not ei.passed:
                rep.strategies.append(f"i30_warn_{ymd}")

        out_parts.append(day_rows)

    result = pd.concat(out_parts, ignore_index=True) if out_parts else work
    if "DT_1" in result.columns:
        result = resolve_overlaps(result)
        result = trim_overlap_durations(result)

    rep.n_imputed_cells = int(result[value_cols].notna().sum().sum())
    return result, rep, ei_results
