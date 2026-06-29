"""Two-level normal imputation with heterogeneous class variances (2l.norm)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept
from pymice.methods.registry import register_method


def _symridge(x: NDArray[np.float64], ridge: float = 1e-4) -> NDArray[np.float64]:
    x = (x + x.T) / 2.0
    if x.shape[0] == 1:
        return x
    return x + np.diag(np.diag(x) * ridge)


def _chol_inv(a: NDArray[np.float64]) -> NDArray[np.float64]:
    a = _symridge(a)
    c = np.linalg.cholesky(a)
    ident = np.eye(a.shape[0], dtype=np.float64)
    return np.linalg.solve(c.T, np.linalg.solve(c, ident))


def _sample_wishart(
    df: float, scale: NDArray[np.float64], rng: np.random.Generator
) -> NDArray[np.float64]:
    p = scale.shape[0]
    df = max(df, float(p) + 1.0)
    chol = np.linalg.cholesky(_symridge(scale / df))
    z = rng.standard_normal((int(df), p))
    return (z @ chol.T).T @ (z @ chol.T)


def impute_2l_norm(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    type: NDArray[np.int_] | None = None,
    intercept: bool = True,
    n_iter: int = 100,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via two-level normal model (R ``mice.impute.2l.norm``)."""
    if type is None:
        raise ValueError("2l.norm requires predictor type codes (include -2 for cluster)")
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    type_vec = np.asarray(type, dtype=np.int_)
    if intercept:
        x_arr = add_intercept(x_arr)
        type_vec = np.concatenate([np.array([2], dtype=np.int_), type_vec])

    cluster_mask = type_vec == -2
    random_mask = type_vec == 2
    if not np.any(cluster_mask):
        raise ValueError("2l.norm requires a cluster indicator (type=-2)")
    gf_full = x_arr[:, cluster_mask].astype(np.int64).ravel()
    classes = np.unique(gf_full[ry])
    class_map = {c: i for i, c in enumerate(classes)}
    gf = np.array([class_map[v] for v in gf_full[ry]], dtype=np.int64)
    n_class = len(classes)
    x_rand = x_arr[:, random_mask]
    n_rc = x_rand.shape[1]

    xg: list[NDArray[np.float64]] = []
    yg: list[NDArray[np.float64]] = []
    xss: list[NDArray[np.float64]] = []
    n_g = np.zeros(n_class, dtype=np.int64)
    for g in range(n_class):
        idx = gf == g
        xg.append(x_rand[ry][idx])
        yg.append(y_arr[ry][idx])
        xss.append(xg[-1].T @ xg[-1])
        n_g[g] = int(np.sum(idx))

    bees = np.zeros((n_class, n_rc), dtype=np.float64)
    ss = np.zeros(n_class, dtype=np.float64)
    mu = np.zeros(n_rc, dtype=np.float64)
    inv_psi = np.eye(n_rc, dtype=np.float64)
    inv_sigma2 = np.ones(n_class, dtype=np.float64)
    sigma2_0 = 1.0
    theta = 1.0

    for _ in range(max(int(n_iter), 1)):
        for g in range(n_class):
            if n_g[g] == 0:
                continue
            vv = _symridge(inv_sigma2[g] * xss[g] + inv_psi)
            bees_var = _chol_inv(vv)
            rhs = xg[g].T @ (inv_sigma2[g] * yg[g]) + inv_psi @ mu
            mean_g = bees_var @ rhs
            bees[g] = mean_g + rng.standard_normal(n_rc) @ np.linalg.cholesky(_symridge(bees_var)).T
            resid = yg[g] - xg[g] @ bees[g]
            ss[g] = float(resid @ resid)

        mu = (
            np.mean(bees, axis=0)
            + rng.standard_normal(n_rc)
            @ np.linalg.cholesky(_chol_inv(_symridge(inv_psi)) / n_class).T
        )
        centered = bees - mu
        inv_psi = _sample_wishart(
            max(n_class - n_rc - 1.0, 2.0),
            _chol_inv(_symridge(centered.T @ centered)),
            rng,
        )
        inv_sigma2 = rng.gamma(
            n_g / 2.0 + 1.0 / (2.0 * theta), scale=2.0 * theta / (ss * theta + sigma2_0)
        )
        h_mean = 1.0 / np.mean(inv_sigma2)
        sigma2_0 = rng.gamma(n_class / (2.0 * theta) + 1.0, scale=2.0 * theta * h_mean / n_class)
        g_mean = float(np.exp(np.mean(np.log(1.0 / np.maximum(inv_sigma2, 1e-12)))))
        theta_denom = n_class * (
            sigma2_0 / h_mean - np.log(max(sigma2_0, 1e-12)) + np.log(max(g_mean, 1e-12)) - 1.0
        )
        theta_scale = 2.0 / max(theta_denom, 1e-6)
        theta = 1.0 / max(rng.gamma(max(n_class / 2.0 - 1.0, 1.0), scale=theta_scale), 1e-12)

    gf_wy = np.array([class_map[v] for v in gf_full[wy]], dtype=np.int64)
    noise = rng.normal(size=int(np.sum(wy))) * np.sqrt(1.0 / inv_sigma2[gf_wy])
    preds = np.sum(x_arr[wy][:, random_mask] * bees[gf_wy], axis=1)
    return preds + noise


register_method("2l.norm", impute_2l_norm)
