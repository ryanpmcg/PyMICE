"""Phase 6b: priors, missingness, resilience."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.adapter import ImputeConfig
from pymice.integrations.weppcliff.missingness import MissingnessKind, classify_missingness
from pymice.integrations.weppcliff.priors import (
    KoppenPriorStore,
    impute_from_prior,
    infer_koppen_zone,
    load_default_priors,
    prior_weight,
)
from pymice.integrations.weppcliff.resilience import resilient_impute_by_cluster


def test_infer_koppen_zone_tropical():
    assert infer_koppen_zone(10.0) == "Am"


def test_prior_weight_zero_without_data():
    assert prior_weight(0, 30) == 0.0


def test_prior_weight_increases_with_n():
    assert prior_weight(60, 30) > prior_weight(10, 30)


def test_classify_persistent_seasonal_sparse_cluster():
    df = pd.DataFrame(
        {
            "CLUSTER": [7] * 40 + [8] * 40,
            "MIN_TEMP": [np.nan] * 40 + list(range(40)),
            "MAX_TEMP": [np.nan] * 40 + list(range(40, 80)),
        }
    )
    profile = classify_missingness(df, ["MIN_TEMP", "MAX_TEMP"], n_min=30)
    assert MissingnessKind.PERSISTENT_SEASONAL in profile.kinds
    assert profile.recommend_prior()


def test_impute_from_prior_fills_empty_cluster():
    store = load_default_priors()
    df = pd.DataFrame(
        {
            "CLUSTER": [3, 3, 3],
            "MIN_TEMP": [np.nan, np.nan, np.nan],
            "MAX_TEMP": [np.nan, np.nan, np.nan],
        }
    )
    out = impute_from_prior(
        df,
        ["MIN_TEMP", "MAX_TEMP"],
        store=store,
        zone="Cfa",
        lat=40.0,
        weight=0.0,
        rng=np.random.default_rng(0),
    )
    assert out["MIN_TEMP"].notna().all()
    assert out["MAX_TEMP"].notna().all()


def test_resilience_uses_prior_for_all_missing_cluster():
    rng = np.random.default_rng(2)
    n = 80
    df = pd.DataFrame(
        {
            "CLUSTER": [3] * n,
            "MIN_TEMP": rng.normal(18, 2, n),
            "MAX_TEMP": rng.normal(28, 2, n),
        }
    )
    df.loc[:, "MIN_TEMP"] = np.nan
    df.loc[:, "MAX_TEMP"] = np.nan
    config = ImputeConfig(pm="t", kg="Cfa", lat=40.0, io=15, seed=3)
    out, report = resilient_impute_by_cluster(df, "midastouch", config)
    assert out["MIN_TEMP"].notna().all()
    assert "koppen_prior" in report.strategies or "mean_fallback" in report.strategies


def test_koppen_store_loads_bundled():
    store = KoppenPriorStore.load()
    assert "Cfa" in store.zones
    prior = store.variable_prior("Cfa", 3, "MAX_TEMP", lat=40.0)
    assert prior is not None
    assert prior.mean > 20.0
