"""Synthetic weather panels and ampute-based imputation validation (Phase 6d)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd

from pymice.ampute import ampute
from pymice.integrations.weppcliff.adapter import ImputeConfig, impute_by_cluster
from pymice.integrations.weppcliff.cluster import assign_cluster_labels
from pymice.integrations.weppcliff.missingness import MissingnessKind, classify_missingness

DEFAULT_VALUE_COLS: tuple[str, ...] = ("MIN_TEMP", "MAX_TEMP", "WIND", "SOLAR")


class WeatherScenario(str, Enum):
    SHORT_GAPS = "short_gaps"
    LONG_GAP_ALL = "long_gap_all"
    PERSISTENT_SEASONAL = "persistent_seasonal"
    VARIABLE_ABSENT = "variable_absent"
    MIXED = "mixed"
    MCAR_AMPUTE = "mcar_ampute"


@dataclass
class ScenarioResult:
    """Amputed panel plus mask of introduced missingness."""

    amputed: pd.DataFrame
    missing_mask: pd.DataFrame
    expected_kind: MissingnessKind
    scenario: WeatherScenario


@dataclass
class ImputationQuality:
    """Hold-out metrics on artificially masked cells."""

    scenario: str
    n_missing: int
    n_filled: int
    rmse: float
    mae: float
    temp_order_ok: bool
    detected_kind: MissingnessKind = MissingnessKind.NONE
    detected_kinds: set[MissingnessKind] = field(default_factory=set)


def synthetic_weather_panel(
    *,
    n_years: int = 3,
    lat: float = 40.0,
    seed: int = 0,
    value_cols: tuple[str, ...] = DEFAULT_VALUE_COLS,
) -> pd.DataFrame:
    """Build a complete multivariate daily weather panel with CLUSTER labels."""
    rng = np.random.default_rng(seed)
    n_days = 365 * n_years
    dates = pd.date_range("2018-01-01", periods=n_days, freq="D")
    ymd = dates.strftime("%Y%m%d").tolist()
    day_of_year = dates.dayofyear.to_numpy(dtype=float)

    seasonal = np.sin(2 * np.pi * day_of_year / 365.25)
    min_temp = 8.0 + 12.0 * seasonal + rng.normal(0, 2.5, n_days)
    max_temp = min_temp + 6.0 + rng.normal(0, 1.5, n_days)
    wind = np.clip(4.0 + 2.0 * np.abs(seasonal) + rng.normal(0, 1.0, n_days), 0.5, None)
    solar = np.clip(12.0 + 8.0 * seasonal + rng.normal(0, 1.5, n_days), 0.0, None)

    values = {
        "MIN_TEMP": min_temp,
        "MAX_TEMP": max_temp,
        "WIND": wind,
        "SOLAR": solar,
    }
    matrix = np.column_stack([values[c] for c in value_cols])
    clusters = assign_cluster_labels(ymd, matrix, lat=lat, n_vars=len(value_cols))

    frame = pd.DataFrame({"YYYYMMDD": ymd, "CLUSTER": clusters})
    for col in value_cols:
        frame[col] = values[col]
    return frame


def _mask_frame(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    return pd.DataFrame(False, index=df.index, columns=value_cols)


def apply_short_gaps(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    gap_len: int = 4,
    n_gaps: int = 10,
    seed: int = 0,
) -> ScenarioResult:
    """Scatter short contiguous row gaps across the panel."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    mask = _mask_frame(df, value_cols)
    n = len(df)
    starts = rng.integers(0, max(n - gap_len, 1), size=n_gaps)
    for start in np.unique(starts):
        stop = min(int(start) + gap_len, n)
        out.loc[start : stop - 1, value_cols] = np.nan
        mask.loc[start : stop - 1, value_cols] = True
    return ScenarioResult(
        amputed=out,
        missing_mask=mask,
        expected_kind=MissingnessKind.SHORT_GAPS,
        scenario=WeatherScenario.SHORT_GAPS,
    )


def apply_long_gap_all(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    start: int = 120,
    length: int = 180,
) -> ScenarioResult:
    """Remove all variables for one long contiguous interval."""
    out = df.copy()
    mask = _mask_frame(df, value_cols)
    stop = min(start + length, len(df))
    out.loc[start : stop - 1, value_cols] = np.nan
    mask.loc[start : stop - 1, value_cols] = True
    return ScenarioResult(
        amputed=out,
        missing_mask=mask,
        expected_kind=MissingnessKind.LONG_GAP_ALL,
        scenario=WeatherScenario.LONG_GAP_ALL,
    )


