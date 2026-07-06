"""Helpers for two-level ``2l.lmer`` / ``2l.bin`` posterior sampling."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import _chol_safe, add_intercept, estimice


def _symmetrize_psd(mat: NDArray[np.float64]) -> NDArray[np.float64]:
    mat = (mat + mat.T) / 2.0
    vals, vecs = np.linalg.eigh(mat)
    vals = np.maximum(vals, 0.0)
    return vecs @ np.diag(vals) @ vecs.T


def _draw_mvn(
    mean: NDArray[np.float64], cov: NDArray[np.float64], rng: np.random.Generator
) -> NDArray[np.float64]:
    cov = _symmetrize_psd(cov)
    chol = _chol_safe(cov)
    return mean + chol @ rng.standard_normal(mean.size)


def _rwishart(
    df: float, scale: NDArray[np.float64], rng: np.random.Generator
) -> NDArray[np.float64]:
    p = scale.shape[0]
    z = np.zeros((p, p), dtype=np.float64)
    dfs = df - np.arange(p, dtype=np.float64)
    z[np.diag_indices(p)] = np.sqrt(rng.chisquare(np.maximum(dfs, 1e-6)))
    if p > 1:
        tril = np.tril_indices(p, k=-1)
        z[tril] = rng.standard_normal(tril[0].size)
    draw = z @ scale
    return draw.T @ draw


def fit_random_intercept_lmer(
    y: NDArray[np.float64],
    x_fix: NDArray[np.float64],
    cluster: NDArray[np.int64],
) -> tuple[NDArray[np.float64], float, float, NDArray[np.float64], dict[int, NDArray[np.float64]]]:
    """
    Fit homoscedastic random-intercept model via method-of-moments / GLS.

    Returns beta_hat, sigma2_hat, psi_hat, cluster_blups, fitted residuals info.
    """
    x_fix = add_intercept(x_fix) if x_fix.ndim == 1 or x_fix.shape[1] >= 0 else x_fix
    if x_fix.ndim == 1:
        x_fix = x_fix.reshape(-1, 1)
    x_fix = add_intercept(x_fix)

    clusters = np.unique(cluster)
    n = y.size
    n_g = clusters.size
    grand = float(np.mean(y))
    group_means = np.array([np.mean(y[cluster == g]) for g in clusters], dtype=np.float64)
    within = y - group_means[cluster]
    msb = float(np.sum(clusters.size * (group_means - grand) ** 2) / max(n_g - 1, 1))
    msw = float(np.sum(within**2) / max(n - n_g, 1))
    k_bar = n / max(n_g, 1)
    psi = max(msb - msw / max(k_bar, 1), 1e-8)
    sigma2 = max(msw, 1e-8)

    est = estimice(x_fix, y, ridge=1e-4)
    beta = est.coef
    blups = {
        int(g): np.array([float(np.mean(y[cluster == g]) - grand)], dtype=np.float64)
        for g in clusters
    }
    return beta, sigma2, psi, group_means, blups


def draw_lmer_imputations(
    y: NDArray[np.float64],
    ry: NDArray[np.bool_],
    x_fix: NDArray[np.float64],
    z_rand: NDArray[np.float64],
    cluster: NDArray[np.int64],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    """Posterior draws for ``2l.lmer`` (random-intercept homoscedastic normal)."""
    x_fix = np.asarray(x_fix, dtype=np.float64)
    z_rand = np.asarray(z_rand, dtype=np.float64)
    if z_rand.ndim == 1:
        z_rand = z_rand.reshape(-1, 1)
    if z_rand.shape[1] == 0:
        z_rand = np.ones((cluster.size, 1), dtype=np.float64)

    x_obs = add_intercept(x_fix[ry])
    y_obs = y[ry]
    cluster[ry]
    est = estimice(x_obs, y_obs, ridge=1e-4)
    beta = est.coef
    resid = y_obs - x_obs @ beta
    df = max(int(np.sum(ry)) - x_obs.shape[1], 1)
    sigmahat = float(np.sqrt(np.sum(resid**2) / df))
    sigma2_star = df * sigmahat**2 / max(rng.chisquare(df), 1e-6)

    cov_beta = est.cov * sigma2_star
    beta_star = _draw_mvn(beta, cov_beta, rng)

    clusters = np.unique(cluster)
    n_g = clusters.size
    q = z_rand.shape[1]
    rancoef = np.zeros((n_g, q), dtype=np.float64)
    for i, g in enumerate(clusters):
        mask = (cluster == g) & ry
        if np.any(mask):
            rancoef[i] = np.mean(resid[mask])  # BLUP proxy for RI
    lambda_mat = rancoef.T @ rancoef
    temp_psi = _rwishart(n_g + q, np.eye(q), rng)
    try:
        psi_star = np.linalg.inv(
            _chol_safe(np.linalg.inv(lambda_mat + np.eye(q) * 1e-6)) @ temp_psi
        )
    except np.linalg.LinAlgError:
        psi_star = np.eye(q) * float(np.var(resid))
    psi_star = _symmetrize_psd(psi_star)

    out = np.empty(int(np.sum(wy)), dtype=np.float64)
    idx = 0
    for g in np.unique(cluster[wy]):
        mask_wy = wy & (cluster == g)
        n_miss = int(np.sum(mask_wy))
        if np.any((cluster == g) & ry):
            ri = int(np.where(clusters == g)[0][0])
            myi = rancoef[ri]
            vyi = psi_star
        else:
            myi = np.zeros(q, dtype=np.float64)
            vyi = psi_star
        bi_star = _draw_mvn(myi, vyi, rng)
        preds = x_fix[mask_wy] @ beta_star[1:] if x_fix.shape[1] else beta_star[0]
        if x_fix.shape[1]:
            preds = add_intercept(x_fix[mask_wy]) @ beta_star
        else:
            preds = np.full(n_miss, beta_star[0], dtype=np.float64)
        re_contrib = z_rand[mask_wy] @ bi_star
        noise = rng.normal(size=n_miss) * np.sqrt(sigma2_star)
        out[idx : idx + n_miss] = preds + re_contrib + noise
        idx += n_miss
    return out
