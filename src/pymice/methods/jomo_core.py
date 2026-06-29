"""Unified JOMO-style multilevel joint Gibbs samplers (Python port of mitml/jomo)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pymice.methods.mvn_joint import (
    _chol_safe,
    _draw_cluster_effects,
    _impute_row,
    _initialize_missing,
    _sample_invwishart,
    _sigma_for_row,
)


@dataclass
class JomoPrior:
    """Conjugate prior knobs (mitml ``prior`` list elements)."""

    b_inv: NDArray[np.float64] | None = None
    d_inv: NDArray[np.float64] | None = None
    a: float | None = None


def _lstsq_beta(x: NDArray[np.float64], y: NDArray[np.float64]) -> NDArray[np.float64]:
    q, p = x.shape[1], y.shape[1]
    beta = np.zeros((q, p), dtype=np.float64)
    for j in range(p):
        mask = np.isfinite(y[:, j])
        if int(np.sum(mask)) <= q:
            continue
        coef, _, _, _ = np.linalg.lstsq(x[mask], y[mask, j], rcond=None)
        beta[:, j] = coef
    return beta


def ml_jomo_impute(
    y: NDArray[np.float64],
    clusters: NDArray[np.int_],
    *,
    x: NDArray[np.float64] | None = None,
    z: NDArray[np.float64] | None = None,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
    random_l1: str = "none",
    prior: JomoPrior | None = None,
) -> NDArray[np.float64]:
    """
    Multilevel joint MVN imputation (jomo1rancon / pan-style).

    Model: ``y = X @ beta + Z @ u_cluster + eps`` with optional heterogeneous
    level-1 covariance (``random_l1``) and random slopes via ``z``.
    """
    n, p = y.shape
    n_clusters = int(np.max(clusters)) + 1
    if x is None:
        x = np.ones((n, 1), dtype=np.float64)
    if z is None:
        z = np.zeros((n, 0), dtype=np.float64)
    q = x.shape[1]
    nq = z.shape[1]

    work = _initialize_missing(y, rng)
    beta = _lstsq_beta(x, np.nan_to_num(work, nan=0.0))
    sigma = np.eye(p, dtype=np.float64)
    psi = np.eye(max(nq * p, 1), dtype=np.float64) * 0.1 if nq else np.eye(p) * 0.1
    u_slopes = np.zeros((n_clusters, nq, p), dtype=np.float64) if nq else None
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
            base = x[idx] @ beta + cluster_fx[g]
            if nq and u_slopes is not None:
                base = base + z[idx] @ u_slopes[g]
            fitted[idx] = base

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
        if nq and u_slopes is not None:
            for g in range(n_clusters):
                idx = clusters == g
                if not np.any(idx):
                    continue
                z_g = z[idx]
                resid_g = residuals[idx]
                for j in range(p):
                    if z_g.shape[1] == 0:
                        continue
                    coef, _, _, _ = np.linalg.lstsq(z_g, resid_g[:, j], rcond=None)
                    u_slopes[g, :, j] = coef

        cluster_fx = _draw_cluster_effects(residuals, clusters, n_clusters, psi[:p, :p], sigma, rng)

        fitted = np.zeros((n, p), dtype=np.float64)
        for g in range(n_clusters):
            idx = clusters == g
            if not np.any(idx):
                continue
            base = x[idx] @ beta + cluster_fx[g]
            if nq and u_slopes is not None:
                base = base + z[idx] @ u_slopes[g]
            fitted[idx] = base
        resid2 = work - fitted

        beta = _lstsq_beta(x, np.nan_to_num(work, nan=0.0))

        if random_l1 == "none":
            scale = np.eye(p) + resid2.T @ resid2
            if prior and prior.b_inv is not None:
                scale = scale + prior.b_inv
            sigma = _sample_invwishart(max(n - q + 1.0, float(p) + 2.0), scale, rng)
        else:
            assert sigma_by_cluster is not None
            for g in range(n_clusters):
                idx = clusters == g
                if not np.any(idx):
                    continue
                resid_g = resid2[idx]
                scale = np.eye(p) + resid_g.T @ resid_g
                sigma_by_cluster[g] = _sample_invwishart(
                    max(int(np.sum(idx)) - q + 1.0, float(p) + 2.0),
                    scale,
                    rng,
                )
            sigma = (
                np.mean(np.stack(sigma_by_cluster, axis=0), axis=0)
                if random_l1 == "mean"
                else sigma_by_cluster[0]
            )

        if nq:
            u_flat = u_slopes.reshape(n_clusters, nq * p)
            psi_scale = np.eye(nq * p) + u_flat.T @ u_flat
            if prior and prior.d_inv is not None:
                psi_scale = psi_scale + prior.d_inv
            psi_draw = _sample_invwishart(
                max(n_clusters + float(nq * p) + 1.0, float(nq * p) + 2.0),
                psi_scale,
                rng,
            )
            psi = psi_draw
        else:
            psi = _sample_invwishart(
                max(n_clusters + float(p) + 1.0, float(p) + 2.0),
                np.eye(p) + cluster_fx.T @ cluster_fx,
                rng,
            )

    return work


def jomo1con_impute(
    y: NDArray[np.float64],
    *,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
    prior_scale: NDArray[np.float64] | None = None,
) -> NDArray[np.float64]:
    """Single-level continuous joint imputation (jomo1con)."""
    n, p = y.shape
    if prior_scale is None:
        prior_scale = np.eye(p, dtype=np.float64)
    work = _initialize_missing(y, rng)
    total = max(int(n_burn), 0) + max(int(n_iter), 1)
    for _ in range(total):
        mu = np.mean(work, axis=0)
        centered = work - mu
        scatter = centered.T @ centered
        df = max(n + 1.0 - p - 1.0, float(p) + 2.0)
        sigma = _sample_invwishart(df, prior_scale + scatter, rng)
        mu = rng.multivariate_normal(np.mean(work, axis=0), sigma / max(n, 1))
        for i in range(n):
            work[i] = _impute_row(work[i], mu, sigma, rng)
    return work


def impute_by_group(
    y: NDArray[np.float64],
    groups: NDArray[np.int_],
    clusters: NDArray[np.int_] | None,
    *,
    x: NDArray[np.float64] | None,
    z: NDArray[np.float64] | None,
    n_burn: int,
    n_iter: int,
    rng: np.random.Generator,
    random_l1: str,
    prior: JomoPrior | None,
    categorical: bool = False,
) -> NDArray[np.float64]:
    """Run joint imputation within each mitml ``group`` stratum."""
    out = y.copy()
    for gid in np.unique(groups):
        gmask = groups == gid
        y_g = y[gmask]
        if not np.any(~np.isfinite(y_g)):
            continue
        if clusters is not None:
            cl_g = clusters[gmask]
            _, cl_g = np.unique(cl_g, return_inverse=True)
            x_g = x[gmask] if x is not None else None
            z_g = z[gmask] if z is not None else None
            filled = ml_jomo_impute(
                y_g,
                cl_g.astype(np.int_),
                x=x_g,
                z=z_g,
                n_burn=n_burn,
                n_iter=n_iter,
                rng=rng,
                random_l1=random_l1,
                prior=prior,
            )
        else:
            filled = jomo1con_impute(y_g, n_burn=n_burn, n_iter=n_iter, rng=rng)
        out[gmask] = filled
    return out
