"""Phase 6d: ampute weather scenarios and imputation quality benchmarks."""

from __future__ import annotations

import pytest

from pymice.integrations.weppcliff.adapter import ImputeConfig, impute_by_cluster
from pymice.integrations.weppcliff.missingness import MissingnessKind
from pymice.integrations.weppcliff.validation import (
    WeatherScenario,
    apply_weather_scenario,
    enforce_temperature_order,
    run_weather_validation_suite,
    score_imputation,
    synthetic_weather_panel,
    validate_scenario,
)


@pytest.fixture
def impute_config() -> ImputeConfig:
    return ImputeConfig(pm="t", io=25, seed=11, lat=40.0, kg="Cfa")


def test_synthetic_panel_complete_and_clustered():
    panel = synthetic_weather_panel(seed=0)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    assert panel[value_cols].notna().all().all()
    assert panel["CLUSTER"].nunique() >= 4
    assert (panel["MIN_TEMP"] <= panel["MAX_TEMP"]).all()


@pytest.mark.parametrize(
    "scenario,expected",
    [
        (WeatherScenario.SHORT_GAPS, MissingnessKind.SHORT_GAPS),
        (WeatherScenario.LONG_GAP_ALL, MissingnessKind.LONG_GAP_ALL),
        (WeatherScenario.PERSISTENT_SEASONAL, MissingnessKind.PERSISTENT_SEASONAL),
        (WeatherScenario.VARIABLE_ABSENT, MissingnessKind.VARIABLE_ABSENT),
        (WeatherScenario.MIXED, MissingnessKind.MIXED),
    ],
)
def test_scenario_masks_classify(scenario, expected):
    panel = synthetic_weather_panel(seed=1)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    masked = apply_weather_scenario(panel, scenario, value_cols, seed=2)
    assert masked.expected_kind == expected
    assert masked.missing_mask.to_numpy().any()
    assert masked.amputed[value_cols].isna().any().any()


def test_ampute_scenario_introduces_missingness():
    panel = synthetic_weather_panel(seed=3)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    masked = apply_weather_scenario(panel, WeatherScenario.MCAR_AMPUTE, value_cols, seed=4)
    assert masked.amputed[value_cols].isna().sum().sum() > 0


def test_validate_scenario_fills_and_scores(impute_config):
    quality = validate_scenario(WeatherScenario.SHORT_GAPS, impute_config, seed=5)
    assert quality.n_filled == quality.n_missing
    assert quality.rmse < 8.0
    assert quality.temp_order_ok
    assert MissingnessKind.SHORT_GAPS in quality.detected_kinds


@pytest.mark.parametrize("scenario", list(WeatherScenario))
def test_all_scenarios_impute_completely(scenario, impute_config):
    panel = synthetic_weather_panel(seed=6)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    masked = apply_weather_scenario(panel, scenario, value_cols, seed=7)
    work = masked.amputed[["CLUSTER", *value_cols]].copy()
    imputed = enforce_temperature_order(impute_by_cluster(work, "midastouch", impute_config))
    assert imputed[value_cols].notna().all().all()
    quality = score_imputation(
        panel, imputed, masked.missing_mask, value_cols, scenario=scenario.value
    )
    assert quality.n_filled == quality.n_missing
    assert quality.temp_order_ok


def test_pymice_beats_mean_fill_on_absent_variable(impute_config):
    panel = synthetic_weather_panel(seed=8)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    masked = apply_weather_scenario(panel, WeatherScenario.VARIABLE_ABSENT, value_cols)
    work = masked.amputed[["CLUSTER", *value_cols]].copy()

    pymice_cfg = ImputeConfig(pm="t", io=25, seed=11, lat=40.0, kg="Cfa")
    mean_cfg = ImputeConfig(pm="f")

    pymice_out = enforce_temperature_order(impute_by_cluster(work, "midastouch", pymice_cfg))
    mean_out = enforce_temperature_order(impute_by_cluster(work, "midastouch", mean_cfg))

    pymice_score = score_imputation(panel, pymice_out, masked.missing_mask, value_cols)
    mean_score = score_imputation(panel, mean_out, masked.missing_mask, value_cols)
    assert pymice_score.rmse <= mean_score.rmse


def test_validation_suite_runs(impute_config):
    results = run_weather_validation_suite(impute_config, seed=9)
    assert len(results) == len(WeatherScenario)
    assert all(r.n_filled == r.n_missing for r in results)
    assert all(r.temp_order_ok for r in results)