def apply_persistent_seasonal(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    cluster_id: int | None = None,
) -> ScenarioResult:
    """Drop an entire cluster (e.g. all July days when CLUSTER is month)."""
    out = df.copy()
    mask = _mask_frame(df, value_cols)
    if cluster_id is None:
        counts = out.groupby("CLUSTER").size()
        cluster_id = int(counts.idxmax())
    locs = out.index[out["CLUSTER"] == cluster_id]
    out.loc[locs, value_cols] = np.nan
    mask.loc[locs, value_cols] = True
    return ScenarioResult(
        amputed=out,
        missing_mask=mask,
        expected_kind=MissingnessKind.PERSISTENT_SEASONAL,
        scenario=WeatherScenario.PERSISTENT_SEASONAL,
    )


def apply_variable_absent(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    column: str = "MIN_TEMP",
) -> ScenarioResult:
    """Simulate a sensor that never reports one variable."""
    out = df.copy()
    mask = _mask_frame(df, value_cols)
    out[column] = np.nan
    mask[column] = True
    return ScenarioResult(
        amputed=out,
        missing_mask=mask,
        expected_kind=MissingnessKind.VARIABLE_ABSENT,
        scenario=WeatherScenario.VARIABLE_ABSENT,
    )


def apply_mixed(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    seed: int = 0,
) -> ScenarioResult:
    """Combine short gaps, a sparse cluster, and one absent variable."""
    short = apply_short_gaps(df, value_cols, gap_len=3, n_gaps=6, seed=seed)
    seasonal = apply_persistent_seasonal(short.amputed, value_cols)
    absent = apply_variable_absent(seasonal.amputed, value_cols, column="WIND")
    mask = short.missing_mask | seasonal.missing_mask | absent.missing_mask
    return ScenarioResult(
        amputed=absent.amputed,
        missing_mask=mask,
        expected_kind=MissingnessKind.MIXED,
        scenario=WeatherScenario.MIXED,
    )


def apply_ampute_mcar(
    df: pd.DataFrame,
    value_cols: list[str],
    *,
    prop: float = 0.12,
    seed: int = 0,
) -> ScenarioResult:
    """Introduce MCAR missingness via ``pymice.ampute``."""
    matrix = df[value_cols].to_numpy(dtype=np.float64)
    result = ampute(matrix, prop=prop, seed=seed)
    out = df.copy()
    mask = _mask_frame(df, value_cols)
    if result.amp is not None:
        out[value_cols] = result.amp
        mask[value_cols] = np.isnan(result.amp)
    return ScenarioResult(
        amputed=out,
        missing_mask=mask,
        expected_kind=MissingnessKind.SHORT_GAPS,
        scenario=WeatherScenario.MCAR_AMPUTE,
    )


def apply_weather_scenario(
    df: pd.DataFrame,
    scenario: WeatherScenario,
    value_cols: list[str] | None = None,
    *,
    seed: int = 0,
) -> ScenarioResult:
    """Dispatch a named weather missingness scenario."""
    cols = value_cols or [c for c in df.columns if c not in ("YYYYMMDD", "CLUSTER")]
    if scenario == WeatherScenario.SHORT_GAPS:
        return apply_short_gaps(df, cols, seed=seed)
    if scenario == WeatherScenario.LONG_GAP_ALL:
        return apply_long_gap_all(df, cols)
    if scenario == WeatherScenario.PERSISTENT_SEASONAL:
        return apply_persistent_seasonal(df, cols)
    if scenario == WeatherScenario.VARIABLE_ABSENT:
        return apply_variable_absent(df, cols)
    if scenario == WeatherScenario.MIXED:
        return apply_mixed(df, cols, seed=seed)
    if scenario == WeatherScenario.MCAR_AMPUTE:
        return apply_ampute_mcar(df, cols, seed=seed)
    raise ValueError(f"unknown scenario: {scenario}")


