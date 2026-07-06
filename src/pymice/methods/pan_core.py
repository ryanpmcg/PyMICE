"""PAN homoscedastic multilevel Gibbs sampler (R ``pan::pan``, univariate)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.mvn_joint import _chol_safe, _sample_invwishart
from pymice.methods.r_pan_backend import (
    derive_pan_seed_from_mice_seed,
    pan_impute_r,
    use_r_pan_backend,
)


def _symridge(x: NDArray[np.float64], ridge: float = 1e-4) -> NDArray[np.float64]:
    x = (x + x.T) / 2.0
    if x.shape[0] == 1:
        return x
    return x + np.diag(np.diag(x) * ridge)


def _safe_inv(mat: NDArray[np.float64]) -> NDArray[np.float64]:
    chol = _chol_safe(mat)
    ident = np.eye(mat.shape[0], dtype=np.float64)
    return np.linalg.solve(chol.T, np.linalg.solve(chol, ident))


def _init_missing(y: NDArray[np.float64], rng: np.random.Generator) -> NDArray[np.float64]:
    work = y.copy()
    miss = ~np.isfinite(work)
    if not np.any(miss):
        return work
    obs = work[~miss]
    if obs.size == 0:
        raise ValueError("no observed outcomes for 2l.pan")
    work[miss] = rng.choice(obs, size=int(np.sum(miss)))
    return work


def _lstsq_beta(
    pred: NDArray[np.float64],
    y: NDArray[np.float64],
    mask: NDArray[np.bool_],
) -> NDArray[np.float64]:
    x_obs = pred[mask]
    y_obs = y[mask]
    if y_obs.size <= pred.shape[1]:
        return np.zeros(pred.shape[1], dtype=np.float64)
    coef, _, _, _ = np.linalg.lstsq(x_obs, y_obs, rcond=None)
    return coef.astype(np.float64)


def pan_univariate_impute(
    y: NDArray[np.float64],
    subj: NDArray[np.int_],
    pred: NDArray[np.float64],
    zcol: NDArray[np.int_],
    *,
    n_iter: int = 500,
    rng: np.random.Generator,
    use_r_pan: bool | None = None,
    pan_seed: int | None = None,
    mice_seed: int | None = None,
) -> NDArray[np.float64]:
    """
    Gibbs sampler for a univariate two-level model with homogeneous variance.

    Implements the mixed-model structure used by R ``mice.impute.2l.pan`` /
    ``pan::pan`` (Schafer & Yucel, 2002): ``y = pred @ beta + (pred[:, zcol] @ u_g) + eps``.
    """
    y_vec = np.asarray(y, dtype=np.float64).ravel()
    subj_arr = np.asarray(subj, dtype=np.int_)
    pred_arr = np.asarray(pred, dtype=np.float64)
    z_idx = np.asarray(zcol, dtype=np.int_)

    if use_r_pan_backend(use_r_pan):
        seed = pan_seed
        if seed is None and mice_seed is not None:
            seed = derive_pan_seed_from_mice_seed(mice_seed)
        if seed is None:
            seed = int(rng.integers(1, 10**7 + 1))
        try:
            return pan_impute_r(
                y_vec,
                subj_arr,
                pred_arr,
                z_idx,
                n_iter=n_iter,
                pan_seed=seed,
            )
        except RuntimeError:
            if use_r_pan is True:
                raise
    n, p = pred_arr.shape
    q = int(z_idx.size)
    if q == 0:
        raise ValueError("2l.pan requires at least one random effect column")
    m = int(np.max(subj_arr)) + 1
    z = pred_arr[:, z_idx]

    miss = ~np.isfinite(y_vec)
    obs = ~miss
    work = _init_missing(y_vec, rng)

    prior_a = 1.0
    prior_binv = 1.0
    prior_c = float(q)
    prior_dinv = np.eye(q, dtype=np.float64)

    beta = _lstsq_beta(pred_arr, work, obs)
    u = np.zeros((m, q), dtype=np.float64)
    resid0 = work[obs] - pred_arr[obs] @ beta
    sigma2 = max(float(np.var(resid0)) if resid0.size > 1 else 1.0, 1e-4)
    psi = np.eye(q, dtype=np.float64) * min(sigma2, 1.0)

    for _ in range(max(int(n_iter), 1)):
        zu = np.sum(z * u[subj_arr], axis=1)
        fitted = pred_arr @ beta + zu

        work[miss] = rng.normal(fitted[miss], np.sqrt(sigma2))

        y_adj = work - zu
        xtx = pred_arr.T @ pred_arr / sigma2
        beta_prec = np.eye(p) * prior_binv + xtx
        beta_cov = _safe_inv(beta_prec)
        beta = rng.multivariate_normal(beta_cov @ (pred_arr.T @ y_adj / sigma2), beta_cov)

        resid_u = work - pred_arr @ beta
        psi_inv = _safe_inv(psi)
        for g in range(m):
            idx = subj_arr == g
            if not np.any(idx):
                continue
            z_g = z[idx]
            post_prec = psi_inv + (z_g.T @ z_g) / sigma2
            post_cov = _safe_inv(post_prec)
            post_mean = post_cov @ (z_g.T @ resid_u[idx] / sigma2)
            u[g] = rng.multivariate_normal(post_mean, post_cov)

        zu = np.sum(z * u[subj_arr], axis=1)
        resid2 = work - pred_arr @ beta - zu
        df_sigma = max(n - p + prior_a, 1.0)
        sigma2 = max(
            float(
                rng.gamma(
                    df_sigma / 2.0,
                    scale=2.0 / (prior_binv + float(resid2 @ resid2)),
                )
            ),
            1e-8,
        )

        df_psi = max(m + prior_c - q - 1.0, float(q) + 1.0)
        psi = _sample_invwishart(df_psi, prior_dinv + u.T @ u, rng)

    return work
