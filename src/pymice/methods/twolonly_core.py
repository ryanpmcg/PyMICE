"""Shared level-2 aggregation for ``2lonly.norm`` / ``2lonly.pmm``."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.norm import impute_norm
from pymice.methods.pmm import impute_pmm


def _aggregate_level2(
    cluster: NDArray[np.int64],
    x_aug: NDArray[np.float64],
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
) -> tuple[NDArray[np.int64], NDArray[np.float64], NDArray[np.float64]]:
    """Cluster-level means of predictors and outcome (R ``rowsum`` aggregation)."""
    clusters = np.unique(cluster)
    n_pred = x_aug.shape[1]
    x_agg = np.zeros((clusters.size, n_pred), dtype=np.float64)
    y_agg = np.zeros(clusters.size, dtype=np.float64)
    for i, g in enumerate(clusters):
        mask = cluster == g
        x_block = x_aug[mask]
        x_den = np.sum(~np.isnan(x_block), axis=0)
        x_num = np.nansum(x_block, axis=0)
        x_agg[i] = np.divide(x_num, np.maximum(x_den, 1))
        y_den = np.sum(ry[mask])
        y_agg[i] = np.sum(y[mask] * ry[mask]) / max(y_den, 1)
    return clusters, x_agg, y_agg


def imputation_level2(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    *,
    type: NDArray[np.int_] | None,
    method: str,
    **kwargs: object,
) -> NDArray[np.floating]:
    """
    Impute level-2 constants via cluster aggregation (R ``.imputation.level2``).

    Parameters
    ----------
    method
        ``"norm"`` or ``"pmm"``.
    """
    if type is None:
        raise ValueError("2lonly methods require predictor type codes (include -2 for cluster)")
    if int(np.sum(type == -2)) != 1:
        raise ValueError("No class variable")

    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)
    cluster_col = x_arr[:, type_vec == -2].astype(np.int64).ravel()

    cm = np.unique(cluster_col[~ry])
    co = np.unique(cluster_col[ry])
    cobs = np.setdiff1d(co, cm, assume_unique=True)
    csom = np.intersect1d(co, cm, assume_unique=True)
    if csom.size > 0:
        listed = ", ".join(str(int(c)) for c in csom)
        raise ValueError(
            f"Method 2lonly.{method} found the following clusters with partially missing\n"
            f"  level-2 data: {listed}\n"
            "  Method 2lonly.mean can fix such inconsistencies."
        )

    pred_mask = np.isin(type_vec, (1, 2))
    x_aug = np.column_stack([np.ones(x_arr.shape[0]), x_arr[:, pred_mask]])
    cluster_ids, x2, y2 = _aggregate_level2(cluster_col, x_aug, y_arr, ry)

    ry2 = np.isin(cluster_ids, cobs)
    clusters_wy = np.unique(cluster_col[wy])
    wy2 = np.isin(cluster_ids, clusters_wy)

    if method == "norm":
        imp2 = impute_norm(y=y2, ry=ry2, x=x2, wy=wy2, rng=rng, **kwargs)
    elif method == "pmm":
        imp2 = impute_pmm(y=y2, ry=ry2, x=x2, wy=wy2, rng=rng, **kwargs)
    else:
        raise ValueError(f"unknown level-2 method: {method!r}")

    lookup = {int(cid): float(val) for cid, val in zip(cluster_ids[wy2], imp2, strict=True)}
    return np.array([lookup[int(c)] for c in cluster_col[wy]], dtype=np.float64)
