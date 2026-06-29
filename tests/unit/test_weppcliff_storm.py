"""Tests for sub-daily storm template imputation and event-based overlap validation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.adapter import ImputeConfig
from pymice.integrations.weppcliff.ei_validate import i30_proxy, validate_i30_against_donors
from pymice.integrations.weppcliff.overlap import resolve_overlaps
from pymice.integrations.weppcliff.storm_template import (
    apply_template_to_day,
    extract_day_templates,
    select_donor_template,
)
from pymice.integrations.weppcliff.subdaily import impute_subdaily_timeseries


def _synthetic_observed_day(ymd: str, cluster: int = 6, n: int = 4) -> pd.DataFrame:
    base = pd.to_datetime(ymd, format="%Y%m%d")
    rows = []
    for i in range(n):
        t = base + pd.Timedelta(minutes=60 + i * 12)
        rows.append(
            {
                "DT_1": t,
                "YYYYMMDD": ymd,
                "CLUSTER": cluster,
                "DUR": 5.0,
                "PRECIP": 2.0 + i * 0.5,
            }
        )
    return pd.DataFrame(rows)


def test_extract_day_templates():
    obs = pd.concat(
        [
            _synthetic_observed_day("20200601"),
            _synthetic_observed_day("20200602"),
        ],
        ignore_index=True,
    )
    tpls = extract_day_templates(obs)
    assert len(tpls) == 2
    assert tpls[0].bps == 4


def test_apply_template_preserves_daily_total():
    obs = _synthetic_observed_day("20200601")
    tpls = extract_day_templates(obs)
    rng = np.random.default_rng(0)
    donor = select_donor_template(tpls, cluster=6, bps=4, daily_precip=10.0, rng=rng)
    assert donor is not None
    out = apply_template_to_day(donor, yyyymmdd="20200615", daily_precip=10.0, bps=4, cluster=6)
    assert abs(out["PRECIP"].sum() - 10.0) < 0.01


def test_resolve_overlaps_separates_intervals():
    base = pd.to_datetime("20200601")
    df = pd.DataFrame(
        {
            "DT_1": [base, base + pd.Timedelta(minutes=2)],
            "YYYYMMDD": ["20200601", "20200601"],
            "DUR": [10.0, 5.0],
            "PRECIP": [1.0, 2.0],
        }
    )
    out = resolve_overlaps(df)
    ends = out["DT_1"] + pd.to_timedelta(out["DUR"], unit="m")
    assert ends.iloc[0] <= out["DT_1"].iloc[1]


def test_i30_proxy_positive_for_clustered_precip():
    day = _synthetic_observed_day("20200601", n=6)
    assert i30_proxy(day) > 0.0


def test_subdaily_imputation_fills_missing_rows():
    obs = pd.concat(
        [
            _synthetic_observed_day("20200601"),
            _synthetic_observed_day("20200602"),
            _synthetic_observed_day("20200701", cluster=7),
        ],
        ignore_index=True,
    )
    target = _synthetic_observed_day("20200620")
    target["PRECIP"] = np.nan
    target["DUR"] = np.nan
    target["HOUR"] = np.nan
    target["MINUTE"] = np.nan
    target["SECOND"] = np.nan
    imp = target.copy()
    imp["CLUSTER"] = 6
    daily = pd.DataFrame(
        {
            "YYYYMMDD": ["20200620"],
            "BPS": [4],
            "ELEN": [1],
            "PRECIP": [float(obs.loc[obs["YYYYMMDD"] == "20200601", "PRECIP"].sum())],
            "CLUSTER": [6],
        }
    )
    config = ImputeConfig(pm="t", st="t", seed=1)
    out, report, _ei = impute_subdaily_timeseries(
        imp,
        observed_ts=obs,
        daily_events=daily,
        config=config,
    )
    assert out["PRECIP"].notna().all()
    assert "template_20200620" in report.strategies or "storm_template" in report.strategies


def test_ei_validation_warns_on_sparse_intensity():
    donor = _synthetic_observed_day("20200601", n=8)
    imputed = donor.copy()
    imputed["PRECIP"] = 0.1
    result = validate_i30_against_donors(imputed, [donor], min_ratio=0.5)
    assert (
        result.ratio < 0.5
        or result.passed is False
        or result.i30_imputed <= result.i30_donor_median
    )
