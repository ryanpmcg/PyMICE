"""Mixed continuous/categorical joint imputation (jomo1mix-style)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.jomo_categorical import jomo1cat_impute
from pymice.methods.linear import add_intercept
from pymice.methods.mvn_joint import _draw_mean_sigma, _impute_row, _initialize_missing
from pymice.types import VariableSpec


def jomo1mix_impute(
    y_con: NDArray[np.float64],
    y_cat: NDArray[np.float64],
    con_specs: list[VariableSpec],
    cat_specs: list[VariableSpec],
    x: NDArray[np.float64] | None = None,
    *,
    n_burn: int = 100,
    n_iter: int = 10,
    rng: np.random.Generator,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Alternate MVN (continuous) and categorical Gibbs updates."""
    del con_specs
    n = y_con.shape[0]
    if x is None:
        x = np.ones((n, 1), dtype=np.float64)
    x_full = add_intercept(np.asarray(x, dtype=np.float64))

    work_con = _initialize_missing(y_con, rng)
    work_cat = y_cat.copy()
    p = work_con.shape[1]

    total = max(int(n_burn), 0) + max(int(n_iter), 1)
    for _ in range(total):
        mu, sigma = _draw_mean_sigma(work_con, rng, prior_df=1.0, prior_scale=np.eye(p))
        for i in range(n):
            work_con[i] = _impute_row(work_con[i], mu, sigma, rng)

        imputed_cat = jomo1cat_impute(
            work_cat,
            cat_specs,
            x=x_full[:, 1:] if x_full.shape[1] > 1 else None,
            n_burn=0,
            n_iter=1,
            rng=rng,
        )
        work_cat[:] = imputed_cat

    return work_con, work_cat
