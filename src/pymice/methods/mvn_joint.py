"""Multivariate normal joint imputation (single- and multilevel)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _chol_safe(cov: NDArray[np.float64], ridge: float = 1e-8) -> NDArray[np.float64]:
    cov = (cov + cov.T) / 2.0
    p = cov.shape[0]
    for scale in (0.0, ridge, ridge * 10, ridge * 1000, 1e-4):
        try:
            jitter = np.eye(p) * scale
            return np.linalg.cholesky(cov + jitter)
        except np.linalg.LinAlgError:
            continue
    return np.diag(np.sqrt(np.maximum(np.diag(cov), ridge)))


def _sample_invwishart(
    df: float, scale: NDArray[np.float64], rng: np.random.Generator
) -> NDArray[np.float64]:
    """Draw from Inv-Wishart(df, scale) via Wishart on precision."""
    p = scale.shape[0]
    df = max(float(df), float(p) + 2.0)
    chol = _chol_safe(scale / df)
    draws = rng.standard_normal((int(df), p))
    wishart = draws @ chol.T
    precision = wishart.T @ wishart
    return np.linalg.inv(precision)


def _initialize_missing(y: NDArray[np.float64], rng: np.random.Generator) -> NDArray[np.float64]:
    out = y.copy()
    for j in range(out.shape[1]):
        col = out[:, j]
        miss = ~np.isfinite(col)
        if not np.any(miss):
            continue
        obs = col[~miss]
        fill = float(np.mean(obs)) if obs.size else 0.0
        if obs.size:
            fill = rng.choice(obs)
        out[miss, j] = fill
    return out


def _impute_row(
    y_row: NDArray[np.float64],
    mu: NDArray[np.float64],
    sigma: NDArray[np.float64],
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    out = y_row.copy()
    miss = ~np.isfinite(out)
    if not np.any(miss):
        return out
    obs = ~miss
    if not np.any(obs):
        out[miss] = rng.multivariate_normal(mu, sigma)
        return out

    o_idx = np.where(obs)[0]
    m_idx = np.where(miss)[0]
    sigma_oo = sigma[np.ix_(o_idx, o_idx)]
    sigma_mo = sigma[np.ix_(m_idx, o_idx)]
    sigma_mm = sigma[np.ix_(m_idx, m_idx)]
    chol = _chol_safe(sigma_oo)
    alpha = np.linalg.solve(chol, (out[o_idx] - mu[o_idx]))
    cond_mean = mu[m_idx] + sigma_mo @ np.linalg.solve(chol.T, alpha)
    cond_cov = sigma_mm - sigma_mo @ np.linalg.solve(chol.T, np.linalg.solve(chol, sigma_mo.T))
    out[m_idx] = rng.multivariate_normal(cond_mean, cond_cov)
    return out


def _draw_mean_sigma(
    y: NDArray[np.float64],
    rng: np.random.Generator,
    prior_df: float,
    prior_scale: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Posterior draw for mean and covariance (flat conjugate prior)."""
    n, p = y.shape
    ybar = np.mean(y, axis=0)
    centered = y - ybar
    scatter = centered.T @ centered
    df = max(n + prior_df - p - 1.0, float(p) + 2.0)
    scale = prior_scale + scatter + np.outer(ybar, ybar) * n * prior_df / (n + prior_df)
    sigma = _sample_invwishart(df, scale, rng)
    mu = rng.multivariate_normal(ybar, sigma / n)
    return mu, sigma


def mvn_da_impute(
    y: NDArray[np.float64],
    *,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
    prior_scale: NDArray[np.float64] | None = None,
) -> NDArray[np.float64]:
    """Single-level MVN data augmentation (jomo1con-style, continuous only)."""
    n, p = y.shape
    if prior_scale is None:
        prior_scale = np.eye(p, dtype=np.float64)
    work = _initialize_missing(y, rng)
    total = max(int(n_burn), 0) + max(int(n_iter), 1)
    for _ in range(total):
        mu, sigma = _draw_mean_sigma(work, rng, prior_df=1.0, prior_scale=prior_scale)
        for i in range(n):
            work[i] = _impute_row(work[i], mu, sigma, rng)
    return work


def _safe_inv(mat: NDArray[np.float64]) -> NDArray[np.float64]:
    chol = _chol_safe(mat)
    ident = np.eye(mat.shape[0], dtype=np.float64)
    return np.linalg.solve(chol.T, np.linalg.solve(chol, ident))