def enforce_temperature_order(df: pd.DataFrame) -> pd.DataFrame:
    """Swap MIN/MAX when imputation inverts daily range (WEPPCLIFF fallback)."""
    out = df.copy()
    if "MIN_TEMP" not in out.columns or "MAX_TEMP" not in out.columns:
        return out
    bad = out["MIN_TEMP"] > out["MAX_TEMP"]
    if bad.any():
        lo = out.loc[bad, "MAX_TEMP"].copy()
        hi = out.loc[bad, "MIN_TEMP"].copy()
        out.loc[bad, "MIN_TEMP"] = lo
        out.loc[bad, "MAX_TEMP"] = hi
    return out


def _temp_order_ok(df: pd.DataFrame) -> bool:
    if "MIN_TEMP" not in df.columns or "MAX_TEMP" not in df.columns:
        return True
    sub = df[["MIN_TEMP", "MAX_TEMP"]].dropna()
    if sub.empty:
        return True
    return bool((sub["MIN_TEMP"] <= sub["MAX_TEMP"]).all())


def score_imputation(
    truth: pd.DataFrame,
    imputed: pd.DataFrame,
    missing_mask: pd.DataFrame,
    value_cols: list[str],
    *,
    scenario: str = "",
) -> ImputationQuality:
    """Compute hold-out error on artificially masked cells."""
    errs: list[float] = []
    n_missing = 0
    n_filled = 0
    for col in value_cols:
        miss = missing_mask[col].to_numpy()
        n_missing += int(miss.sum())
        filled = miss & imputed[col].notna().to_numpy()
        n_filled += int(filled.sum())
        if not np.any(filled):
            continue
        delta = imputed.loc[filled, col].to_numpy() - truth.loc[filled, col].to_numpy()
        errs.extend(delta.tolist())

    if errs:
        arr = np.asarray(errs, dtype=np.float64)
        rmse = float(np.sqrt(np.mean(arr**2)))
        mae = float(np.mean(np.abs(arr)))
    else:
        rmse = 0.0
        mae = 0.0

    return ImputationQuality(
        scenario=scenario,
        n_missing=n_missing,
        n_filled=n_filled,
        rmse=rmse,
        mae=mae,
        temp_order_ok=_temp_order_ok(imputed),
    )


def validate_scenario(
    scenario: WeatherScenario,
    config: ImputeConfig | None = None,
    *,
    seed: int = 0,
    lat: float = 40.0,
) -> ImputationQuality:
    """Run one scenario end-to-end: mask → impute → score."""
    cfg = config or ImputeConfig(pm="t", io=25, seed=seed, lat=lat, kg="Cfa")
    panel = synthetic_weather_panel(seed=seed, lat=lat)
    value_cols = [c for c in panel.columns if c not in ("YYYYMMDD", "CLUSTER")]
    masked = apply_weather_scenario(panel, scenario, value_cols, seed=seed)

    work = masked.amputed[["CLUSTER", *value_cols]].copy()
    imputed = enforce_temperature_order(impute_by_cluster(work, "midastouch", cfg))

    quality = score_imputation(
        panel,
        imputed,
        masked.missing_mask,
        value_cols,
        scenario=scenario.value,
    )

    # Classify on the masked (pre-impute) panel for expected-kind checks
    pre_profile = classify_missingness(work, value_cols, n_min=30)
    quality.detected_kind = pre_profile.primary
    quality.detected_kinds = set(pre_profile.kinds)
    return quality


def run_weather_validation_suite(
    config: ImputeConfig | None = None,
    *,
    seed: int = 0,
    lat: float = 40.0,
) -> list[ImputationQuality]:
    """Execute all weather scenarios and return quality metrics."""
    results: list[ImputationQuality] = []
    for scenario in WeatherScenario:
        results.append(validate_scenario(scenario, config, seed=seed, lat=lat))
    return results


def format_validation_report(results: list[ImputationQuality]) -> str:
    """Render a compact text table for CLI / scripts."""
    lines = ["scenario           filled   rmse    mae   temp_ok  detected"]
    for r in results:
        lines.append(
            f"{r.scenario:18s} {r.n_filled:5d}/{r.n_missing:<5d} "
            f"{r.rmse:6.2f} {r.mae:6.2f} "
            f"{'yes' if r.temp_order_ok else 'no':7s} {r.detected_kind.value}"
        )
    return "\n".join(lines)
