"""Least-squares estimation and Bayesian normal-model draws (Rubin 1987)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class EstimiceResult:
    coef: NDArray[np.float64]
    residuals: NDArray[np.float64]
    cov: NDArray[np.float64]
    df: int


def _chol_safe(cov: NDArray[np.float64], ridge: float = 1e-5) -> NDArray[np.float64]:
    """Cholesky with progressive ridge fallback for near-singular covariance."""
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)
    for scale in (0.0, ridge, ridge * 10, ridge * 1000, 1e-2, 1e-1):
        try:
            jitter = np.diag(np.diag(cov) * scale + scale)
            return np.linalg.cholesky(cov + jitter)
        except np.linalg.LinAlgError:
            continue
    return np.diag(np.sqrt(np.maximum(np.diag(cov), ridge)))


def remove_lindep(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
) -> NDArray[np.bool_]:
    """Identify linearly independent predictor columns (R ``remove.lindep``)."""
    x_obs = x[ry]
    if x_obs.shape[0] == 0 or x_obs.shape[1] == 0:
        return np.ones(x.shape[1], dtype=bool)

    keep = np.ones(x.shape[1], dtype=bool)
    cols = list(range(x.shape[1]))
    while cols:
        x_sub = x_obs[:, cols]
        rank = np.linalg.matrix_rank(x_sub, tol=1e-8)
        if rank == len(cols):
            break
        _, r = np.linalg.qr(x_sub, mode="reduced")
        diag = np.abs(np.diag(r))
        drop_local = int(np.argmin(diag))
        drop = cols[drop_local]
        keep[drop] = False
        cols.pop(drop_local)

    return keep


def estimice(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    ridge: float = 1e-5,
) -> EstimiceResult:
    """QR least squares with optional ridge fallback (mirrors R ``estimice``)."""
    n, p = x.shape
    df = max(n - p, 1)
    coef, residuals, _, _ = np.linalg.lstsq(x, y, rcond=None)
    fitted = x @ coef
    if residuals.size == 0:
        residuals = y - fitted
    else:
        residuals = residuals  # lstsq returns sum of squared residuals scalar sometimes

    if np.isscalar(residuals) or residuals.ndim == 0:
        residuals = y - fitted
    else:
        residuals = y - fitted

    _q, r = np.linalg.qr(x, mode="reduced")
    try:
        cov = np.linalg.inv(r.T @ r)
    except np.linalg.LinAlgError:
        xtx = r.T @ r
        pen = np.diag(np.diag(xtx) * ridge)
        cov = np.linalg.inv(xtx + pen)

    return EstimiceResult(coef=coef, residuals=residuals, cov=cov, df=df)


def norm_draw(
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
    x: NDArray[np.float64],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    rank_adjust: bool = True,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Draw regression coefficients and residual scale (R ``.norm.draw``)."""
    est = estimice(x[ry], y[ry], ridge=ridge)
    sigma_star = float(np.sqrt(np.sum(est.residuals**2) / rng.chisquare(est.df)))
    sym_cov = (est.cov + est.cov.T) / 2.0
    chol_v = _chol_safe(sym_cov, ridge=ridge)
    beta_star = est.coef + chol_v @ rng.standard_normal(x.shape[1]) * sigma_star

    if rank_adjust and np.any(np.isnan(est.coef)):
        est.coef = np.nan_to_num(est.coef, nan=0.0)
        beta_star = np.nan_to_num(beta_star, nan=0.0)

    return est.coef, beta_star, sigma_star


def norm_fix(
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
    x: NDArray[np.float64],
    ridge: float = 1e-5,
) -> tuple[NDArray[np.float64], float]:
    """Fixed OLS coefficients and residual SD (R ``.norm.fix``)."""
    est = estimice(x[ry], y[ry], ridge=ridge)
    denom = max(int(np.sum(ry)) - x.shape[1] - 1, 1)
    sigma = float(np.sqrt(np.sum(est.residuals**2) / denom))
    return est.coef, sigma


def add_intercept(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Prepend intercept column (R ``cbind(1, x)``)."""
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    if x.shape[1] == 0:
        return np.ones((x.shape[0], 1), dtype=np.float64)
    return np.column_stack([np.ones(x.shape[0], dtype=np.float64), x])


def matchindex(
    d: NDArray[np.float64],
    t: NDArray[np.float64],
    k: int,
    rng: np.random.Generator,
) -> NDArray[np.int_]:
    """PMM donor indices (port of R ``matchindex`` C++). Returns 0-based indices."""
    n1 = d.size
    n0 = t.size
    if n1 == 0 or n0 == 0:
        return np.array([], dtype=np.int_)

    k = max(1, min(k, n1))

    ishuf = rng.permutation(n1)
    yshuf = d[ishuf]
    isort = np.argsort(yshuf, kind="stable")
    id_order = ishuf[isort]
    ysort = d[id_order]

    h = rng.integers(1, k + 1, size=n0)

    idx = np.zeros(n0, dtype=np.int_)
    for i in range(n0):
        val = t[i]
        hi = int(h[i])
        r = int(np.searchsorted(ysort, val, side="left"))
        l = r - 1
        count = 0
        while count < hi and l >= 0 and r < n1:
            if val - ysort[l] < ysort[r] - val:
                idx[i] = id_order[l]
                l -= 1
            else:
                idx[i] = id_order[r]
                r += 1
            count += 1
        while count < hi and l >= 0:
            idx[i] = id_order[l]
            l -= 1
            count += 1
        while count < hi and r < n1:
            idx[i] = id_order[r]
            r += 1
            count += 1

    return idx
