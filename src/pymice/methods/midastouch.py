"""Weighted predictive mean matching (midastouch)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.registry import register_method

_SMINX = float(np.sqrt(np.finfo(float).eps))


def _bootfunc_plain(n: int, rng: np.random.Generator) -> NDArray[np.float64]:
    draws = rng.integers(0, n, size=n)
    counts = np.bincount(draws, minlength=n).astype(np.float64)
    return counts


def _minmax(x: NDArray[np.float64]) -> NDArray[np.float64]:
    maxx = np.sqrt(np.finfo(float).max)
    minx = _SMINX
    return np.clip(x, minx, maxx)


def impute_midastouch(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    ridge: float = 1e-5,
    midas_kappa: float | None = None,
    outout: bool = True,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via distance-aided PMM (R ``mice.impute.midastouch``)."""
    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)
    y_arr = np.asarray(y, dtype=np.float64)
    x_full = add_intercept(x_arr)

    x_obs = x_full[ry]
    x_mis = x_full[wy]
    y_obs = y_arr[ry]
    nobs = int(x_obs.shape[0])
    nmis = int(x_mis.shape[0])
    if nobs == 0 or nmis == 0:
        return np.array([], dtype=np.float64)

    m = x_obs.shape[1]
    omega = _bootfunc_plain(nobs, rng)
    cx = omega[:, None] * x_obs
    xcx = x_obs.T @ cx
    if ridge > 0:
        diag = np.diag(xcx).copy()
        diag[0] *= 1.0
        diag[1:] *= 1.0 + ridge
        np.fill_diagonal(xcx, diag)
    diag0 = np.diag(xcx) == 0
    if np.any(diag0):
        np.fill_diagonal(xcx, np.maximum(np.diag(xcx), max(_SMINX, ridge)))

    xy = cx.T @ y_obs
    beta = np.linalg.solve(xcx, xy)
    yhat_obs = x_obs @ beta

    if midas_kappa is None:
        mean_y = float(np.dot(y_obs, omega) / nobs)
        eps = y_obs - yhat_obs
        num = float(np.dot(omega, eps**2))
        den = float(np.dot(omega, (y_obs - mean_y) ** 2))
        r2 = 1.0 - num / den if den > 0 else 0.0
        midas_kappa = min((50.0 * r2 / max(1.0 - r2, 1e-12)) ** (3.0 / 8.0), 100.0)
        if not np.isfinite(midas_kappa):
            midas_kappa = 3.0

    if outout:
        xx_pre = np.einsum("ij,ik->ijk", x_obs, x_obs) * omega[:, None, None]
        ridge_idx = np.arange(m) * (m + 1)
        xx_array = np.tile(xcx.ravel()[:, None], (1, nobs)) - xx_pre.reshape(m * m, nobs)
        if ridge > 0:
            for col in range(nobs):
                vals = xx_array[ridge_idx, col]
                zero = vals == 0
                vals[~zero] *= 1.0 + ridge
                vals[zero] = max(_SMINX, ridge)
                xx_array[ridge_idx, col] = vals
        xy_array = np.tile(xy[:, None], (1, nobs)) - (x_obs * y_obs[:, None] * omega[:, None]).T
        beta_array = np.zeros((m, nobs), dtype=np.float64)
        for col in range(nobs):
            mat = xx_array[:, col].reshape(m, m)
            vec = xy_array[:, col]
            try:
                beta_array[:, col] = np.linalg.solve(mat, vec)
            except np.linalg.LinAlgError:
                beta_array[:, col] = np.linalg.lstsq(mat, vec, rcond=None)[0]
        yhat_don = np.sum(x_obs * beta_array.T, axis=1)
        yhat_rec = x_mis @ beta_array
        dist = yhat_don[:, None] - yhat_rec.T
    else:
        yhat_mis = x_mis @ beta
        dist = yhat_obs[:, None] - yhat_mis[None, :]

    delta = 1.0 / (np.abs(dist) ** midas_kappa + 1e-12)
    delta = _minmax(delta)
    probs = delta * omega[:, None]
    col_sums = _minmax(np.sum(probs, axis=0))
    probs = probs / col_sums

    out = np.empty(nmis, dtype=np.float64)
    for j in range(nmis):
        p = probs[:, j]
        p = p / np.sum(p)
        idx = int(rng.choice(nobs, p=p))
        out[j] = y_obs[idx]
    return out


register_method("midastouch", impute_midastouch)
