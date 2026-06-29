"""Adaptive imputation with fallback chain (6b)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pymice.integrations.weppcliff.adapter import (
    ImputeConfig,
    _mean_fill,
    _needs_unified_2l,
    _numeric_value_cols,
    _run_2l_norm,
    _run_jomo_block,
    _run_mice_on_frame,
)
from pymice.integrations.weppcliff.diagnostics import ImputationReport
from pymice.integrations.weppcliff.missingness import classify_missingness
from pymice.integrations.weppcliff.nonstationary import adjacent_cluster_ids, attach_year_block
from pymice.integrations.weppcliff.priors.blend import impute_from_prior, prior_weight
from pymice.integrations.weppcliff.priors.store import KoppenPriorStore, load_default_priors


def _count_imputed(before: pd.DataFrame, after: pd.DataFrame, cols: list[str]) -> int:
    n = 0
    for col in cols:
        if col not in before.columns or col not in after.columns:
            continue
        was = before[col].isna()
        now = after[col].notna()
        n += int((was & now).sum())
    return n


def _pool_adjacent_cluster(
    out: pd.DataFrame,
    cluster_id: int,
    value_cols: list[str],
    *,
    imp_method: str,
    config: ImputeConfig,
    granularity: str = "month",
) -> pd.DataFrame:
    """Impute sparse cluster rows using donor rows from adjacent clusters."""
    neighbors = adjacent_cluster_ids(cluster_id, granularity)
    locs = out.index[out["CLUSTER"] == cluster_id]
    if len(locs) == 0:
        return out

    donor_mask = out["CLUSTER"].isin(neighbors)
    donor = out.loc[donor_mask, value_cols]
    if donor.notna().all(axis=1).sum() < 5:
        return out

    tmp = out.loc[locs, value_cols].copy()
    if not tmp.isna().any().any():
        return out

    pooled = pd.concat([donor, tmp], ignore_index=True)
    filled = _run_mice_on_frame(pooled, imp_method=imp_method, config=config)
    out.loc[locs, value_cols] = filled.iloc[-len(tmp) :][value_cols].to_numpy()
    return out


def resilient_impute_by_cluster(
    fil_df: pd.DataFrame,
    imp_method: str,
    config: ImputeConfig,
    *,
    prior_store: KoppenPriorStore | None = None,
    granularity: str = "seasonal",
    date_index: pd.Index | None = None,
    dates_yyyymmdd: list[str] | None = None,
    report: ImputationReport | None = None,
) -> tuple[pd.DataFrame, ImputationReport]:
    """
    Impute with fallback chain:

    local FCS → adjacent-cluster pool → 2l.norm → Köppen prior → mean fill.
    """
    rep = report or ImputationReport(
        granularity=granularity,
        koppen_zone=config.kg,
        nonstationary=str(config.ns).upper() == "T",
    )
    value_cols = _numeric_value_cols(fil_df, [c for c in fil_df.columns if c != "CLUSTER"])
    n_min = max(30, 5 * len(value_cols))
    profile = classify_missingness(fil_df, value_cols, n_min=n_min)
    rep.missingness = profile

    store = prior_store or load_default_priors()
    zone = store.resolve_zone(config.kg, config.lat, config.lon)
    rep.koppen_zone = zone

    before = fil_df.copy()
    out = fil_df.copy()

    work = out
    if str(config.ns).upper() == "T" and date_index is not None:
        work = attach_year_block(out, date_index, dates_yyyymmdd)

    mice_cols = list(value_cols)
    if "_YEAR_BLOCK_" in work.columns:
        mice_cols = [*value_cols, "_YEAR_BLOCK_"]

    use_jomo = str(config.jm).upper() == "T"

    if _needs_unified_2l(work, value_cols, len(value_cols)):
        if use_jomo:
            rep.strategies.append("jomo_unified")
            try:
                result = _run_jomo_block(work, value_cols, imp_method=imp_method, config=config)
                rep.n_imputed_cells += _count_imputed(before, result, value_cols)
                return result, rep
            except Exception:
                rep.strategies.append("jomo_failed")
        rep.strategies.append("2l.norm_unified")
        try:
            result = _run_2l_norm(work, value_cols, imp_method=imp_method, config=config)
            rep.n_imputed_cells += _count_imputed(before, result, value_cols)
            return result, rep
        except Exception:
            rep.strategies.append("2l.norm_failed")

    for cluster in work["CLUSTER"].dropna().unique():
        locs = work.index[work["CLUSTER"] == cluster]
        tmp = work.loc[locs, mice_cols].copy()
        if not tmp[value_cols].isna().any().any():
            continue

        n_complete = int(tmp[value_cols].notna().all(axis=1).sum())
        cid = int(cluster)

        if n_complete < n_min and profile.recommend_adjacent_pooling():
            rep.strategies.append(f"adjacent_pool_c{cid}")
            work = _pool_adjacent_cluster(
                work,
                cid,
                mice_cols,
                imp_method=imp_method,
                config=config,
                granularity=granularity,
            )
            tmp = work.loc[locs, mice_cols].copy()

        try:
            if use_jomo:
                filled = _run_jomo_block(
                    work.loc[locs].copy(),
                    value_cols,
                    imp_method=imp_method,
                    config=config,
                )
                rep.strategies.append(f"jomo_c{cid}")
            else:
                filled = _run_mice_on_frame(tmp, imp_method=imp_method, config=config)
                rep.strategies.append(f"fcs_c{cid}")
            work.loc[locs, value_cols] = filled[value_cols].to_numpy()
        except Exception:
            rep.strategies.append(f"jomo_failed_c{cid}" if use_jomo else f"fcs_failed_c{cid}")

    if profile.recommend_prior() or work[value_cols].isna().any().any():
        w = 1.0 - prior_weight(
            int(work[value_cols].notna().all(axis=1).sum()),
            n_min,
        )
        rep.prior_weight = max(rep.prior_weight, w)
        rep.strategies.append("koppen_prior")
        rng = np.random.default_rng(config.seed)
        work = impute_from_prior(
            work,
            value_cols,
            store=store,
            zone=zone,
            lat=config.lat,
            lon=config.lon,
            granularity=granularity,
            weight=w,
            rng=rng,
        )

    if work[value_cols].isna().any().any():
        rep.strategies.append("mean_fallback")
        work = _mean_fill(work, value_cols, work["CLUSTER"])

    rep.n_imputed_cells += _count_imputed(before, work, value_cols)
    return work, rep
