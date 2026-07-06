"""Two-level homoscedastic normal imputation via lmer-style sampling (2l.lmer)."""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import _chol_safe, add_intercept, estimice
from pymice.methods.r_lme4_backend import lme4_impute_r, use_r_lme4_backend
from pymice.methods.registry import register_method
from pymice.methods.twol_re_utils import _draw_mvn, _rwishart, _symmetrize_psd


def impute_2l_lmer(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    intercept: bool = True,
    use_r_lmer: bool | None = None,
    lme4_seed: int | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via two-level normal model (R ``mice.impute.2l.lmer``; random-intercept GLS)."""
    if type is None:
        raise ValueError("2l.lmer requires predictor type codes (include -2 for cluster)")
    y_arr = np.asarray(y, dtype=np.float64).copy()
    x_arr = np.asarray(x, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)

    cluster_mask = type_vec == -2
    rand_mask = type_vec == 2
    fix_mask = type_vec > 0
    if not np.any(cluster_mask):
        raise ValueError("2l.lmer requires a cluster indicator (type=-2)")

    if use_r_lme4_backend(use_r_lmer):
        seed = lme4_seed if lme4_seed is not None else int(rng.integers(1, 2**31 - 1))
        try:
            return lme4_impute_r(
                np.asarray(y, dtype=np.float64),
                ry,
                x_arr,
                type_vec,
                wy,
                method="lmer",
                seed=seed,
            )
        except RuntimeError:
            if use_r_lmer is True:
                raise

    cluster = x_arr[:, cluster_mask].astype(np.int64).ravel()
    x_fix = x_arr[:, fix_mask]
    z_rand = x_arr[:, rand_mask] if np.any(rand_mask) else np.ones((x_arr.shape[0], 1))
    if intercept:
        x_fix = add_intercept(x_fix)

    xobs = x_fix[ry]
    yobs = y_arr[ry]
    zobs = z_rand[ry]
    cl_obs = cluster[ry]
    if xobs.shape[0] < xobs.shape[1] + 2:
        warnings.warn("lmer does not run. Simplify imputation model", stacklevel=2)
        return y_arr[wy]

    est = estimice(xobs, yobs, ridge=1e-4)
    beta = est.coef
    resid = yobs - xobs @ beta
    df = max(int(np.sum(ry)) - xobs.shape[1], 1)
    sigmahat = float(np.sqrt(np.sum(resid**2) / df))
    sigma2_star = df * sigmahat**2 / max(rng.chisquare(df), 1e-6)

    beta_star = _draw_mvn(beta, est.cov * sigma2_star, rng)

    levels = np.unique(cluster)
    q = z_rand.shape[1]
    rancoef = np.zeros((levels.size, q), dtype=np.float64)
    for i, lev in enumerate(levels):
        mask = cl_obs == lev
        if np.any(mask):
            rancoef[i] = (
                np.mean(resid[mask])
                if q == 1
                else np.linalg.lstsq(zobs[mask], resid[mask], rcond=None)[0]
            )

    lambda_mat = rancoef.T @ rancoef
    temp_psi = _rwishart(levels.size + q, np.eye(q), rng)
    try:
        inv_lambda = np.linalg.inv(lambda_mat + np.eye(q) * 1e-6)
        psi_star = np.linalg.inv(_chol_safe(inv_lambda @ temp_psi))
    except np.linalg.LinAlgError:
        psi_star = np.eye(q) * float(np.var(resid))
    psi_star = _symmetrize_psd(psi_star)

    y_out = y_arr.copy()
    for lev in levels:
        mask_wy = wy & (cluster == lev)
        if not np.any(mask_wy):
            continue
        if lev in np.unique(cl_obs):
            int(np.where(levels == lev)[0][0])
            z_i = zobs[cl_obs == lev]
            resid_i = resid[cl_obs == lev]
            if q == 1:
                myi = np.array([float(np.mean(resid_i))], dtype=np.float64)
            else:
                myi = np.linalg.lstsq(z_i, resid_i, rcond=None)[0]
            vyi = psi_star
        else:
            myi = np.zeros(q, dtype=np.float64)
            vyi = psi_star
        bi_star = _draw_mvn(myi, vyi, rng)
        preds = x_fix[mask_wy] @ beta_star
        re = z_rand[mask_wy] @ bi_star
        noise = rng.normal(size=int(np.sum(mask_wy))) * np.sqrt(sigma2_star)
        y_out[mask_wy] = preds + re + noise
    return y_out[wy]


register_method("2l.lmer", impute_2l_lmer)
