"""Parallel MICE chains (``futuremice`` analogue)."""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

import numpy as np

from pymice.engine import mice
from pymice.types import Mids


def _run_chain(args: tuple[int, dict[str, Any]]) -> Mids:
    index, kwargs = args
    kw = dict(kwargs)
    kw["m"] = 1
    base_seed = kw.get("seed")
    if base_seed is not None:
        kw["seed"] = int(base_seed) + index
    return mice(**kw)


def merge_mids(results: list[Mids]) -> Mids:
    """Combine ``m`` single-chain ``Mids`` objects into one object."""
    if not results:
        raise ValueError("no mids objects to merge")
    base = results[0]
    m = len(results)
    imp: dict[str, np.ndarray] = {}
    for name in base.imp:
        cols = [res.imp[name][:, 0:1] for res in results]
        imp[name] = np.hstack(cols)
    return Mids(
        data=base.data.copy(),
        column_names=list(base.column_names),
        imp=imp,
        m=m,
        where=base.where.copy(),
        method=dict(base.method),
        predictor_matrix=base.predictor_matrix.copy(),
        visit_sequence=list(base.visit_sequence),
        blocks={k: list(v) for k, v in base.blocks.items()},
        iteration=base.iteration,
        seed=base.seed,
        nmis=dict(base.nmis),
        chain_mean={k: v.copy() for k, v in base.chain_mean.items()},
        chain_var={k: v.copy() for k, v in base.chain_var.items()},
        ignore=base.ignore.copy() if base.ignore is not None else None,
        variable_specs=list(base.variable_specs),
        block_predictor_matrix=(
            {k: v.copy() for k, v in base.block_predictor_matrix.items()}
            if base.block_predictor_matrix is not None
            else None
        ),
        post=dict(base.post) if base.post is not None else None,
    )


def parallel_mice(
    data: Any,
    *,
    m: int = 5,
    n_jobs: int | None = None,
    **kwargs: Any,
) -> Mids:
    """
    Run independent imputation chains in parallel (R ``futuremice`` workflow).

    Each chain uses ``m=1`` internally; results are merged into one ``Mids``.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    if m == 1:
        return mice(data, m=1, **kwargs)

    workers = n_jobs or min(m, os.cpu_count() or 1)
    chain_kwargs = {"data": data, **kwargs}
    tasks = [(i, chain_kwargs) for i in range(m)]

    if workers == 1:
        return merge_mids([_run_chain(t) for t in tasks])

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_run_chain, t): t[0] for t in tasks}
        ordered: list[Mids | None] = [None] * m
        for fut in as_completed(futures):
            idx = futures[fut]
            ordered[idx] = fut.result()
    return merge_mids([r for r in ordered if r is not None])
