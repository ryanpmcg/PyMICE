"""Quadratic-term imputation via polynomial combination (quadratic)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.linear import add_intercept, norm_draw
from pymice.methods.logreg import _fit_logistic_irls
from pymice.methods.pmm import impute_pmm
from pymice.methods.registry import register_method


def impute_quadratic(
    y: NDArray[np.floating],
    ry: NDArray[np.bool_],
    x: NDArray[np.floating],
    wy: NDArray[np.bool_],
    rng: np.random.Generator,
    quad_outcome: str | int | None = None,
    **_: object,
) -> NDArray[np.floating]:
    """Impute via polynomial combination method (R ``mice.impute.quadratic``)."""
    if quad_outcome is None:
        raise ValueError("Argument 'quad_outcome' for mice.impute.quadratic has not been specified")
    y_arr = np.asarray(y, dtype=np.float64)
    x_arr = np.asarray(x, dtype=np.float64)
    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)

    if isinstance(quad_outcome, int):
        if quad_outcome < 0 or quad_outcome >= x_arr.shape[1]:
            raise ValueError("quad_outcome index out of range for predictors")
        qcol = quad_outcome
    else:
        raise ValueError("quad_outcome must be a column index for matrix data")

    x_aug = add_intercept(x_arr)
    y2 = y_arr**2
    outcome = x_aug[:, qcol + 1]
    parm_coef, _, _ = norm_draw(
        outcome,
        ry,
        add_intercept(np.column_stack([y_arr, y2])),
        rng=rng,
    )
    zobs = np.column_stack([y_arr, y2])[ry] @ parm_coef[1:3]
    zmis = impute_pmm(zobs, ry, x_arr, wy, rng=rng)
    zstar = zobs.copy()
    zstar[~ry] = zmis
    zstar = zstar.astype(np.float64)

    b1, b2 = float(parm_coef[1]), float(parm_coef[2])
    if abs(b2) < 1e-12:
        return np.full(int(np.sum(wy)), float(np.nanmean(y_arr[ry])), dtype=np.float64)

    disc = 4.0 * b2 * zstar + b1**2
    disc = np.maximum(disc, 0.0)
    y_low = -(np.sqrt(disc) + b1) / (2.0 * b2)
    y_up = (np.sqrt(disc) - b1) / (2.0 * b2)
    y_min = -b1 / (2.0 * b2)

    q_obs = outcome[ry]
    (y_arr[ry] > y_min).astype(np.float64)
    q_mean, q_sd = float(np.mean(q_obs)), float(np.std(q_obs))
    z_mean, z_sd = float(np.mean(zstar[ry])), float(np.std(zstar[ry]))

    aug_q = np.array(
        [
            q_obs,
            q_mean + q_sd,
            q_mean - q_sd,
            q_mean + q_sd,
            q_mean - q_sd,
            q_mean,
            q_mean,
            q_mean,
            q_mean,
        ],
        dtype=np.float64,
    )
    aug_v = np.array([1, 1, 1, 0, 0, 1, 1, 0, 0], dtype=np.float64)
    aug_z = np.array(
        [
            zstar[ry],
            z_mean,
            z_mean,
            z_mean,
            z_mean,
            z_mean + z_sd,
            z_mean - z_sd,
            z_mean + z_sd,
            z_mean - z_sd,
        ],
        dtype=np.float64,
    )
    w = np.array([1.0] * (aug_q.size - 8) + [3.0 / 8.0] * 8, dtype=np.float64)
    design = add_intercept(np.column_stack([aug_q, aug_z, aug_q * aug_z]))
    beta, _ = _fit_logistic_irls(design, aug_v, w)

    q_mis = outcome[wy]
    z_mis = zstar[wy]
    pred_design = add_intercept(np.column_stack([q_mis, z_mis, q_mis * z_mis]))
    logits = pred_design @ beta
    prob = 1.0 / (1.0 + np.exp(-logits))
    idy = rng.random(int(np.sum(wy))) <= prob
    ystar = y_low[wy].copy()
    ystar[idy] = y_up[wy][idy]
    return ystar


register_method("quadratic", impute_quadratic)
