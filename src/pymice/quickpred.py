"""Quick predictor-matrix selection (R ``quickpred``)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _as_threshold_matrix(
    value: float | NDArray[np.floating],
    n: int,
    *,
    square: bool,
) -> NDArray[np.float64]:
    if np.isscalar(value):
        base = np.full(n, float(value), dtype=np.float64)
        if square:
            return np.tile(base, (n, 1))
        return base
    arr = np.asarray(value, dtype=np.float64)
    if square:
        if arr.shape != (n, n):
            raise ValueError(f"threshold matrix must have shape ({n}, {n})")
        return arr
    if arr.shape != (n,):
        raise ValueError(f"threshold vector must have length {n}")
    return arr


def _pairwise_usable_fraction(observed: NDArray[np.bool_]) -> NDArray[np.float64]:
    """Proportion of usable cases per column as predictor (R ``md.pairs`` / ``minpuc``)."""
    n_obs, n_var = observed.shape
    puc = np.zeros(n_var, dtype=np.float64)
    for j in range(n_var):
        both = observed[:, j]
        if n_obs:
            puc[j] = float(np.mean(both))
    return puc


def quickpred(
    data: NDArray[np.floating],
    *,
    mincor: float | NDArray[np.floating] = 0.1,
    minpuc: float | NDArray[np.floating] = 0.0,
    include: str | list[str] = "",
    exclude: str | list[str] = "",
    method: str = "pearson",
    column_names: list[str] | None = None,
) -> NDArray[np.int_]:
    """Build a binary predictor matrix from pairwise correlations (R ``quickpred``)."""
    matrix = np.asarray(data, dtype=np.float64)
    if matrix.ndim != 2:
        raise ValueError("data must be a 2-D array")
    _n_obs, n_var = matrix.shape
    names = column_names or [f"V{i + 1}" for i in range(n_var)]

    if method not in ("pearson", "kendall", "spearman"):
        raise ValueError("method must be 'pearson', 'kendall', or 'spearman'")

    observed = np.isfinite(matrix)
    r_ind = observed.astype(np.float64)

    v = np.zeros((n_var, n_var), dtype=np.float64)
    for i in range(n_var):
        for j in range(n_var):
            mask = observed[:, i] & observed[:, j]
            if int(np.sum(mask)) < 2:
                continue
            c = np.corrcoef(matrix[mask, i], matrix[mask, j])[0, 1]
            v[i, j] = abs(c) if np.isfinite(c) else 0.0

    u = np.zeros((n_var, n_var), dtype=np.float64)
    for j in range(n_var):
        for k in range(n_var):
            mask = observed[:, j] & observed[:, k]
            if int(np.sum(mask)) < 2:
                continue
            if method == "pearson":
                c = np.corrcoef(matrix[mask, j], r_ind[mask, k])[0, 1]
            else:
                from scipy import stats

                if method == "spearman":
                    c = stats.spearmanr(matrix[mask, j], r_ind[mask, k]).correlation
                else:
                    c = stats.kendalltau(matrix[mask, j], r_ind[mask, k]).correlation
            u[j, k] = abs(c) if c is not None and np.isfinite(c) else 0.0

    maxc = np.maximum(v, u)
    mincor_mat = _as_threshold_matrix(mincor, n_var, square=True)
    pred = (maxc > mincor_mat).astype(np.int_)

    minpuc_vec = _as_threshold_matrix(minpuc, n_var, square=False)
    if np.any(minpuc_vec != 0):
        puc = _pairwise_usable_fraction(observed)
        pred[:, puc < minpuc_vec] = 0

    def _name_indices(spec: str | list[str]) -> list[int]:
        if not spec:
            return []
        items = [spec] if isinstance(spec, str) else list(spec)
        return [names.index(item) for item in items]

    for j in _name_indices(exclude):
        pred[:, j] = 0
    for j in _name_indices(include):
        pred[:, j] = 1

    np.fill_diagonal(pred, 0)
    complete_cols = np.where(np.all(observed, axis=0))[0]
    pred[complete_cols, :] = 0
    return pred.astype(np.int_)
