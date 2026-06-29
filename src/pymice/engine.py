"""FCS / MICE Gibbs sampler engine."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
from numpy.typing import NDArray

import pymice.methods  # noqa: F401 — register built-in methods
from pymice.data_form import as_data_matrix
from pymice.design import obtain_design
from pymice.imputation_setup import (
    check_blocks,
    make_block_predictor_matrix,
    make_blocks,
    make_method,
    make_predictor_matrix,
    make_visit_sequence,
    predictor_row_for_block,
)
from pymice.initialize import initialize_imputations, where_indices
from pymice.methods.linear import remove_lindep
from pymice.methods.registry import get_method, get_multivariate_method, is_multivariate_method
from pymice.passive import evaluate_passive, is_passive
from pymice.postprocess import PostContext, PostHook, execute_post, normalize_post
from pymice.types import Mids, VariableKind, VariableSpec


def mice(
    data: NDArray[Any] | dict[str, NDArray[Any]],
    m: int = 5,
    method: str | Mapping[str, str] | None = None,
    predictor_matrix: NDArray[np.int_] | None = None,
    visit_sequence: list[str] | None = None,
    maxit: int = 5,
    max_iter: int | None = None,
    seed: int | None = None,
    where: NDArray[np.bool_] | None = None,
    ignore: NDArray[np.bool_] | None = None,
    column_names: list[str] | None = None,
    variable_specs: list[VariableSpec] | dict[str, VariableSpec] | None = None,
    data_init: NDArray[np.float64] | None = None,
    print_flag: bool = False,
    verbose: bool | None = None,
    n_jobs: int = 1,
    blocks: dict[str, list[str]] | None = None,
    block_predictor_matrix: dict[str, list[int] | NDArray[np.int_]] | None = None,
    default_method: tuple[str, str, str, str] = ("pmm", "logreg", "polyreg", "polr"),
    n_burn: int = 100,
    n_iter: int = 10,
    random_l1: str = "none",
    prior: object | None = None,
    post: dict[str, PostHook] | list[str] | None = None,
    post_extras: dict[str, object] | None = None,
) -> Mids:
    """Run MICE (Fully Conditional Specification) on incomplete data."""
    if max_iter is not None:
        maxit = max_iter
    if verbose is not None:
        print_flag = verbose
    if n_jobs != 1:
        from pymice.parallel import parallel_mice

        return parallel_mice(
            data,
            m=m,
            n_jobs=n_jobs,
            method=method,
            predictor_matrix=predictor_matrix,
            visit_sequence=visit_sequence,
            maxit=maxit,
            seed=seed,
            where=where,
            ignore=ignore,
            column_names=column_names,
            variable_specs=variable_specs,
            data_init=data_init,
            verbose=print_flag,
            blocks=blocks,
            block_predictor_matrix=block_predictor_matrix,
            default_method=default_method,
            n_burn=n_burn,
            n_iter=n_iter,
            random_l1=random_l1,
            prior=prior,
            post=post,
            post_extras=post_extras,
        )

    matrix, names, specs = as_data_matrix(
        data,
        column_names=column_names,
        variable_specs=variable_specs,
    )
    n_obs, _ = matrix.shape

    if m < 1:
        raise ValueError("m must be >= 1")
    if maxit < 0:
        raise ValueError("maxit must be >= 0")

    if blocks is None:
        blocks = make_blocks(names)
    else:
        blocks = check_blocks(blocks, names)
    if predictor_matrix is None:
        predictor_matrix = make_predictor_matrix(names, blocks)
    if visit_sequence is None:
        visit_sequence = make_visit_sequence(names, blocks)

    observed = ~np.isnan(matrix)
    if where is None:
        where = np.isnan(matrix)
    else:
        where = np.asarray(where, dtype=bool)
        if where.shape != matrix.shape:
            raise ValueError("where must match data shape")

    if ignore is None:
        ignore = np.zeros(n_obs, dtype=bool)
    else:
        ignore = np.asarray(ignore, dtype=bool)
        if ignore.shape != (n_obs,):
            raise ValueError("ignore must have length n_obs")

    methods = make_method(
        names,
        specs,
        where,
        blocks=blocks,
        method=method,
        default_method=default_method,
    )
    block_pred = _normalize_block_predictor_matrix(block_predictor_matrix, names, blocks)
    if block_pred is None and any(is_multivariate_method(m) for m in methods.values()):
        block_pred = make_block_predictor_matrix(names, blocks)
    rng = np.random.default_rng(seed)
    post_map = normalize_post(names, post)

    work = matrix.copy()
    imp = initialize_imputations(
        work,
        names,
        m,
        where,
        observed,
        ignore,
        blocks,
        visit_sequence,
        methods,
        rng,
        data_init=data_init,
    )

    chain_mean: dict[str, NDArray[np.float64]] = {}
    chain_var: dict[str, NDArray[np.float64]] = {}
    for name in names:
        if name in imp:
            chain_mean[name] = np.full((max(maxit, 1), m), np.nan)
            chain_var[name] = np.full((max(maxit, 1), m), np.nan)

    if maxit > 0:
        _sampler(
            work,
            names,
            specs,
            m,
            maxit,
            observed,
            where,
            ignore,
            imp,
            blocks,
            methods,
            visit_sequence,
            predictor_matrix,
            block_pred,
            rng,
            chain_mean,
            chain_var,
            print_flag,
            n_burn=n_burn,
            n_iter=n_iter,
            random_l1=random_l1,
            prior=prior,
            post=post_map,
            post_extras=post_extras or {},
        )

    nmis = {name: int(np.sum(where[:, j])) for j, name in enumerate(names)}
    return Mids(
        data=matrix,
        column_names=names,
        imp=imp,
        m=m,
        where=where,
        method=methods,
        predictor_matrix=predictor_matrix,
        visit_sequence=visit_sequence,
        blocks=blocks,
        iteration=maxit,
        seed=seed,
        nmis=nmis,
        chain_mean=chain_mean,
        chain_var=chain_var,
        ignore=ignore,
        variable_specs=specs,
        block_predictor_matrix=block_pred,
        post={k: (v if isinstance(v, str) else "<callable>") for k, v in post_map.items()},
    )


def _normalize_block_predictor_matrix(
    block_predictor_matrix: dict[str, list[int] | NDArray[np.int_]] | None,
    column_names: list[str],
    blocks: dict[str, list[str]],
) -> dict[str, NDArray[np.int_]] | None:
    del blocks
    if block_predictor_matrix is None:
        return None
    out: dict[str, NDArray[np.int_]] = {}
    n = len(column_names)
    for block_name, row in block_predictor_matrix.items():
        arr = np.asarray(row, dtype=np.int_)
        if arr.shape != (n,):
            raise ValueError(f"block_predictor_matrix['{block_name}'] must have length {n}")
        out[block_name] = arr
    return out


def _sampler(
    data: NDArray[np.float64],
    column_names: list[str],
    specs: list[VariableSpec],
    m: int,
    maxit: int,
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
    ignore: NDArray[np.bool_],
    imp: dict[str, NDArray[np.float64]],
    blocks: dict[str, list[str]],
    method: dict[str, str],
    visit_sequence: list[str],
    predictor_matrix: NDArray[np.int_],
    block_predictor_matrix: dict[str, NDArray[np.int_]] | None,
    rng: np.random.Generator,
    chain_mean: dict[str, NDArray[np.float64]],
    chain_var: dict[str, NDArray[np.float64]],
    print_flag: bool,
    *,
    n_burn: int,
    n_iter: int,
    random_l1: str,
    prior: object | None,
    post: dict[str, PostHook],
    post_extras: dict[str, object],
) -> None:
    """Main Gibbs sampler loop (mirrors R ``sampler()``)."""
    for iteration in range(1, maxit + 1):
        if print_flag:
            print("\n iter imp variable")

        for imp_num in range(m):
            if print_flag:
                print(f"  {iteration}  {imp_num + 1}", end="")

            _apply_imputations(
                data, column_names, imp, observed, where, imp_num, visit_sequence, blocks
            )

            for block in visit_sequence:
                meth = method[block]
                if meth == "":
                    continue
                if print_flag:
                    print(f" {block}", end="")

                if is_passive(meth):
                    if len(blocks[block]) != 1:
                        raise ValueError("passive imputation requires a univariate block")
                    name = blocks[block][0]
                    j = column_names.index(name)
                    wy = where[:, j]
                    drawn = evaluate_passive(meth, data, column_names, wy)
                    imp[name][:, imp_num] = drawn
                    widx = where_indices(where[:, j])
                    missing_in_where = ~observed[widx, j]
                    data[widx[missing_in_where], j] = imp[name][missing_in_where, imp_num]
                    continue

                pred_row = predictor_row_for_block(
                    block,
                    column_names,
                    predictor_matrix,
                    blocks,
                    block_predictor_matrix=block_predictor_matrix,
                )

                if is_multivariate_method(meth):
                    impute_fn = get_multivariate_method(meth)
                    drawn_map = impute_fn(
                        data=data,
                        column_names=column_names,
                        block_vars=blocks[block],
                        type_row=pred_row,
                        observed=observed,
                        where=where,
                        ignore=ignore,
                        rng=rng,
                        n_burn=n_burn,
                        n_iter=n_iter,
                        random_l1=random_l1,
                        prior=prior,
                        variable_specs=specs,
                    )
                    for name, drawn in drawn_map.items():
                        j = column_names.index(name)
                        imp[name][:, imp_num] = drawn
                        widx = where_indices(where[:, j])
                        missing_in_where = ~observed[widx, j]
                        data[widx[missing_in_where], j] = drawn[missing_in_where]
                    continue

                impute_fn = get_method(meth)

                for name in blocks[block]:
                    j = column_names.index(name)
                    widx = where_indices(where[:, j])
                    if widx.size == 0:
                        continue

                    type_row = predictor_matrix[j, :]
                    pred_idx = [c for c in range(len(type_row)) if c != j and type_row[c] != 0]
                    if meth.startswith("2l.") or meth == "2lonly.mean":
                        x = data[:, pred_idx].astype(np.float64)
                    else:
                        x = obtain_design(data, j, pred_idx, specs)
                    y = data[:, j]
                    spec = specs[j]

                    wy = where[:, j]
                    ry = _complete_cases(x, y) & observed[:, j] & ~ignore
                    keep = remove_lindep(x, y, ry)
                    x = x[:, keep]
                    ry = _complete_cases(x, y) & observed[:, j] & ~ignore

                    if not np.any(wy):
                        continue

                    kwargs: dict[str, object] = {}
                    if meth.startswith("2l.") or meth == "2lonly.mean":
                        kwargs["type"] = type_row[pred_idx]
                    if meth.startswith("2l."):
                        kwargs["n_iter"] = n_iter
                    if meth in ("polyreg", "polr") and spec.levels:
                        kwargs["levels"] = spec.levels
                    if meth == "cart" and spec.kind != VariableKind.NUMERIC:
                        kwargs["levels"] = spec.levels
                        kwargs["classification"] = True
                    if meth == "2lonly.mean":
                        kwargs["levels"] = spec.levels
                        kwargs["kind"] = spec.kind
                    y_fit = y
                    if meth == "logreg" and spec.kind == VariableKind.BINARY:
                        lo, hi = spec.levels[0], spec.levels[1]
                        y_fit = (y == hi).astype(np.float64)

                    drawn = impute_fn(y=y_fit, ry=ry, x=x, wy=wy, rng=rng, **kwargs)
                    if meth == "logreg" and spec.kind == VariableKind.BINARY:
                        lo, hi = spec.levels[0], spec.levels[1]
                        drawn = np.where(drawn > 0.5, hi, lo).astype(np.float64)
                    imp[name][:, imp_num] = drawn
                    _apply_post(
                        name,
                        j,
                        data,
                        column_names,
                        imp,
                        observed,
                        where,
                        imp_num,
                        post,
                        post_extras,
                    )

        k2 = iteration - 1
        for block in visit_sequence:
            for name in blocks[block]:
                if name not in imp:
                    continue
                chain_mean[name][k2, :] = np.nanmean(imp[name], axis=0)
                chain_var[name][k2, :] = np.nanvar(imp[name], axis=0)

        if print_flag:
            print()


def _apply_post(
    name: str,
    j: int,
    data: NDArray[np.float64],
    column_names: list[str],
    imp: dict[str, NDArray[np.float64]],
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
    imp_num: int,
    post: dict[str, PostHook],
    post_extras: dict[str, object],
) -> None:
    cmd = post.get(name, "")
    if not cmd:
        widx = where_indices(where[:, j])
        missing_in_where = ~observed[widx, j]
        data[widx[missing_in_where], j] = imp[name][missing_in_where, imp_num]
        return
    ctx = PostContext(
        imp=imp,
        data=data,
        column_names=column_names,
        name=name,
        imp_num=imp_num,
        observed=observed,
        where=where,
        extras=dict(post_extras),
    )
    execute_post(cmd, ctx)
    widx = where_indices(where[:, j])
    missing_in_where = ~observed[widx, j]
    data[widx[missing_in_where], j] = imp[name][missing_in_where, imp_num]


def _apply_imputations(
    data: NDArray[np.float64],
    column_names: list[str],
    imp: dict[str, NDArray[np.float64]],
    observed: NDArray[np.bool_],
    where: NDArray[np.bool_],
    imp_num: int,
    visit_sequence: list[str],
    blocks: dict[str, list[str]],
) -> None:
    """Write current imputation draw into working data (missing cells only)."""
    for block in visit_sequence:
        for name in blocks[block]:
            j = column_names.index(name)
            missing = (~observed[:, j]) & where[:, j]
            if not np.any(missing):
                continue
            wy = where[:, j]
            data[missing, j] = imp[name][missing[wy], imp_num]


def _complete_cases(x: NDArray[np.float64], y: NDArray[np.float64]) -> NDArray[np.bool_]:
    return np.isfinite(x).all(axis=1) & np.isfinite(y)


def _complete_cases_x(x: NDArray[np.float64]) -> NDArray[np.bool_]:
    return np.isfinite(x).all(axis=1)