def _draw_cluster_effects(
    residuals: NDArray[np.float64],
    clusters: NDArray[np.int_],
    n_clusters: int,
    psi: NDArray[np.float64],
    sigma: NDArray[np.float64],
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    p = psi.shape[0]
    effects = np.zeros((n_clusters, p), dtype=np.float64)
    psi_inv = _safe_inv(psi)
    sigma_inv = _safe_inv(sigma)
    for g in range(n_clusters):
        idx = clusters == g
        n_g = int(np.sum(idx))
        if n_g == 0:
            continue
        mean_g = np.mean(residuals[idx], axis=0)
        post_cov = _safe_inv(psi_inv + n_g * sigma_inv)
        post_mean = post_cov @ (n_g * sigma_inv @ mean_g)
        effects[g] = rng.multivariate_normal(post_mean, post_cov)
    return effects


def _sigma_for_row(
    clusters: NDArray[np.int_],
    sigma_common: NDArray[np.float64],
    sigma_by_cluster: list[NDArray[np.float64]] | None,
    row: int,
) -> NDArray[np.float64]:
    if sigma_by_cluster is None:
        return sigma_common
    return sigma_by_cluster[int(clusters[row])]


def ml_pan_impute(
    y: NDArray[np.float64],
    clusters: NDArray[np.int_],
    x: NDArray[np.float64] | None = None,
    *,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
    random_l1: str = "none",
) -> NDArray[np.float64]:
    """Multilevel MVN imputation with random intercept (pan / jomo1ran-style)."""
    n, p = y.shape
    n_clusters = int(np.max(clusters)) + 1
    if x is None:
        x = np.ones((n, 1), dtype=np.float64)
    q = x.shape[1]

    work = _initialize_missing(y, rng)
    beta = np.zeros((q, p), dtype=np.float64)
    sigma = np.eye(p, dtype=np.float64)
    psi = np.eye(p, dtype=np.float64) * 0.1
    cluster_fx = np.zeros((n_clusters, p), dtype=np.float64)
    sigma_by_cluster: list[NDArray[np.float64]] | None = None
    if random_l1 in ("mean", "full"):
        sigma_by_cluster = [np.eye(p, dtype=np.float64) for _ in range(n_clusters)]

    total = max(int(n_burn), 0) + max(int(n_iter), 1)
    for _ in range(total):
        fitted = np.zeros((n, p), dtype=np.float64)
        for g in range(n_clusters):
            idx = clusters == g
            if not np.any(idx):
                continue
            fitted[idx] = x[idx] @ beta + cluster_fx[g]

        residuals = work - fitted
        for i in range(n):
            miss = ~np.isfinite(work[i])
            if not np.any(miss):
                continue
            row = work[i].copy()
            obs = ~miss
            o_idx = np.where(obs)[0]
            m_idx = np.where(miss)[0]
            mu_i = fitted[i]
            sigma_i = _sigma_for_row(clusters, sigma, sigma_by_cluster, i)
            sigma_oo = sigma_i[np.ix_(o_idx, o_idx)]
            sigma_mo = sigma_i[np.ix_(m_idx, o_idx)]
            sigma_mm = sigma_i[np.ix_(m_idx, m_idx)]
            chol = _chol_safe(sigma_oo)
            alpha = np.linalg.solve(chol, row[o_idx] - mu_i[o_idx])
            cond_mean = mu_i[m_idx] + sigma_mo @ np.linalg.solve(chol.T, alpha)
            cond_cov = sigma_mm - sigma_mo @ np.linalg.solve(
                chol.T, np.linalg.solve(chol, sigma_mo.T)
            )
            row[m_idx] = rng.multivariate_normal(cond_mean, cond_cov)
            work[i] = row

        residuals = work - fitted
        cluster_fx = _draw_cluster_effects(residuals, clusters, n_clusters, psi, sigma, rng)

        fitted = np.zeros((n, p), dtype=np.float64)
        for g in range(n_clusters):
            idx = clusters == g
            if np.any(idx):
                fitted[idx] = x[idx] @ beta + cluster_fx[g]
        resid2 = work - fitted

        for j in range(p):
            yj = work[:, j]
            mask = np.isfinite(yj)
            if int(np.sum(mask)) <= q:
                continue
            x_obs = x[mask]
            y_obs = yj[mask]
            coef, _, _, _ = np.linalg.lstsq(x_obs, y_obs, rcond=None)
            beta[:, j] = coef

        if random_l1 == "none":
            sigma = _sample_invwishart(
                max(n - q + 1.0, float(p) + 2.0),
                np.eye(p) + resid2.T @ resid2,
                rng,
            )
        else:
            assert sigma_by_cluster is not None
            for g in range(n_clusters):
                idx = clusters == g
                if not np.any(idx):
                    continue
                resid_g = resid2[idx]
                sigma_by_cluster[g] = _sample_invwishart(
                    max(int(np.sum(idx)) - q + 1.0, float(p) + 2.0),
                    np.eye(p) + resid_g.T @ resid_g,
                    rng,
                )
            if random_l1 == "mean":
                sigma = np.mean(np.stack(sigma_by_cluster, axis=0), axis=0)
            else:
                sigma = sigma_by_cluster[0]
        psi = _sample_invwishart(
            max(n_clusters + float(p) + 1.0, float(p) + 2.0),
            np.eye(p) + cluster_fx.T @ cluster_fx,
            rng,
        )

    return work
