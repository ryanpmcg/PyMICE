"""Drop-in replacements for WEPPCLIFF ``impute_by_cluster`` / ``impute_by_df``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pymice import complete, mice
from pymice.imputation_setup import make_blocks
from pymice.integrations.weppcliff.setup import build_mice_plan
from pymice.quickpred import quickpred
from pymice.types import VariableKind, VariableSpec


@dataclass
class ImputeConfig:
    """WEPPCLIFF imputation flags (subset of ``WeppcliffConfig``)."""

    im: str = "DEFAULT"
    io: int = 100
    qi: str = "f"
    iv: str = "f"
    pm: str = "t"
    ns: str = "f"
    kg: str = "AUTO"
    jm: str = "f"
    lat: float = 45.0
    lon: float = 0.0
    seed: int = 42
    granularity: str = "seasonal"
    verb: str = "f"
    st: str = "t"


def _numeric_value_cols(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]


def _mean_fill(
    df: pd.DataFrame, value_cols: list[str], cluster: pd.Series | None = None
) -> pd.DataFrame:
    out = df.copy()
    value_cols = _numeric_value_cols(out, value_cols)
    if cluster is not None:
        for cid in cluster.dropna().unique():
            locs = out.index[cluster == cid]
            subset = out.loc[locs, value_cols]
            for col in value_cols:
                mean = subset[col].mean()
                if pd.isna(mean):
                    mean = out[col].mean()
                if pd.isna(mean):
                    mean = 0
                out.loc[locs, col] = subset[col].fillna(mean)
    for col in value_cols:
        mean = out[col].mean()
        if pd.isna(mean):
            mean = 0
        out[col] = out[col].fillna(mean)
    return out


def _matrix_to_frame(
    matrix: NDArray[np.float64],
    column_names: list[str],
    specs: list[VariableSpec],
    template: pd.DataFrame,
) -> pd.DataFrame:
    out = template.copy()
    for j, name in enumerate(column_names):
        col = matrix[:, j]
        spec = specs[j]
        if spec.kind in (VariableKind.BINARY, VariableKind.UNORDERED) and spec.levels:
            rounded = np.round(col).astype(int)
            out[name] = rounded
        else:
            out[name] = col
    return out


def _run_mice_on_frame(
    df: pd.DataFrame,
    *,
    imp_method: str,
    config: ImputeConfig,
    partition: str = "scatter",
) -> pd.DataFrame:
    if df.empty or not df.columns.any():
        return df
    if not df.isna().any().any():
        return df

    plan = build_mice_plan(
        df,
        imp_method=imp_method,
        io_cap=config.io,
        quick_impute=str(config.qi).upper() == "T",
        im_override=config.im,
        partition=partition,
        seed=config.seed,
    )
    mids = mice(
        **plan,
        print_flag=str(config.iv).upper() == "T",
    )
    completed = complete(mids, 1)
    if not isinstance(completed, np.ndarray):
        raise TypeError("expected numpy array from complete()")
    return _matrix_to_frame(
        completed,
        plan["column_names"],
        plan["variable_specs"],
        df,
    )


def _cluster_complete_counts(fil_df: pd.DataFrame, value_cols: list[str]) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for cid in fil_df["CLUSTER"].dropna().unique():
        sub = fil_df.loc[fil_df["CLUSTER"] == cid, value_cols]
        numeric = sub.copy()
        for col in value_cols:
            if str(numeric[col].dtype) == "category":
                numeric[col] = numeric[col].astype(str)
        complete = numeric.notna().all(axis=1).sum()
        counts[cid] = int(complete)
    return counts


def _needs_unified_2l(fil_df: pd.DataFrame, value_cols: list[str], n_vars: int) -> bool:
    n_min = max(30, 5 * n_vars)
    counts = _cluster_complete_counts(fil_df, value_cols)
    if not counts:
        return True
    return min(counts.values()) < n_min


def _jomo_multivariate_method(imp_method: str, *, im_override: str, quick_impute: bool) -> str:
    """Map WEPPCLIFF method override to ``jomoImpute`` or ``panImpute``."""
    from pymice.integrations.weppcliff.setup import resolve_imp_method

    method_str, _ = resolve_imp_method(
        imp_method,
        im_override=im_override,
        quick_impute=quick_impute,
    )
    if method_str in ("2l.pan", "panimpute", "pan"):
        return "panImpute"
    return "jomoImpute"


def _run_jomo_block(
    fil_df: pd.DataFrame,
    value_cols: list[str],
    *,
    imp_method: str,
    config: ImputeConfig,
) -> pd.DataFrame:
    """Multivariate JOMO/PAN block with CLUSTER as level-2 indicator."""
    from pymice.integrations.weppcliff.constraints import non_negative_posts, temperature_posts
    from pymice.integrations.weppcliff.setup import (
        adaptive_maxit,
        dataframe_to_matrix,
        resolve_imp_method,
    )
    from pymice.methods.jomo_formula import type_row_from_roles

    work = fil_df.copy()
    clusters = pd.to_numeric(work["CLUSTER"], errors="coerce")
    codes, _ = pd.factorize(clusters)
    work["_CLUSTER_CODE_"] = codes.astype(float)

    extra_fixed: list[str] = []
    if "_YEAR_BLOCK_" in work.columns:
        extra_fixed.append("_YEAR_BLOCK_")

    names = ["_CLUSTER_CODE_", *value_cols, *extra_fixed]
    sub = work[names].copy()

    matrix, specs = dataframe_to_matrix(sub, names)
    where = np.isnan(matrix)
    where[:, 0] = False
    for col in extra_fixed:
        where[:, names.index(col)] = False

    n_complete = int(np.sum(np.all(~np.isnan(matrix), axis=1)))
    maxit = adaptive_maxit(n_complete, matrix.shape[0], config.io)
    _, maxit_cap = resolve_imp_method(
        imp_method,
        im_override=config.im,
        quick_impute=str(config.qi).upper() == "T",
    )
    if maxit_cap is not None:
        maxit = min(maxit, maxit_cap)

    mv_method = _jomo_multivariate_method(
        imp_method,
        im_override=config.im,
        quick_impute=str(config.qi).upper() == "T",
    )
    blocks = make_blocks(value_cols, partition="collect")
    block_name = next(iter(blocks))
    type_row = type_row_from_roles(
        names,
        targets=value_cols,
        fixed=extra_fixed or None,
        cluster="_CLUSTER_CODE_",
    )
    block_pred = {block_name: type_row}
    methods = {block_name: mv_method}
    post = {**temperature_posts(names), **non_negative_posts(names)}

    mids = mice(
        matrix,
        column_names=names,
        variable_specs=specs,
        m=1,
        maxit=maxit,
        method=methods,
        blocks=blocks,
        block_predictor_matrix=block_pred,
        where=where,
        post=post,
        seed=config.seed,
        print_flag=str(config.iv).upper() == "T",
        n_burn=min(50, max(20, maxit)),
        n_iter=min(10, max(2, maxit // 5)),
    )
    completed = complete(mids, 1)
    if not isinstance(completed, np.ndarray):
        raise TypeError("expected numpy array from complete()")
    filled = _matrix_to_frame(completed, names, specs, sub)
    out = fil_df.copy()
    out[value_cols] = filled[value_cols]
    return out


def _run_2l_norm(
    fil_df: pd.DataFrame,
    value_cols: list[str],
    *,
    imp_method: str,
    config: ImputeConfig,
) -> pd.DataFrame:
    """Unified multilevel imputation with CLUSTER as level-2 indicator."""
    work = fil_df[["CLUSTER", *value_cols]].copy()
    clusters = pd.to_numeric(work["CLUSTER"], errors="coerce")
    codes, _ = pd.factorize(clusters)
    work["_CLUSTER_CODE_"] = codes.astype(float)
    impute_cols = ["_CLUSTER_CODE_", *value_cols]
    sub = work[impute_cols].copy()

    names = list(sub.columns)
    n_complete = int(sub.notna().all(axis=1).sum())
    maxit = min(config.io, max(20, int(np.ceil(100 - 100 * n_complete / max(len(sub), 1)))))

    from pymice.integrations.weppcliff.setup import dataframe_to_matrix, resolve_imp_method

    matrix, specs = dataframe_to_matrix(sub, names)
    np.isnan(matrix)
    method_str, maxit_cap = resolve_imp_method(
        imp_method,
        im_override=config.im,
        quick_impute=str(config.qi).upper() == "T",
    )
    if maxit_cap is not None:
        maxit = min(maxit, maxit_cap)

    pred = quickpred(matrix, mincor=0.2, minpuc=0.05, column_names=names)
    blocks = make_blocks(names, partition="scatter")
    methods = {name: "2l.norm" if name in value_cols else "" for name in names}
    methods["_CLUSTER_CODE_"] = ""
    for name in value_cols:
        methods[name] = "2l.norm" if method_str in ("2l.norm", "2l.pan") else method_str

    type_row = np.array([0, -2] + [2] * (len(names) - 2), dtype=np.int_)
    block_pred = {name: type_row.copy() for name in names if name in value_cols}

    mids = mice(
        matrix,
        column_names=names,
        variable_specs=specs,
        m=1,
        maxit=maxit,
        method=methods,
        predictor_matrix=pred,
        blocks=blocks,
        block_predictor_matrix=block_pred,
        seed=config.seed,
        print_flag=str(config.iv).upper() == "T",
    )
    completed = complete(mids, 1)
    if not isinstance(completed, np.ndarray):
        raise TypeError("expected numpy array from complete()")
    filled = _matrix_to_frame(completed, names, specs, sub)
    out = fil_df.copy()
    out[value_cols] = filled[value_cols]
    return out


def _config_from_any(config: ImputeConfig | Any | None) -> ImputeConfig:
    if config is None:
        return ImputeConfig()
    if isinstance(config, ImputeConfig):
        return config
    return ImputeConfig(
        im=getattr(config, "im", "DEFAULT"),
        io=int(getattr(config, "io", 100)),
        qi=str(getattr(config, "qi", "f")),
        iv=str(getattr(config, "iv", "f")),
        pm=str(getattr(config, "pm", "t")),
        ns=str(getattr(config, "ns", "f")),
        kg=str(getattr(config, "kg", "AUTO")),
        lat=float(getattr(config, "lat", 45.0)),
        lon=float(getattr(config, "lon", 0.0)),
        verb=str(getattr(config, "verb", "f")),
        granularity=str(getattr(config, "impute_granularity", "seasonal")),
        st=str(getattr(config, "st", "t")),
        jm=str(getattr(config, "jm", "f")),
        seed=int(getattr(config, "seed", 42)),
    )


def impute_by_cluster(
    fil_df: pd.DataFrame,
    imp_method: str,
    config: ImputeConfig | Any | None = None,
    *,
    fallback_mean: bool = True,
    date_index: pd.Index | None = None,
    dates_yyyymmdd: list[str] | None = None,
) -> pd.DataFrame:
    """
    Impute missing values within each CLUSTER group using PyMICE FCS.

    Falls back to cluster means when ``config.pm`` is ``f`` or on failure.
    """
    config = _config_from_any(config)

    if "CLUSTER" not in fil_df.columns:
        raise ValueError("fil_df must contain a CLUSTER column")

    value_cols = _numeric_value_cols(
        fil_df,
        [c for c in fil_df.columns if c not in ("CLUSTER", "_YEAR_BLOCK_")],
    )
    if not value_cols:
        return fil_df

    if str(config.pm).upper() != "T":
        return _mean_fill(fil_df, value_cols, fil_df["CLUSTER"])

    try:
        from pymice.integrations.weppcliff.diagnostics import format_report
        from pymice.integrations.weppcliff.resilience import resilient_impute_by_cluster

        out, report = resilient_impute_by_cluster(
            fil_df,
            imp_method,
            config,
            granularity=config.granularity,
            date_index=date_index,
            dates_yyyymmdd=dates_yyyymmdd,
        )
        if str(config.verb).upper() == "T" or str(config.iv).upper() == "T":
            print(format_report(report))
        return out
    except Exception:
        if fallback_mean:
            return _mean_fill(fil_df, value_cols, fil_df["CLUSTER"])
        raise


def impute_by_df(
    fil_df: pd.DataFrame,
    imp_method: str,
    config: ImputeConfig | Any | None = None,
    *,
    fallback_mean: bool = True,
) -> pd.DataFrame:
    """Impute across the full dataframe (no cluster split)."""
    config = _config_from_any(config)

    value_cols = [c for c in fil_df.columns if c != "_YEAR_BLOCK_"]
    if str(config.pm).upper() != "T":
        return _mean_fill(fil_df, value_cols)

    try:
        if fil_df.isna().any().any():
            return _run_mice_on_frame(
                fil_df,
                imp_method=imp_method,
                config=config,
                partition="collect",
            )
        return fil_df
    except Exception:
        if fallback_mean:
            return _mean_fill(fil_df, value_cols)
        raise
