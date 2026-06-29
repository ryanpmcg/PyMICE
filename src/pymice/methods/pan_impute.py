"""panImpute — multilevel homoscedastic joint imputation."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.jomo_core import ml_jomo_impute
from pymice.methods.jomo_formula import build_design_matrices
from pymice.methods.multivariate import (
    parse_type_row,
    prepare_block_data,
    single_to_imputes,
)
from pymice.methods.registry import register_multivariate_method


def impute_pan(
    data: NDArray[np.float64],
    column_names: list[str],
    block_vars: list[str],
    type_row: NDArray[np.int_],
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
    rng: np.random.Generator,
    n_burn: int = 100,
    n_iter: int = 10,
    random_l1: str = "none",
    **_: object,
) -> dict[str, NDArray[np.float64]]:
    """Impute a block jointly with PAN (R ``mice.impute.panImpute``)."""
    spec = parse_type_row(type_row, column_names)
    if spec.cluster is None:
        raise ValueError(
            "panImpute requires a cluster indicator (type=-2). "
            "Use jomoImpute for single-level joint imputation."
        )

    work = prepare_block_data(data, column_names, block_vars, observed, where)
    target_idx = [column_names.index(v) for v in spec.targets]
    y = work[:, target_idx].astype(np.float64)

    x, z, clusters, _ = build_design_matrices(work, column_names, spec)
    if clusters is None:
        raise ValueError("cluster indicator missing after parse")

    imputed_targets = ml_jomo_impute(
        y,
        clusters,
        x=x,
        z=z,
        n_burn=n_burn,
        n_iter=n_iter,
        rng=rng,
        random_l1=random_l1,
    )

    completed = work.copy()
    for local_j, name in enumerate(spec.targets):
        j = column_names.index(name)
        completed[:, j] = imputed_targets[:, local_j]

    return single_to_imputes(completed, column_names, observed, where, spec.targets)


register_multivariate_method("panImpute", impute_pan)
