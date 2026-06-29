"""Two-level PAN imputation for a single outcome (2l.pan)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.mvn_joint import ml_pan_impute
from pymice.methods.registry import register_method


def _group_means(
    y: NDArray[np.float64],
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
        means = {c: np.nanmean(y[ry & (cluster_col == c)]) for c in classes}
        for c in classes:
            out[cluster_col == c, col] = means[c]
    return out


def impute_2l_pan(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    intercept: bool = True,
    paniter: int = 100,
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
        x_arr = _group_means(y_arr, ry, x_arr, type_vec)
        type_vec = type_vec.copy()
        type_vec[type_vec == 3] = 1
        type_vec[type_vec == 4] = 2

    cluster_mask = type_vec == -2
    if not np.any(cluster_mask):
        raise ValueError("2l.pan requires a cluster indicator (type=-2)")

    clusters_raw = x_arr[:, cluster_mask].astype(np.int64).ravel()
    _, clusters = np.unique(clusters_raw, return_inverse=True)

    pred_mask = type_vec != -2
    pred = x_arr[:, pred_mask]
    y_mat = y_arr.copy()
    y_mat[~ry] = np.nan
    y_mat = y_mat.reshape(-1, 1)
    x_fixed = pred

    imputed = ml_pan_impute(
        y_mat,
        clusters,
        x=x_fixed,
        n_burn=max(int(paniter) // 2, 10),
        n_iter=max(int(paniter) // 10, 5),
        rng=rng,
        random_l1="none",
    )
    miss_wy = wy & (~ry)
    return imputed[np.where(miss_wy)[0], 0]


register_method("2l.pan", impute_2l_pan)
