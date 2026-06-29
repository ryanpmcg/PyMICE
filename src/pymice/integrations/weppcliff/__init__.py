"""WEPPCLIFF gap-fill adapter for climate and weather models."""

from pymice.integrations.weppcliff.adapter import ImputeConfig, impute_by_cluster, impute_by_df
from pymice.integrations.weppcliff.cluster import (
    assign_cluster_labels,
    build_cluster_candidates,
    season_from_month,
    select_cluster_granularity,
)
from pymice.integrations.weppcliff.diagnostics import ImputationReport, format_report
from pymice.integrations.weppcliff.missingness import MissingnessProfile, classify_missingness
from pymice.integrations.weppcliff.priors import KoppenPriorStore, load_default_priors
from pymice.integrations.weppcliff.resilience import resilient_impute_by_cluster
from pymice.integrations.weppcliff.subdaily import impute_subdaily_timeseries
from pymice.integrations.weppcliff.validation import (
    ImputationQuality,
    ScenarioResult,
    WeatherScenario,
    apply_weather_scenario,
    format_validation_report,
    run_weather_validation_suite,
    score_imputation,
    synthetic_weather_panel,
    validate_scenario,
)

__all__ = [
    "ImputationQuality",
    "ImputationReport",
    "ImputeConfig",
    "KoppenPriorStore",
    "MissingnessProfile",
    "ScenarioResult",
    "WeatherScenario",
    "apply_weather_scenario",
    "assign_cluster_labels",
    "build_cluster_candidates",
    "classify_missingness",
    "format_report",
    "format_validation_report",
    "impute_by_cluster",
    "impute_by_df",
    "impute_subdaily_timeseries",
    "load_default_priors",
    "resilient_impute_by_cluster",
    "run_weather_validation_suite",
    "score_imputation",
    "season_from_month",
    "select_cluster_granularity",
    "synthetic_weather_panel",
    "validate_scenario",
]
