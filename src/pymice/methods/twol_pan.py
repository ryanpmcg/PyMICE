"""Two-level PAN imputation for a single outcome (2l.pan)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.pan_core import pan_univariate_impute
from pymice.methods.registry import register_method


def _group_means(
    ry: NDArray[np.bool_],
    x: NDArray[np.float64],
    type_vec: NDArray[np.int_],
) -> NDArray[np.float64]:
    """Add cluster means for type 3/4 predictors (R ``.mice.impute.2l.groupmean``)."""
    cluster_col = x[:, type_vec == -2].ravel()
    aggr_cols = np.where(np.isin(type_vec, (3, 4)))[0]
    if aggr_cols.size == 0:
        return x
    out = x.copy()
    classes = np.unique(cluster_col[ry])
    for col in aggr_cols:
        for c in classes:
            mask = cluster_col == c
            out[mask, col] = np.nanmean(x[ry & mask, col])
    return out


def impute_2l_pan(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    intercept: bool = True,
    paniter: int = 500,
    use_r_pan: bool | None = None,
    pan_seed: int | None = None,
    mice_seed: int | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via homoscedastic two-level PAN (R ``mice.impute.2l.pan``)."""
    if type is None:
        raise ValueError("2l.pan requires predictor type codes (include -2 for cluster)")
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)

    if intercept:
        x_arr = add_intercept(x_arr)
        type_vec = np.concatenate([np.array([2], dtype=np.int_), type_vec])

    if np.any(np.isin(type_vec, (3, 4))):
        x_arr = _group_means(ry, x_arr, type_vec)
        type_vec = type_vec.copy()
        type_vec[type_vec == 3] = 1
        type_vec[type_vec == 4] = 2

    cluster_mask = type_vec == -2
    if not np.any(cluster_mask):
        raise ValueError("2l.pan requires a cluster indicator (type=-2)")

    pred_mask = type_vec != -2
    pred = x_arr[:, pred_mask]
    type_pred = type_vec[pred_mask]
    zcol = np.where(type_pred == 2)[0].astype(np.int_)

    sort_idx = np.arange(x_arr.shape[0], dtype=np.int_)
    clusters_raw = x_arr[:, cluster_mask].astype(np.int64).ravel()
    if np.any(np.diff(clusters_raw) < 0):
        sort_idx = np.argsort(clusters_raw, kind="stable")
        y_arr = y_arr[sort_idx]
        ry = ry[sort_idx]
        wy = wy[sort_idx]
        pred = pred[sort_idx]
        clusters_raw = clusters_raw[sort_idx]

    _, subj = np.unique(clusters_raw, return_inverse=True)
    subj = subj.astype(np.int_)

    y_work = y_arr.copy()
    y_work[~ry] = np.nan

    for _ in range(10):
        imputed = pan_univariate_impute(
            y_work,
            subj,
            pred,
            zcol,
            n_iter=paniter,
            rng=rng,
            use_r_pan=use_r_pan,
            pan_seed=pan_seed,
            mice_seed=mice_seed,
        )
        if np.all(np.isfinite(imputed[wy])):
            break

    if np.any(sort_idx != np.arange(sort_idx.size)):
        unsort = np.empty_like(sort_idx)
        unsort[sort_idx] = np.arange(sort_idx.size)
        return imputed[unsort][wy]
    return imputed[wy]


register_method("2l.pan", impute_2l_pan)
