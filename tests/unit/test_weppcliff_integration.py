"""WEPPCLIFF adapter and cluster selection."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.adapter import ImputeConfig, impute_by_cluster
from pymice.integrations.weppcliff.cluster import (
    season_from_month,
    select_cluster_granularity,
)


def test_season_nh_december_is_winter():
    assert season_from_month(12, lat=40.0) == 1


def test_season_sh_june_is_winter():
    assert season_from_month(6, lat=-40.0) == 1


def test_select_granularity_never_global():
    dates = pd.date_range("2020-01-01", periods=400, freq="D").strftime("%Y%m%d").tolist()
    gran, labels = select_cluster_granularity(dates, n_vars=3)
    assert gran in ("seasonal", "month", "half_month", "quarter_month")
    assert len(np.unique(labels)) >= 4


def test_impute_by_cluster_fills_numeric_gaps():
    rng = np.random.default_rng(1)
    n = 120
    clusters = np.repeat(np.arange(1, 13), n // 12)
    df = pd.DataFrame(
        {
            "CLUSTER": clusters,
            "MIN_TEMP": rng.normal(10, 5, n),
            "MAX_TEMP": rng.normal(20, 5, n),
        }
    )
    df.loc[5:15, "MIN_TEMP"] = np.nan
    df.loc[8:12, "MAX_TEMP"] = np.nan
    config = ImputeConfig(pm="t", io=30, seed=7)
    out = impute_by_cluster(df, "midastouch", config)
    assert out["MIN_TEMP"].notna().all()
    assert out["MAX_TEMP"].notna().all()


def test_impute_jomo_block_fills_coupled_gaps():
    rng = np.random.default_rng(2)
    n = 96
    clusters = np.repeat(np.arange(1, 13), n // 12)
    df = pd.DataFrame(
        {
            "CLUSTER": clusters,
            "MIN_TEMP": rng.normal(5, 3, n),
            "MAX_TEMP": rng.normal(15, 3, n),
            "PRECIP": rng.exponential(2.0, n),
        }
    )
    df.loc[10:25, ["MIN_TEMP", "MAX_TEMP", "PRECIP"]] = np.nan
    config = ImputeConfig(pm="t", jm="t", io=30, seed=11)
    out = impute_by_cluster(df, "midastouch", config)
    assert out[["MIN_TEMP", "MAX_TEMP", "PRECIP"]].notna().all().all()


def test_impute_mean_fallback_when_pm_off():
    df = pd.DataFrame(
        {
            "CLUSTER": [1, 1, 2, 2],
            "X": [1.0, np.nan, 3.0, np.nan],
        }
    )
    config = ImputeConfig(pm="f")
    out = impute_by_cluster(df, "midastouch", config)
    assert out.loc[1, "X"] == 1.0
    assert out.loc[3, "X"] == 3.0
