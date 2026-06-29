"""jomoImpute — multivariate joint imputation (jomo1con / jomo1cat / jomo1mix / jomo1ran)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pymice.methods.jomo_categorical import jomo1cat_impute
from pymice.methods.jomo_core import JomoPrior, impute_by_group, jomo1con_impute, ml_jomo_impute
from pymice.methods.jomo_formula import build_design_matrices
from pymice.methods.jomo_mixed import jomo1mix_impute
from pymice.methods.multivariate import (
    parse_type_row,
    prepare_block_data,
    single_to_imputes,
)
from pymice.methods.registry import register_multivariate_method
from pymice.types import VariableKind, VariableSpec


def _split_targets(
    column_names: list[str],
    targets: list[str],
    specs: list[VariableSpec] | None,
) -> tuple[list[str], list[str], list[VariableSpec], list[VariableSpec]]:
    if specs is None:
        return targets, [], [], []

    spec_map = {s.name: s for s in specs}
    con: list[str] = []
    cat: list[str] = []
    con_specs: list[VariableSpec] = []
    cat_specs: list[VariableSpec] = []
    for name in targets:
        spec = spec_map.get(name)
        if spec is None or spec.kind == VariableKind.NUMERIC:
            con.append(name)
            if spec is not None:
                con_specs.append(spec)
            else:
                con_specs.append(VariableSpec(name, VariableKind.NUMERIC))
        else:
            cat.append(name)
            cat_specs.append(spec)
    return con, cat, con_specs, cat_specs


def _parse_prior(prior: object | None, n_targets: int) -> JomoPrior | None:
    if prior is None:
        return None
    if isinstance(prior, JomoPrior):
        return prior
    if isinstance(prior, dict):
        b_inv = prior.get("Binv") or prior.get("b_inv")
        d_inv = prior.get("Dinv") or prior.get("d_inv")
        a = prior.get("a")
        return JomoPrior(
            b_inv=np.asarray(b_inv, dtype=np.float64) if b_inv is not None else None,
            d_inv=np.asarray(d_inv, dtype=np.float64) if d_inv is not None else None,
            a=float(a) if a is not None else None,
        )
    return None


def _impute_continuous_block(
    work: NDArray[np.float64],
    column_names: list[str],
    con_names: list[str],
    *,
    x,
    z,
    clusters,
    groups,
    n_burn: int,
    n_iter: int,
    rng: np.random.Generator,
    random_l1: str,
    prior: JomoPrior | None,
) -> dict[str, NDArray[np.float64]]:
    target_idx = [column_names.index(v) for v in con_names]
    y = work[:, target_idx].astype(np.float64)

    if groups is not None:
        y_out = impute_by_group(
            y,
            groups,
            clusters,
            x=x,
            z=z,
            n_burn=n_burn,
            n_iter=n_iter,
            rng=rng,
            random_l1=random_l1,
            prior=prior,
        )
    elif clusters is not None:
        y_out = ml_jomo_impute(
            y,
            clusters,
            x=x,
            z=z,
            n_burn=n_burn,
            n_iter=n_iter,
            rng=rng,
            random_l1=random_l1,
            prior=prior,
        )
    else:
        y_out = jomo1con_impute(y, n_burn=n_burn, n_iter=n_iter, rng=rng)

    return {name: y_out[:, j] for j, name in enumerate(con_names)}


def impute_jomo(
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
    variable_specs: list[VariableSpec] | None = None,
    prior: object | None = None,
    **_: object,
) -> dict[str, NDArray[np.float64]]:
    """Impute a block jointly (R ``mice.impute.jomoImpute`` / mitml ``jomoImpute``)."""
    if random_l1 not in ("none", "mean", "full"):
        raise ValueError("random_l1 must be one of 'none', 'mean', or 'full'")
    if random_l1 != "none" and int(np.sum(type_row == -2)) == 0:
        raise ValueError("random.L1 requires a cluster indicator (type=-2)")

    spec = parse_type_row(type_row, column_names)
    work = prepare_block_data(data, column_names, block_vars, observed, where)
    jomo_prior = _parse_prior(prior, len(spec.targets))

    con_names, cat_names, con_specs, cat_specs = _split_targets(
        column_names,
        spec.targets,
        variable_specs,
    )

    x, z, clusters, groups = build_design_matrices(work, column_names, spec)
    if x is None and (spec.fixed or spec.cluster is not None):
        x = np.ones((work.shape[0], 1), dtype=np.float64)

    imputed: dict[str, NDArray[np.float64]] = {}

    if con_names and cat_names:
        con_idx = [column_names.index(v) for v in con_names]
        cat_idx = [column_names.index(v) for v in cat_names]
        x_pred = x[:, 1:] if x is not None and x.shape[1] > 1 else None
        y_con, y_cat = jomo1mix_impute(
            work[:, con_idx],
            work[:, cat_idx],
            con_specs,
            cat_specs,
            x=x_pred,
            n_burn=n_burn,
            n_iter=n_iter,
            rng=rng,
        )
        for j, name in enumerate(con_names):
            imputed[name] = y_con[:, j]
        for j, name in enumerate(cat_names):
            imputed[name] = y_cat[:, j]
    elif cat_names:
        cat_idx = [column_names.index(v) for v in cat_names]
        x_pred = x[:, 1:] if x is not None and x.shape[1] > 1 else None
        y_cat = jomo1cat_impute(
            work[:, cat_idx],
            cat_specs,
            x=x_pred,
            n_burn=n_burn,
            n_iter=n_iter,
            rng=rng,
        )
        imputed = {name: y_cat[:, j] for j, name in enumerate(cat_names)}
    elif con_names:
        imputed = _impute_continuous_block(
            work,
            column_names,
            con_names,
            x=x,
            z=z,
            clusters=clusters,
            groups=groups,
            n_burn=n_burn,
            n_iter=n_iter,
            rng=rng,
            random_l1=random_l1,
            prior=jomo_prior,
        )

    completed = work.copy()
    for name, col in imputed.items():
        j = column_names.index(name)
        completed[:, j] = col

    return single_to_imputes(completed, column_names, observed, where, spec.targets)


register_multivariate_method("jomoImpute", impute_jomo)
