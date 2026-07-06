"""Construct and bind ``Mids`` objects (R ``as.mids``, ``cbind.mids``, ``rbind.mids``)."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pymice.types import Mids


def as_mids(
    data: NDArray[np.floating],
    imp: dict[str, NDArray[np.floating]],
    *,
    column_names: list[str] | None = None,
    m: int | None = None,
    where: NDArray[np.bool_] | None = None,
    method: dict[str, str] | None = None,
    predictor_matrix: NDArray[np.int_] | None = None,
    visit_sequence: list[str] | None = None,
    blocks: dict[str, list[str]] | None = None,
    nmis: dict[str, int] | None = None,
    iteration: int = 0,
    seed: int | None = None,
    chain_mean: dict[str, NDArray[np.floating]] | None = None,
    chain_var: dict[str, NDArray[np.floating]] | None = None,
    logged_events: list[dict[str, int | str]] | None = None,
    **kwargs: Any,
) -> Mids:
    """Construct a ``Mids`` object from components (R ``as.mids()`` / ``mids()``)."""
    del kwargs
    data = np.asarray(data, dtype=np.float64)
    if column_names is None:
        column_names = [f"V{i + 1}" for i in range(data.shape[1])]
    if m is None:
        m = int(next(iter(imp.values())).shape[1]) if imp else 0
    if where is None:
        where = np.isnan(data)
    if method is None:
        method = {name: "" for name in column_names}
    if predictor_matrix is None:
        n = len(column_names)
        predictor_matrix = np.zeros((n, n), dtype=np.int_)
    if visit_sequence is None:
        visit_sequence = list(column_names)
    if blocks is None:
        blocks = {name: [name] for name in column_names}
    if nmis is None:
        nmis = {name: int(np.sum(where[:, j])) for j, name in enumerate(column_names)}

    return Mids(
        data=data.copy(),
        column_names=list(column_names),
        imp={k: np.asarray(v, dtype=np.float64).copy() for k, v in imp.items()},
        m=int(m),
        where=np.asarray(where, dtype=bool),
        method=dict(method),
        predictor_matrix=np.asarray(predictor_matrix, dtype=np.int_),
        visit_sequence=list(visit_sequence),
        blocks=dict(blocks),
        iteration=int(iteration),
        seed=seed,
        nmis=dict(nmis),
        chain_mean={k: v.copy() for k, v in (chain_mean or {}).items()},
        chain_var={k: v.copy() for k, v in (chain_var or {}).items()},
        logged_events=list(logged_events or []),
    )


def cbind_mids(x: Mids, y: Mids | NDArray[np.floating], **bind_kwargs: Any) -> Mids:
    """Bind columns onto a ``Mids`` object (R ``cbind.mids()``)."""
    if isinstance(y, Mids):
        if y.n_obs != x.n_obs:
            raise ValueError("cbind_mids requires equal number of rows")
        new_names = list(x.column_names) + [n for n in y.column_names if n not in x.column_names]
        new_data = np.column_stack(
            [x.data, y.data[:, [y.column_names.index(n) for n in new_names[len(x.column_names) :]]]]
        )
        new_imp = dict(x.imp)
        for name in y.column_names:
            if name in new_imp:
                continue
            new_imp[name] = y.imp.get(name, np.full((int(np.sum(x.where[:, 0])), y.m), np.nan))
        new_where = np.column_stack([x.where, y.where])
        new_method = {**x.method, **y.method}
        n_x = x.predictor_matrix.shape[0]
        n_y = y.predictor_matrix.shape[0]
        pred = np.zeros((n_x + n_y, n_x + n_y), dtype=np.int_)
        pred[:n_x, :n_x] = x.predictor_matrix
        pred[n_x:, n_x:] = y.predictor_matrix
        return as_mids(
            new_data,
            new_imp,
            column_names=new_names,
            m=x.m,
            where=new_where,
            method=new_method,
            predictor_matrix=pred,
            visit_sequence=list(x.visit_sequence)
            + [v for v in y.visit_sequence if v not in x.visit_sequence],
            blocks={**x.blocks, **y.blocks},
            nmis={**x.nmis, **y.nmis},
            iteration=x.iteration,
            seed=x.seed,
            chain_mean={**x.chain_mean, **y.chain_mean},
            chain_var={**x.chain_var, **y.chain_var},
            logged_events=list(x.logged_events) + list(y.logged_events),
            **bind_kwargs,
        )

    arr = np.asarray(y, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.shape[0] != x.n_obs:
        raise ValueError("cbind_mids matrix must have nrow(data) rows")
    name = bind_kwargs.get("name", f"V{arr.shape[1]}")
    names = [*list(x.column_names), name]
    return as_mids(
        np.column_stack([x.data, arr]),
        x.imp,
        column_names=names,
        m=x.m,
        where=np.column_stack([x.where, np.isnan(arr)]),
        method=x.method,
        predictor_matrix=np.pad(x.predictor_matrix, ((0, 1), (0, 1))),
        visit_sequence=x.visit_sequence,
        blocks=x.blocks,
        nmis=x.nmis,
        iteration=x.iteration,
        seed=x.seed,
    )


def rbind_mids(x: Mids, y: Mids) -> Mids:
    """Stack observations on two ``Mids`` objects (R ``rbind.mids()``)."""
    if x.column_names != y.column_names:
        raise ValueError("rbind_mids requires identical column names")
    if x.m != y.m:
        raise ValueError("rbind_mids requires equal m")
    new_data = np.vstack([x.data, y.data])
    new_where = np.vstack([x.where, y.where])
    new_imp = {}
    for name in x.column_names:
        xi = x.imp.get(name)
        yi = y.imp.get(name)
        if xi is not None and yi is not None:
            new_imp[name] = np.vstack([xi, yi])
        elif xi is not None:
            new_imp[name] = xi.copy()
        elif yi is not None:
            new_imp[name] = yi.copy()
    return as_mids(
        new_data,
        new_imp,
        column_names=list(x.column_names),
        m=x.m,
        where=new_where,
        method=x.method,
        predictor_matrix=x.predictor_matrix.copy(),
        visit_sequence=list(x.visit_sequence),
        blocks=dict(x.blocks),
        nmis={name: int(np.sum(new_where[:, j])) for j, name in enumerate(x.column_names)},
        iteration=max(x.iteration, y.iteration),
        seed=x.seed,
        chain_mean=x.chain_mean,
        chain_var=x.chain_var,
        logged_events=list(x.logged_events) + list(y.logged_events),
    )
