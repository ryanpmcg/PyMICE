"""Two-level logistic imputation (2l.bin) — random-intercept GLMM sampling."""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import _chol_safe, add_intercept
from pymice.methods.logreg import _fit_logistic_irls
from pymice.methods.r_lme4_backend import lme4_impute_r, use_r_lme4_backend
from pymice.methods.registry import register_method
from pymice.methods.twol_re_utils import _draw_mvn, _rwishart, _symmetrize_psd


def impute_2l_bin(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    intercept: bool = True,
    random_effects: str = "laplace",
    use_r_lmer: bool | None = None,
    lme4_seed: int | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute binary outcomes via two-level logistic model (R ``mice.impute.2l.bin``)."""
    if type is None:
        raise ValueError("2l.bin requires predictor type codes (include -2 for cluster)")
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)

    cluster_mask = type_vec == -2
    rand_mask = type_vec == 2
    fix_mask = type_vec > 0
    if not np.any(cluster_mask):
        raise ValueError("2l.bin requires a cluster indicator (type=-2)")

    if use_r_lme4_backend(use_r_lmer):
        seed = lme4_seed if lme4_seed is not None else int(rng.integers(1, 2**31 - 1))
        try:
            return lme4_impute_r(
                np.asarray(y, dtype=np.float64),
                ry,
                x_arr,
                type_vec,
                wy,
                method="bin",
                seed=seed,
                random_effects=random_effects,
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
    yobs = np.clip(y_arr[ry], 1e-9, 1 - 1e-9)
    z_rand[ry]
    cl_obs = cluster[ry]
    weights = np.ones(xobs.shape[0], dtype=np.float64)

    try:
        beta, cov = _fit_logistic_irls(
            add_intercept(xobs[:, 1:] if x_fix.shape[1] > 1 else xobs), yobs, weights
        )
    except Exception:
        warnings.warn("glmer does not run. Simplify imputation model", stacklevel=2)
        return y_arr[wy]

    beta_star = _draw_mvn(beta, cov, rng)

    levels = np.unique(cluster)
    q = z_rand.shape[1]
    rancoef = np.zeros((levels.size, q), dtype=np.float64)
    for i, lev in enumerate(levels):
        mask = cl_obs == lev
        if np.any(mask):
            eta = xobs[mask] @ beta[: xobs.shape[1]]
            rancoef[i] = np.mean(yobs[mask] - 1.0 / (1.0 + np.exp(-eta)))

    lambda_mat = rancoef.T @ rancoef + np.eye(q) * 1e-4
    temp_psi = _rwishart(levels.size + q, np.eye(q), rng)
    psi_star = np.linalg.inv(_chol_safe(np.linalg.inv(lambda_mat) @ temp_psi))
    psi_star = _symmetrize_psd(psi_star)

    cl_mis = np.unique(cluster[wy])
    cl_obs_set = set(np.unique(cl_obs).tolist())
    bi_lookup: dict[int, NDArray[np.float64]] = {}
    for lev in cl_mis:
        if lev in cl_obs_set:
            ri = int(np.where(levels == lev)[0][0])
            myi = rancoef[ri]
            vyi = psi_star * 0.5
        else:
            myi = np.zeros(q, dtype=np.float64)
            vyi = psi_star
        bi_lookup[int(lev)] = _draw_mvn(myi, vyi, rng)

    eta = x_fix[wy] @ beta_star[: x_fix.shape[1]]
    re = np.array([bi_lookup[int(c)][0] for c in cluster[wy]], dtype=np.float64)
    logit = eta + re
    prob = 1.0 / (1.0 + np.exp(-logit))
    return (rng.random(int(np.sum(wy))) <= prob).astype(np.float64)


register_method("2l.bin", impute_2l_bin)
